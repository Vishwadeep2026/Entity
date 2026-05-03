





import sys
import os   
import threading
import speech_recognition as sr
import ollama
from PIL import Image
import pytesseract
import keyboard  
import cv2
import numpy as np
import subprocess
import uuid
import pyautogui
import hashlib
import base64
import sqlite3
import datetime
import platform
from cryptography.fernet import Fernet
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QBuffer, QIODevice, QSize
from PyQt6.QtGui import QColor, QPainter, QPen, QShortcut, QKeySequence, QImage, QPixmap, QIcon, QTextOption

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

MODEL_NAME = "qwen3-vl:235b-instruct-cloud"
NFS_DECRYPT_MODEL_NAME = "qwen3-vl:235b-instruct-cloud"
REALTIME_MODE_SCRIPT = r"C:\Users\admin\OneDrive\Desktop\Projects\Sample.py"
MICROBOT_SCRIPT = r"C:\Users\admin\OneDrive\Desktop\Projects\SDFG.py"
AUTOBOT_SCRIPT = r"C:\Users\admin\OneDrive\Desktop\Projects\ENT.py"

VISION_OUT_SYSTEM_PROMPT = (
    "You are a vision-based AI assistant for Vision OUT (webcam view).\n"
    "Treat the provided images as real visual input from the user's environment.\n"
    "Do not mention “image”; you should mention “vision” instead.\n"
    "Do not say that you cannot see the image.\n"
    "Prioritize the latest image as the current view.\n"
    "Reply quickly in one short line or a medium-length sentence describing only what is visible."
)

VISION_IN_SYSTEM_PROMPT = (
    "You are a vision-based AI assistant for Vision IN (screen capture view).\n"
    "Treat the provided images as real visual input from the user's screen.\n"
    "Do not mention “image”; you should mention “vision” instead.\n"
    "Do not say that you cannot see the image.\n"
    "Prioritize the latest image as the current view.\n"
    "Reply quickly in one short line or a medium-length sentence describing only what is visible on screen."
)

GMAIL_AGENT_PROMPT = """
You are a Gmail Automation Agent.

Purpose:
Perform Gmail sending operations only using Python and yagmail.

Rules:

1. Never ask unnecessary questions.

2. If recipient email is missing, ask only:
'Recipient Gmail address?'

3. If recipient exists, immediately generate and execute Gmail sending code.

4. Never explain the code.

5. Never provide extra conversation.

6. Output only executable Python code.

7. Use yagmail library only.

8. Always use this structure:

import yagmail

yag = yagmail.SMTP("vishwadeep2026@gmail.com", "miftvgquwmgymuyh")

yag.send(
    to=RECIPIENT,
    subject=SUBJECT,
    contents=CONTENT
)

print("Email sent!")

9. Used strictly for:
- Sending emails
- Gmail notifications
- Gmail automation

10. Do not perform any task unrelated to Gmail operations.

Behavior:

If user says:
"Send hello to abc@gmail.com"

Output only Python code.

If user says:
"Send mail"

Reply only:
Recipient Gmail address?
"""

with open(r"C:\Users\admin\OneDrive\Desktop\AI\JARVIS_BEHAVE.txt", "r", encoding="utf-8") as f:
    behavior = f.read()

with open(r"C:\Users\admin\OneDrive\Desktop\AI\NFS-AI\Encrypt_behave.txt", "r", encoding="utf-8") as f:
    behavior3 = f.read()

with open(r"C:\Users\admin\OneDrive\Desktop\AI\NFS-AI\Decrypt_behave.txt", "r", encoding="utf-8") as f:
    behavior4 = f.read()

with open(r"C:\Users\admin\OneDrive\Desktop\AI\NFS-AI\Decrypt_behave2.txt", "r", encoding="utf-8") as f:
    behavior6 = f.read()

def ask_gwen(question):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content":behavior
            },
            {"role": "user", "content": question}
        ]
    )
    return response["message"]["content"].strip()

# Decryption functions
save_path = r"C:\Users\admin\OneDrive\Desktop\AI"
filename = os.path.join(save_path, "webcam.png")

def capture_intruder_image():
    save_path = r"C:\Users\admin\OneDrive\Desktop\AI"
    os.makedirs(save_path, exist_ok=True)

    img_name = f"intruder_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img_path = os.path.join(save_path, img_name)

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    if ret:
        cv2.imwrite(img_path, frame)

    cap.release()
    return img_path

def gds():
    try:
        output = subprocess.check_output("wmic diskdrive get serialnumber", shell=True)
        lines = output.decode().splitlines()
        serials = [line.strip() for line in lines if line.strip() and "SerialNumber" not in line]
        return serials[0] if serials else "unknown"
    except:
        return "unknown"

