import os
import time
import shutil
import json
import urllib.parse
from command_router import execute_intent, get_user_profile

def print_header(title):
    print(f"\n{'='*50}")
    print(f" {title} ")
    print(f"{'='*50}")

def print_result(name, result):
    status = "[PASS]" if result.success else "[FAIL]"
    print(f"{status} {name}: {result.message}")

def wait_for_user():
    print("Waiting 2 seconds before continuing...")
    time.sleep(2)

def test_applications():
    print_header("APPLICATION LAUNCH TESTS")
    apps = [
        "chrome", "edge", "word", "excel", "powerpoint", "vscode", 
        "copilot", "microsoft store", "lenovo vantage", "photos", 
        "settings", "calculator", "paint", "pc manager", "smart connect", 
        "notepad", "file explorer", "task manager", "control panel", 
        "downloads", "desktop", "documents"
    ]
    
    for app in apps:
        # For folders, command router opens explorer, we can just use the mapped string
        res = execute_intent("open_application", {"app_name": app})
        print_result(app.upper(), res)
        time.sleep(1) # Small pause to let windows open

def test_websites():
    print_header("WEBSITE TESTS")
    sites = [
        "youtube.com", "google.com", "github.com", "linkedin.com", 
        "gmail.com", "chatgpt.com", "claude.ai", "perplexity.ai", 
        "reddit.com", "amazon.com", "spotify.com", "discord.com", 
        "web.whatsapp.com", "figma.com", "canva.com", "drive.google.com", 
        "docs.google.com", "sheets.google.com", "slides.google.com"
    ]
    
    for site in sites:
        res = execute_intent("open_website", {"url": site})
        print_result(site, res)
        time.sleep(1)

def test_file_system():
    print_header("FILE SYSTEM TESTS")
    test_dir = os.path.join(get_user_profile(), "Desktop", "maverik_verification_dir")
    test_file = os.path.join(test_dir, "test_file.txt")
    renamed_file = os.path.join(test_dir, "renamed_file.txt")
    copy_dir = os.path.join(get_user_profile(), "Desktop", "maverik_verification_copy")
    
    # Clean up first
    if os.path.exists(test_dir): shutil.rmtree(test_dir)
    if os.path.exists(copy_dir): shutil.rmtree(copy_dir)

    print_result("Create Folder", execute_intent("create_folder", {"path": test_dir}))
    print_result("Create File", execute_intent("create_file", {"path": test_file, "content": "Initial Content"}))
    print_result("Write File", execute_intent("write_to_file", {"path": test_file, "content": "Written Content"}))
    print_result("Append File", execute_intent("append_to_file", {"path": test_file, "content": "Appended Content"}))
    
    read_res = execute_intent("read_file", {"path": test_file})
    print_result("Read File", read_res)
    if read_res.success: print(f"   -> Content: {repr(read_res.details)}")
        
    print_result("Rename File", execute_intent("rename_file", {"old_name": test_file, "new_name": renamed_file}))
    
    # Create copy dir
    execute_intent("create_folder", {"path": copy_dir})
    copied_file = os.path.join(copy_dir, "renamed_file.txt")
    print_result("Copy File", execute_intent("copy_file", {"source": renamed_file, "destination": copy_dir}))
    
    print_result("Move File", execute_intent("move_file", {"source": copied_file, "destination": os.path.join(test_dir, "moved_file.txt")}))
    
    print_result("Delete File", execute_intent("delete_file", {"path": os.path.join(test_dir, "moved_file.txt")}))
    
    # Move folder
    print_result("Rename Folder", execute_intent("rename_folder", {"old_name": test_dir, "new_name": test_dir + "_renamed"}))
    renamed_dir = test_dir + "_renamed"
    
    print_result("Move Folder", execute_intent("move_folder", {"source": renamed_dir, "destination": copy_dir}))
    
    # Open Folder (Visual)
    print_result("Open Folder", execute_intent("open_folder", {"path": copy_dir}))
    
    # Delete Folders
    print_result("Delete Folder", execute_intent("delete_folder", {"path": copy_dir}))

def test_search():
    print_header("SEARCH TESTS")
    print("Note: Fast search requires indexing. Assuming search_engine is operational.")
    
    res = execute_intent("search_file", {"query": "python", "extension": ".py"})
    print_result("Search Python Files", res)
    if res.success: print(f"   -> Found {len(json.loads(res.details))} files")
        
    res = execute_intent("search_folder", {"query": "project"})
    print_result("Search Folders (project)", res)
    if res.success: print(f"   -> Found {len(json.loads(res.details))} folders")

def test_notepad():
    print_header("NOTEPAD AUTOMATION TESTS")
    temp_note = os.path.join(get_user_profile(), "Desktop", "notepad_test.txt")
    print_result("Notepad Write/Open", execute_intent("notepad_write", {"path": temp_note, "content": "This is an automated test from Maverik."}))

if __name__ == "__main__":
    print("Starting Maverik Comprehensive Verification Suite")
    
    wait_for_user()
    test_file_system()
    
    wait_for_user()
    test_search()
    
    wait_for_user()
    test_notepad()
    
    print("\nWARNING: The next tests will open many applications and browser tabs.")
    wait_for_user()
    test_websites()
    
    wait_for_user()
    test_applications()
    
    print("\nVerification Complete.")
