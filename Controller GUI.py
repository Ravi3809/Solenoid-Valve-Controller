import tkinter as tk
from tkinter import messagebox
import serial
import time
import sys

# ==========================================
# CONFIGURATION & SETTINGS
# ==========================================
SERIAL_PORT = "COM11" #Change this port number where your arduino is connected
BAUD_RATE = 9600
TIMEOUT = 1

# Color Palette (Dark Theme)
COLOR_BG = '#000000'        # Pure Black
COLOR_TEXT_WHITE = '#FFFFFF'
COLOR_TEXT_YELLOW = '#FFFF00'
COLOR_TEXT_CYAN = '#00FFFF'     # Used for Hardware Mode
COLOR_TEXT_ORANGE = '#FF9900'   # Used for Simulation Mode
COLOR_ACCENT_GREEN = '#00FF00'
COLOR_ACCENT_RED = '#FF0000'
COLOR_BTN_START = '#006600'
COLOR_BTN_STOP = '#660000'

class SolenoidController:
    def __init__(self, root):
        self.root = root
        self.root.title("Power Controller")
        self.root.geometry("500x600") # Increased height slightly
        self.root.configure(bg=COLOR_BG)

        # --- System State ---
        self.power_state = False
        self.arduino = None
        self.voltage_var = tk.StringVar(value="5.0") 
        self.is_simulation = False # Flag to track mode

        # --- Initialization ---
        self.connect_arduino()
        self.setup_ui()
        
        # Log the initial state
        if self.is_simulation:
            self.log_event("Started in SIMULATION MODE (No Hardware).")
        else:
            self.log_event("Started in HARDWARE MODE (Arduino Connected).")

    # ==========================================
    # HARDWARE COMMUNICATION
    # ==========================================
    def connect_arduino(self):
        """Attempts to establish serial connection with Arduino."""
        try:
            self.arduino = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=TIMEOUT)
            self.is_simulation = False
            print(f"Connected to {SERIAL_PORT}")
        except Exception as e:
            # If ANY error occurs (port not found, wrong library, etc.), switch to Sim mode
            self.is_simulation = True
            self.arduino = None
            print(f"Connection Failed: {e}")
            # We don't show a popup here anymore, the UI indicator will show it.

    def send_trigger(self, state):
        """Sends control signal to Arduino (1 for ON, 0 for OFF)."""
        if self.arduino and self.arduino.is_open:
            try:
                signal = b'1' if state else b'0'
                self.arduino.write(signal)
            except Exception as e:
                self.log_event(f"Comm Error: {e}")
        else:
            # Simulation behavior: Just print to console
            pass

    # ==========================================
    # CORE LOGIC
    # ==========================================
    def start_power(self):
        self.power_state = True
        self.send_trigger(True)
        self.update_display_state()
        self.log_event(f"START - Solenoid Valve OPEN")

    def stop_power(self):
        if messagebox.askyesno("Confirm Stop", "Stop power supply?"):
            self._force_stop("STOPPED - Normal Shutdown")

    def emergency_stop(self, event=None):
        self._force_stop("⚠️ EMERGENCY STOP TRIGGERED")

    def _force_stop(self, log_message):
        self.power_state = False
        self.send_trigger(False)
        self.update_display_state()
        self.log_event(log_message)

    # ==========================================
    # GUI SETUP
    # ==========================================
    def setup_ui(self):
        # --- 1. Header Title ---
        tk.Label(self.root, text="SOLENOID VALVE CONTROLLER ⚡",
                 font=("Arial", 16, "bold"),
                 bg=COLOR_BG, fg=COLOR_TEXT_YELLOW).pack(pady=(15, 5))

        # --- 2. MODE INDICATOR (NEW) ---
        mode_text = "MODE: HARDWARE CONTROL" if not self.is_simulation else "MODE: SIMULATION"
        mode_color = COLOR_TEXT_CYAN if not self.is_simulation else COLOR_TEXT_ORANGE
        
        self.lbl_mode = tk.Label(self.root, text=mode_text,
                                 font=("Courier", 10, "bold"),
                                 bg=COLOR_BG, fg=mode_color)
        self.lbl_mode.pack(pady=(0, 15))

        # --- 3. Status Indicator (LED & Text) ---
        status_frame = tk.Frame(self.root, bg=COLOR_BG)
        status_frame.pack(pady=10)

        self.led_canvas = tk.Canvas(status_frame, width=60, height=60,
                                    bg=COLOR_BG, highlightthickness=2, 
                                    highlightbackground=COLOR_TEXT_WHITE)
        self.led_canvas.pack(side=tk.LEFT, padx=(0, 15))
        self.led_indicator = self.led_canvas.create_oval(5, 5, 55, 55, 
                                                         fill=COLOR_ACCENT_RED, 
                                                         outline=COLOR_TEXT_WHITE, width=2)

        self.status_label = tk.Label(status_frame, text="VALVE: CLOSED",
                                     font=("Arial", 18, "bold"),
                                     bg=COLOR_BG, fg=COLOR_TEXT_WHITE)
        self.status_label.pack(side=tk.LEFT)

        # --- 4. Control Buttons ---
        btn_frame = tk.Frame(self.root, bg=COLOR_BG)
        btn_frame.pack(pady=20)

        self.btn_start = tk.Button(btn_frame, text="OPEN VALVE",
                                   bg=COLOR_BTN_START, fg=COLOR_TEXT_WHITE,
                                   font=("Arial", 11, "bold"), width=12,
                                   activebackground=COLOR_ACCENT_GREEN,
                                   command=self.start_power)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(btn_frame, text="CLOSE VALVE",
                                  bg=COLOR_BTN_STOP, fg=COLOR_TEXT_WHITE,
                                  font=("Arial", 11, "bold"), width=12,
                                  state=tk.DISABLED,
                                  activebackground=COLOR_ACCENT_RED,
                                  command=self.stop_power)
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        # --- 5. Emergency Stop ---
        tk.Button(self.root, text="E-STOP",
                  bg=COLOR_ACCENT_RED, fg="black",
                  font=("Arial", 11, "bold"), width=10, height=2,
                  activebackground="#990000",
                  command=self.emergency_stop).pack(pady=10)

        # --- 6. Event Log ---
        tk.Label(self.root, text="SYSTEM EVENT LOG:",
                 bg=COLOR_BG, fg=COLOR_TEXT_YELLOW,
                 font=("Arial", 10, "bold")).pack(pady=(10, 0))

        log_frame = tk.Frame(self.root, bg="white")
        log_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(log_frame, bg="#CCCCCC")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_list = tk.Listbox(log_frame,
                                   bg='black', fg=COLOR_TEXT_CYAN,
                                   font=("Courier", 9, "bold"),
                                   height=8,
                                   yscrollcommand=scrollbar.set)
        self.log_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_list.yview)

        # --- 7. Keyboard Bindings ---
        self.root.bind('<Control-s>', lambda e: self.start_power())
        self.root.bind('<Control-q>', lambda e: self.stop_power())
        self.root.bind('<Escape>', lambda e: self.emergency_stop())

    # ==========================================
    # HELPER METHODS
    # ==========================================
    def update_display_state(self):
        if self.power_state:
            # ON State
            self.status_label.config(text="VALVE: OPEN", fg=COLOR_ACCENT_GREEN)
            self.led_canvas.itemconfig(self.led_indicator, fill=COLOR_ACCENT_GREEN)
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            # OFF State
            self.status_label.config(text="VALVE: CLOSED", fg=COLOR_TEXT_WHITE)
            self.led_canvas.itemconfig(self.led_indicator, fill=COLOR_ACCENT_RED)
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)

    def log_event(self, message):
        timestamp = time.strftime('%H:%M:%S')
        entry = f"[{timestamp}] {message}"
        self.log_list.insert(tk.END, entry)
        self.log_list.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SolenoidController(root)
    root.mainloop()
