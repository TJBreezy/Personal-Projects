import psutil
import time
import tkinter as tk
from tkinter import messagebox
import os
import sys

def radical_popup(title, msg):
    root = tk.Tk()
    root.withdraw()  # Hide main window
    root.attributes("-topmost", True)  # Always on top
    messagebox.showwarning(title, msg)
    root.destroy()

def setup_autostart():
    startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    bat_path = os.path.join(startup_path, "BatteryBro.bat")
    
    if not os.path.exists(bat_path):
        with open(bat_path, "w") as f:
            f.write(f'start "" "{sys.executable.replace("python.exe", "pythonw.exe")}" "{os.path.abspath(__file__)}"')

def battery_check():
    while True:
        battery = psutil.sensors_battery()
        if not battery:
            # Exit silently if no battery is detected
            sys.exit(0)
            
        percent = battery.percent
        plugged = battery.power_plugged

        if percent <= 20 and not plugged:
            radical_popup("Low Battery Alert 🚨", 
                        f"Hey bro! 🔋 Your juice is at {percent}%!\n"
                        "Time to plug in before we go dark! 🔌😎")
                        
        elif percent >= 85 and plugged:
            radical_popup("Chill on Charging ⚡", 
                        f"Yo! Battery's {percent}% full!\n"
                        "Unplug that cord and let's stay fresh! 🆒🔋")
                        
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    setup_autostart()
    battery_check()