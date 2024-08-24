This educational script demonstrates a common cybersecurity threat: stealthy Wi-Fi password extraction from a Windows machine. Designed as part of a broader cybersecurity awareness course, this script showcases how attackers can move a script to the Startup folder, hide it from users, add it to the Windows Registry for persistence, and extract saved Wi-Fi passwords—all without user detection.

Features
Stealth Mode: The script hides itself by moving to the Windows Startup folder and applying hidden attributes, ensuring it runs silently on startup.
Registry Persistence: Automatically adds itself to the Windows Registry to guarantee it runs every time the system boots.
Wi-Fi Profile Extraction: Gathers all saved Wi-Fi profiles and retrieves their passwords using the netsh command.
Automated Emailing: Sends the extracted Wi-Fi credentials to a specified email address using a secure SMTP connection.
How It Works
Startup Persistence: The script checks if it’s already in the Startup folder. If not, it moves itself there, hides its presence, and relaunches from the new location.
Registry Injection: It then adds an entry to the Windows Registry to ensure it persists across reboots.
Network Check: The script waits for an active internet connection before proceeding.
Password Extraction: Using the netsh command, it retrieves all saved Wi-Fi passwords from the system.
Data Exfiltration: Finally, it sends the collected data via email, providing a real-world example of how attackers exfiltrate sensitive information.
Ethical Use
This script is provided strictly for educational purposes to raise awareness about potential security vulnerabilities in Wi-Fi network management on Windows machines. Users are advised to implement strong cybersecurity measures, such as regular auditing of Startup programs and registry entries, to prevent unauthorized access.

Disclaimer
Misuse of this script can lead to severe legal consequences. The author assumes no responsibility for any illegal use or damage caused by this script. Use responsibly and ethically.