def gdc():
    mac = str(uuid.getnode())
    node = platform.node()
    system = platform.system()
    release = platform.release()
    disk_serial = gds()
    raw = f"{mac}{node}{system}{release}{disk_serial}"
    return hashlib.sha256(raw.encode()).hexdigest(), raw

def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key[:32])


def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def decrypt_file(file_path, password):
    if not os.path.exists(file_path):
        msg = "File does not exist."
        print(msg)
        return False, msg

    filename = os.path.basename(file_path)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    key = generate_key(password)
    fernet = Fernet(key)
    device_code, raw_info = gdc()

    conn = sqlite3.connect("secure_files.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs WHERE filename=? AND password_hash=?", (filename, password_hash))
    row = cur.fetchone()
    conn.close()

    if not row:
        msg = "❌ Password incorrect or file not registered."
        print(msg)
        return False, msg

    if row[3] != device_code:
        msg = "❌ Device mismatch! Unauthorized."
        print(msg)
        return False, msg

    try:
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        original_path = file_path.replace(".secure", "")
        if not os.path.splitext(original_path)[1]:
            original_path += ".recovered"
        with open(original_path, 'wb') as f:
            f.write(decrypted_data)
        msg = f"✅ File decrypted: {original_path}"
        print(msg)
        return True, msg
    except:
        msg = "❌ Decryption failed. Wrong password or corrupted file."
        print(msg)
        return False, msg

# ------------------ SIGNALS ------------------
class Signals(QObject):
    reply = pyqtSignal(str)
    usertext = pyqtSignal(str)
    clear_user = pyqtSignal()

signals = Signals()


