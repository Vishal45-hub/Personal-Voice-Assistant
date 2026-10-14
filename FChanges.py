import tkinter as tk
from tkinter import messagebox
import datetime
import speech_recognition as sr
import webbrowser
import os
from dotenv import load_dotenv
load_dotenv()
import random
import requests
import win32com.client
import threading

# Initialize voice engine
speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Voice = speaker.GetVoices().Item(0)  # 0 for male, 1 for female

def speak(text):
    speaker.Speak(text)

# Functions for assistant
def wish():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning! I am Coco.")
    elif 12 <= hour < 18:
        speak("Good Afternoon! I am Coco.")
    else:
        speak("Good Evening! I am Coco.")
    speak("How can I help you?")

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
    except Exception as e:
        print("Say that again please...")
        return "None"
    return query.lower()

def tell_news():
    api_key = os.getenv("NEWS_API_KEY", "")
    news_url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"

    try:
        news = requests.get(news_url).json()
        articles = news["articles"]
        speak("Here are the top news headlines.")
        for i, article in enumerate(articles[:5], 1):
            speak(f"News {i}: {article['title']}")
    except:
        speak("Sorry, I am unable to fetch the news right now.")

def answer_general_knowledge(question):
    try:
        url = f"https://api.duckduckgo.com/?q={question}&format=json"
        res = requests.get(url)
        data = res.json()
        answer = data.get('AbstractText', "I don't know the answer to that.")
        speak(answer)
    except:
        speak("Sorry, I couldn't fetch the answer.")

def run_coco():
    wish()
    while True:
        query = take_command()

        if "stop" in query or "bye" in query:
            speak("Goodbye!")
            break

        if "open youtube" in query:
            webbrowser.open("https://www.youtube.com")
            speak("Opening YouTube.")

        elif "open google" in query:
            webbrowser.open("https://www.google.com")
            speak("Opening Google.")

        elif "play music" in query:
            music_dir = 'C:\\Music'  # Change this path to your music folder
            songs = os.listdir(music_dir)
            os.startfile(os.path.join(music_dir, random.choice(songs)))
            speak("Playing music.")

        elif "time" in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")

        elif "news" in query:
            tell_news()

        else:
            # Attempt to answer general knowledge
            speak("Let me find that out.")
            answer_general_knowledge(query)

# GUI Part
class CocoApp:
    def __init__(self, master):
        self.master = master
        master.title("Coco - Desktop Assistant")

        master.configure(bg="white")

        self.label = tk.Label(master, text="Welcome! Click the button and say 'Hey Coco' to start.",
                              font=("Helvetica", 14), bg="white")
        self.label.pack(pady=20)

        self.start_button = tk.Button(master, text="Start Coco", command=self.start_listening,
                                      font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
        self.start_button.pack(pady=20)

        self.quit_button = tk.Button(master, text="Exit", command=master.quit,
                                     font=("Helvetica", 12), bg="red", fg="white", padx=10, pady=5)
        self.quit_button.pack(pady=10)

    def start_listening(self):
        threading.Thread(target=self.listen_for_wakeword).start()

    def listen_for_wakeword(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            speak("Listening for Hey Coco...")
            while True:
                audio = recognizer.listen(source)
                try:
                    query = recognizer.recognize_google(audio, language='en-in').lower()
                    if "hey coco" in query:
                        speak("Yes Sir, I am listening.")
                        run_coco()
                        break
                except:
                    continue

if __name__ == "__main__":
    root = tk.Tk()
    app = CocoApp(root)
    root.mainloop()