import sys
import cv2
import pytesseract
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from PIL import Image
import numpy as np
from transformers import pipeline

# Load Hugging Face text-to-text model
nlp_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

class OCRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EyeBalled - PyQt Edition")
        self.resize(1000, 700)

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

        # Preprocess image for OCR (grayscale + threshold)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        pil_image = Image.fromarray(thresh)

        # OCR
        extracted_text = pytesseract.image_to_string(pil_image)
        self.text_output.setPlainText(extracted_text)

        # NLP Interpretation
        try:
            result = nlp_pipeline(extracted_text, max_length=100, clean_up_tokenization_spaces=True)
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