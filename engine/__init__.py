"""Core monitoring engine package for neurogaze."""

from .attention_engine import (
    DISTRACTED_ALERT_AUDIO,
    DROWSY_ALERT_AUDIO,
    POSTURE_ALERT_AUDIO,
    analyze_attention_frame,
    play_alert_audio,
)

__all__ = [
    "DISTRACTED_ALERT_AUDIO",
    "DROWSY_ALERT_AUDIO",
    "POSTURE_ALERT_AUDIO",
    "analyze_attention_frame",
    "play_alert_audio",
]
