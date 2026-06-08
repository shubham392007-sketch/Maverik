import threading
import time
import uuid

active_timers = {}

def start_timer(duration_seconds: int, name: str = "Timer"):
    timer_id = str(uuid.uuid4())
    end_time = time.time() + duration_seconds
    
    active_timers[timer_id] = {
        "id": timer_id,
        "name": name,
        "end_time": end_time,
        "duration": duration_seconds,
        "status": "running"
    }
    
    def timer_thread():
        time.sleep(duration_seconds)
        if timer_id in active_timers and active_timers[timer_id]["status"] == "running":
            active_timers[timer_id]["status"] = "finished"
            
    threading.Thread(target=timer_thread, daemon=True).start()
    return active_timers[timer_id]

def get_active_timers():
    current_time = time.time()
    timers = []
    for tid, t in list(active_timers.items()):
        remaining = max(0, int(t["end_time"] - current_time))
        if t["status"] == "running" and remaining == 0:
             t["status"] = "finished"
        timers.append({
            "id": t["id"],
            "name": t["name"],
            "remaining_seconds": remaining,
            "status": t["status"]
        })
    return timers

def stop_timer(timer_id=None):
    if timer_id and timer_id in active_timers:
        active_timers[timer_id]["status"] = "stopped"
        return True
    elif not timer_id:
        # Stop all
        for tid in active_timers:
            active_timers[tid]["status"] = "stopped"
        return True
    return False

def clear_finished_timers():
    for tid in list(active_timers.keys()):
        if active_timers[tid]["status"] in ["finished", "stopped"]:
            del active_timers[tid]
