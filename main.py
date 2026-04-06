import sys

import cv2
from PyQt5.QtCore import QPropertyAnimation, QRect, QTimer, Qt
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from engine.attention_engine import (
    DISTRACTED_ALERT_AUDIO,
    DROWSY_ALERT_AUDIO,
    analyze_attention_frame,
    play_alert_audio,
)
from utils.theme import (
    APP_NAME,
    OVERLAY_TEXT_COLOR,
    PRIMARY_TEXT_COLOR,
    SECONDARY_TEXT_COLOR,
    SURFACE_BORDER_COLOR,
    WINDOW_BACKGROUND_COLOR,
)


class SplashScreen(QMainWindow):
    """Display a short welcome screen before the live monitoring view opens."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setFixedSize(1000, 600)
        self.setStyleSheet(f"background-color: {WINDOW_BACKGROUND_COLOR};")

        self.splash_label = QLabel(self)
        self.splash_label.setText(f"Welcome to {APP_NAME}")
        self.splash_label.setFont(QFont("Arial", 30, QFont.Bold))
        self.splash_label.setAlignment(Qt.AlignCenter)
        self.splash_label.setStyleSheet(f"color: {PRIMARY_TEXT_COLOR};")
        self.splash_label.setGeometry(0, 200, 1000, 100)

        self.animation_label = QLabel(self)
        self.animation_label.setText("Initializing live monitoring...")
        self.animation_label.setFont(QFont("Arial", 20))
        self.animation_label.setAlignment(Qt.AlignCenter)
        self.animation_label.setStyleSheet(f"color: {SECONDARY_TEXT_COLOR};")
        self.animation_label.setGeometry(0, 300, 1000, 50)

        self.animation = QPropertyAnimation(self.animation_label, b"geometry")
        self.animation.setDuration(2000)
        self.animation.setStartValue(QRect(0, 300, 1000, 50))
        self.animation.setEndValue(QRect(0, 500, 1000, 50))
        self.animation.finished.connect(self.hide_splash_screen)
        self.animation.start()

    def hide_splash_screen(self):
        """Dismiss the loading text and open the primary camera window."""
        self.animation_label.setVisible(False)
        self.show_main_window()

    def show_main_window(self):
        """Create the live monitoring window after the splash screen finishes."""
        self.main_window = CameraWindow()
        self.main_window.show()
        self.close()


class CameraWindow(QMainWindow):
    """Render the profile panel and live camera feed for neurogaze."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)

        self.video_capture = None
        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self.update_frame)
        self.drowsiness_timer = 0.0
        self.distraction_period = 0.0

        self.profile_record = {"name": "", "age": "", "picture": None}
        self.init_ui()

    def init_ui(self):
        """Build the desktop layout for the user profile and camera panel."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        profile_layout = QVBoxLayout()
        profile_layout.setSpacing(20)
        profile_layout.setAlignment(Qt.AlignTop)

        profile_title = QLabel("User Profile", self)
        profile_title.setFont(QFont("Arial", 18, QFont.Bold))
        profile_title.setStyleSheet(f"color: {PRIMARY_TEXT_COLOR};")
        profile_layout.addWidget(profile_title)

        self.profile_picture_label = QLabel(self)
        self.profile_picture_label.setAlignment(Qt.AlignCenter)
        self.profile_picture_label.setFixedSize(150, 150)
        self.profile_picture_label.setStyleSheet(
            f"border: 1px solid {SURFACE_BORDER_COLOR}; border-radius: 10px;"
        )
        profile_layout.addWidget(self.profile_picture_label)

        select_picture_button = QPushButton("Select Picture", self)
        select_picture_button.clicked.connect(self.select_profile_picture)
        profile_layout.addWidget(select_picture_button)

        form_layout = QFormLayout()
        self.name_input = QLineEdit(self)
        self.age_input = QLineEdit(self)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Age:", self.age_input)
        profile_layout.addLayout(form_layout)

        save_profile_button = QPushButton("Save Profile", self)
        save_profile_button.clicked.connect(self.save_profile_record)
        profile_layout.addWidget(save_profile_button)

        self.profile_display = QLabel(self)
        self.profile_display.setAlignment(Qt.AlignTop)
        self.profile_display.setWordWrap(True)
        self.profile_display.setStyleSheet(
            "border: 1px solid #d0d3d6; padding: 12px; color: #2c3e50; background-color: #ffffff;"
        )
        profile_layout.addWidget(self.profile_display)
        profile_layout.addStretch(1)

        profile_widget = QWidget(self)
        profile_widget.setLayout(profile_layout)
        profile_widget.setFixedWidth(300)
        profile_widget.setStyleSheet(
            "background-color: #f5f6f7;"
            "border-right: 1px solid #d7dbdd;"
            "color: #2c3e50;"
            "QLabel { color: #2c3e50; }"
            "QLineEdit { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 5px; padding: 6px; color: #2c3e50; }"
            "QPushButton { background-color: #3498db; color: #ffffff; border: none; border-radius: 6px; padding: 8px 12px; }"
            "QPushButton:hover { background-color: #2980b9; }"
            "QPushButton:pressed { background-color: #217dbb; }"
        )

        main_layout.addWidget(profile_widget)

        camera_layout = QVBoxLayout()
        camera_layout.setSpacing(20)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        self.camera_dropdown = QComboBox(self)
        self.camera_dropdown.addItems(["Select Camera", "0", "1"])
        self.camera_dropdown.currentIndexChanged.connect(self.switch_camera_source)
        controls_layout.addWidget(self.camera_dropdown)

        self.start_button = QPushButton("Start Camera", self)
        self.start_button.setFixedSize(150, 40)
        self.start_button.clicked.connect(self.start_camera_stream)
        controls_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera", self)
        self.stop_button.setFixedSize(150, 40)
        self.stop_button.clicked.connect(self.stop_camera_stream)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addStretch(1)

        camera_layout.addLayout(controls_layout)

        self.display_label = QLabel(self)
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.display_label.setScaledContents(True)
        self.display_label.setText("Camera feed will appear here.")
        self.display_label.setStyleSheet(
            f"border: 1px solid {SURFACE_BORDER_COLOR}; background-color: #111; color: {SECONDARY_TEXT_COLOR};"
        )
        camera_layout.addWidget(self.display_label)

        main_layout.addLayout(camera_layout)
        central_widget.setLayout(main_layout)

    def select_profile_picture(self):
        """Allow the user to attach a profile image to the session."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Profile Picture",
            "",
            "Images (*.png *.jpg *.jpeg)",
        )
        if file_name:
            pixmap = QPixmap(file_name)
            self.profile_picture_label.setPixmap(
                pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.profile_record["picture"] = file_name

    def save_profile_record(self):
        """Store the entered profile details and refresh the summary panel."""
        name = self.name_input.text()
        age = self.age_input.text()

        if not name or not age:
            self.profile_display.setText("Please enter both name and age.")
            return

        self.profile_record["name"] = name
        self.profile_record["age"] = age
        self.render_profile_summary()

    def render_profile_summary(self):
        """Show a compact profile summary beside the live camera feed."""
        profile_text = (
            f"Name: {self.profile_record['name']}\n"
            f"Age: {self.profile_record['age']}"
        )
        self.profile_display.setText(profile_text)

    def start_camera_stream(self):
        """Open the selected camera source and begin refreshing the UI frame."""
        camera_index = (
            int(self.camera_dropdown.currentText())
            if self.camera_dropdown.currentText() != "Select Camera"
            else 0
        )
        self.video_capture = cv2.VideoCapture(camera_index)
        if self.video_capture.isOpened():
            self.frame_timer.start(33)

    def stop_camera_stream(self):
        """Stop the refresh timer and release the active camera source."""
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        self.frame_timer.stop()

    def update_frame(self):
        """Analyze the latest frame and show alert overlays in the preview panel."""
        if not self.video_capture:
            return

        frame_available, frame = self.video_capture.read()
        if not frame_available:
            return

        distraction_ratio, drowsiness_ratio, annotated_frame = analyze_attention_frame(frame)

        if distraction_ratio <= 38:
            self.distraction_period += 1 / 15.0
        elif drowsiness_ratio < 4:
            self.drowsiness_timer += 1 / 15.0
        else:
            self.distraction_period = 0.0
            self.drowsiness_timer = 0.0

        if self.distraction_period >= 8:
            print("Distraction alert triggered.")
            play_alert_audio(DISTRACTED_ALERT_AUDIO)
            self.distraction_period = 0.0
        elif self.drowsiness_timer >= 8:
            print("Drowsiness alert triggered.")
            play_alert_audio(DROWSY_ALERT_AUDIO)
            self.drowsiness_timer = 0.0

        cv2.putText(
            annotated_frame,
            f"Drowsiness Timer: {round(self.drowsiness_timer, 1)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            OVERLAY_TEXT_COLOR,
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            annotated_frame,
            f"Distraction Period: {round(self.distraction_period, 1)}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            OVERLAY_TEXT_COLOR,
            1,
            cv2.LINE_AA,
        )

        rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        height, width, _ = rgb_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888,
        )
        self.display_label.setPixmap(QPixmap(q_image))

    def switch_camera_source(self):
        """Swap to a new camera source when the user changes the selector."""
        if self.video_capture:
            self.video_capture.release()
        self.start_camera_stream()


if __name__ == "__main__":
    application = QApplication(sys.argv)
    splash_screen = SplashScreen()
    splash_screen.show()
    sys.exit(application.exec_())


