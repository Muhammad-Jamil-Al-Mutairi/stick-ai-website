
https://github.com/user-attachments/assets/ba0bb45a-93cf-4739-8bf0-84cf08ff9165




# Stick.AI: Predictive Mobility & Fall Detection System 🦯🧠






[![Live Dashboard](https://img.shields.io/badge/Live_Dashboard-Online-success?style=for-the-badge)](https://muhammad-jamil-al-mutairi.github.io/stick-ai-website/)
[![Hardware](https://img.shields.io/badge/Hardware-Arduino_UNO_Q-00979D?style=for-the-badge&logo=arduino)](https://store.arduino.cc)
[![AI](https://img.shields.io/badge/AI-Edge_Impulse-FF3366?style=for-the-badge)](https://edgeimpulse.com)

The AI Stick is a comprehensive Internet of Things (IoT) medical device and telemetry dashboard. It transforms a standard walking stick into a smart mobility aid capable of real-time pulse oximetry monitoring and AI-driven emergency fall detection. 

By bridging bare-metal C++ sensor reading with a cloud-based Linux Python container, this project successfully streams complex biomechanical data to a Qualcomm Snapdragon-powered Neural Network for real-time classification, ultimately broadcasting the results to a live Firebase web dashboard.

---

## 📂 Repository Structure

This repository is organized by architectural function:

* 📁 **`3D_models/`** - Onshape `.STL` and `.STEP` files for the custom printed handle and enclosures.
* 📁 **`arduino_edge_node/`** - C++ firmware for the Arduino UNO Q (I2C sensor polling and bridging).
* 📁 **`hardware_schematic/`** - Circuit diagrams, Fritzing layouts, and electrical documentation.
* 📁 **`project_photos/`** - Physical prototype images and live demonstration media.
* 📁 **`python_cloud_bridge/`** - The `main.py` state machine and the `aarch64` TensorFlow Lite AI model.
* 📁 **`web_dashboard/`** - HTML, CSS, and JS files powering the live Firebase telemetry dashboard.

---

## 🏗️ System Architecture

This project operates across three major engineering domains:

1. **Bare-Metal Edge Hardware:** An Arduino UNO Q acts as the physical edge node, utilizing heavily optimized timing loops to read an MPU-6050 (IMU) and a MAX30102 (Pulse Oximeter). It processes heartbeat peak-detection locally and buffers accelerometer data at exactly 25Hz.
2. **Cloud AI Bridge:** A custom Python container intercepts the hardware telemetry. It runs a custom-trained, quantized Edge Impulse classification model locally on the Qualcomm chip, bypassing standard latency bottlenecks.
3. **Real-Time Telemetry Dashboard:** The Python bridge patches inference results (e.g., `✅ Walking Safely`, `🚨 FALL DETECTED`) and vital signs to a Firebase Realtime Database. A sleek web dashboard listens to this database to render live, animated charts and status badges remotely.

---

## 🔌 Circuit Schematic & Hardware

The electrical system requires precise I2C communication between the sensors and the microcontroller. 

![Stick.AI Circuit Schematic](hardware_schematic/schematic.png) *(Note: Change `schematic.png` to your actual file name!)*

**Core Components:**
* **Microcontroller:** Arduino UNO Q 
* **IMU:** GY-521 (MPU-6050 6-DoF Accelerometer & Gyroscope)
* **Vitals:** RCWL-0530 (MAX30102 Pulse Oximetry & Heart Rate)
* **Communication:** I2C Protocol

---

## 🖨️ 3D Design & Enclosure

To make the system physically viable, custom mounts and enclosures were designed in **Onshape**. The mechanical designs focus on ergonomics and secure housing for the I2C wiring, protecting the delicate sensor arrays from impact during a detected fall. The design files were rapidly prototyped and printed using a Creality Ender 3 V3 SE.

* **Interactive CAD:** [View the complete 3D design workspace on Onshape](https://cad.onshape.com/documents/027696098c048843e6e8f9b6/w/f13f1546ddf5b77709304479/e/49368f70d675277c00a1590c)

---

## 🚀 Installation & Usage

### 1. Hardware Setup
Flash the C++ script located in the `arduino_edge_node` folder to your Arduino UNO Q. Ensure the I2C sensors are wired according to the schematic.

### 2. Booting the AI Bridge
Open the Arduino App Lab. Run the `main.py` script located in the `python_cloud_bridge` folder. The script will automatically configure the environment, unlock Linux execution permissions for the `.eim` model, and boot the Neural Network.

### 3. Web Dashboard
The dashboard is currently live via GitHub pages. You can monitor the system telemetry in real-time here: **[Stick.AI Live Dashboard](https://muhammad-jamil-al-mutairi.github.io/stick-ai-website/)**

---
*Engineered by Muhammad Jamil Almutairi — Shaqra University, Department of Computer Engineering*
