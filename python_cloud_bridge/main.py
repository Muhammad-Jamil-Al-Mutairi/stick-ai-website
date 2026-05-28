print("🚀 Initiating Final Board Architecture (Local File Mode)...")
import sys
import subprocess
import os
import threading
import time

# ==============================================================================
# 1. ENVIRONMENT SETUP
# ==============================================================================
def setup_environment():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "edge_impulse_linux", "requests"])
    except Exception:
        pass

    # Force Python to look in the exact folder where this script is running
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "model.eim")
    
    if not os.path.exists(model_path):
        print(f"❌ Error: Could not find model.eim at {model_path}")
        return False, None
        
    print(f"🔓 Unlocking Linux execution permissions...")
    try:
        os.chmod(model_path, 0o777)
        print("✅ Permissions granted!")
    except Exception as e:
        print(f"❌ Failed to unlock permissions: {e}")
        return False, None
        
    return True, model_path

success, local_model_name = setup_environment()
if not success:
    sys.exit()

# ==============================================================================
# 2. EDGE IMPULSE AI LOGIC
# ==============================================================================
# ... (Keep the rest of your AI Logic exactly the same!) ...

# ==============================================================================
# 2. EDGE IMPULSE AI LOGIC
# ==============================================================================
from arduino.app_utils import App, Bridge
from edge_impulse_linux.runner import ImpulseRunner
import requests

FIREBASE_URL = "https://stick-ai-system-default-rtdb.europe-west1.firebasedatabase.app/sensors.json"

current_state = { 
    "accelX": 0.0, 
    "accelY": 0.0, 
    "accelZ": 0.0, 
    "heartRate": 0,
    "status": "Initializing..." 
}

# The Absolute Path Fix for the uploaded file
model_path = os.path.abspath(local_model_name)
print(f"🔍 Pointing AI Runner to absolute path: {model_path}")

try:
    runner = ImpulseRunner(model_path) 
    model_info = runner.init()
    print("🧠 SUCCESS: Neural Network Booted on the UNO Q!")
except Exception as e:
    print(f"❌ Failed to boot AI: {e}")
    sys.exit()

sensor_buffer = []

def on_movement(x, y, z):
    global sensor_buffer
    
    current_state["accelX"] = round(x, 2)
    current_state["accelY"] = round(y, 2)
    current_state["accelZ"] = round(z, 2)
    
    sensor_buffer.extend([x, y, z])
    
    if len(sensor_buffer) >= 168:
        res = runner.classify(sensor_buffer[:168])
        
        print("\n--- Live AI Telemetry ---", flush=True)
        
        highest_score = 0
        current_prediction = "Walking"
        
        for label in res["result"]["classification"]:
            score = res["result"]["classification"][label]
            print(f"    {label}: {score:.2f}", flush=True)
            
            if score > highest_score:
                highest_score = score
                current_prediction = label
                
        if current_prediction == "Fall" and highest_score > 0.80:
            current_state["status"] = "🚨 FALL DETECTED 🚨"
            print("🚨🚨 CRITICAL EMERGENCY DETECTED: FALL 🚨🚨", flush=True)
        elif current_prediction == "Drop":
            current_state["status"] = "⚠️ Stick Dropped"
        else:
            current_state["status"] = "✅ Walking Safely"

        sensor_buffer = sensor_buffer[84:]

def firebase_worker():
    while True:
        try:
            requests.patch(FIREBASE_URL, json=current_state, timeout=2)
        except Exception:
            pass 
        time.sleep(1.0) 

threading.Thread(target=firebase_worker, daemon=True).start()

def on_log(message):
    if message.startswith("HR_DEBUG:"):
        try:
            data_parts = message.split(":")[1].split(",")
            bpm_val = int(data_parts[0])
            ir_val = int(data_parts[1])
            if ir_val > 20000 and bpm_val > 40:
                current_state["heartRate"] = bpm_val
        except Exception:
            pass
    else:
        print(f"C++ Hardware Log: {message}", flush=True)

try:
    Bridge.provide("record_sensor_movement", on_movement)
    Bridge.provide("log_data_properly", on_log)
except Exception as e:
    print(f"Bridge warning: {e}", flush=True)

def loop():
    time.sleep(1.0)

print("⚡ System fully armed and waiting for C++ sensor data...")
App.run(user_loop=loop)
