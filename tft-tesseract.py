import cv2
import pytesseract
import pyautogui
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk, Toplevel
from PIL import Image, ImageTk
import time
import threading
import keyboard
import ctypes
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont

pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0

pytesseract.pytesseract.tesseract_cmd = 'tesseract'

champions_by_cost = {
    "1-cost": ["Ashe", "Blitzcrank", "Elise", "Lillia", "Jax", "Jayce", "Poppy", "Nomsy", "Seraphine", "Soraka", "Twitch", "Warwick", "Ziggs", "Zoe"],
    "2-cost": ["Ahri", "Akali", "Cassiopeia", "Galio", "Kassadin", "Kog'Maw", "Nilah", "Nunu", "Rumble", "Shyvana", "Syndra", "Tristana", "Zilean"],
    "3-cost": ["Bard", "Ezreal", "Hecarim", "Hwei", "Jinx", "Katarina", "Mordekaiser", "Neeko", "Shen", "Swain", "Veigar", "Vex", "Wukong"],
    "4-cost": ["Fiora", "Gwen", "Kalista", "Karma", "Nami", "Nasus", "Olaf", "Rakan", "Ryze", "Tahm Kench", "Taric", "Varus"],
    "5-cost": ["Briar", "Camille", "Diana", "Milio", "Morgana", "Norra & Yuumi", "Smolder", "Xerath"]
}

champion_pools = {
    "1-cost": {champ: 30 for champ in champions_by_cost["1-cost"]},
    "2-cost": {champ: 25 for champ in champions_by_cost["2-cost"]},
    "3-cost": {champ: 18 for champ in champions_by_cost["3-cost"]},
    "4-cost": {champ: 10 for champ in champions_by_cost["4-cost"]},
    "5-cost": {champ: 9 for champ in champions_by_cost["5-cost"]}
}

strong_charms = ["Gear Swap", "Crystal Ball", "Minor Wish", "Zoomify", "Pyromania", "Hugify", "Shivinate", "Die Roll", "Dress Down" , "Conjure Anvil", "Minor Mimicry" , "Golden Dummy", "Truce", "Discount","Yordle Spirit", "Earthquake", "Conjure Spatula", "Tinker", "All Fives", "Major Mimicry", "Summon Dragon", "Conjure Artifact", "Magnum Opus"]

selected_champions = []

root = tk.Tk()
root.title("Champion Selection")
root.attributes("-topmost", True)

show_screenshot = tk.BooleanVar()

def open_pool_tracker():
    tracker_window = Toplevel(root)
    tracker_window.title("Pool Tracker")
    tracker_window.attributes("-topmost", True)

    def update_label(champ_label, cost_tier, champ_name):
        champ_label.config(text=str(champion_pools[cost_tier][champ_name]))

    def decrease_count(cost_tier, champ_name, champ_label):
        if champion_pools[cost_tier][champ_name] > 0:
            champion_pools[cost_tier][champ_name] -= 1
            update_label(champ_label, cost_tier, champ_name)

    def increase_count(cost_tier, champ_name, champ_label):
        champion_pools[cost_tier][champ_name] += 1
        update_label(champ_label, cost_tier, champ_name)

    frames = {}
    for cost_tier, champions in champion_pools.items():
        toggle_button = ttk.Button(tracker_window, text=cost_tier, command=lambda f=cost_tier: toggle_frame(frames[f]))
        toggle_button.pack(fill="x", expand=True, padx=5, pady=5)

        frame = tk.Frame(tracker_window)
        frame.pack(fill="x", expand=True, padx=5, pady=5)
        frame.pack_forget()
        frames[cost_tier] = frame

        for champ_name, pool_size in champions.items():
            row_frame = tk.Frame(frame)
            row_frame.pack(fill="x", expand=True, padx=5, pady=2)

            champ_label = tk.Label(row_frame, text=champ_name, width=20, anchor="w")
            champ_label.pack(side="left")

            count_label = tk.Label(row_frame, text=str(pool_size), width=5)
            count_label.pack(side="left")

            minus_button = tk.Button(row_frame, text="-", command=lambda ct=cost_tier, cn=champ_name, cl=count_label: decrease_count(ct, cn, cl))
            minus_button.pack(side="left")

            plus_button = tk.Button(row_frame, text="+", command=lambda ct=cost_tier, cn=champ_name, cl=count_label: increase_count(ct, cn, cl))
            plus_button.pack(side="left")

def toggle_frame(frame):
    if frame.winfo_viewable():
        frame.pack_forget()
    else:
        frame.pack(fill="x", expand=True)

