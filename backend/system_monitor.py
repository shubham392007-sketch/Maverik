import psutil
import time
import platform

last_net_io = None
last_net_time = None

def get_system_stats():
    global last_net_io, last_net_time
    # CPU usage
    cpu_usage = psutil.cpu_percent(interval=0)
    cpu_name = platform.processor() or "Unknown CPU"
    
    # RAM usage
    ram = psutil.virtual_memory()
    
    # Disk usage (C: drive)
    try:
        disk = psutil.disk_usage('C:\\')
    except Exception:
        disk = psutil.disk_usage('/')

    # Network Activity (speed)
    current_net_io = psutil.net_io_counters()
    current_time = time.time()
    
    upload_speed = 0
    download_speed = 0
    if last_net_io and last_net_time:
        time_diff = current_time - last_net_time
        if time_diff > 0:
            upload_speed = (current_net_io.bytes_sent - last_net_io.bytes_sent) / time_diff # bytes/sec
            download_speed = (current_net_io.bytes_recv - last_net_io.bytes_recv) / time_diff # bytes/sec

    last_net_io = current_net_io
    last_net_time = current_time
    
    # Battery Status
    battery = psutil.sensors_battery()
    
    # System Uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    
    return {
        "cpu": {
            "percent": cpu_usage,
            "name": cpu_name
        },
        "ram": {
            "percent": ram.percent,
            "used_gb": round(ram.used / (1024 ** 3), 1),
            "total_gb": round(ram.total / (1024 ** 3), 1)
        },
        "disk": {
            "percent": disk.percent,
            "used_gb": round(disk.used / (1024 ** 3), 1),
            "total_gb": round(disk.total / (1024 ** 3), 1)
        },
        "network": {
            "upload_bps": upload_speed,
            "download_bps": download_speed
        },
        "battery": {
            "percent": battery.percent if battery else 100,
            "is_plugged": battery.power_plugged if battery else True
        },
        "uptime": uptime_seconds
    }
