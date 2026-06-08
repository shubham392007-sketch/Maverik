import os
import subprocess
import webbrowser
import shutil
import glob
import json
import urllib.parse
import pyperclip
from datetime import datetime
from search_engine import search_engine
from database import get_custom_app_path, add_custom_app, get_favorite, add_favorite

class CommandResult:
    def __init__(self, success: bool, message: str, details: str = ""):
        self.success = success
        self.message = message
        self.details = details

def get_user_profile() -> str:
    return os.environ.get("USERPROFILE", "C:\\")

def resolve_path(path_str) -> str:
    """Helper to resolve paths like 'downloads' to actual paths"""
    # Handle None or empty values from AI engine
    if not path_str or str(path_str).strip().lower() in ('none', 'null', ''):
        return os.path.join(get_user_profile(), "Desktop")
        
    path_str = str(path_str).strip()
    
    # Check for keywords
    lower_path = path_str.lower()
    path_map = {
        "downloads": os.path.join(get_user_profile(), "Downloads"),
        "documents": os.path.join(get_user_profile(), "Documents"),
        "desktop": os.path.join(get_user_profile(), "Desktop"),
        "pictures": os.path.join(get_user_profile(), "Pictures"),
        "music": os.path.join(get_user_profile(), "Music"),
        "videos": os.path.join(get_user_profile(), "Videos")
    }
    
    for key, val in path_map.items():
        if lower_path == key or lower_path == f"{key} folder":
            return val
            
    # If it's just a file name without a path, default to Desktop
    if not os.path.isabs(path_str) and "\\" not in path_str and "/" not in path_str:
        return os.path.join(get_user_profile(), "Desktop", path_str)
        
    return path_str

