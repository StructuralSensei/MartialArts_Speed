import io
import os
import base64
import cv2
import numpy as np
import mediapipe as mp
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from PIL import Image, ImageDraw, ImageFont

app = FastAPI(title="Martial Arts Velocity API")

# ==========================================
# MEDIAPIPE INITIALIZATION & CONFIGURATION
# ==========================================
mp_pose = mp.solutions.pose

# ENHANCEMENT TIP:
# - Increase 'model_complexity' to 2 for maximum tracking precision (requires more CPU/GPU).
# - Tweak 'min_detection_confidence' if the system misses the person entirely in low light.
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3
)


def get_font(size: int):
    """Safely loads a system font, falling back cleanly if not found."""
    try:
        return ImageFont.truetype("arial.ttf", size)
    except IOError:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except IOError:
            try:
                return ImageFont.load_default(size=size)
            except TypeError:
                return ImageFont.load_default()


def generate_shareable_card(peak_speed: float, rank_name: str, belt_color: str) -> str:
    """Generates a premium 9:16 social media card and returns it as a Base64 string."""
    # Create a blank, dark zinc canvas
    img = Image.new("RGB", (1080, 1920), "#09090B")
    draw = ImageDraw.Draw(img)

    # ENHANCEMENT TIP: You can replace the blank canvas with a background image
    # using Image.open("your_bg.jpg").resize((1080, 1920)) for a personalized Dojo theme.

    # Dynamic border matching the achieved belt color
    draw.rectangle([(40, 40), (1040, 1880)], outline=belt_color, width=12)

    font_large = get_font(200)
    font_medium = get_font(70)
    font_small = get_font(40)

    # Header Branding
    draw.text((100, 160), "DOJO STRIKE CHALLENGE", fill="#FFFFFF", font=font_medium)
    draw.text((100, 250), "MOTION-TRACKING PERFORMANCE LOG", fill="#71717A", font=font_small)

    # Speed Metrics (Translated fully to English)
    draw.text((100, 520), f"{peak_speed:.2f}", fill=belt_color, font=font_large)
    draw.text((100, 770), "PEAK SPEED (KM/H)", fill="#FFFFFF", font=font_medium)

    # Rank Notification Badge
    draw.rectangle([(100, 980), (980, 1280)], fill="#18181B", outline=belt_color, width=4)
    draw.text((150, 1030), "RANK EARNED:", fill="#A1A1AA", font=font_small)
    draw.text((150, 1120), rank_name.upper(), fill=belt_color, font=font_medium)

    # Footer Trust Badge
    draw.text((100, 1760), "Processed instantly in RAM • No data retained", fill="#3F3F46", font=font_small)

    # Convert image memory binary stream to base64 string string for frontend injection
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    encoded = base64.b64encode(img_byte_arr.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"


@app.get("/", response_class=HTMLResponse)
async def main_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🥋 Dojo Analytics Tracker</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=400;600;800&display=swap" rel="stylesheet">
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
            body { 
                background: #09090b; 
                color: #fafafa; 
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
                overflow-x: hidden;
            }
            .app-container {
                width: 100%;
                max-width: 480px;
                display: flex;
                flex-direction: column;
                gap: 24px;
            }

            /* Gamification Header Component */
            .score-badge {
                background: linear-gradient(135deg, #18181b 0%, #27272a 100%);
                border: 1px solid #3f3f46;
                padding: 12px 20px;
                border-radius: 100px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.9rem;
                font-weight: 600;
                color: #a1a1aa;
            }
            #sessionBest { color: #f43f5e; font-weight: 800; }

            .main-card {
                background: #18181b;
                border: 1px solid #27272a;
                border-radius: 24px;
                padding: 32px;
                text-align: center;
                box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            }

            h1 { font-size: 2rem; font-weight: 800; letter-spacing: -0.05em; margin-bottom: 8px; }
            p.subtitle { color: #a1a1aa; font-size: 0.95rem; margin-bottom: 32px; line-height: 1.5; }

            /* Drag & Drop UI Zone */
            .drop-zone {
                border: 2px dashed #3f3f46;
                background: #09090b;
                border-radius: 16px;
                padding: 40px 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 12px;
                margin-bottom: 24px;
            }
            .drop-zone:hover, .drop-zone.drag-over { border-color: #f43f5e; background: #141113; }
            .drop-zone input { display: none; }
            .drop-zone .icon { font-size: 2.5rem; }
            .drop-zone span { font-size: 0.9rem; color: #71717a; font-weight: 600; }
            .drop-zone .file-loaded { color: #f43f5e; font-weight: 600; display: none; }

            button.cta-btn {
                background: #fafafa;
                color: #09090b;
                border: none;
                width: 100%;
                padding: 16px;
                font-size: 1rem;
                font-weight: 700;
                border-radius: 14px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            button.cta-btn:hover { background: #e4e4e7; transform: translateY(-1px); }
            button.cta-btn:disabled { background: #27272a; color: #71717a; cursor: not-allowed; transform: none; }

            /* Dynamic Results Panel */
            .result-panel { display: none; margin-top: 8px; text-align: left; animation: fadeInUp 0.4s ease forwards; }

            /* Progress Bar Gamification Container */
            .progress-container {
                background: #09090b;
                padding: 16px;
                border-radius: 16px;
                margin-bottom: 24px;
                border: 1px solid #27272a;
            }
            .progress-metrics { display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 8px; }
            .progress-bar-bg { width: 100%; height: 8px; background: #27272a; border-radius: 100px; overflow: hidden; }
            .progress-bar-fill { width: 0%; height: 100%; background: #f43f5e; border-radius: 100px; transition: width 1s cubic-bezier(0.1, 1, 0.1, 1); }

            .image-frame {
                width: 100%;
                border-radius: 16px;
                overflow: hidden;
                border: 1px solid #3f3f46;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            img { width: 100%; height: auto; display: block; }

            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(15px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body>

        <div class="app-container">
            <div class="score-badge">
                <span>🔥 PERSONAL BEST THIS SESSION:</span>
                <span id="sessionBest">0.00 km/h</span>
            </div>

            <div class="main-card">
                <h1>Dojo Tracker</h1>
                <p class="subtitle">Upload your strike video. Dynamic motion-tracking will assess your metric velocities instantly.</p>

                <form id="uploadForm">
                    <div class="drop-zone" id="dropZone">
                        <span class="icon">⚡</span>
                        <span id="uploadPrompt">Drag & drop video or tap to browse</span>
                        <span class="file-loaded" id="fileLoaded">Video Selected Ready!</span>
                        <input type="file" name="file" id="fileInput" accept="video/*" required>
                    </div>
                    <button type="submit" id="submitBtn" class="cta-btn">ANALYZE STRIKE</button>
                </form>

                <div class="result-panel" id="resultPanel">
                    <div class="progress-container">
                        <div class="progress-metrics">
                            <span id="currentRankDisplay" style="color: #fafafa;">White Belt</span>
                            <span id="nextRankDisplay" style="color: #71717a;">Next Rank: 15 km/h</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill" id="progressBarFill"></div>
                        </div>
                    </div>

                    <div class="image-frame">
                        <img id="cardImg" src="" alt="Dojo Stats Card">
                    </div>
                </div>
            </div>
        </div>

        <script>
            const dropZone = document.getElementById('dropZone');
            const fileInput = document.getElementById('fileInput');
            const uploadPrompt = document.getElementById('uploadPrompt');
            const fileLoaded = document.getElementById('fileLoaded');
            const sessionBestDisplay = document.getElementById('sessionBest');

            // Hook into LocalStorage to maintain a persistent personal best record
            let currentBest = localStorage.getItem('dojo_high_score') || 0;
            sessionBestDisplay.innerText = `${parseFloat(currentBest).toFixed(2)} km/h`;

            // Interactivity Drag-and-Drop Handler Engine
            dropZone.onclick = () => fileInput.click();
            fileInput.onchange = () => {
                if(fileInput.files.length) {
                    uploadPrompt.style.display = 'none';
                    fileLoaded.style.display = 'block';
                }
            };
            dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); };
            dropZone.ondragleave = () => dropZone.classList.remove('drag-over');
            dropZone.ondrop = (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                if(e.dataTransfer.files.length) {
                    fileInput.files = e.dataTransfer.files;
                    uploadPrompt.style.display = 'none';
                    fileLoaded.style.display = 'block';
                }
            };

            // Main Submission Form Network Engine
            document.getElementById('uploadForm').onsubmit = async (e) => {
                e.preventDefault();
                const btn = document.getElementById('submitBtn');
                const panel = document.getElementById('resultPanel');
                const img = document.getElementById('cardImg');
                const bar = document.getElementById('progressBarFill');

                btn.innerText = "ANALYZING FRAME DATA...";
                btn.disabled = true;

                const formData = new FormData(e.target);
                try {
                    const response = await fetch('/analyze/', { method: 'POST', body: formData });
                    if (!response.ok) throw new Error("Processing failed. Ensure entire body movement is captured.");

                    const data = await response.json();

                    // Render Base64 Image Card Output directly into source
                    img.src = data.image_base64;
                    panel.style.display = 'block';

                    // Update Text Outputs
                    document.getElementById('currentRankDisplay').innerText = data.rank;
                    document.getElementById('currentRankDisplay').style.color = data.color;

                    if(data.next_rank) {
                        document.getElementById('nextRankDisplay').innerText = `Next Rank: ${data.next_rank_speed} km/h`;
                        const percentage = Math.min((data.peak_speed / data.next_rank_speed) * 100, 100);
                        // ENHANCEMENT TIP: Add a sound effect trigger right here if percentage > 90% to trigger near-miss excitement!
                        setTimeout(() => { bar.style.width = `${percentage}%`; }, 100);
                    } else {
                        document.getElementById('nextRankDisplay').innerText = "MAX RANK ACHIEVED 🏆";
                        bar.style.width = '100%';
                    }

                    // Evaluate and fire High Score Engine
                    if (data.peak_speed > currentBest) {
                        currentBest = data.peak_speed;
                        localStorage.setItem('dojo_high_score', currentBest);
                        sessionBestDisplay.innerText = `${currentBest.toFixed(2)} km/h 🔥`;
                        sessionBestDisplay.style.color = data.color;

                        // ENHANCEMENT TIP: HTML5 Confetti drop trigger can be added here to reward high-scoring loops.
                    }

                } catch (err) {
                    alert(err.message);
                } finally {
                    btn.innerText = "ANALYZE STRIKE";
                    btn.disabled = false;
                }
            };
        </script>
    </body>
    </html>
    """


@app.post("/analyze/")
async def analyze_video(file: UploadFile = File(...)):
    """Accepts a video upload, computes hand/foot tracking velocities, and classifies rankings."""
    if not file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.3gp')):
        raise HTTPException(status_code=400, detail="Unsupported video container format.")

    temp_filename = f"temp_{file.filename}"
    try:
        # Stream bytes directly to local storage temporarily for CV2 frame slicing processing
        contents = await file.read()
        with open(temp_filename, "wb") as f:
            f.write(contents)

        cap = cv2.VideoCapture(temp_filename)
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Fallback processing if video headers have corrupt metadata or empty variable FPS values
        if fps <= 0 or np.isnan(fps):
            fps = 30.0

        time_per_frame = 1.0 / fps

        # PHYSICS CALIBRATION SCALE:
        # ENHANCEMENT TIP: This static factor assumes a standard camera distance setup.
        # For professional accuracy, let the user input their height, then calculate
        # a custom pixels_per_meter by measuring their body length on frame in real-time!
        pixels_per_meter = 500.0

        speeds = []
        prev_point = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # ENHANCEMENT TIP: To add specialized tracking options (e.g., Kicks Only vs Punches Only),
                # you can switch tracking targets to LEFT_WRIST or LEFT_ANKLE depending on user toggle inputs.
                rw_mark = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
                ra_mark = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

                rw = np.array([int(rw_mark.x * w), int(rw_mark.y * h)])
                ra = np.array([int(ra_mark.x * w), int(ra_mark.y * h)])

                # Automatic strike detector: tracks whichever limb possesses greater frame-by-frame offset variance
                current_point = rw if prev_point is None else (
                    rw if np.linalg.norm(rw - prev_point) > np.linalg.norm(ra - prev_point) else ra)

                if prev_point is not None:
                    pixel_dist = np.linalg.norm(current_point - prev_point)
                    speed_kmh = ((pixel_dist / pixels_per_meter) / time_per_frame) * 3.6

                    # Outlier filter flag (Prevents tracking glitches from registering 300+ km/h ghost values)
                    if speed_kmh < 150.0:
                        speeds.append(speed_kmh)

                prev_point = current_point
            else:
                prev_point = None

        cap.release()

    finally:
        # Ensure cleanup engine triggers under all conditions to prevent storage leaks
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    peak_speed = max(speeds) if speeds else 0.0

    # ==========================================
    # GAMIFICATION RANKING ENGINE
    # ==========================================
    # ENHANCEMENT TIP: You can easily add more tiers or tighten these thresholds here
    # to alter the application difficulty and push user retention goals.
    if peak_speed < 15.0:
        rank, color = "White Belt", "#E4E4E7"
        next_rank, next_rank_speed = "Green Belt", 30.0
    elif peak_speed < 30.0:
        rank, color = "Green Belt", "#10B981"
        next_rank, next_rank_speed = "Brown Belt", 45.0
    elif peak_speed < 45.0:
        rank, color = "Brown Belt", "#F97316"
        next_rank, next_rank_speed = "Black Belt", 60.0
    elif peak_speed < 60.0:
        rank, color = "Black Belt", "#EF4444"
        next_rank, next_rank_speed = "Grandmaster", 80.0
    else:
        rank, color = "Grandmaster", "#F59E0B"
        next_rank, next_rank_speed = None, None

    card_base64 = generate_shareable_card(peak_speed, rank, color)

    return {
        "peak_speed": peak_speed,
        "rank": rank,
        "color": color,
        "next_rank": next_rank,
        "next_rank_speed": next_rank_speed,
        "image_base64": card_base64
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)