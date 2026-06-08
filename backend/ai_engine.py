import google.generativeai as genai
import json
import os

import random

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        k, v = line.strip().split('=', 1)
                        os.environ[k.strip()] = v.strip()
        except:
            pass

load_env()

keys_str = os.environ.get("BRAIN_API_KEYS", "")
BRAIN_API_KEYS = [k.strip() for k in keys_str.split(",") if k.strip()]
if not BRAIN_API_KEYS:
    BRAIN_API_KEYS = ["PLEASE_SET_API_KEYS_IN_ENV"]

def get_configured_model(model_name='gemini-2.5-flash'):
    key = random.choice(BRAIN_API_KEYS)
    genai.configure(api_key=key)
    return genai.GenerativeModel(model_name)

def get_intent_from_prompt(user_input: str):
    system_prompt = """
    You are the brain of MAVERIK, an AI Operating System for Windows 11.
    Your job is to analyze the user's natural language command and output a JSON response 
    determining the intent and parameters.
    
    DO NOT output anything other than raw JSON.
    
    Supported intents:
    # Basic
    - open_website: { "intent": "open_website", "parameters": { "url": "website url" }, "response": "Opening website for you." }
      Examples of URLs: youtube.com, google.com, github.com, mail.google.com (for Gmail), linkedin.com, chatgpt.com, claude.ai, perplexity.ai, x.com, instagram.com, facebook.com, netflix.com, amazon.com, reddit.com, open.spotify.com, web.whatsapp.com, discord.com, figma.com, canva.com.
    
    - search_website: { "intent": "search_website", "parameters": { "target": "youtube/github/google/amazon/wikipedia/leetcode/etc", "query": "search query" }, "response": "Searching website." }
    
    - open_application: { "intent": "open_application", "parameters": { "app_name": "app name" }, "response": "Opening application." }
      Supported apps include: Chrome, Edge, Word, Excel, PowerPoint, VS Code, Codex, Trae, Copilot, Microsoft Store, Lenovo Vantage, Photos, Settings, Calculator, Paint, PC Manager, Smart Connect, Notepad, File Explorer, Task Manager, Control Panel, Downloads, Documents, Desktop.
      
    - search_google: { "intent": "search_google", "parameters": { "query": "search query" }, "response": "Searching Google." }
    - system_info: { "intent": "system_info", "parameters": {}, "response": "Getting system information." }
    - chat: { "intent": "chat", "parameters": {}, "response": "conversational response" }
    
    # Custom App Learning
    - learn_app_path: { "intent": "learn_app_path", "parameters": { "app_name": "Cursor", "path": "C:\\path\\to\\app.exe" }, "response": "I'll remember that application." }

    # Clipboard Manager
    - clipboard_action: { "intent": "clipboard_action", "parameters": { "action": "show|copy|save|clear", "content": "optional text to copy", "path": "optional file path to save to" }, "response": "Clipboard action performed." }

    # Email System
    - email_action: { "intent": "email_action", "parameters": { "recipient": "email@example.com", "subject": "Subject", "body": "Body" }, "response": "Generating email preview." }

    # Favorites System
    - favorite_action: { "intent": "favorite_action", "parameters": { "action": "add|open", "name": "favorite name", "path": "optional path to add" }, "response": "Favorites action performed." }

    # Downloads Manager
    - downloads_action: { "intent": "downloads_action", "parameters": { "action": "show_recent|delete_installers|organize" }, "response": "Managing downloads." }

    # Folder Operations
    - open_folder: { "intent": "open_folder", "parameters": { "folder": "folder name or path" }, "response": "Opening folder." }
    - create_folder: { "intent": "create_folder", "parameters": { "path": "folder name or path" }, "response": "Folder created." }
    - rename_folder: { "intent": "rename_folder", "parameters": { "old_name": "...", "new_name": "..." }, "response": "Folder renamed." }
    - move_folder: { "intent": "move_folder", "parameters": { "source": "...", "destination": "..." }, "response": "Folder moved." }
    - delete_folder: { "intent": "delete_folder", "parameters": { "path": "...", "confirmed": true/false }, "response": "Folder deleted." }
    - search_folder: { "intent": "search_folder", "parameters": { "query": "..." }, "response": "Searching for folder." }
    
    # File Operations
    - open_file: { "intent": "open_file", "parameters": { "path": "file name or path" }, "response": "Opening file." }
    - create_file: { "intent": "create_file", "parameters": { "path": "file name", "content": "optional content" }, "response": "File created." }
    - write_to_file: { "intent": "write_to_file", "parameters": { "path": "...", "content": "..." }, "response": "Wrote to file." }
    - append_to_file: { "intent": "append_to_file", "parameters": { "path": "...", "content": "..." }, "response": "Appended to file." }
    - read_file: { "intent": "read_file", "parameters": { "path": "..." }, "response": "Reading file." }
    - rename_file: { "intent": "rename_file", "parameters": { "old_name": "...", "new_name": "..." }, "response": "File renamed." }
    - move_file: { "intent": "move_file", "parameters": { "source": "...", "destination": "..." }, "response": "File moved." }
    - copy_file: { "intent": "copy_file", "parameters": { "source": "...", "destination": "..." }, "response": "File copied." }
    - delete_file: { "intent": "delete_file", "parameters": { "path": "...", "confirmed": true/false }, "response": "File deleted." }
    - search_file: { "intent": "search_file", "parameters": { "query": "file name keyword", "extension": "pdf, docx, mp4, etc or null", "min_size": "integer in bytes or null if not specified" }, "response": "Searching for file." }
    - file_info: { "intent": "file_info", "parameters": { "path": "..." }, "response": "Getting file details." }
    
    # Notepad Operations
    - notepad_write: { "intent": "notepad_write", "parameters": { "content": "...", "path": "optional file name" }, "response": "Opening Notepad." }
    
    # Bulk Operations
    - create_multiple_files: { "intent": "create_multiple_files", "parameters": { "files": ["file1.ext", "file2.ext"] }, "response": "Created files." }
    - create_project_structure: { "intent": "create_project_structure", "parameters": { "type": "react/python etc", "path": "project name" }, "response": "Creating project." }
    - organize_folder: { "intent": "organize_folder", "parameters": { "path": "folder name" }, "response": "Organizing folder." }

    # Time & Timers
    - get_time: { "intent": "get_time", "parameters": {}, "response": "The current time is..." }
    - get_date: { "intent": "get_date", "parameters": {}, "response": "Today's date is..." }
    - start_timer: { "intent": "start_timer", "parameters": { "duration_seconds": 1500, "name": "Study Timer" }, "response": "Starting timer." }
    - stop_timer: { "intent": "stop_timer", "parameters": { "timer_id": "optional string ID" }, "response": "Stopping timer." }
    
    # Window Management
    - window_action: { "intent": "window_action", "parameters": { "action": "open|close|minimize|maximize|restore|switch|focus|arrange", "target": "Chrome/Notepad/all etc", "layout": "side_by_side|cascade|tile|split_left|split_right" }, "response": "Managing windows." }

    IMPORTANT RULE FOR DELETION:
    If the user asks to delete a file or folder, always include a boolean "confirmed" parameter. 
    Set it to `false` UNLESS the user explicitly says "Yes, delete it" or explicitly confirms the deletion in the same prompt.

    Example 1:
    User: "Search YouTube for React Tutorial"
    {"intent": "search_website", "parameters": {"target": "youtube", "query": "React Tutorial"}, "response": "Searching YouTube for React Tutorial."}
    
    Example 2:
    User: "Remember that Cursor is at C:\\Users\\Shubham\\AppData\\Local\\Programs\\Cursor\\Cursor.exe"
    {"intent": "learn_app_path", "parameters": {"app_name": "Cursor", "path": "C:\\Users\\Shubham\\AppData\\Local\\Programs\\Cursor\\Cursor.exe"}, "response": "I'll remember that application."}
    
    Example 3:
    User: "Send email to bob@example.com about meeting"
    {"intent": "email_action", "parameters": {"recipient": "bob@example.com", "subject": "Meeting", "body": "Hi Bob,\\n\\nLet's schedule a meeting.\\n\\nThanks"}, "response": "Opening mail client with your email draft."}
    """
    
    import time
    last_error = None
    
    for attempt in range(5):
        try:
            model = get_configured_model()
            response = model.generate_content([system_prompt, f"User: {user_input}"])
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()
            return json.loads(text)
        except Exception as e:
            last_error = e
            if "429" in str(e):
                print(f"Rate limit hit, retrying with new key... (Attempt {attempt+1}/5)")
                time.sleep(1.5)  # Pause to let the quota refresh slightly
                continue
            else:
                break
                
    print(f"AI Engine error: {last_error}")
    return {
        "success": False,
        "response": f"AI Error: {str(last_error)}",
        "intent": "chat",
        "parameters": {}
    }

