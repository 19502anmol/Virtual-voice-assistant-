# Virtual-voice-assistant-
A Python-based Voice Assistant that recognizes speech, understands commands, and responds with voice. Features include web search, Wikipedia, music play, weather updates, app control, reminders, and more. Built using SpeechRecognition, pyttsx3, and NLP."
🎙 Voice Assistant (Python)

A simple yet powerful AI-based Voice Assistant built in Python.
It recognizes user commands (via speech or text), processes them, and responds with voice. The assistant can open websites, search Google/Wikipedia, tell time/date, check weather, manage notes, crack jokes, and more!

✨ Features

🎤 Voice + Text Input → Works with microphone (speech recognition) or typed commands.

🗣 Text-to-Speech → Human-like voice responses using pyttsx3.

🌐 Web Browsing → Open Google, YouTube, GitHub, LinkedIn, WhatsApp, Gmail, StackOverflow.

📖 Wikipedia → Fetch quick 2-line summaries.

☁ Weather Info → Get live weather using OpenWeather API.

🕒 Time & Date → Ask current time or today’s date.

📝 Notes → Save, read, and clear notes from notes.txt.

😂 Jokes → Light jokes for fun.

❓ Help Command → Lists available features.

🛠️ Tech Stack

Python 3.8+

Libraries:

pyttsx3 (Text-to-Speech)

speech_recognition (Voice Input)

wikipedia (Summaries)

requests (Weather API)

webbrowser, datetime, os, re, etc.

🚀 Setup & Installation

Clone the repository:

git clone https://github.com/your-username/voice-assistant.git
cd voice-assistant


Install dependencies:

pip install pyttsx3 SpeechRecognition wikipedia requests


(Optional) Set up OpenWeather API Key for weather:

export OPENWEATHER_API_KEY=your_api_key_here   # Linux/Mac
setx OPENWEATHER_API_KEY "your_api_key_here"   # Windows


Run the assistant:

python assistant.py

📌 Example Commands

time → tells current time

date → tells today’s date

open youtube → opens YouTube in browser

search for machine learning → Google search

wikipedia Python → 2-line Wikipedia summary

weather in Delhi → current weather

note Buy milk → saves a note

read notes → reads saved notes

clear notes → deletes notes

joke → random joke

help → show help text

exit → quit assistant

🧩 Future Improvements

Multi-language support (Hindi/English).

Integration with IoT/Smart Home devices.

Smarter NLP (intent detection with ML models).

GUI version for desktop/mobile.
