import win32com.client  # For text-to-speech
import speech_recognition as sr
from datetime import datetime
import wikipedia
import webbrowser as wb
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import threading
import smtplib
import psutil
import time
import pywhatkit as kit
import pyjokes
import re
import tkinter as tk
from tkinter import messagebox

# ================== Your Original Functions ===================

def play_song(song_name):
    try:
        kit.playonyt(song_name)
        speak(f"Playing {song_name} on YouTube.")
        print(f"Playing {song_name} on YouTube.")
    except Exception as e:
        speak("Sorry, I couldn't play the song.")
        print(f"Error: {e}")

speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(audio):
    speaker.Speak(audio)

def monitor_battery():
    while True:
        battery = psutil.sensors_battery()
        percent = battery.percent
        plug_status = battery.power_plugged

        if percent <= 20 and not plug_status:
            speak(f"Warning! Battery is at {percent}%. Please plug in your charger.")
            print(f"Warning! Battery is at {percent}%. Please plug in your charger.")

        if plug_status:
            print(f"Charging... Battery is at {percent}%")

        time.sleep(60)

def wishMe():
    battery_thread = threading.Thread(target=monitor_battery)
    battery_thread.daemon = True
    battery_thread.start()

    hour = int(datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")

    speak("I am your assistant. Please tell me how may I help you")

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("Adjusting for ambient noise. Please wait...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("Listening...")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            return query.lower()

        except sr.WaitTimeoutError:
            speak("Sorry, I didn't hear anything. Please try again.")
            return None
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand what you said.")
            return None
        except sr.RequestError:
            speak("Sorry, I'm having trouble connecting to the service.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            speak("An unexpected error occurred.")
            return None

def sendEmail(to, content):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login('youremail@gmail.com', 'your-password')
        server.sendmail('youremail@gmail.com', to, content)
        server.close()
        speak("Email has been sent!")
    except Exception as e:
        print(e)
        speak("Sorry, I couldn't send the email.")

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

def get_weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        weather = {
            "City": data["name"],
            "Temperature": data["main"]["temp"],
            "Description": data["weather"][0]["description"],
            "Humidity": data["main"]["humidity"],
            "Wind Speed": data["wind"]["speed"]
        }
        weather_report = (
            f"The weather in {weather['City']} is {weather['Description']}. "
            f"The temperature is {weather['Temperature']} degrees Celsius. "
            f"The humidity is {weather['Humidity']}%, and the wind speed is {weather['Wind Speed']} meters per second."
        )
        return weather_report
    else:
        return f"Error: {response.status_code}, {response.json()}"

def weather():
    speak("Please tell me the city name for the weather forecast.")
    print("Please tell me the city name.")
    city = takeCommand()
    if city:
        weather_report = get_weather(city)
        speak(weather_report)
        print(weather_report)
    else:
        speak("I couldn't hear the city name. Please try again.")
        print("No city was provided.")

def get_word_info_free(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'title' not in data:
            word_info = data[0]
            word_type = word_info['meanings'][0]['partOfSpeech']
            definition = word_info['meanings'][0]['definitions'][0]['definition']
            speak(f"Here is the definition of {word}: {definition}")
            print(f"Word: {word}")
            print(f"Part of Speech: {word_type}")
            print(f"Definition: {definition}")

            synonyms = word_info['meanings'][0].get('synonyms', [])
            if synonyms:
                speak(f"Synonyms: {', '.join(synonyms)}")
                print(f"Synonyms: {', '.join(synonyms)}")

            antonyms = word_info['meanings'][0].get('antonyms', [])
            if antonyms:
                speak(f"Antonyms: {', '.join(antonyms)}")
                print(f"Antonyms: {', '.join(antonyms)}")
        else:
            speak(f"Sorry, I couldn't find information for {word}.")
            print(f"Sorry, I couldn't find information for {word}.")
    except requests.exceptions.RequestException as e:
        speak(f"Sorry, I couldn't fetch the word information. {str(e)}")
        print(f"Error: {str(e)}")

def define_word(query):
    words = query.split("define")
    if len(words) > 1:
        word = words[1].strip()
        if word:
            get_word_info_free(word)
        else:
            speak("Please provide a word to define.")
            print("Please provide a word to define.")
    else:
        speak("I couldn't understand the word. Please say 'define' followed by a word.")
        print("I couldn't understand the word. Please say 'define' followed by a word.")

def battery_status():
    battery = psutil.sensors_battery()
    percent = battery.percent
    speak(f"Your current battery percentage is {percent}%.")
    print(f"Battery percentage: {percent}%")

def note_down():
    speak("What would you like to note down?")
    print("Please tell me what you want to note down:")
    note_content = takeCommand()
    if note_content:
        home_dir = os.path.expanduser("~")
        file_path = os.path.join(home_dir, "Documents", "notes.txt")
        try:
            documents_folder = os.path.join(home_dir, "Documents")
            if not os.path.exists(documents_folder):
                os.makedirs(documents_folder)
            with open(file_path, "a") as file:
                file.write(note_content + "\n")
            speak(f"Your note has been saved at {file_path}")
            print(f"Note saved at: {file_path}")
        except Exception as e:
            speak("Sorry, there was an error saving your note.")
            print(f"Error: {e}")
    else:
        speak("You didn't provide any note.")
        print("No note was provided.")

def navigate_to_location(location):
    wb.open(f"https://www.google.com/maps?q={location}")
    speak(f"Opening Google Maps for {location}.")

def perform_calculation(query):
    try:
        expression = re.findall(r'(\d+\.?\d*)\s*([+\-/xX])\s(\d+\.?\d*)', query)
        if expression:
            num1, operator, num2 = expression[0]
            num1, num2 = float(num1), float(num2)
            if operator in ['+', 'add']:
                result = num1 + num2
            elif operator in ['-', 'subtract']:
                result = num1 - num2
            elif operator in ['*', 'x', 'times', 'multiplied by']:
                result = num1 * num2
            elif operator in ['/', 'divide', 'divided by']:
                result = num1 / num2
            else:
                speak("Sorry, I couldn't perform the calculation.")
                return
            speak(f"The result is {result}")
            print(f"Result: {result}")
        else:
            speak("Sorry, I couldn't understand the calculation.")
    except Exception as e:
        speak("An error occurred while performing the calculation.")
        print(f"Calculation Error: {e}")

def set_alarm():
    speak("At what time should I set the alarm? Please say the time in HH:MM format.")
    alarm_time = takeCommand()
    while True:
        current_time = time.strftime("%H:%M")
        if current_time == alarm_time:
            speak("It's time to wake up!")
            break
        time.sleep(60)

def set_timer():
    speak("For how many minutes would you like to set the timer?")
    minutes_input = takeCommand()
    try:
        minutes_input = minutes_input.lower().replace("minute", "").replace("minutes", "").strip()
        minutes = int(minutes_input)
        speak(f"Timer set for {minutes} minutes.")
        time.sleep(minutes * 60)
        speak("Time's up! Times up! Times Up!")
        print(f"Timer for {minutes} minutes is up!")
    except ValueError:
        speak("Sorry, I didn't understand that. Please specify the time in minutes.")
        print("Invalid input.")

def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)

def times():
    current_time = datetime.now().strftime("%I:%M:%S %p")
    speak("The current time is")
    speak(current_time)
    print("The current time is", current_time)

def date():
    now = datetime.now()
    speak("The current date is")
    speak(f"{now.day} {now.strftime('%B')} {now.year}")
    print(f"The current date is {now.day}/{now.month}/{now.year}")

def google_search(query):
    query = query.replace("search", "").strip()
    search_query = '+'.join(query.split())
    url = f"https://www.google.com/search?q={search_query}"
    wb.open(url)
    speak(f"Here are the search results for {query}")

# ===================== GUI Part =======================

# def start_assistant():
#     wishMe()
#     while True:
#         query = takeCommand()
#         if query is None:
#             continue

#         if 'thanks' in query or 'thank you' in query:
#             speak("Anytime! I'm happy to assist.")
#             continue
#         if 'exit' in query or 'stop' in query:
#             speak("Goodbye! Have a nice day!")
#             break
#         if "time" in query:
#             times()
#         elif "date" in query:
#             date()
#         elif any(op in query for op in ['add', 'subtract', 'multiply', 'divide', 'x', '*', '+', '-', '/', 'calculate']):
#             perform_calculation(query)
#         elif 'define' in query:
#             define_word(query)
#         elif 'wikipedia' in query:
#             speak('Searching Wikipedia...')
#             query = query.replace("wikipedia", "")
#             results = wikipedia.summary(query, sentences=2)
#             speak("According to Wikipedia")
#             print(results)
#             speak(results)
#         elif "note down" in query:
#             note_down()
#         elif 'open youtube' in query:
#             wb.open("https://youtube.com")
#             break
#         elif 'open google' in query:
#             wb.open("https://google.com")
#             break
#         elif 'email to me' in query:
#             try:
#                 speak("What should I say?")
#                 content = takeCommand()
#                 to = "Xyz@gmail.com"
#                 sendEmail(to, content)
#             except Exception as e:
#                 print(e)
#                 speak("Sorry, I couldn't send the email.")
#         elif 'weather' in query:
#             weather()
#         elif 'play' in query and 'song' in query:
#             song_name = query.replace('play', '').replace('song', '').strip()
#             if song_name:
#                 play_song(song_name)
#                 break
#             else:
#                 speak("Sorry, I didn't catch the song name.")
#         elif 'search' in query:
#             google_search(query)
#             break
#         elif 'navigate to' in query or 'open google maps for' in query:
#             location = query.replace("navigate to", "").replace("open google maps for", "").strip()
#             if location:
#                 navigate_to_location(location)
#                 break
#         elif 'joke' in query:
#             tell_joke()
#         elif "shutdown" in query:
#             speak("Shutting down the system, goodbye!")
#             os.system("shutdown /s /f /t 1")
#             break
#         elif "restart" in query:
#             speak("Restarting the system, please wait!")
#             os.system("shutdown /r /f /t 1")
#             break
#         elif "set timer" in query:
#             set_timer()
#         elif "battery" in query or "percentage" in query:
#             battery_status()
#         elif 'news' in query:
# Legacy hardcoded API key assignment removed.
#             url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
#             response = requests.get(url).json()
#             if response["status"] == "ok":
#                 articles = response["articles"]
#                 speak("Here are the top headlines:")
#                 for article in articles[:5]:
#                     headline = article["title"]
#                     speak(headline)
#                     print(headline)
#             else:
#                 speak("Sorry, I couldn't fetch the news.")

# def exit_program():
#     if messagebox.askokcancel("Exit", "Do you really want to exit?"):
#         root.destroy()

# root = tk.Tk()
# root.title("Voice Assistant")
# root.geometry("400x300")
# root.configure(bg="#f0f0f0")

# title_label = tk.Label(root, text="Voice Assistant", font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#333")
# title_label.pack(pady=20)

# start_button = tk.Button(root, text="Start Assistant", command=start_assistant, font=("Arial", 14), bg="#4CAF50", fg="white", padx=20, pady=10)
# start_button.pack(pady=10)

# exit_button = tk.Button(root, text="Exit", command=exit_program, font=("Arial", 14), bg="#f44336", fg="white", padx=20, pady=10)
# exit_button.pack(pady=10)

# root.protocol("WM_DELETE_WINDOW", exit_program)
# root.mainloop()
