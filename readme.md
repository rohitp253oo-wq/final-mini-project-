# neurogaze

neurogaze is a professional-grade desktop application for real-time focus assistance and attention monitoring. Leveraging MediaPipe facial analysis, OpenCV computer vision, and modern PyQt5 UI, neurogaze provides enterprise-ready monitoring of user attention, drowsiness detection, and distraction awareness with intelligent audio-visual feedback.

---

## 🚀 Features

- **Real-time attention analysis** using advanced facial landmark detection
- **Intelligent drowsiness detection** with configurable sensitivity thresholds
- **Distraction monitoring** with immediate visual and audio alerts
- **Session profile dashboard** for tracking focus metrics over time
- **Enterprise-grade architecture** with separated concerns: UI, processing engine, and utilities
- **Audio alert system** delivering non-intrusive notifications for attention lapses

---

## 📁 Project Structure

```plaintext
neurogaze/
├── main.py                     # Application entry point
├── face_landmarks.py           # Backward-compatible import wrapper
├── requirements.txt            # Python dependencies
├── engine/
│   ├── __init__.py
│   └── attention_engine.py     # Core attention analysis and alert logic
├── utils/
│   ├── __init__.py
│   ├── theme.py                # UI styling and visual constants
│   ├── camera_preview.py       # Camera utility functions
│   └── icon_gallery.py         # UI icon resources
├── Audio/
│   ├── Distracted.ogg
│   ├── Posture.ogg
│   └── Sleepy.ogg
├── media/
├── core_tracking/              # Advanced tracking modules
└── models/
    └── face_landmarker.task
```

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/rohitp253oo-wq/final-mini-project-.git
cd neurogaze
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

```bash
python main.py
```

Launch the application, select your camera source, and begin monitoring. neurogaze will continuously analyze focus patterns, display real-time attention metrics, and alert you when drowsiness or significant distraction is detected.

---

## ⚙️ Core Dependencies

- **PyQt5** – Modern desktop UI framework
- **OpenCV** – Camera capture and frame processing
- **MediaPipe Tasks** – Facial landmark recognition and analysis
- **sounddevice & soundfile** – Non-blocking audio alert delivery

---

## 📊 Use Cases

- **Workplace focus optimization** – Monitor employee attention during critical tasks
- **Educational environments** – Detect student engagement and drowsiness
- **Research and development** – Prototype attention-aware human-computer interaction systems
- **Professional productivity** – Personal focus tracking during deep work sessions

---

## 🏗️ Architecture

neurogaze follows a clean separation of concerns:

- **`main.py`** – PyQt5 UI layer and session management
- **`engine/attention_engine.py`** – Core computer vision and attention analysis
- **`utils/`** – Shared utilities for theming, camera operations, and resources

---

## 🤝 Contributing

To extend neurogaze:
- Add UI improvements in `main.py`
- Update styling constants in `utils/theme.py`
- Enhance analysis logic in `engine/attention_engine.py`
- Place experimental tracking modules in `core_tracking/`

---

## 📝 License

This project is provided as-is for professional use.
