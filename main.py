import os
import speech_recognition as sr
import pyttsx3
import webbrowser
import urllib.parse
from typing import Optional
import music  # your music.py with links

# -------------------- VOICE SETUP --------------------
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text: str) -> None:
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()


# -------------------- AI PLACEHOLDER --------------------
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_AVAILABLE = bool(OPENAI_KEY)
client = None

if OPENAI_AVAILABLE:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
    except Exception:
        OPENAI_AVAILABLE = False

def ai_process(command: str) -> Optional[str]:
    """Process AI command if key exists"""
    if not OPENAI_AVAILABLE or not client:
        return "AI service not available."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": command}]
        )
        return response.choices[0].message.content
    except Exception:
        return "Error calling AI service."


# -------------------- COMMAND HANDLER --------------------
def process_command(command: str) -> None:
    cmd = command.lower().strip()

    if not cmd:
        speak("What should I do?")
        return

    # Google search fallback for questions
    if cmd.startswith(("who is ", "what is ", "who's ")):
        speak(f"Searching the web for {cmd}")
        url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(cmd)
        webbrowser.open(url)
        return

    # Predefined websites
    sites = {
        "open google": "https://www.google.com",
        "open youtube": "https://www.youtube.com",
        "open gmail": "https://www.gmail.com",
        "open facebook": "https://www.facebook.com",
        "open twitter": "https://www.twitter.com",
        "open instagram": "https://www.instagram.com"
    }

    if cmd in sites:
        speak(f"Opening {cmd.replace('open ', '')}")
        webbrowser.open(sites[cmd])
        return

    # Play music or YouTube search
    if cmd.startswith("play "):
        song = cmd[5:].strip()
        if song in music.music:
            speak(f"Playing {song}")
            webbrowser.open(music.music[song])
        else:
            speak(f"Searching YouTube for {song}")
            url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(song)
            webbrowser.open(url)
        return

    # News fallback
    if "news" in cmd:
        speak("Opening news")
        webbrowser.open("https://news.google.com")
        return

    # AI ask command
    if cmd.startswith(("ask ", "ai ")):
        question = cmd.split(" ", 1)[1].strip() if " " in cmd else ""
        if not question:
            speak("What would you like me to ask?")
            return
        reply = ai_process(question)
        speak(reply)
        return

    # Command not recognized
    speak("Command not recognized")


# -------------------- MAIN LOOP --------------------
if __name__ == "__main__":
    print("Jarvis is ready. How can I help you?")
    speak("Initializing Jarvis")

    try:
        while True:
            try:
                with sr.Microphone() as source:
                    print("Listening...")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)

                try:
                    command = recognizer.recognize_google(audio).lower().strip()
                    print(f"You said: {command}")
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    continue
                except sr.RequestError as e:
                    print("Recognition API error:", e)
                    continue

                # Wake word
                if command == "jarvis":
                    speak("Yes?")
                    continue
                if command.startswith("jarvis "):
                    process_command(command[7:])
                    continue

                # Stop command
                if any(x in command for x in ("exit", "stop")):
                    speak("Goodbye!")
                    print("Jarvis stopped.")
                    break

                # Process normal command
                process_command(command)

            except sr.WaitTimeoutError:
                print("Listening timed out, trying again...")
            except Exception as e:
                print("Error:", repr(e))

    except KeyboardInterrupt:
        print("Stopped by user")