class HoverButton(QPushButton):
    def __init__(self, normal_icon, hover_icon, click_icon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.normal_icon = QIcon(normal_icon)
        self.hover_icon = QIcon(hover_icon)
        self.click_icon = QIcon(click_icon)
        self.setIcon(self.normal_icon)

    def enterEvent(self, event):
        self.setIcon(self.hover_icon)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(self.normal_icon)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.setIcon(self.click_icon)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.underMouse():
            self.setIcon(self.hover_icon)
        else:
            self.setIcon(self.normal_icon)
        super().mouseReleaseEvent(event)

# ------------------ UI ------------------
class MainUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setWindowTitle(" E N T I T Y ")
        self.setWindowIcon(QIcon(r"D:\R1.ico"))
        self.background_image_path = r"C:\Users\admin\OneDrive\Desktop\JARVIS-2026\UI-JARVIS.png"
        self.background_pixmap = QPixmap(self.background_image_path)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.screen = QApplication.primaryScreen()
        self.screen_size = self.screen.size() if self.screen else None

        self.base_w = 900
        self.base_h = 600
        self.setMinimumSize(self.base_w, self.base_h)

        self.scale = 1.0
        self.scale_x = 1.0
        self.scale_y = 1.0

        self.setGeometry(100, 100, self.base_w, self.base_h)

        self.cloak = False
        self.capture_count = 0
        self.vision_out_dir = r"C:\Users\admin\OneDrive\Desktop\AI\VISION_OUT"
        os.makedirs(self.vision_out_dir, exist_ok=True)
        self.remote_process = None
        self.vo_process = None
        self.realtime_mode_process = None
        self.autobot_process = None
        self.microbot_processes = []

        self.notepad1 = QTextEdit(self)
        self.notepad2 = QTextEdit(self)

        self.round_btn = QPushButton("", self)
        self.rect_btn = HoverButton(
            r"C:\Users\admin\OneDrive\Desktop\JARVIS-2026\SEND-JARVIS.png",
            r"C:\Users\admin\OneDrive\Desktop\JARVIS-2026\SEND-HOVER-JARVIS.png",
            r"C:\Users\admin\OneDrive\Desktop\JARVIS-2026\SEND-CLICK-JARVIS.png",
            "",
            self,
        )

        # Keep old names as aliases so existing logic continues to work.
        self.user_box = self.notepad1
        self.output_box = self.notepad2
        self.submit_btn = self.rect_btn
        self.mic_btn = self.round_btn
        self.widgets = [self.notepad1, self.notepad2, self.rect_btn, self.round_btn]

        self.mic_icon_path = r"C:\Users\admin\OneDrive\Desktop\JARVIS-2026\MIC-JARVIS.png"

        # Base structure variables from the UI reference. Edit these for quick tuning.
        self.ui_structure = {
            "rect_btn_width_sub": 1650,
            "rect_btn_height_sub": 1000,
            "rect_btn_x_sub": 1100,
            "rect_btn_y_sub": 680,
            "pad_width_sub": 320,
            "pad_height_sub": 820,
            "pad_height2_sub": 740,
            "pad_x_sub": 160,
            "pad_y_sub": 764,
            "notepad2_y_add": 450,
            "round_btn_size": 120,
            "round_btn_x_add": 910,
            "round_btn_y_add": 300,
        }

        # Fine per-widget offsets. Positive/negative values move or resize each control.
        self.ui_offsets = {
            "notepad1_x": 0,
            "notepad1_y": 0,
            "notepad1_w": 0,
            "notepad1_h": 0,
            "notepad2_x": 0,
            "notepad2_y": 40,
            "notepad2_w": 0,
            "notepad2_h": 80,
            "rect_btn_x": 0,
            "rect_btn_y": 0,
            "rect_btn_w": 0,
            "rect_btn_h": 0,
            "round_btn_x": 0,
            "round_btn_y": 0,
            "round_btn_size": 0,
        }

        # Mini mode attributes
        self.q_mini = False
        self.default_w = self.base_w
        self.default_h = self.base_h

        self.init_ui()
        signals.reply.connect(self.output_box.setPlainText)
        signals.usertext.connect(self.user_box.setPlainText)
        signals.clear_user.connect(self.user_box.clear)

        self.save_dir = r"C:\Users\admin\OneDrive\Desktop\LO"
        os.makedirs(self.save_dir, exist_ok=True)
        self.save_path = os.path.join(self.save_dir, "scrt.png")

        self.vision_in_dir = r"C:\Users\admin\OneDrive\Desktop\AI\VISION_IN"
        os.makedirs(self.vision_in_dir, exist_ok=True)
        self.capture_count = 0
        self.capture_in_count = 0

        self.setWindowState(Qt.WindowState.WindowNoState)
        self.resize(self.base_w, self.base_h)
        self.move(300, 200)
        self.activateWindow()
        self.setFocus()

        # ----------------- SHORTCUT -----------------
        self.focus_shortcut = QShortcut(QKeySequence("A"), self)
        self.focus_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.focus_shortcut.activated.connect(self.force_focus)

        # ----------------- GLOBAL HOTKEYS -----------------
        self.register_global_hotkeys()

    # -------- FOCUS FUNCTION --------
    def force_focus(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.setWindowState(Qt.WindowState.WindowActive)
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    # -------- GLOBAL HOTKEY THREAD-SAFE --------
    def register_global_hotkeys(self):
        step = 10
        # Force focus
        keyboard.add_hotkey('shift+a', lambda: threading.Thread(target=self.force_focus).start())
        # Arrow keys for movement
        keyboard.add_hotkey('up', lambda: self.move(self.x(), self.y() - step))
        keyboard.add_hotkey('down', lambda: self.move(self.x(), self.y() + step))
        keyboard.add_hotkey('left', lambda: self.move(self.x() - step, self.y()))
        keyboard.add_hotkey('right', lambda: self.move(self.x() + step, self.y()))
        # Q mini toggle
        keyboard.add_hotkey('shift+h', self.toggle_mini)
        # Scale keys
        keyboard.add_hotkey('shift+z', lambda: self.adjust_scale(0.1))
        keyboard.add_hotkey('shift+x', lambda: self.adjust_scale(-0.1))
        keyboard.add_hotkey('shift+c', lambda: self.adjust_scale_x(0.1))
        keyboard.add_hotkey('shift+b', lambda: self.adjust_scale_x(-0.1))
        keyboard.add_hotkey('shift+v', lambda: self.adjust_scale_y(0.1))
        keyboard.add_hotkey('shift+n', lambda: self.adjust_scale_y(-0.1))
        # Reset to default
        keyboard.add_hotkey('shift+m', self.reset_to_default)
        # HUD capture
        keyboard.add_hotkey('shift+s', lambda: self.hud_capture())
        # OpenCV capture
        keyboard.add_hotkey('shift+g', self.capture_with_opencv)
        # Screenshot capture
        keyboard.add_hotkey('shift+f', self.capture_screenshot_and_send)
        # Transparent area capture
        keyboard.add_hotkey('shift+d', self.capture_transparent_area)

    # -------- SCALE HELPERS --------
    def adjust_scale(self, delta):
        self.scale = min(1.6, max(0.6, self.scale + delta))
        self.update_layout()
    def adjust_scale_x(self, delta):
        self.scale_x = max(0.5, self.scale_x + delta)
        self.update_layout()
    def adjust_scale_y(self, delta):
        self.scale_y = max(0.5, self.scale_y + delta)
        self.update_layout()

    # -------- RESET TO DEFAULT --------
    def reset_to_default(self):
        self.scale = 1.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.setWindowState(Qt.WindowState.WindowNoState)
        self.resize(self.base_w, self.base_h)
        self.update_layout()

    # -------- MINI TOGGLE --------
    def toggle_mini(self):
        if not self.q_mini:
            self.default_w = self.width()
            self.default_h = self.height()
            self.resize(50, 50)
            for w in self.widgets:
                w.hide()
            self.q_mini = True
        else:
            self.resize(self.default_w, self.default_h)
            for w in self.widgets:
                w.show()
            self.update_layout()
            self.q_mini = False

    # -------- UI --------
    def init_ui(self):
        note_style = (
            "background-color: rgba(0,255,255,0); "
            "color: cyan; "
            "font-size: 22px; "
            "border: 0;"
        )

        self.notepad1.setStyleSheet(note_style)
        self.notepad1.setFontFamily("Roboto")
        self.notepad1.setPlaceholderText(" Ask Entity anything... ")

        self.notepad2.setStyleSheet(note_style)
        self.notepad2.setFontFamily("Roboto")
        self.notepad2.setReadOnly(True)
        self.notepad2.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.notepad2.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.notepad2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.notepad2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.round_btn.setIcon(QIcon(self.mic_icon_path))
        self.round_btn.setStyleSheet("background: transparent; border: 0;")
        self.rect_btn.setStyleSheet("background: transparent; border: 0;")

        self.rect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.round_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rect_btn.clicked.connect(self.process_text)
        self.round_btn.clicked.connect(self.process_voice)
        self.update_layout()

    def _scale_design_rect(self, x, y, w, h, win_w, win_h):
        design_w = max(1, self.screen_size.width() if self.screen_size else 1920)
        design_h = max(1, self.screen_size.height() if self.screen_size else 1080)

        sx = win_w / design_w
        sy = win_h / design_h

        x = int(x * sx * self.scale_x)
        y = int(y * sy * self.scale_y)
        w = int(w * sx * self.scale * self.scale_x)
        h = int(h * sy * self.scale * self.scale_y)

        w = max(20, w)
        h = max(20, h)

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x + w > win_w:
            w = max(20, win_w - x)
        if y + h > win_h:
            h = max(20, win_h - y)

        return x, y, w, h

    def update_layout(self):
        win_w = self.width()
        win_h = self.height()
        if win_w <= 0 or win_h <= 0:
            return

        design_w = self.screen_size.width() if self.screen_size else 1920
        design_h = self.screen_size.height() if self.screen_size else 1080
        s = self.ui_structure
        off = self.ui_offsets

        rect_btn_width = max(120, (design_w - s["rect_btn_width_sub"]) + off["rect_btn_w"])
        rect_btn_height = max(60, (design_h - s["rect_btn_height_sub"]) + off["rect_btn_h"])
        rect_btn_x = (design_w - s["rect_btn_x_sub"]) + off["rect_btn_x"]
        rect_btn_y = 430

        pad_width = max(320, (design_w - s["pad_width_sub"]) + off["notepad1_w"])
        pad_height = max(120, (design_h - s["pad_height_sub"]) + off["notepad1_h"])
        pad_height2 = max(120, (design_h - s["pad_height2_sub"]) + off["notepad2_h"])
        pad_x = (design_w - pad_width - s["pad_x_sub"]) + off["notepad1_x"]
        pad_y = (design_h - pad_height - s["pad_y_sub"]) + off["notepad1_y"]

        pad2_x = pad_x + off["notepad2_x"]
        pad2_y = (pad_y + s["notepad2_y_add"]) + off["notepad2_y"]
        pad2_w = max(320, pad_width + off["notepad2_w"])

        round_size = max(44, s["round_btn_size"] + off["round_btn_size"])
        round_x = (rect_btn_width + s["round_btn_x_add"]) + off["round_btn_x"]
        round_y = 410

        n1 = self._scale_design_rect(pad_x, pad_y, pad_width, pad_height, win_w, win_h)
        n2 = self._scale_design_rect(pad2_x, pad2_y, pad2_w, pad_height2, win_w, win_h)
        b1 = self._scale_design_rect(rect_btn_x, rect_btn_y, rect_btn_width, rect_btn_height, win_w, win_h)
        b2 = self._scale_design_rect(round_x, round_y, round_size, round_size, win_w, win_h)

        self.notepad1.setGeometry(*n1)
        self.notepad2.setGeometry(*n2)
        self.rect_btn.setGeometry(*b1)
        self.round_btn.setGeometry(*b2)

        self.rect_btn.setIconSize(QSize(b1[2], b1[3] + 80))
        self.round_btn.setIconSize(QSize(b2[2], b2[3]))
        self.round_btn.setStyleSheet(
            f"background: transparent; border: 0; border-radius: {max(10, min(b2[2], b2[3]) // 2)}px;"
        )

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if not self.q_mini:
            self.update_layout()

    # -------- HUD BACKGROUND --------
    def paintEvent(self, e):
        if self.cloak:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.background_pixmap.isNull():
            p.drawPixmap(self.rect(), self.background_pixmap)
        else:
            p.fillRect(self.rect(), QColor(8, 24, 40))

        # Slight tint improves text readability over bright images.
        p.fillRect(self.rect(), QColor(0, 0, 0, 40))

    # -------- HUD OCR --------
    def hud_capture(self):
        for w in self.widgets: w.hide()
        self.repaint(); QApplication.processEvents()
        QTimer.singleShot(50, self.take_screenshot)

    def take_screenshot(self):
        screen = QApplication.primaryScreen()
        geo = self.frameGeometry()
        pixmap = screen.grabWindow(0, geo.x(), geo.y(), geo.width(), geo.height())
        pixmap.save(self.save_path)
        for w in self.widgets: w.show()
        try:
            img = Image.open(self.save_path)
            text = pytesseract.image_to_string(img).strip()
            if text:
                signals.usertext.emit(text)

        except:
            pass

    # -------- OPENCV CAPTURE --------
    def capture_with_opencv(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            self.capture_count += 1
            filename = f"s{self.capture_count}.png"
            save_path = os.path.join(self.vision_out_dir, filename)
            cv2.imwrite(save_path, frame)
            
            # Get all .png files in vision_out_dir
            import glob
            image_files = glob.glob(os.path.join(self.vision_out_dir, "*.png"))
            if image_files:
                # Encode all images
                import base64
                images_b64 = []
                for img_file in image_files:
                    with open(img_file, "rb") as f:
                        images_b64.append(base64.b64encode(f.read()).decode('utf-8'))
                
                # Call AI with user text and all images
                user_text = self.user_box.toPlainText().strip()
                response = ollama.chat(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": VISION_OUT_SYSTEM_PROMPT},
                        {"role": "user", "content": user_text, "images": images_b64}
                    ]
                )
                ai_reply = response["message"]["content"].strip()
                signals.reply.emit(ai_reply)
        cap.release()

    def capture_screenshot_and_send(self):
        # Hide the UI temporarily for clean screenshot
        self.hide()
        # Use QTimer to ensure UI is hidden before taking screenshot
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._take_screenshot_after_hide)

    def _take_screenshot_after_hide(self):
        try:
            screenshot = pyautogui.screenshot()
            self.capture_in_count += 1
            filename = f"in{self.capture_in_count}.png"
            save_path = os.path.join(self.vision_in_dir, filename)
            screenshot.save(save_path)
            
            # Get all .png files in vision_in_dir
            import glob
            image_files = glob.glob(os.path.join(self.vision_in_dir, "*.png"))
            if image_files:
                # Encode all images
                import base64
                images_b64 = []
                for img_file in image_files:
                    with open(img_file, "rb") as f:
                        images_b64.append(base64.b64encode(f.read()).decode('utf-8'))
                
                # Call AI with user text and all images
                user_text = self.user_box.toPlainText().strip()
                response = ollama.chat(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": VISION_IN_SYSTEM_PROMPT},
                        {"role": "user", "content": user_text, "images": images_b64}
                    ]
                )
                ai_reply = response["message"]["content"].strip()
                signals.reply.emit(ai_reply)
        finally:
            # Show the UI again
            self.show()

    def capture_transparent_area(self):
        save_dir = r"C:\Users\admin\OneDrive\Desktop\AI\SD"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "cap_img.png")
        screen = QApplication.primaryScreen()
        geo = self.frameGeometry()
        pixmap = screen.grabWindow(0, geo.x(), geo.y(), geo.width(), geo.height())
        pixmap.save(save_path)

    # -------- ENCRYPT FUNCTION --------
    def run_encrypt(self):
        import uuid
        import hashlib
        import base64
        import sqlite3
        import datetime
        import platform
        import subprocess
        from cryptography.fernet import Fernet

        def gds():
            try:
                output = subprocess.check_output("wmic diskdrive get serialnumber", shell=True)
                lines = output.decode().splitlines()
                serials = [line.strip() for line in lines if line.strip() and "SerialNumber" not in line]
                return serials[0] if serials else "unknown"
            except:
                return "unknown"

        def gdc():
            mac = str(uuid.getnode())
            node = platform.node()
            system = platform.system()
            release = platform.release()
            disk_serial = gds()
            raw = f"{mac}{node}{system}{release}{disk_serial}"
            return hashlib.sha256(raw.encode()).hexdigest(), raw

        def generate_key(password):
            key = hashlib.sha256(password.encode()).digest()
            return base64.urlsafe_b64encode(key[:32])

        def encrypt_file(file_path, password):
            if not os.path.exists(file_path):
                print("File does not exist.")
                return False

            filename = os.path.basename(file_path)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            key = generate_key(password)
            fernet = Fernet(key)
            device_code, raw_info = gdc()

            encrypt_dir = r"C:\Users\admin\OneDrive\Desktop\AI\Encrypt"
            os.makedirs(encrypt_dir, exist_ok=True)
            output_path = os.path.join(encrypt_dir, filename + ".secure")
            with open(file_path, 'rb') as f:
                data = f.read()
            encrypted = fernet.encrypt(data)

            with open(output_path, 'wb') as f:
                f.write(encrypted)

            conn = sqlite3.connect("secure_files.db")
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                password_hash TEXT,
                device_code TEXT,
                created_at TEXT
            )''')
            cur.execute("INSERT INTO logs (filename, password_hash, device_code, created_at) VALUES (?, ?, ?, ?)", (
                os.path.basename(output_path), password_hash, device_code,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            conn.close()
            print(f"✅ File encrypted: {output_path}")
            # Append to Decrypt_behave2.txt
            with open(r"C:\Users\admin\OneDrive\Desktop\AI\NFS-AI\Decrypt_behave2.txt", "a") as f:
                f.write(f"\n\nPath: {output_path}\nPassword: {password}\n\n")
            return True

        response5 = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content":behavior3
            },
            {"role": "user", "content": self.user_box.toPlainText().strip()}
            ]
        )
        r = response5["message"]["content"].strip()

        signals.clear_user.emit()

        print(f'endat: {self.user_box.toPlainText().strip()}')

        print(r)

        # Parse file_path and password from AI response
        import re
        path_match = re.search(r'<path>(.*?)<epath>', r)
        file_path = path_match.group(1) if path_match else ""
        pass_match = re.search(r'<passw>(.*?)<epassw>', r)
        password = pass_match.group(1) if pass_match else ""



        # Remove 'r' and quotes to get clean strings
        file_path2 = file_path[2:-1] if file_path.startswith('r"') and file_path.endswith('"') else file_path
        password2 = password[2:-1] if password.startswith('r"') and password.endswith('"') else password

        print(f"AI Path: {file_path2}")
        print(f"AI Password: {password2}")


        if file_path2 and password2:
            if encrypt_file(file_path2, password2):
                signals.reply.emit("Encrypted")
            else:
                signals.reply.emit("Encryption failed")
        else:
            print("Failed to parse file path and password from AI response.")
            signals.reply.emit("Encryption failed")

    def run_nfs_decrypt_flow(self):
        data_txt_path = r"C:\Users\admin\OneDrive\Desktop\AI\NFS-AI\Data.txt"
        data2_txt_path = r"C:\Users\admin\OneDrive\Desktop\AI\NFS-AI\Data2.txt"
        decrypt_dir = r"C:\Users\admin\OneDrive\Desktop\AI\Decrypt"
        cam_path = os.path.join(decrypt_dir, "CAM.png")
        owner_path = r"C:\Users\admin\OneDrive\Desktop\AI\Decrypt\Owner.png"

        try:
            # Webcam capture is intentionally skipped during decrypt flow.
            if os.path.exists(cam_path) and os.path.exists(owner_path):
                cam_b64 = encode_image(cam_path)
                owner_b64 = encode_image(owner_path)

                response = ollama.chat(
                    model=NFS_DECRYPT_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": behavior4},
                        {
                            "role": "user",
                            "content": "Analyze the captured image for decryption attempt.",
                            "images": [cam_b64, owner_b64],
                        },
                    ],
                )
                ai_response = response["message"]["content"].strip()
                print("AI Response:", ai_response)

                try:
                    ai_result = int(ai_response)
                except ValueError:
                    with open(data_txt_path, "w", encoding="utf-8") as f:
                        f.write("You are not allowed")
                    signals.reply.emit("Invalid owner-check response. Decryption blocked.")
                    return

                if ai_result == 0:
                    with open(data_txt_path, "w", encoding="utf-8") as f:
                        f.write("You are not allowed")
                    signals.reply.emit("You are not allowed")
                    return
                elif ai_result == 1:
                    with open(data_txt_path, "w", encoding="utf-8") as f:
                        f.write("allowed")
                else:
                    with open(data_txt_path, "w", encoding="utf-8") as f:
                        f.write("You are not allowed")
                    signals.reply.emit("Owner check failed. Decryption blocked.")
                    return
            else:
                with open(data_txt_path, "w", encoding="utf-8") as f:
                    f.write("allowed")

            with open(data2_txt_path, "r", encoding="utf-8") as f:
                user_input = f.read().strip()

            response2 = ollama.chat(
                model=NFS_DECRYPT_MODEL_NAME,
                messages=[
                    {"role": "system", "content": behavior6},
                    {"role": "user", "content": user_input},
                ],
            )
            ai_response2 = response2["message"]["content"].strip()
            print("Second AI Response:", ai_response2)

            import re

            path_match = re.search(r"<path>(.*?)<epath>", ai_response2)
            file_path = path_match.group(1) if path_match else ""
            pass_match = re.search(r"<passw>(.*?)<epassw>", ai_response2)
            password = pass_match.group(1) if pass_match else ""

            file_path2 = file_path[2:-1] if file_path.startswith('r"') and file_path.endswith('"') else file_path
            password2 = password[2:-1] if password.startswith('r"') and password.endswith('"') else password

            print(f"AI Path: {file_path2}")
            print(f"AI Password: {password2}")

            if file_path2 and password2:
                ok, msg = decrypt_file(file_path2, password2)
                signals.reply.emit(msg)
                if ok:
                    signals.clear_user.emit()
            else:
                signals.reply.emit("Failed to parse file path and password from AI response.")
        except Exception as e:
            signals.reply.emit(f"NFS decrypt flow failed: {e}")

    def start_realtime_mode(self):
        if self.realtime_mode_process is not None and self.realtime_mode_process.poll() is None:
            signals.reply.emit("Realtime mode is already running.")
            return

        if not os.path.exists(REALTIME_MODE_SCRIPT):
            signals.reply.emit(f"Realtime mode file not found: {REALTIME_MODE_SCRIPT}")
            return

        try:
            self.realtime_mode_process = subprocess.Popen([sys.executable, REALTIME_MODE_SCRIPT])
            signals.reply.emit("Realtime mode started.")
        except Exception as e:
            signals.reply.emit(f"Failed to start realtime mode: {e}")

    def stop_realtime_mode(self):
        if self.realtime_mode_process is None or self.realtime_mode_process.poll() is not None:
            self.realtime_mode_process = None
            signals.reply.emit("Realtime mode is not running.")
            return

        try:
            self.realtime_mode_process.terminate()
            self.realtime_mode_process.wait(timeout=5)
        except Exception:
            try:
                self.realtime_mode_process.kill()
            except Exception:
                pass
        finally:
            self.realtime_mode_process = None

        signals.reply.emit("Realtime mode stopped.")

    def start_microbot(self):
        if not os.path.exists(MICROBOT_SCRIPT):
            signals.reply.emit(f"Microbot file not found: {MICROBOT_SCRIPT}")
            return

        try:
            proc = subprocess.Popen([sys.executable, MICROBOT_SCRIPT])
            self.microbot_processes = [p for p in self.microbot_processes if p.poll() is None]
            self.microbot_processes.append(proc)
            signals.reply.emit(f"Microbot started. Running instances: {len(self.microbot_processes)}")
        except Exception as e:
            signals.reply.emit(f"Failed to start microbot: {e}")

    def stop_microbot(self):
        running_processes = [p for p in self.microbot_processes if p.poll() is None]

        if not running_processes:
            self.microbot_processes = []
            signals.reply.emit("Microbot is not running.")
            return

        stopped_count = 0
        for proc in running_processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                stopped_count += 1
            except Exception:
                try:
                    proc.kill()
                    stopped_count += 1
                except Exception:
                    pass

        self.microbot_processes = [p for p in self.microbot_processes if p.poll() is None]
        signals.reply.emit(f"Microbot stopped. Closed instances: {stopped_count}")

    def start_autobot(self):
        if self.autobot_process is not None and self.autobot_process.poll() is None:
            signals.reply.emit("Autobot is already running.")
            return

        if not os.path.exists(AUTOBOT_SCRIPT):
            signals.reply.emit(f"Autobot file not found: {AUTOBOT_SCRIPT}")
            return

        try:
            self.autobot_process = subprocess.Popen([sys.executable, AUTOBOT_SCRIPT])
            signals.reply.emit("Autobot started.")
        except Exception as e:
            signals.reply.emit(f"Failed to start autobot: {e}")

    def process_text(self):
        q = self.user_box.toPlainText().strip()
        if not q: return

        if q == '!realtimemode@#$':
            self.start_realtime_mode()
            self.user_box.clear()
            return

        if q == '*realtimemode@#$':
            self.stop_realtime_mode()
            self.user_box.clear()
            return

        if q == '!microbot@#$':
            self.start_microbot()
            self.user_box.clear()
            return

        if q == '!autobot@#$':
            self.start_autobot()
            self.user_box.clear()
            return

        if q == '*microbot@#$':
            self.stop_microbot()
            self.user_box.clear()
            return

        if q == '@out.':
            # Kill remote process if running
            if self.remote_process is not None and self.remote_process.poll() is None:
                self.remote_process.terminate()
                self.remote_process.wait()
                self.remote_process = None
            if self.vo_process is None or self.vo_process.poll() is not None:
                vo_script = r"C:\Users\admin\OneDrive\Desktop\Projects\VO-remote_execution.py"
                if os.path.exists(vo_script):
                    self.vo_process = subprocess.Popen([sys.executable, vo_script])
            self.user_box.clear()
            return
        threading.Thread(target=self.run_gwen, args=(q,), daemon=True).start()

    def run_gwen(self, q):
        response = ask_gwen(q)
        print(response)
        if "@#ettyiop" in response:
            parts = response.split("@#ettyiop", 1)
            signals.reply.emit(parts[0])
            # Execute the remote execution script only if not already running
            
            print("Executing remote script...")
            import subprocess
            if self.remote_process is None or self.remote_process.poll() is not None:
                remote_script = r"C:\Users\admin\OneDrive\Desktop\Projects\Remote-execution.py"
                if os.path.exists(remote_script):
                    self.remote_process = subprocess.Popen([sys.executable, remote_script])

        elif "@#ennyiop" in response:
            parts = response.split("@#ennyiop", 1)
            signals.reply.emit(parts[0])
            # Execute the encryption script inline
            print("Executing encryption script...")
            threading.Thread(target=self.run_encrypt, daemon=True).start()

        elif "@#eddyiop" in response:
            parts = response.split("@#eddyiop", 1)
            signals.reply.emit(parts[0])
            # Write user input to Data2.txt
            with open(r"C:\Users\admin\OneDrive\Desktop\AI\NFS-AI\Data2.txt", "w", encoding="utf-8") as f:
                f.write(self.user_box.toPlainText().strip())
            print("Executing NFS decrypt flow inline...")
            threading.Thread(target=self.run_nfs_decrypt_flow, daemon=True).start()




        elif "@#eooyiop" in response:
            parts = response.split("@#eooyiop", 1)
            signals.reply.emit(parts[0])
            # Kill the remote execution script if running
            print("Killing remote script...")
            if self.remote_process is not None and self.remote_process.poll() is None:
                self.remote_process.terminate()
                self.remote_process.wait()
                self.remote_process = None

        elif "@#ejjyiop" in response:
            print("Processing vision-based response...")
            parts = response.split("@#ejjyiop", 1)
            signals.reply.emit(parts[0])
            print("Processing vision-based_IN response...")
            self.capture_screenshot_and_send()

        elif "@#eggyiop" in response:
            print("Processing gmail response...")
            parts = response.split("@#eggyiop", 1)
            signals.reply.emit(parts[0])
            response_ai = ollama.chat(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": GMAIL_AGENT_PROMPT},
                    {"role": "user", "content": self.user_box.toPlainText().strip()}
                ]
            )
            ai_reply = response_ai["message"]["content"].strip()
            exec(ai_reply)
            signals.reply.emit('Processed sir')
            print("Processing gmail response...")

        elif "@#evvyiop" in response:
            print("Processing vision-based response...")
            parts = response.split("@#evvyiop", 1)
            signals.reply.emit(parts[0])
            print("Processing vision-based response...")
            import cv2
            import base64
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                self.capture_count += 1
                filename = f"vision_{self.capture_count}.png"
                save_path = os.path.join(self.vision_out_dir, filename)
                cv2.imwrite(save_path, frame)
                _, buffer = cv2.imencode('.png', frame)
                img_b64 = base64.b64encode(buffer).decode('utf-8')
                # Call AI (using Model 6, assuming same model for now)
                response_ai = ollama.chat(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": VISION_OUT_SYSTEM_PROMPT},
                        {"role": "user", "content": self.user_box.toPlainText().strip(), "images": [img_b64]}
                    ]
                )
                ai_reply = response_ai["message"]["content"].strip()
                signals.reply.emit(ai_reply)
            else:
                signals.reply.emit("Failed to capture webcam.")

        else:
            signals.reply.emit(response)
            print(response)

    # -------- VOICE --------
    def process_voice(self):
        threading.Thread(target=self.listen_voice, daemon=True).start()

    def listen_voice(self):
        r = sr.Recognizer()
        with sr.Microphone() as src:
            r.adjust_for_ambient_noise(src, 0.5)
            audio = r.listen(src)
        try:
            text = r.recognize_google(audio)
            signals.usertext.emit(text)
            self.run_gwen(text)
        except:
            pass

# ------------------ RUN ------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    ui.raise_()
    ui.activateWindow()
    sys.exit(app.exec())
