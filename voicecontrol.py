import speech_recognition as sr
import pyautogui
import pyperclip
import time
import os

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for commands...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
        except sr.WaitTimeoutError:
            print("Listening timed out.")
        return None

def execute_command(command):
    if "copy" in command:  # Pronunciation: "KAH-pee"
        pyautogui.hotkey('ctrl', 'c')
        print("Copied to clipboard.")

    elif "write" in command:  
        pyautogui.hotkey('ctrl', 'v')
        print("Pasted from clipboard at the current cursor position.")

    elif "delete" in command:  # Pronunciation: "duh-LEET"
        pyautogui.press('delete')
        print("Deleted selected item.")

    elif "select all" in command:  # Pronunciation: "suh-LEKT awl"
        pyautogui.hotkey('ctrl', 'a')
        print("Selected all text.")

    elif "move up" in command:  # Pronunciation: "moov UP"
        pyautogui.move(0, -50)
        print("Moved up.")

    elif "move down" in command:  # Pronunciation: "moov DOWN"
        pyautogui.move(0, 50)
        print("Moved down.")

    elif "move left" in command:  # Pronunciation: "moov LEFT"
        pyautogui.move(-50, 0)
        print("Moved left.")

    elif "move right" in command:  # Pronunciation: "moov RITE"
        pyautogui.move(50, 0)
        print("Moved right.")

    elif "left click" in command:  # Pronunciation: "LEFT klik"
        pyautogui.click()
        print("Left clicked.")

    elif "right click" in command:  # Pronunciation: "RITE klik"
        pyautogui.click(button='right')
        print("Right clicked.")

    elif "double click" in command:  # Pronunciation: "DUH-buhl klik"
        pyautogui.doubleClick()
        print("Double clicked.")

    elif "scroll up" in command:  # Pronunciation: "SKROHL UP"
        pyautogui.scroll(10)
        print("Scrolled up.")

    elif "scroll down" in command:  # Pronunciation: "SKROHL DOWN"
        pyautogui.scroll(-10)
        print("Scrolled down.")

    elif "zoom in" in command:  # Pronunciation: "ZOOM in"
        pyautogui.hotkey('ctrl', '+')
        print("Zoomed in.")

    elif "zoom out" in command:  # Pronunciation: "ZOOM out"
        pyautogui.hotkey('ctrl', '-')
        print("Zoomed out.")

    elif "capitalize" in command:  # Pronunciation: "KAP-ih-tuh-lyze"
        pyautogui.keyDown('shift')
        time.sleep(0.2)
        pyautogui.keyUp('shift')
        print("Shift activated for capitalization.")

    elif "lowercase" in command:  # Pronunciation: "LOH-er-case"
        print("Typing in lowercase by default.")

    elif "type" in command:  # Pronunciation: "TIPE"
        words = command.replace("type", "").strip()
        pyautogui.write(words)
        print(f"Typed: {words}")

    elif "open notepad" in command:  # Pronunciation: "OH-puhn NOTE-pad"
        os.system("notepad.exe")
        print("Opened Notepad.")

    elif "close notepad" in command:  # Pronunciation: "KLOHZ NOTE-pad"
        os.system("taskkill /f /im notepad.exe")
        print("Closed Notepad.")

    elif "open new folder" in command:  # Pronunciation: "OH-puhn NEW FOHL-der"
        pyautogui.hotkey('ctrl', 'shift', 'n')
        print("Opened a new folder.")

    else:
        print("Command not recognized.")

if __name__ == "__main__":
    print("Voice-controlled mouse and keyboard script running...")
    while True:
        command = listen_for_command()
        if command:
            if "exit" in command or "quit" in command:  # Pronunciation: "EK-sit" or "KWIT"
                print("Exiting program.")
                break
            execute_command(command)
