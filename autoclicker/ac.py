import tkinter as tk
import time
import threading
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, Key, KeyCode

# Global variables to control the autoclicker
clicking = False
mouse = Controller()
enabled = True

# Define the key combination to toggle the autoclicker
toggle_key = {Key.shift, Key.ctrl, KeyCode(char="Q")}
pressed_keys = set()

# Emergency stop key
stop_key = Key.esc

# Flag to track emergency stops
emergency_stopped = False

def clicker():
    while True:
        if clicking and enabled:
            mouse.click(Button.left, 1)
        time.sleep(0.001)  # Adjust this for click speed

def on_key_press(key):
    global clicking
    global enabled
    global emergency_stopped  # Allow updating from within the function

    if key == stop_key:
        # Emergency stop
        clicking = False
        enabled = False
        emergency_stopped = True
        status_var.set("Autoclicker Disabled (Emergency)")
        return
    
    if enabled and not emergency_stopped:
        pressed_keys.add(key)
        if toggle_key.issubset(pressed_keys):
            clicking = not clicking
            status_var.set("Clicking" if clicking else "Stopped")

def on_key_release(key):
    pressed_keys.discard(key)

# Function to reset the autoclicker after an emergency stop
def reset_autoclicker():
    global clicking
    global enabled
    global emergency_stopped
    clicking = False
    enabled = True
    emergency_stopped = False
    status_var.set("Ready To Use")

# Thread to run the autoclicker in the background
clicker_thread = threading.Thread(target=clicker, daemon=True)
clicker_thread.start()

# Create the GUI
root = tk.Tk()
root.title("Autoclicker GUI")

# Label to indicate the current status
status_var = tk.StringVar(value="Ready To Use")
status_label = tk.Label(root, textvariable=status_var)
status_label.pack(pady=10)

# Function to enable or disable the autoclicker feature
def toggle_autoclicker():
    global clicking
    global enabled
    enabled = not enabled
    if not enabled:
        clicking = False
        status_var.set("Autoclicker Disabled")
    else:
        status_var.set("Ready To Use")
        pressed_keys.clear()  # Clear pressed keys to avoid unintended toggles
    
    update_button_text()  # Update the button text based on the current state

# Button to reset the autoclicker after an emergency stop
reset_button = tk.Button(root, text="Reset Autoclicker", command=reset_autoclicker)
reset_button.pack(pady=10)

# Button to enable or disable the autoclicker
toggle_button = tk.Button(root, text="Disable Autoclicker", command=toggle_autoclicker)
toggle_button.pack(pady=10)

# Function to update the toggle button text based on the enabled state
def update_button_text():
    toggle_button.config(text="Disable Autoclicker" if enabled else "Enable Autoclicker")

# Start the key listener in a separate thread
listener_thread = threading.Thread(
    target=lambda: Listener(on_press=on_key_press, on_key_release=on_key_release).run(), daemon=True)
listener_thread.start()

# Run the GUI event loop
root.mainloop()
