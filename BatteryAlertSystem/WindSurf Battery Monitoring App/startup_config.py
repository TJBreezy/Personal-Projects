import os
import sys
import winreg as reg

def add_to_startup():
    """Add the battery monitor to Windows startup"""
    batch_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "start_battery_monitor.bat"))
    vbs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "run_hidden.vbs"))
    
    # Create the key in Windows registry
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, "BatteryMonitor", 0, reg.REG_SZ, f'wscript.exe "{vbs_path}" "{batch_path}"')
        reg.CloseKey(key)
        return True
    except WindowsError:
        return False

def remove_from_startup():
    """Remove the battery monitor from Windows startup"""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
        reg.DeleteValue(key, "BatteryMonitor")
        reg.CloseKey(key)
        return True
    except WindowsError:
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--add":
            success = add_to_startup()
            print("Successfully added to startup" if success else "Failed to add to startup")
        elif sys.argv[1] == "--remove":
            success = remove_from_startup()
            print("Successfully removed from startup" if success else "Failed to remove from startup")
