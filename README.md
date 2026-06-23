# 🥋 Dojo Tracker: Motion-Tracking Strike Analytics

An ultra-modern, minimalist web application that utilizes advanced C++ computer vision frameworks to analyze martial arts strike velocities (punches and kicks) in real-time. Built with a responsive, gamified glassmorphism interface engineered to drive user engagement and repetitive training loops.
![Dojo Tracker Interface](Example%20Strike.png)
---

## ✨ Features

* **Gamified Belt Progression Loop:** Instantly maps peak strike speeds to corresponding martial arts belt rankings (White through Grandmaster).
* **Dopamine-Driven UI Retention:** Integrates browser `localStorage` to track and flash Session Personal Bests, encouraging continuous improvement ("Just one more try").
* **Dynamic Visual Progression:** Live progress bars tracking exact percentages needed to unlock the next belt tier.
* **Shareable High-Fidelity Performance Cards:** Dynamically constructs a premium 9:16 social-media-ready digital athletic log embedded inside a Base64 string payload.
* **Privacy-Centric Architecture:** Processes video frame matrices dynamically inside memory (RAM). Zero video data or user media is cached or stored permanently.

---

## 🛠️ Tech Stack & Requirements

* **Backend Framework:** FastAPI (Python 3.11.9, 64-bit strictly required)
* **ASGI Server:** Uvicorn
* **Computer Vision Pipeline:** Google MediaPipe Pose Landmarker Engine (BlazePose) & OpenCV
* **Image Generation Suite:** Pillow (PIL)
* **Frontend Design System:** Custom CSS Glassmorphism vanilla framework utilizing the *Plus Jakarta Sans* typeface

---
![Dojo Tracker Interface](WebUI.png)
## 🚀 Step-by-Step Installation

### 1. Initialize and Activate Environment
Ensure you are using a 64-bit installation of Python 3.11.9:
```bash
cd C:\PythonStudio\MartialArts_Speed
.\.venv\Scripts\activate
2. Install Dependencies
Install all tracked packages directly via the pinned environment specification sheet:

Bash
python -m pip install --no-cache-dir -r requirements.txt
3. Launch the Application Server
Run the application locally via Uvicorn:

Bash
python main.py
🌐 Accessing the Tracker
Once the server initializes, Uvicorn will listen across all network blocks. Access the UI through your local loopback address:

👉 http://localhost:8000 or http://127.0.0.1:8000

Note: Navigating to http://0.0.0.0:8000 directly in a browser will throw an ERR_ADDRESS_INVALID error.

🛠️ Windows Core Troubleshooting Guide
If the backend fails to load MediaPipe solutions, cross-verify your system against these two parameters:

Architecture Check (Bitness):
MediaPipe requires a 64-bit Python architecture. Verify your virtual environment by running:

Bash
python -c "import platform; print(platform.architecture())"
Must output ('64bit', 'WindowsPE').

Missing C++ Framework Runtimes:
If you encounter silent tracking initialization crashes, your operating system is missing the core Microsoft Visual C++ dependencies.

Download the official Microsoft Visual C++ Redistributable (X64) framework patch, install it, and restart your IDE/Terminal environment.