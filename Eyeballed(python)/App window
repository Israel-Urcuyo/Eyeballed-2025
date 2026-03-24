import sys
import cv2
import subprocess
import pytesseract  # Optional: fallback/debug
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from PIL import Image
import numpy as np
from transformers import pipeline
import os

# Load NLP model
nlp_pipeline = pipeline("text-generation", model="gpt2")

# Shared directory
SHARED_DIR = "shared"
INPUT_IMAGE_PATH = os.path.join(SHARED_DIR, "input.jpg")
OCR_OUTPUT_PATH = os.path.join(SHARED_DIR, "output.txt")
SWIFT_BINARY_PATH = "./ocr"

class OCRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EyeBalled - PyQt Edition")
        self.setFixedSize(1000, 700)

        # Camera setup
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            raise RuntimeError("[FATAL] Cannot open camera.")

        # UI Components
        self.video_label = QLabel()
        self.capture_button = QPushButton("Take Picture")
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.nlp_output = QTextEdit()
        self.nlp_output.setReadOnly(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.capture_button)

        text_layout = QHBoxLayout()
        text_layout.addWidget(self.text_output)
        text_layout.addWidget(self.nlp_output)
        layout.addLayout(text_layout)

        self.setLayout(layout)

        # Timer for live camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # Connect button
        self.capture_button.clicked.connect(self.capture_frame)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def capture_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.text_output.setPlainText("[ERROR] Failed to capture frame.")
            return

        # Save image for Swift OCR
        os.makedirs(SHARED_DIR, exist_ok=True)
        cv2.imwrite(INPUT_IMAGE_PATH, frame)

        # Call Swift OCR binary
        try:
            subprocess.run([SWIFT_BINARY_PATH], check=True)
        except Exception as e:
            self.text_output.setPlainText(f"[ERROR] Swift OCR failed: {str(e)}")
            self.nlp_output.setPlainText("")
            return

        # Read OCR result
        try:
            with open(OCR_OUTPUT_PATH, "r") as f:
                extracted_text = f.read().strip()
        except FileNotFoundError:
            extracted_text = "[ERROR] No OCR output found."

        self.text_output.setPlainText(extracted_text)

        # NLP Interpretation
        if not extracted_text or "[ERROR]" in extracted_text:
            self.nlp_output.setPlainText("[INFO] No valid text detected.")
            return

        try:
            prompt = f"You are being fed vague homework prompts. Using what you know, answer the homework prompts as concisely as possible.\n\nPrompt:\n{extracted_text}\n\nAnswer:"
            result = nlp_pipeline(prompt, max_length=100, do_sample=True, temperature=0.7)
            answer = result[0]["generated_text"]
        except Exception as e:
            answer = f"[ERROR] NLP processing failed: {str(e)}"

        self.nlp_output.setPlainText(answer)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OCRApp()
    window.show()
    sys.exit(app.exec_())