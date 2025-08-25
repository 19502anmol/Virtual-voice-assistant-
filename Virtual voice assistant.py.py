import os
import re
import sys
import time
import json
import queue
import random
import webbrowser
import datetime as dt
from typing import Optional

# --- Optional imports guarded for graceful fallback ---
try:
    import pyttsx3
except Exception:  # pragma: no cover
    pyttsx3 = None

try:
    import speech_recognition as sr
except Exception:  # pragma: no cover
    sr = None

try:
    import wikipedia
    wikipedia.set_lang("en")
except Exception:  # pragma: no cover
    wikipedia = None

import requests


# ---------------- Utilities ---------------- #
DEF_NOTES_FILE = "notes.txt"
WAKE_WORDS = {"jarvis", "assistant", "anmol", "hey", "hello"}
BROWSER_SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "linkedin": "https://www.linkedin.com",
    "stackoverflow": "https://stackoverflow.com",
    "whatsapp": "https://web.whatsapp.com",
    "gmail": "https://mail.google.com",
}


def now_time_str() -> str:
    # Local system time (India users will get IST if OS is set to IST)
    return dt.datetime.now().strftime("%I:%M %p")


def today_date_str() -> str:
    return dt.datetime.now().strftime("%A, %d %B %Y")


# ---------------- Speech Engine ---------------- #
class Speaker:
    def __init__(self):
        self.engine = None
        if pyttsx3:
            try:
                self.engine = pyttsx3.init()
                # Slightly slow for clarity
                rate = self.engine.getProperty('rate')
                self.engine.setProperty('rate', max(140, rate - 30))
            except Exception:
                self.engine = None

    def say(self, text: str):
        print(f"Assistant: {text}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass


# ---------------- Listener (Voice/Text) ---------------- #
class Listener:
    def __init__(self, speaker: Speaker):
        self.speaker = speaker
        self.voice_ok = False
        self.recognizer = None
        self.mic = None
        if sr:
            try:
                self.recognizer = sr.Recognizer()
                self.mic = sr.Microphone()
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                self.voice_ok = True
            except Exception:
                self.voice_ok = False

    def listen(self, prompt: Optional[str] = None) -> str:
        if prompt:
            self.speaker.say(prompt)
        if self.voice_ok:
            try:
                with self.mic as source:
                    print("Listening...")
                    audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=8)
                text = self.recognizer.recognize_google(audio, language='en-IN')
                print(f"You (voice): {text}")
                return text.lower().strip()
            except Exception as e:
                print(f"[Voice error -> Switching to text mode] {e}")
                self.voice_ok = False
        # Text input fallback
        return input("You (type): ").lower().strip()


# ---------------- Intent Parsing ---------------- #
HELP_TEXT = (
    "Main aapki madad kar sakta hoon. Try these:\n"
    "• time / date\n"
    "• open <site> (youtube, google, github, linkedin, stackoverflow, whatsapp, gmail)\n"
    "• search for <query>\n"
    "• wikipedia <topic>\n"
    "• weather in <city>\n"
    "• note <text> | read notes | clear notes\n"
    "• joke\n"
    "• stop/exit/quit\n"
)

JOKES = [
    "Programmer ka favourite place? Foo-Bar!",
    "Python dev: 'Indentation is my cardio.'",
    "Network admin ka password kya hota hai? 'password'... (just kidding, kabhi mat use karna!)",
    "AI bola: Main galti kabhi nahi karta... bas unpredictable hoon!",
]


def has_wake_word(text: str) -> bool:
    toks = set(re.split(r"\W+", text.lower()))
    return bool(WAKE_WORDS & toks)


