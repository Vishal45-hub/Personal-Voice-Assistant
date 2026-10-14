import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import webbrowser
from datetime import datetime
import wikipedia
import requests
import os
from dotenv import load_dotenv
load_dotenv()
import random

# Initialize recognizer
recognizer = sr.Recognizer()

# Mic animation frames
mic_frames = ["🎤", "🎙", "🎧", "🔊", "🎚"]
current_frame = 0
mic_animating = False

# Typing animation frames
typing_frames = ["Assistant: Typing.", "Assistant: Typing..", "Assistant: Typing..."]
typing_index = 0
typing_animating = False

# Speak using gTTS
def speak(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        filename = f"voice{random.randint(1,100000)}.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"Error in speaking: {e}")

# Exit function
def exit_fullscreen(event=None):
    speak("Exiting.")
    window.destroy()

# Log chat in chat box
def log_chat(who, text):
    chat_box.configure(state='normal')
    chat_box.insert(tk.END, f"{who}: {text}\n")
    chat_box.configure(state='disabled')
    chat_box.see(tk.END)

# Navigate using Google Maps
def navigate_to_location(location):
    url = f"https://www.google.com/maps/search/{location.replace(' ', '+')}"
    speak(f"Navigating to {location}")
    log_chat("Assistant", f"Opening Google Maps for {location}")
    webbrowser.open(url)

# Resume listening after button press
def resume_listening():
    talk_button.pack_forget()
    window.after(100, listen_and_respond)

# Function to fetch a joke from JokeAPI
def fetch_joke():
    try:
        url = "https://v2.jokeapi.dev/joke/Any?type=single"
        response = requests.get(url)
        data = response.json()

        if 'joke' in data:
            joke = data['joke']
        else:
            joke = f"{data['setup']} - {data['delivery']}"

        speak(joke)
        log_chat("Assistant", joke)
        assistant_response_var.set(f"Assistant: {joke}")

        window.after(1000, listen_and_respond)

    except Exception as e:
        speak("Sorry, I couldn't fetch a joke at the moment.")
        log_chat("Assistant", "Error fetching joke.")
        window.after(1000, listen_and_respond)

# Play song on YouTube
def play_song_on_youtube(song_name):
    url = f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}"
    speak(f"Playing {song_name} on YouTube")
    log_chat("Assistant", f"Playing {song_name} on YouTube")
    webbrowser.open(url)

def get_current_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

# Function to get the current date
def get_current_date():
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y")

# Search Google
def search_google(query):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    speak(f"Searching Google for {query}")
    log_chat("Assistant", f"Searching Google for {query}")
    webbrowser.open(url)

def get_latest_news():
    try:
        # Your NewsAPI key
        API_KEY = os.getenv("NEWS_API_KEY", "")

        # API URL for NewsAPI
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"

        # Send a request to the NewsAPI
        response = requests.get(url)
        news_data = response.json()

        if news_data["status"] == "ok" and "articles" in news_data:
            articles = news_data["articles"]
            news_headlines = [article["title"] for article in articles[:5]]  # Get top 5 headlines

            # Format news response
            news_response = "Here are the latest news headlines: "
            for idx, headline in enumerate(news_headlines, 1):
                news_response += f"\n{idx}. {headline}"

            return news_response
        else:
            return "Sorry, I couldn't fetch the news at the moment."

    except Exception as e:
        return f"An error occurred while fetching the news: {e}"


# Typing animation function
def start_typing_animation():
    global typing_animating
    typing_animating = True
    animate_typing()

def stop_typing_animation():
    global typing_animating
    typing_animating = False

def animate_typing():
    global typing_index
    if typing_animating:
        assistant_response_var.set(typing_frames[typing_index])
        typing_index = (typing_index + 1) % len(typing_frames)
        window.after(400, animate_typing)

# Search Wikipedia
def search_wikipedia(query):
    speak(f"Searching Wikipedia for {query}")
    log_chat("Assistant", f"Searching Wikipedia for {query}")
    try:
        start_typing_animation()
        window.update()
        summary = wikipedia.summary(query, sentences=2)
        stop_typing_animation()
        assistant_response_var.set("Assistant: Answer shown in chat box.")
        log_chat("Assistant", summary)
        speak(summary)
    except wikipedia.exceptions.DisambiguationError:
        stop_typing_animation()
        assistant_response_var.set("Assistant: Multiple results, please be more specific.")
        log_chat("Assistant", "Multiple results found.")
        speak("There are multiple results. Please be more specific.")
    except wikipedia.exceptions.PageError:
        stop_typing_animation()
        assistant_response_var.set("Assistant: No Wikipedia page found.")
        log_chat("Assistant", "No Wikipedia page found.")
        speak("Sorry, no page found for that query.")

