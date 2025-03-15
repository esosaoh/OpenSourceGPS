from typing import Dict, Any
import time
import psutil
import platform
import os
import google.generativeai as genai

from app.core.config import GEMINI_API_KEY

# Track application startup time
START_TIME = time.time()

async def get_health_status() -> Dict[str, Any]:
    """Get the health status of the application and its dependencies."""
    
    # Check Gemini API status
    gemini_status = {"status": "unknown", "message": ""}
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Return only 'OK' if you can process this message.")
        if "ok" in response.text.lower():
            gemini_status = {"status": "ok"}
        else:
            gemini_status = {"status": "degraded", "message": "Unexpected response from API"}
    except Exception as e:
        gemini_status = {"status": "error", "message": str(e)}
    
    # Get system metrics
    system_info = {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": {
            "percent": psutil.virtual_memory().percent,
            "used_mb": psutil.virtual_memory().used / (1024 * 1024),
            "total_mb": psutil.virtual_memory().total / (1024 * 1024)
        },
        "disk_usage": {
            "percent": psutil.disk_usage('/').percent,
            "used_gb": psutil.disk_usage('/').used / (1024 * 1024 * 1024),
            "total_gb": psutil.disk_usage('/').total / (1024 * 1024 * 1024)
        },
        "platform": platform.platform(),
        "python_version": platform.python_version()
    }
    
    return {
        "status": gemini_status,
        "uptime_seconds": time.time() - START_TIME,
        "dependencies": {
            "gemini_api": gemini_status
        },
        "system": system_info
    }