def execute_intent(intent: str, parameters: dict) -> CommandResult:
    """
    Executes a given intent on the Windows system.
    """
    try:
        # Basic
        if intent == "open_website":
            url = parameters.get("url") or ""
            if not url.startswith("http"):
                url = "https://" + url
            webbrowser.open(url)
            return CommandResult(True, f"Opened website: {url}")
            
        elif intent == "search_website":
            target = (parameters.get("target") or "").lower()
            query = parameters.get("query") or ""
            encoded_query = urllib.parse.quote(query)
            
            # Map targets to their search URLs
            search_urls = {
                "youtube": f"https://www.youtube.com/results?search_query={encoded_query}",
                "github": f"https://github.com/search?q={encoded_query}",
                "google": f"https://www.google.com/search?q={encoded_query}",
                "amazon": f"https://www.amazon.com/s?k={encoded_query}",
                "amazon in": f"https://www.amazon.in/s?k={encoded_query}",
                "amazon.in": f"https://www.amazon.in/s?k={encoded_query}",
                "wikipedia": f"https://en.wikipedia.org/wiki/Special:Search?search={encoded_query}",
                "leetcode": "https://leetcode.com/problemset/all/" # Leetcode doesn't have a simple GET search
            }
            
            url = search_urls.get(target, f"https://www.google.com/search?q={target}+{encoded_query}")
            webbrowser.open(url)
            return CommandResult(True, f"Searched {target} for: {query}")
            
        elif intent == "learn_app_path":
            app_name = parameters.get("app_name") or ""
            app_path = parameters.get("path") or ""
            if not app_name or not app_path:
                return CommandResult(False, "Missing app name or path.")
            
            if not os.path.exists(app_path):
                return CommandResult(False, f"Path does not exist: {app_path}")
                
            add_custom_app(app_name, app_path)
            return CommandResult(True, f"I have remembered that {app_name} is located at {app_path}.")
            
        elif intent == "open_application":
            app_name = (parameters.get("app_name") or "").lower()
            
            # 1. Check custom DB
            custom_path = get_custom_app_path(app_name)
            if custom_path and os.path.exists(custom_path):
                subprocess.Popen(f'"{custom_path}"', shell=True)
                return CommandResult(True, f"Opened application from memory: {app_name}")
                
            # 2. Check hardcoded map
            app_map = {
                "chrome": "chrome.exe",
                "google chrome": "chrome.exe",
                "edge": "msedge.exe",
                "microsoft edge": "msedge.exe",
                "vscode": "code",
                "vs code": "code",
                "word": "winword.exe",
                "excel": "excel.exe",
                "powerpoint": "powerpnt.exe",
                "calculator": "calc.exe",
                "notepad": "notepad.exe",
                "file explorer": "explorer.exe",
                "files": "explorer.exe",
                "explorer": "explorer.exe",
                "task manager": "taskmgr.exe",
                "settings": "ms-settings:",
                "terminal": "wt.exe",
                "cmd": "cmd.exe",
                "powershell": "powershell.exe",
                "recycle bin": "explorer.exe shell:RecycleBinFolder",
                "microsoft store": "ms-windows-store:",
                "paint": "mspaint.exe",
                "copilot": "microsoft-edge://?url=https://copilot.microsoft.com",
                "lenovo vantage": "lenovovantage:",
                "photos": "ms-photos:",
                "pc manager": "pcmanager.exe",
                "control panel": "control",
                "downloads": os.path.join(get_user_profile(), "Downloads"),
                "documents": os.path.join(get_user_profile(), "Documents"),
                "desktop": os.path.join(get_user_profile(), "Desktop"),
                "trae": "trae",
                "codex": "codex"
            }
            
            if app_name in app_map:
                exe = app_map[app_name]
                try:
                    if exe.startswith("ms-") or exe.startswith("microsoft-edge:") or exe.startswith("lenovovantage:"):
                        os.startfile(exe)
                    elif ":" in exe and "\\" in exe:
                        # Absolute path (could be a folder like Downloads)
                        if os.path.isdir(exe):
                            os.startfile(exe)
                        else:
                            subprocess.Popen(f'"{exe}"', shell=True)
                    else:
                        # Use cmd /c start to rely on Windows Registry App Paths (e.g., chrome.exe, excel.exe)
                        subprocess.Popen(f'cmd /c start "" {exe}', shell=True)
                    return CommandResult(True, f"Opened application: {app_name}")
                except Exception as e:
                    return CommandResult(False, f"Failed to open {app_name}: {str(e)}")
                
            # 3. Fallback: Quick scan Start Menu common locations
            start_menu_paths = [
                os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
                os.path.join(get_user_profile(), "AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs")
            ]
            
            found_path = None
            for sm_path in start_menu_paths:
                if not os.path.exists(sm_path): continue
                for root, _, files in os.walk(sm_path):
                    for f in files:
                        if f.lower().endswith(".lnk") and app_name in f.lower():
                            found_path = os.path.join(root, f)
                            break
                    if found_path: break
                if found_path: break
                
            if found_path:
                subprocess.Popen(f'"{found_path}"', shell=True)
                # Save to DB for next time
                add_custom_app(app_name, found_path)
                return CommandResult(True, f"Found and opened application: {app_name}")
                
            # If all fails, try executing as-is (e.g., if it's in PATH)
            try:
                subprocess.Popen(app_name, shell=True)
                return CommandResult(True, f"Attempted to open: {app_name}")
            except Exception:
                return CommandResult(False, f"Could not find application: {app_name}")

        elif intent == "search_google":
            query = parameters.get("query") or ""
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return CommandResult(True, f"Searched Google for: {query}")
            
        elif intent == "clipboard_action":
            action = parameters.get("action", "show")
            if action == "show":
                content = pyperclip.paste()
                return CommandResult(True, "Clipboard content", content)
            elif action == "copy":
                pyperclip.copy(parameters.get("content", ""))
                return CommandResult(True, "Copied text to clipboard.")
            elif action == "clear":
                pyperclip.copy("")
                return CommandResult(True, "Clipboard cleared.")
            elif action == "save":
                path = resolve_path(parameters.get("path", f"clipboard_{int(datetime.now().timestamp())}.txt"))
                content = pyperclip.paste()
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return CommandResult(True, f"Saved clipboard to {path}")
                
        elif intent == "email_action":
            to = parameters.get("recipient", "")
            sub = urllib.parse.quote(parameters.get("subject", ""))
            body = urllib.parse.quote(parameters.get("body", ""))
            webbrowser.open(f"mailto:{to}?subject={sub}&body={body}")
            return CommandResult(True, f"Opened mail client to send email to {to}. Please review and send.")
            
        elif intent == "favorite_action":
            action = parameters.get("action", "open")
            name = parameters.get("name", "")
            if action == "add":
                path = resolve_path(parameters.get("path", ""))
                add_favorite(name, path)
                return CommandResult(True, f"Added {name} to favorites.")
            else:
                if name.lower() in ("favorites", "all favorites"):
                    # Return list of favorites
                    conn = __import__("database").get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, path FROM favorites")
                    rows = cursor.fetchall()
                    conn.close()
                    favs = [{"name": r["name"], "path": r["path"]} for r in rows]
                    return CommandResult(True, f"You have {len(favs)} favorites.", json.dumps(favs))
                    
                path = get_favorite(name)
                if path:
                    if os.path.exists(path):
                        os.startfile(path)
                    else:
                        webbrowser.open(path)
                    return CommandResult(True, f"Opened favorite: {name}")
                return CommandResult(False, f"Favorite not found: {name}")
                
        elif intent == "downloads_action":
            action = parameters.get("action", "show_recent")
            downloads_dir = os.path.join(get_user_profile(), "Downloads")
            if action == "show_recent":
                files = []
                for f in os.listdir(downloads_dir):
                    fp = os.path.join(downloads_dir, f)
                    if os.path.isfile(fp):
                        files.append((fp, os.path.getmtime(fp)))
                files.sort(key=lambda x: x[1], reverse=True)
                recent = [os.path.basename(f[0]) for f in files[:10]]
                return CommandResult(True, "Recent downloads", ", ".join(recent))
            elif action == "delete_installers":
                deleted = 0
                for f in os.listdir(downloads_dir):
                    if f.lower().endswith((".exe", ".msi")):
                        os.remove(os.path.join(downloads_dir, f))
                        deleted += 1
                return CommandResult(True, f"Deleted {deleted} installers from Downloads.")
            elif action == "organize":
                # Reuse organize folder logic
                parameters["path"] = downloads_dir
                intent = "organize_folder" # Pass through to folder handler below
            
        # Folder Operations
        elif intent == "open_folder":
            folder = parameters.get("folder") or parameters.get("path") or ""
            path = resolve_path(folder)
            subprocess.Popen(f'explorer "{path}"', shell=True)
            return CommandResult(True, f"Opened folder: {path}")

        elif intent == "create_folder":
            path = resolve_path(parameters.get("path") or parameters.get("folder") or "")
            os.makedirs(path, exist_ok=True)
            return CommandResult(True, f"Created folder: {path}")

        elif intent == "rename_folder":
            old_name = resolve_path(parameters.get("old_name") or "")
            new_name = resolve_path(parameters.get("new_name") or "")
            if not os.path.exists(old_name):
                return CommandResult(False, f"Folder not found: {old_name}")
            os.rename(old_name, new_name)
            return CommandResult(True, f"Renamed folder to: {os.path.basename(new_name)}")

        elif intent == "move_folder":
            source = resolve_path(parameters.get("source") or "")
            dest = resolve_path(parameters.get("destination") or "")
            if not os.path.exists(source):
                return CommandResult(False, f"Source folder not found: {source}")
            if os.path.exists(dest) and not os.path.isdir(dest):
                return CommandResult(False, "Destination must be a folder")
            shutil.move(source, dest)
            return CommandResult(True, f"Moved folder to: {dest}")

        elif intent == "delete_folder":
            path = resolve_path(parameters.get("path") or "")
            if os.path.exists(path):
                shutil.rmtree(path)
                return CommandResult(True, f"Deleted folder: {path}")
            return CommandResult(False, f"Folder not found: {path}")

        elif intent == "search_folder":
            query = parameters.get("query") or ""
            results = search_engine.search(query=query, limit=20)
            folders = [r for r in results if r["is_folder"]]
            if folders:
                return CommandResult(True, f"Found {len(folders)} folders for '{query}'", json.dumps(folders))
            return CommandResult(False, f"No folders found for '{query}'")

        # File Operations
        elif intent == "open_file":
            path = resolve_path(parameters.get("path") or "")
            if os.path.exists(path):
                # Windows opens file with default program
                os.startfile(path)
                return CommandResult(True, f"Opened file: {path}")
            return CommandResult(False, f"File not found: {path}")

        elif intent == "create_file":
            path = resolve_path(parameters.get("path") or "")
            content = parameters.get("content") or ""
            parent_dir = os.path.dirname(path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return CommandResult(True, f"Created file: {path}")

        elif intent == "write_to_file":
            path = resolve_path(parameters.get("path") or "")
            content = parameters.get("content") or ""
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return CommandResult(True, f"Wrote to file: {path}")

        elif intent == "append_to_file":
            path = resolve_path(parameters.get("path") or "")
            content = parameters.get("content") or ""
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n" + content)
            return CommandResult(True, f"Appended to file: {path}")

        elif intent == "read_file":
            path = resolve_path(parameters.get("path") or "")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read(2000)
                return CommandResult(True, f"Read file {path}", content)
            return CommandResult(False, f"File not found: {path}")

        elif intent == "rename_file":
            old_name = resolve_path(parameters.get("old_name") or "")
            new_name = resolve_path(parameters.get("new_name") or "")
            if not os.path.exists(old_name):
                return CommandResult(False, f"File not found: {old_name}")
            os.rename(old_name, new_name)
            return CommandResult(True, f"Renamed file to: {os.path.basename(new_name)}")

        elif intent == "move_file":
            source = resolve_path(parameters.get("source") or "")
            dest = resolve_path(parameters.get("destination") or "")
            if not os.path.exists(source):
                return CommandResult(False, f"File not found: {source}")
            shutil.move(source, dest)
            return CommandResult(True, f"Moved file to: {dest}")

        elif intent == "copy_file":
            source = resolve_path(parameters.get("source") or "")
            dest = resolve_path(parameters.get("destination") or "")
            if not os.path.exists(source):
                return CommandResult(False, f"Source file not found: {source}")
            if os.path.isdir(dest):
                dest = os.path.join(dest, os.path.basename(source))
            shutil.copy2(source, dest)
            return CommandResult(True, f"Copied file to: {dest}")

        elif intent == "delete_file":
            path = resolve_path(parameters.get("path") or "")
            if os.path.exists(path):
                os.remove(path)
                return CommandResult(True, f"Deleted file: {path}")
            return CommandResult(False, f"File not found: {path}")

        elif intent == "search_file":
            query = parameters.get("query") or ""
            ext = parameters.get("extension")
            min_size = parameters.get("min_size")
            try:
                min_size = int(min_size) if min_size else None
            except:
                min_size = None
                
            results = search_engine.search(query=query, extension=ext, min_size=min_size, limit=20)
            files = [r for r in results if not r["is_folder"]]
            if files:
                return CommandResult(True, f"Found {len(files)} files.", json.dumps(files))
            return CommandResult(False, f"No files found for '{query}'")

        elif intent == "file_info":
            path = resolve_path(parameters.get("path") or "")
            if os.path.exists(path):
                stats = os.stat(path)
                size_kb = stats.st_size / 1024
                created = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                details = f"Size: {size_kb:.2f} KB\nCreated: {created}"
                return CommandResult(True, f"File info for: {path}", details)
            return CommandResult(False, f"File not found: {path}")

        # Notepad Operations
        elif intent == "notepad_write":
            content = parameters.get("content", "")
            filename = parameters.get("path", "")
            if not filename:
                filename = f"notepad_temp_{int(datetime.now().timestamp())}.txt"
            path = resolve_path(filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            subprocess.Popen(f'notepad.exe "{path}"', shell=True)
            return CommandResult(True, f"Opened Notepad with content")

        # Bulk Operations
        elif intent == "create_multiple_files":
            files = parameters.get("files", [])
            created = []
            for fname in files:
                path = resolve_path(fname)
                os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    pass
                created.append(fname)
            return CommandResult(True, f"Created {len(created)} files", ", ".join(created))

        elif intent == "create_project_structure":
            proj_type = parameters.get("type", "").lower()
            proj_name = parameters.get("path", "NewProject")
            path = resolve_path(proj_name)
            os.makedirs(path, exist_ok=True)
            
            if "python" in proj_type:
                os.makedirs(os.path.join(path, "src"))
                os.makedirs(os.path.join(path, "tests"))
                with open(os.path.join(path, "main.py"), "w") as f: f.write("print('Hello World')")
                with open(os.path.join(path, "requirements.txt"), "w") as f: pass
                return CommandResult(True, f"Created Python project at {path}")
            elif "react" in proj_type or "web" in proj_type:
                os.makedirs(os.path.join(path, "src"))
                os.makedirs(os.path.join(path, "public"))
                with open(os.path.join(path, "index.html"), "w") as f: f.write("<html><body></body></html>")
                with open(os.path.join(path, "src", "App.js"), "w") as f: f.write("export default function App() { return <div>App</div> }")
                return CommandResult(True, f"Created React project structure at {path}")
            else:
                return CommandResult(True, f"Created folder structure at {path}")

        elif intent == "organize_folder":
            folder = resolve_path(parameters.get("path", "downloads"))
            if not os.path.exists(folder):
                return CommandResult(False, f"Folder not found: {folder}")
                
            docs_dir = os.path.join(get_user_profile(), "Documents")
            pics_dir = os.path.join(get_user_profile(), "Pictures")
            os.makedirs(docs_dir, exist_ok=True)
            os.makedirs(pics_dir, exist_ok=True)
            
            moved = 0
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                if os.path.isfile(item_path):
                    ext = item.lower().split('.')[-1] if '.' in item else ''
                    if ext in ['pdf', 'doc', 'docx', 'txt', 'csv']:
                        shutil.move(item_path, os.path.join(docs_dir, item))
                        moved += 1
                    elif ext in ['jpg', 'jpeg', 'png', 'gif']:
                        shutil.move(item_path, os.path.join(pics_dir, item))
                        moved += 1
            return CommandResult(True, f"Organized folder: {folder}. Moved {moved} files.")

        # Time & Timers
        elif intent == "get_time":
            return CommandResult(True, f"The current time is {datetime.now().strftime('%I:%M %p')}")

        elif intent == "get_date":
            return CommandResult(True, f"Today's date is {datetime.now().strftime('%B %d, %Y')}")

        elif intent == "start_timer":
            import timers
            duration = int(parameters.get("duration_seconds", 60))
            name = parameters.get("name", "Timer")
            timers.start_timer(duration, name)
            return CommandResult(True, f"Started {name} for {duration} seconds.")

        elif intent == "stop_timer":
            import timers
            tid = parameters.get("timer_id", None)
            timers.stop_timer(tid)
            return CommandResult(True, "Stopped timer(s).")
            
        # Window Management
        elif intent == "window_action":
            raw_action = parameters.get("action") or ""
            raw_target = parameters.get("target") or ""
            raw_layout = parameters.get("layout") or ""
            
            # Handle cases where AI returns a list instead of a string
            action = raw_action if isinstance(raw_action, str) else str(raw_action[0]) if raw_action else ""
            action = action.lower()
            
            if isinstance(raw_target, list):
                targets = [str(t).lower() for t in raw_target]
                target = targets[0] if targets else ""
            else:
                target = str(raw_target).lower()
                targets = [target]
            
            layout = raw_layout if isinstance(raw_layout, str) else str(raw_layout[0]) if raw_layout else ""
            layout = layout.lower()
            
            try:
                import pygetwindow as gw
                import pyautogui
                
                if action == "minimize":
                    if target in ["all", "everything"]:
                        pyautogui.hotkey('win', 'd')
                        return CommandResult(True, "Minimized all windows.")
                    else:
                        wins = gw.getWindowsWithTitle(target) if target else [gw.getActiveWindow()]
                        for w in wins:
                            if w and not w.isMinimized: w.minimize()
                        return CommandResult(True, f"Minimized {target or 'current window'}.")
                        
                elif action == "maximize":
                    wins = gw.getWindowsWithTitle(target) if target and target != "current window" else [gw.getActiveWindow()]
                    for w in wins:
                        if w: w.maximize()
                    return CommandResult(True, f"Maximized window.")
                    
                elif action == "close":
                    wins = gw.getWindowsWithTitle(target)
                    for w in wins:
                        if w: w.close()
                    return CommandResult(True, f"Closed {target}.")
                    
                elif action == "switch" or action == "focus":
                    wins = gw.getWindowsWithTitle(target)
                    if wins and wins[0]:
                        wins[0].activate()
                        return CommandResult(True, f"Switched to {target}.")
                        
                elif action == "arrange" or action == "open":
                    if "side" in layout or "split" in layout or len(targets) >= 2:
                        import time as _time
                        # Try to snap windows side by side
                        if len(targets) >= 2:
                            for i, t in enumerate(targets):
                                wins = gw.getWindowsWithTitle(t)
                                if wins and wins[0]:
                                    wins[0].activate()
                                    _time.sleep(0.3)
                                    if i == 0:
                                        pyautogui.hotkey('win', 'left')
                                    else:
                                        pyautogui.hotkey('win', 'right')
                                    _time.sleep(0.3)
                        else:
                            pyautogui.hotkey('win', 'left')
                        return CommandResult(True, "Arranged windows side by side.")
                    else:
                        pyautogui.hotkey('win', 'left')
                        return CommandResult(True, "Arranged window.")
                        
                return CommandResult(True, f"Attempted window action: {action}")
            except Exception as w_e:
                return CommandResult(False, f"Window management error: {w_e}")

        elif intent == "chat":
            return CommandResult(True, "Chat response processed.")
            
        else:
            return CommandResult(False, f"Unsupported intent: {intent}")
            
    except Exception as e:
        return CommandResult(False, f"Error executing {intent}: {str(e)}")
