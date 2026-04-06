"""Core frame-analysis utilities for the neurogaze desktop monitor."""

from pathlib import Path
import threading
import time

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

try:
    import sounddevice as sd
    import soundfile as sf
except ImportError:
    sd = None
    sf = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = PROJECT_ROOT / "Audio"
MODEL_PATH = PROJECT_ROOT / "models" / "face_landmarker.task"
ALERT_COOLDOWN_SECONDS = 3.0
_last_audio_timestamp = 0.0
DEFAULT_RATIO_VALUE = 100.0


def load_alert_audio(path: Path):
    """Load an alert clip from disk and return the audio payload used by the player."""
    if sf is None:
        print("Audio support unavailable: install `soundfile` and `sounddevice`.")
        return None

    try:
        audio_data, sample_rate = sf.read(str(path), dtype="float32")
        return {
            "data": audio_data,
            "sample_rate": sample_rate,
            "path": str(path),
        }
    except Exception as exc:
        print(f"Audio disabled for {path}: {exc}")
        return None


DISTRACTED_ALERT_AUDIO = load_alert_audio(AUDIO_DIR / "Distracted.ogg")
DROWSY_ALERT_AUDIO = load_alert_audio(AUDIO_DIR / "Sleepy.ogg")
POSTURE_ALERT_AUDIO = load_alert_audio(AUDIO_DIR / "Posture.ogg")


def render_face_landmarks(rgb_frame, detection_result):
    """Draw lightweight face landmarks on the frame for live monitoring feedback."""
    annotated_frame = np.copy(rgb_frame)
    frame_height, frame_width = annotated_frame.shape[:2]

    for face_landmarks in detection_result.face_landmarks:
        for landmark in face_landmarks:
            x_axis = int(landmark.x * frame_width)
            y_axis = int(landmark.y * frame_height)
            cv2.circle(annotated_frame, (x_axis, y_axis), 1, (0, 255, 0), -1)

    return annotated_frame


def _play_audio_worker(audio_clip):
    if sd is None:
        return

    try:
        sd.stop()
        sd.play(audio_clip["data"], audio_clip["sample_rate"], blocking=True)
    except Exception as exc:
        print(f"Audio playback skipped: {exc}")


def play_alert_audio(audio_clip):
    """Play an alert clip asynchronously so the camera view remains responsive."""
    global _last_audio_timestamp

    if audio_clip is None:
        return

    now = time.monotonic()
    if now - _last_audio_timestamp < ALERT_COOLDOWN_SECONDS:
        return

    _last_audio_timestamp = now
    threading.Thread(target=_play_audio_worker, args=(audio_clip,), daemon=True).start()


def calculate_face_ratio(detection_result, frame_height, frame_width, distance):
    """Normalize a facial distance against the forehead-to-chin distance."""
    face_top_x = detection_result.face_landmarks[0][10].x * frame_width
    face_top_y = detection_result.face_landmarks[0][10].y * frame_height
    face_bottom_x = detection_result.face_landmarks[0][152].x * frame_width
    face_bottom_y = detection_result.face_landmarks[0][152].y * frame_height

    face_distance = np.sqrt(
        (face_top_x - face_bottom_x) ** 2 + (face_top_y - face_bottom_y) ** 2
    )
    return round(distance / face_distance * 100, 2)


def measure_left_eyelid_gap(detection_result, frame_height, frame_width):
    """Measure the vertical gap between the upper and lower left eyelids."""
    upper_lid_y = detection_result.face_landmarks[0][386].y * frame_height
    lower_lid_y = detection_result.face_landmarks[0][374].y * frame_height
    return abs(upper_lid_y - lower_lid_y)


def measure_inter_eye_distance(detection_result, frame_height, frame_width):
    """Measure the distance between the iris points to estimate head orientation."""
    left_eye_x = detection_result.face_landmarks[0][468].x * frame_width
    right_eye_x = detection_result.face_landmarks[0][473].x * frame_width
    left_eye_y = detection_result.face_landmarks[0][468].y * frame_height
    right_eye_y = detection_result.face_landmarks[0][473].y * frame_height

    return np.sqrt(
        (left_eye_x - right_eye_x) ** 2 + (right_eye_y - left_eye_y) ** 2
    )


base_options = python.BaseOptions(model_asset_path=str(MODEL_PATH))
landmarker_options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True,
    output_facial_transformation_matrixes=True,
    num_faces=1,
)
FACE_LANDMARKER = vision.FaceLandmarker.create_from_options(landmarker_options)


def analyze_attention_frame(frame):
    """Return distraction and drowsiness ratios alongside the annotated camera frame."""
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    frame_height, frame_width, _ = frame.shape
    detection_result = FACE_LANDMARKER.detect(mp_image)
    distraction_ratio = DEFAULT_RATIO_VALUE
    drowsiness_ratio = DEFAULT_RATIO_VALUE

    if not detection_result.face_landmarks:
        return distraction_ratio, drowsiness_ratio, frame

    try:
        eyelid_gap = measure_left_eyelid_gap(detection_result, frame_height, frame_width)
        eye_distance = measure_inter_eye_distance(detection_result, frame_height, frame_width)
        drowsiness_ratio = calculate_face_ratio(
            detection_result, frame_height, frame_width, eyelid_gap
        )
        distraction_ratio = calculate_face_ratio(
            detection_result, frame_height, frame_width, eye_distance
        )
    except Exception as exc:
        print(f"Frame analysis warning: {exc}")

    annotated_frame = render_face_landmarks(mp_image.numpy_view(), detection_result)
    return distraction_ratio, drowsiness_ratio, annotated_frame
