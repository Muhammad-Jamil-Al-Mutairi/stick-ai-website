print("🚀 Initiating Final Board Architecture...")
import sys
import subprocess
import os
import threading
import time

# ==============================================================================
# 1. ENVIRONMENT OVERRIDE
# ==============================================================================
def setup_environment():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "edge_impulse_linux", "requests"])
    except Exception:
        pass

    import requests 

    print("🗑️ Clearing wrong architecture cache...")
    if os.path.exists("model.eim"):
        os.remove("model.eim")
        print("✅ Old file purged.")

    # YOUR PERFECT AARCH64 URL:
    MODEL_URL = "https://raw.githubusercontent.com/Muhammad-Jamil-Al-Mutairi/stick-ai-website/main/stick-ai-fall-detection-linux-aarch64-v12-impulse-%231.eim"
    
    print("🌐 Downloading UNO Q AI Brain...")
    try:
        response = requests.get(MODEL_URL)
        if response.status_code == 200 and not response.text.strip().startswith("<!DOCTYPE html>"):
            with open("model.eim", "wb") as f:
                f.write(response.content)
            print("✅ Binary model downloaded!")
        else:
            print("❌ Failed: GitHub returned a webpage. Check the URL!")
            return False
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        return False
        
    print("🔓 Unlocking Linux execution permissions...")
    try:
        os.chmod("model.eim", 0o777)
        print("✅ Permissions granted!")
    except Exception as e:
        print(f"❌ Failed to unlock permissions: {e}")
        return False
        
    return True

if not setup_environment():
    sys.exit()

# ==============================================================================
# 2. EDGE IMPULSE AI LOGIC
# ==============================================================================
from arduino.app_utils import App, Bridge
from edge_impulse_linux.runner import ImpulseRunner
import requests

FIREBASE_URL = "https://stick-ai-system-default-rtdb.europe-west1.firebasedatabase.app/sensors.json"

# --- UPDATE 1: Added the status field to the memory state ---
current_state = { 
    "accelX": 0.0, 
    "accelY": 0.0, 
    "accelZ": 0.0, 
    "heartRate": 0,
    "status": "Initializing..." 
}

# The Absolute Path Fix 
model_path = os.path.abspath("model.eim")
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
        
        # --- UPDATE 2: Logic to determine the highest prediction ---
        highest_score = 0
        current_prediction = "Walking"
        
        for label in res["result"]["classification"]:
            score = res["result"]["classification"][label]
            print(f"    {label}: {score:.2f}", flush=True)
            
            if score > highest_score:
                highest_score = score
                current_prediction = label
                
        # --- UPDATE 3: Push the winning status to Firebase ---
        if current_prediction == "Fall" and highest_score > 0.80:
            current_state["status"] = "🚨 FALL DETECTED 🚨"
            print("🚨🚨 CRITICAL EMERGENCY DETECTED: FALL 🚨🚨", flush=True)
        elif current_prediction == "Drop":
            current_state["status"] = "⚠️ Stick Dropped"
        else:
            current_state["status"] = "✅ Walking Safely"

        # Slide the window
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