# ---------------- Actions ---------------- #
class Actions:
    def __init__(self, speaker: Speaker):
        self.speaker = speaker

    def act_time(self):
        self.speaker.say(f"Abhi {now_time_str()} baj rahe hain.")

    def act_date(self):
        self.speaker.say(f"Aaj {today_date_str()} hai.")

    def act_open(self, site: str):
        url = BROWSER_SITES.get(site)
        if not url:
            # try as raw url if looks like domain
            if re.match(r"^[\w-]+(\.[\w-]+)+$", site):
                url = f"https://{site}"
        if url:
            webbrowser.open(url)
            self.speaker.say(f"Opening {site} in your browser.")
        else:
            self.speaker.say("Kaunsa site kholna hai? e.g., 'open youtube'.")

    def act_search(self, query: str):
        q = query.strip().replace(' ', '+')
        webbrowser.open(f"https://www.google.com/search?q={q}")
        self.speaker.say(f"Searching Google for {query}.")

    def act_wikipedia(self, topic: str):
        if not wikipedia:
            self.speaker.say("Wikipedia library missing. 'pip install wikipedia' karke dobara try karein.")
            return
        try:
            summary = wikipedia.summary(topic, sentences=2)
            self.speaker.say(summary)
        except Exception:
            self.speaker.say("Maaf kijiye, Wikipedia se info nahi mil payi.")

    def act_weather(self, city: str):
        key = os.getenv("OPENWEATHER_API_KEY")
        if not key:
            self.speaker.say("Weather ke liye OPENWEATHER_API_KEY set karein, tab main bataunga.")
            return
        try:
            url = (
                "https://api.openweathermap.org/data/2.5/weather?q="
                f"{city}&appid={key}&units=metric"
            )
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if data.get("cod") != 200:
                self.speaker.say("City nahi mili. Sahi naam bolein.")
                return
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            self.speaker.say(f"{city.title()} ka temp {temp}°C hai, {desc}.")
        except Exception:
            self.speaker.say("Weather laate waqt error aaya.")

    def act_note(self, text: str):
        with open(DEF_NOTES_FILE, 'a', encoding='utf-8') as f:
            f.write(text.strip() + "\n")
        self.speaker.say("Note save ho gaya.")

    def act_read_notes(self):
        if not os.path.exists(DEF_NOTES_FILE):
            self.speaker.say("Abhi koi notes nahi hain.")
            return
        with open(DEF_NOTES_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if not content:
            self.speaker.say("Notes file khaali hai.")
        else:
            self.speaker.say("Aapke notes:")
            for line in content.splitlines():
                self.speaker.say(line)

    def act_clear_notes(self):
        try:
            if os.path.exists(DEF_NOTES_FILE):
                os.remove(DEF_NOTES_FILE)
            self.speaker.say("Notes delete kar diye gaye hain.")
        except Exception:
            self.speaker.say("Notes delete nahi ho paaye.")

    def act_joke(self):
        self.speaker.say(random.choice(JOKES))


# ---------------- Parser ---------------- #
COMMAND_PATTERNS = [
    (re.compile(r"\btime\b|\bsamay\b"), lambda a, m: a.act_time()),
    (re.compile(r"\bdate\b|\btaareekh\b"), lambda a, m: a.act_date()),
    (re.compile(r"^open\s+([\w.-]+)"), lambda a, m: a.act_open(m.group(1)) ),
    (re.compile(r"^search\s+for\s+(.+)"), lambda a, m: a.act_search(m.group(1)) ),
    (re.compile(r"^wikipedia\s+(.+)"), lambda a, m: a.act_wikipedia(m.group(1)) ),
    (re.compile(r"^weather\s+in\s+(.+)"), lambda a, m: a.act_weather(m.group(1)) ),
    (re.compile(r"^note\s+(.+)"), lambda a, m: a.act_note(m.group(1)) ),
    (re.compile(r"^read\s+notes?$"), lambda a, m: a.act_read_notes() ),
    (re.compile(r"^clear\s+notes?$"), lambda a, m: a.act_clear_notes() ),
    (re.compile(r"\bjoke\b"), lambda a, m: a.act_joke() ),
    (re.compile(r"\bhelp\b"), lambda a, m: a.speaker.say(HELP_TEXT) ),
]


# ---------------- Main Loop ---------------- #
class Assistant:
    def __init__(self):
        self.speaker = Speaker()
        self.listener = Listener(self.speaker)
        self.actions = Actions(self.speaker)
        self.speaker.say("Namaste! Main aapka voice assistant hoon. 'help' bolo ya poochho.")

    def handle_text(self, text: str) -> bool:
        if not text:
            return True
        # global exits
        if any(kw in text for kw in ["exit", "quit", "stop", "goodbye"]):
            self.speaker.say("Thik hai, milte hain phir. Bye!")
            return False
        # ignore wake word if present
        t = text
        if has_wake_word(text):
            t = re.sub(r"^(hey|hello|jarvis|assistant|anmol)\s*", "", text).strip()
        # match commands
        for pattern, action in COMMAND_PATTERNS:
            m = pattern.search(t)
            if m:
                action(self.actions, m)
                return True
        # default fallback
        self.speaker.say("Maaf kijiye, mujhe samajh nahi aaya. 'help' bolo commands dekhne ke liye.")
        return True

    def run(self):
        while True:
            try:
                text = self.listener.listen()
                if not self.handle_text(text):
                    break
            except KeyboardInterrupt:
                self.speaker.say("Interrupted. Bye!")
                break
            except Exception as e:
                print(f"[Error] {e}")
                time.sleep(0.5)


if __name__ == "__main__":
    Assistant().run()