def capture_screen():
    screenshot = pyautogui.screenshot(region=(0, 900, 1920, 180))
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def recognize_characters(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)
    d = pytesseract.image_to_data(binary_image, config="--psm 6", output_type=pytesseract.Output.DICT)

    print("OCR results:")
    for i in range(len(d['text'])):
        print(f"Text: {d['text'][i]}, Coordinates: ({d['left'][i]}, {d['top'][i]}) Width: {d['width'][i]} Height: {d['height'][i]})")

    return d

def fast_click(x, y):
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)

def purchase_character(character_name, ocr_data):
    found = False
    for i, text in enumerate(ocr_data['text']):
        if character_name.lower() in text.lower():
            found = True
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            w = ocr_data['width'][i]
            h = ocr_data['height'][i]
            x_center = x + w // 2
            y_center = y + h // 2 + 900

            fast_click(x_center, y_center)

            status_label.config(text=f"{character_name} found and clicked!")
            return True
    if not found:
        status_label.config(text=f"{character_name} not found.")
    return False

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.charm_coordinates = []
        self.running = True
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, 1920, 1080)
        self.show()

    def paintEvent(self, event):
        if not self.running:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(255, 0, 0))

        for coord in self.charm_coordinates:
            x, y, w, h = coord
            painter.drawRect(x, y, w, h)
            painter.setFont(QFont('Arial', 16))
            painter.drawText(x, y - 10, "Strong Charm")

    def update_overlay(self, ocr_data):
        if not self.running:
            return
        self.charm_coordinates.clear()
        for i, text in enumerate(ocr_data['text']):
            if text.strip():  # Boş metinleri filtrelemek için
                for charm in strong_charms:
                    if charm.lower() in text.lower():
                        x = ocr_data['left'][i]
                        y = ocr_data['top'][i] + 900
                        w = ocr_data['width'][i]
                        h = ocr_data['height'][i]
                        self.charm_coordinates.append((x, y, w, h))
        self.update()


    def stop(self):
        self.running = False
        self.charm_coordinates.clear()
        self.update()

def start_detection(overlay):
    global is_running
    is_running = True
    overlay.running = True
    while is_running:
        screen_region = capture_screen()
        ocr_data = recognize_characters(screen_region)
        for character in selected_champions:
            purchase_character(character, ocr_data)
        overlay.update_overlay(ocr_data)
        if show_screenshot.get():
            show_screenshot_in_ui(screen_region)
        time.sleep(0.1)

def stop_detection():
    global is_running
    is_running = False
    overlay.stop()
    status_label.config(text="Scanning stopped.")
    print("Scanning stopped.")

def on_checkbox_click():
    global selected_champions
    selected_champions = [champion for champion, var in checkboxes.items() if var.get()]
    print(f"Selected champions: {selected_champions}")

def on_start_button_click(overlay):
    if selected_champions:
        detection_thread = threading.Thread(target=start_detection, args=(overlay,))
        detection_thread.start()
    else:
        messagebox.showwarning("Warning", "Please select at least one champion.")

def show_screenshot_in_ui(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(image)
    imgtk = ImageTk.PhotoImage(image=img)
    screenshot_label.config(image=imgtk)
    screenshot_label.image = imgtk

frames = {}
checkboxes = {}
def toggle_frame(frame):
    if frame.winfo_viewable():
        frame.pack_forget()
    else:
        frame.pack(fill="x", expand=True)

for cost, champions in champions_by_cost.items():
    toggle_button = ttk.Button(root, text=cost, command=lambda f=cost: toggle_frame(frames[f]))
    toggle_button.pack(fill="x", expand=True)

    frame = tk.Frame(root)
    frame.pack(fill="x", expand=True)
    frame.pack_forget()
    frames[cost] = frame

    for champion in champions:
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(frame, text=champion, variable=var, command=on_checkbox_click)
        checkbox.pack(anchor='w')
        checkboxes[champion] = var

pool_tracker_button = tk.Button(root, text="Pool Tracker", command=open_pool_tracker)
pool_tracker_button.pack()

show_checkbox = tk.Checkbutton(root, text="Show Screenshot", variable=show_screenshot)
show_checkbox.pack()

start_button = tk.Button(root, text="Start", command=lambda: on_start_button_click(overlay))
start_button.pack()

stop_button = tk.Button(root, text="Stop", command=stop_detection)
stop_button.pack()

status_label = tk.Label(root, text="Program ready.", fg="blue")
status_label.pack()

screenshot_label = tk.Label(root)
screenshot_label.pack()

def keyboard_listener():
    while True:
        if keyboard.is_pressed("F1"):
            stop_detection()
        elif keyboard.is_pressed("F2"):
            on_start_button_click(overlay)
        time.sleep(0.1)

keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
keyboard_thread.start()

app = QApplication(sys.argv)
overlay = Overlay()

root.mainloop()

sys.exit(app.exec_())