import io
from PIL import ImageGrab
import pyperclip

def analyze_clipboard_content():
    try:
        # Check if clipboard contains an image first
        image = ImageGrab.grabclipboard()
        if image is not None:
            img_byte_arr = io.BytesIO()
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(img_byte_arr, format='PNG')
            
            prompt = "Analyze this image from the clipboard. Describe what it is, any text present, and relevant context."
            vision_model = get_configured_model("gemini-2.5-flash")
            image_parts = [{"mime_type": "image/png", "data": img_byte_arr.getvalue()}]
            response = vision_model.generate_content([prompt, image_parts[0]])
            return response.text

        # Otherwise, assume it's text
        clipboard_text = pyperclip.paste()
        if not clipboard_text or not clipboard_text.strip():
            return "The clipboard is currently empty or contains unsupported data."
            
        prompt = f"""
        Analyze the following text that was copied to the clipboard. 
        Provide a concise summary, highlight any key entities (like links, emails, or action items), 
        and suggest what the user might want to do with this content.
        
        Clipboard Content:
        "{clipboard_text}"
        """
        text_model = get_configured_model()
        response = text_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing clipboard: {str(e)}"

def analyze_screenshot_image(image_data: bytes):
    try:
        prompt = "Analyze this screenshot. Describe what applications are open, what the user is currently looking at, and any prominent text or context."
        
        vision_model = get_configured_model("gemini-2.5-flash")
        
        image_parts = [
            {
                "mime_type": "image/png",
                "data": image_data
            }
        ]
        
        response = vision_model.generate_content([prompt, image_parts[0]])
        return response.text
    except Exception as e:
        return f"Error analyzing screenshot: {str(e)}"
