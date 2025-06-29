import psutil
import time
import threading
from plyer import notification
import pystray
from PIL import Image, ImageDraw
import os
import sys

class BatteryMonitor:
    def __init__(self):
        self.running = True
        self.monitoring = True
        self.icon = None
        self.last_notification_state = None  # Track last notification state
        self.create_icon()

    def create_icon(self):
        # Create a simple icon (a colored circle)
        image = Image.new('RGB', (64, 64), color='white')
        dc = ImageDraw.Draw(image)
        dc.ellipse([0, 0, 64, 64], fill='green')

        menu = (
            pystray.MenuItem('Toggle Monitoring', self.toggle_monitoring),
            pystray.MenuItem('Exit', self.stop_monitoring)
        )
        self.icon = pystray.Icon("battery_monitor", image, "Battery Monitor", menu)

    def toggle_monitoring(self, icon, item):
        self.monitoring = not self.monitoring
        status = "enabled" if self.monitoring else "disabled"
        notification.notify(
            title="Battery Monitor 🔋",
            message=f"Monitoring {status}",
            app_icon=None,
            timeout=3,
        )
        self.last_notification_state = None  # Reset notification state when toggling

    def stop_monitoring(self, icon, item):
        self.running = False
        self.icon.stop()

    def get_battery_info(self):
        battery = psutil.sensors_battery()
        if battery:
            return battery.percent, battery.power_plugged
        return None, None

    def check_battery(self):
        fun_messages_low = [
            "Yo, bro! Your battery's running on empty! Plug me in! 🔌",
            "Battery's getting hangry! Feed me some electrons! ⚡",
            "SOS! Battery's down bad! Need juice ASAP! 🆘",
            "Bruh, don't let me die like this! Charge me! 🙏",
        ]
        
        fun_messages_high = [
            "Sheesh! I'm fully loaded bro! Unplug me! 🔋",
            "Battery's too thicc with charge! Disconnect! 💪",
            "I'm charged AF! Time to go wireless! 🚀",
            "Battery's living its best life! Time to unplug! ✨",
        ]

        while self.running:
            if self.monitoring:
                percent, plugged = self.get_battery_info()
                
                if percent is not None:
                    current_state = None
                    
                    if percent <= 20 and not plugged:
                        current_state = "low_unplugged"
                    elif percent >= 85 and plugged:
                        current_state = "high_plugged"
                    
                    # Only notify if state has changed or if we're in a warning state that hasn't been addressed
                    if current_state != self.last_notification_state:
                        if current_state == "low_unplugged":
                            notification.notify(
                                title="Low Battery! 🔋",
                                message=fun_messages_low[int(time.time()) % len(fun_messages_low)],
                                app_icon=None,
                                timeout=5,
                            )
                        elif current_state == "high_plugged":
                            notification.notify(
                                title="High Battery! ⚡",
                                message=fun_messages_high[int(time.time()) % len(fun_messages_high)],
                                app_icon=None,
                                timeout=5,
                            )
                        
                        self.last_notification_state = current_state
                    
                    # Clear notification state if conditions are good
                    if (percent > 20 or plugged) and (percent < 85 or not plugged):
                        if self.last_notification_state is not None:
                            notification.notify(
                                title="Battery's Good! 😎",
                                message="Thanks bro! Battery's in the sweet spot now!",
                                app_icon=None,
                                timeout=5,
                            )
                            self.last_notification_state = None
            
            time.sleep(30)  # Check every 30 seconds

    def run(self):
        # Start the battery monitoring in a separate thread
        monitor_thread = threading.Thread(target=self.check_battery)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Run the system tray icon
        self.icon.run()

if __name__ == "__main__":
    monitor = BatteryMonitor()
    monitor.run()