# Animate mic while listening
def animate_mic():
    global current_frame
    if mic_animating:
        status_var.set(mic_frames[current_frame] + " Listening...")
        current_frame = (current_frame + 1) % len(mic_frames)
        window.after(400, animate_mic)

# Voice command processing
def listen_and_respond():
    global mic_animating
    try:
        with sr.Microphone() as source:
            mic_animating = True
            animate_mic()
            window.update()
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        mic_animating = False
        status_var.set("⚡ Processing...")

        command = recognizer.recognize_google(audio).lower()
        user_input_var.set("You said: " + command)
        log_chat("User", command)

        if "exit" in command or "quit" in command:
            response = "Goodbye! Have a nice day"
            log_chat("Assistant", response)
            assistant_response_var.set("Assistant: " + response)
            speak(response)
            window.destroy()
            return



        elif "what is your name" in command:
            response = "My name is Python Assistant."

        elif "how are you" in command or "how r u" in command:
            response = "I'm just a bunch of code, but I'm doing great!"

        elif "thank you" in command or "thanks" in command:
            response = "You're very welcome! I'm always here to help."

        # Other cases for time, date, weather, etc.

        else:
            response = "Sorry, I didn't understand that."

        assistant_response_var.set("Assistant: " + response)
        log_chat("Assistant", response)
        speak(response)

    except sr.UnknownValueError:
        mic_animating = False
        error_msg = "Sorry, I couldn't understand. Please try again."
        assistant_response_var.set("Assistant: " + error_msg)
        log_chat("Assistant", error_msg)
        speak(error_msg)

    except sr.RequestError:
        mic_animating = False
        error_msg = "Could not connect to the speech service."
        assistant_response_var.set("Assistant: " + error_msg)
        log_chat("Assistant", error_msg)
        speak(error_msg)
        return

    window.after(1000, listen_and_respond)


# Greet user on startup
def greet_user():
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning!"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"

    greeting_message = f"{greeting} How can I assist you today?"
    log_chat("Assistant", greeting_message)
    assistant_response_var.set("Assistant: " + greeting_message)
    speak(greeting_message)

API_KEY_weather = os.getenv("OPENWEATHER_API_KEY", "")

# Function to get weather data for a city
def get_weather(city):
    try:
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}q={city}&appid={API_KEY_weather}&units=metric"
        response = requests.get(complete_url)
        data = response.json()

        if data["cod"] == 200:
            main = data["main"]
            weather_desc = data["weather"][0]["description"]
            temperature = main["temp"]
            humidity = main["humidity"]
            pressure = main["pressure"]
            city_name = data["name"]

            weather_report = f"The current weather in {city_name} is {weather_desc}. The temperature is {temperature}°C with a humidity of {humidity}% and pressure of {pressure} hPa."
            return weather_report
        else:
            return "Sorry, I couldn't find the weather for that city."

    except Exception as e:
        return f"An error occurred while fetching weather data: {e}"

# -------------------- GUI -------------------- #
window = tk.Tk()
window.title("Voice Assistant")

window.geometry("1200x700")
window.configure(bg="black")
window.grid_rowconfigure(0, minsize=20)

status_var = tk.StringVar()
status_label = tk.Label(window, textvariable=status_var, font=("Helvetica", 16), fg="yellow", bg="black")
status_label.pack(pady=10)
status_var.set("Initializing...")

exit_label = tk.Label(window, text="Press ESC to exit", font=("Helvetica", 16), fg="white", bg="black")
exit_label.pack(pady=5)

user_input_var = tk.StringVar()
user_input_label = tk.Label(window, textvariable=user_input_var, font=("Helvetica", 18), fg="lightgreen", bg="black")
user_input_label.pack()

assistant_response_var = tk.StringVar()
assistant_response_label = tk.Label(window, textvariable=assistant_response_var, font=("Helvetica", 18), fg="cyan", bg="black")
assistant_response_label.pack(pady=5)

chat_box = scrolledtext.ScrolledText(window, width=100, height=20, font=("Consolas", 14), bg="black", fg="white", wrap=tk.WORD)
chat_box.pack(pady=10)
chat_box.configure(state='disabled')

talk_button = tk.Button(window, text="Talk Again", font=("Helvetica", 16), command=resume_listening, bg="green", fg="white")

window.bind("<Escape>", exit_fullscreen)

greet_user()
window.after(1000, listen_and_respond)
window.mainloop()