# Focus Sense

Focus Sense is a desktop attention-monitoring assistant built for real-time focus, drowsiness, and awareness tracking. It uses MediaPipe face landmarks, OpenCV frame processing, and a PyQt interface to deliver live visual feedback and alert sounds without changing the underlying tracking logic.

---

## 🚀 Features

- **Real-time focus monitoring** with live face landmark analysis
- **Drowsiness and distraction timers** rendered directly on the camera preview
- **Audio alert system** for fatigue and off-task behavior
- **Profile panel** for a lightweight user session overview
- **Modular code layout** that separates the UI layer, engine logic, and shared utilities

---

## 📁 Project Structure

```plaintext
Focus-Sense/
├── main.py                     # Desktop application entry point
├── face_landmarks.py           # Backward-compatible import wrapper
├── requirements.txt            # Python dependencies
├── engine/
│   ├── __init__.py
│   └── attention_engine.py     # Core frame analysis and alert logic
├── utils/
│   ├── __init__.py
│   ├── theme.py                # Branding and UI theme constants
│   ├── camera_preview.py       # Standalone camera preview helper
│   └── icon_gallery.py         # Kivy icon browser helper
├── Audio/
│   ├── Distracted.ogg
│   ├── Posture.ogg
│   └── Sleepy.ogg
├── media/
├── mediapipe_experiments/
└── models/
    └── face_landmarker.task
```

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/focus-sense.git
cd focus-sense
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the application

```bash
python main.py
```

When the app opens, choose a camera source and start the feed. Focus Sense will display the live preview, render attention overlays, and play alerts when distraction or drowsiness thresholds are crossed.

---

## ⚙️ Core Dependencies

- **PyQt5** for the desktop interface
- **OpenCV** for camera capture and frame rendering
- **MediaPipe Tasks** for facial landmark detection
- **sounddevice** and **soundfile** for non-blocking alert playback

---

## 💡 Typical Use Cases

- Personal focus monitoring during study or work sessions
- Drowsiness awareness during long desktop tasks
- Prototype research for attention-aware computer vision interfaces

---

## 🤝 Contributing

If you plan to extend the project, keep UI updates in `main.py`, shared visual constants in `utils/theme.py`, and frame-processing logic in `engine/attention_engine.py`.
