from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

from database import init_db, add_chat_message, get_chat_history, add_command_history, get_command_history, get_setting, set_setting, clear_chat_history, clear_command_history
from system_monitor import get_system_stats
from command_router import execute_intent
from ai_engine import get_intent_from_prompt, analyze_clipboard_content, analyze_screenshot_image
from search_engine import search_engine
import timers
import base64

app = FastAPI(title="Maverik AI Backend")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()
    # Start the background file indexer
    search_engine.start_background_indexer()

class CommandRequest(BaseModel):
    command: str

@app.get("/api/system-stats")
def system_stats():
    return get_system_stats()

@app.get("/api/timers")
def active_timers():
    timers.clear_finished_timers()
    return timers.get_active_timers()

@app.get("/api/search")
def search_api(query: str = "", ext: str = None, min_size: int = None, limit: int = 50):
    results = search_engine.search(query, ext, min_size, limit)
    return {"status": "success", "results": results}

@app.get("/api/recent-files")
def recent_files_api(limit: int = 10):
    results = search_engine.get_recent_files(limit)
    return {"status": "success", "results": results}

class TrackOpenRequest(BaseModel):
    path: str

@app.post("/api/track-open")
def track_open_api(req: TrackOpenRequest):
    search_engine.track_file_open(req.path)
    return {"status": "success"}

@app.get("/api/history")
def history():
    return get_command_history()

@app.get("/api/chat")
def chat_history():
    return get_chat_history()

@app.delete("/api/history")
def delete_history():
    clear_command_history()
    return {"status": "success"}

@app.delete("/api/chat")
def delete_chat():
    clear_chat_history()
    return {"status": "success"}

class AnalyzeScreenshotRequest(BaseModel):
    region: bool = False

@app.post("/api/analyze-screenshot")
def analyze_screenshot(req: AnalyzeScreenshotRequest):
    try:
        from PIL import ImageGrab
        import io
        
        # Grab full screen
        image = ImageGrab.grab()
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        
        analysis = analyze_screenshot_image(img_byte_arr.getvalue())
        add_chat_message("user", "Analyze Screen")
        add_chat_message("maverik", analysis, action_type="screen_analysis", status="Completed")
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/analyze-clipboard")
def analyze_clipboard():
    try:
        analysis = analyze_clipboard_content()
        add_chat_message("user", "Analyze Clipboard")
        add_chat_message("maverik", analysis, action_type="clipboard_analysis", status="Completed")
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/tts")
def generate_tts(req: CommandRequest):
    import requests
    import os
    
    # User's provided Voice API key
    TTS_API_KEY = os.environ.get("GEMINI_VOICE_API_KEY", "PLEASE_SET_API_KEY_IN_ENV")
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={TTS_API_KEY}"
    
    payload = {
        "input": {"text": req.command},
        # You can use a standard voice or a Journey voice
        "voice": {"languageCode": "en-US", "name": "en-US-Journey-F"},
        "audioConfig": {"audioEncoding": "MP3"}
    }
    
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return {"status": "success", "audioContent": data["audioContent"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/command")
def process_command(req: CommandRequest):
    start_time = time.time()
    user_input = req.command
    
    # Save user message to chat
    add_chat_message("user", user_input)
    
    # Get Intent from AI
    ai_response = get_intent_from_prompt(user_input)
    intent = ai_response.get("intent") or "chat"
    parameters = ai_response.get("parameters") or {}
    response_text = ai_response.get("response") or "I have processed your command."
    
    print(f"[Maverik] Input: '{user_input}' -> Intent: '{intent}', Params: {parameters}")
    
    # Execute Intent
    result_details = ""
    if intent == "system_info":
        stats = get_system_stats()
        response_text = f"CPU is at {stats['cpu']['percent']}%, RAM at {stats['ram']['percent']}%. " + response_text
        result_success = True
    elif intent in ["delete_folder", "delete_file"] and not parameters.get("confirmed", False):
        response_text = response_text or "Are you sure you want to delete this? Please reply 'Yes, delete it' to confirm."
        result_success = True
        intent = "chat"
    elif intent != "chat":
        result = execute_intent(intent, parameters)
        result_success = result.success
        result_details = result.details
        print(f"[Maverik] Execution result: success={result.success}, message='{result.message}'")
        if not result.success:
            response_text = result.message
    else:
        result_success = True
        
    execution_time = round(time.time() - start_time, 2)
    status_str = "Completed" if result_success else "Failed"
    
    # Save AI response to chat
    add_chat_message("maverik", response_text, action_type=intent, status=status_str)
    
    # If it was an action command, add to command history
    if intent != "chat":
        add_command_history(user_input, intent, status_str, execution_time)
        
    return {
        "intent": intent,
        "parameters": parameters,
        "response": response_text,
        "details": result_details,
        "success": result_success,
        "execution_time": execution_time
    }

class SettingRequest(BaseModel):
    key: str
    value: str

@app.post("/api/settings")
def save_setting(req: SettingRequest):
    set_setting(req.key, req.value)
    return {"status": "success"}

@app.get("/api/settings/{key}")
def retrieve_setting(key: str):
    value = get_setting(key)
    return {"key": key, "value": value}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
