import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import win32com.client
import speech_recognition as sr
from datetime import datetime
import wikipedia
import webbrowser as wb
import os
import requests
import threading
import psutil
import time
import pywhatkit as kit
import pyjokes
import re
from dotenv import load_dotenv
import sv_ttk
import math
import winsound
import sys

# Load environment variables
load_dotenv()

class VoiceAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("DEEPAK AI Assistant")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        # Initialize speech engine
        try:
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize speech engine: {e}")
            sys.exit(1)

        # Contacts dictionary
        self.contacts = {
            "vishal": os.getenv("VISHAL_CONTACT", ""),
            "amar": os.getenv("AMAR_CONTACT", ""),
            "akshat": os.getenv("AKSHAT_CONTACT", ""),
            "google": os.getenv("GOOGLE_CONTACT", ""),
            "ritika": os.getenv("RITIKA_CONTACT", "")
        }

        # Weather API Key
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY", "")

        # Setup UI
        self.setup_ui()

        # Start battery monitoring
        self.start_battery_monitor()

        # Greet user
        self.wish_me()

    def setup_ui(self):
        """Set up the user interface"""
        sv_ttk.set_theme("dark")

        # Custom fonts
        self.title_font = ("Segoe UI", 18, "bold")
        self.subtitle_font = ("Segoe UI", 12)
        self.button_font = ("Segoe UI", 10, "bold")

        # Main frame
        self.main_frame = tk.Frame(self.root, bg='#121212')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create UI sections
        self.create_header()
        self.create_content_area()
        self.create_controls()
        self.create_status_bar()

        # Animation variables
        self.is_listening = False
        self.animation_thread = None

    def create_header(self):
        """Create the header section"""
        header_frame = tk.Frame(self.main_frame, bg='#1F1B24')
        header_frame.pack(fill=tk.X, pady=(0, 10), padx=10)

        # Logo and title
        logo_frame = tk.Frame(header_frame, bg='#1F1B24')
        logo_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.logo_label = tk.Label(logo_frame, text="🤖", font=("Arial", 28), bg='#1F1B24', fg='#BB86FC')
        self.logo_label.pack(side=tk.LEFT)

        title_frame = tk.Frame(header_frame, bg='#1F1B24')
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(title_frame, text="DEEPAK AI", font=self.title_font, bg='#1F1B24', fg='white').pack(side=tk.TOP, anchor='w')
        tk.Label(title_frame, text="Your Personal Voice Assistant", font=self.subtitle_font, bg='#1F1B24', fg='#BB86FC').pack(side=tk.TOP, anchor='w')

        # Voice visualization
        viz_frame = tk.Frame(header_frame, bg='#1F1B24')
        viz_frame.pack(side=tk.RIGHT, padx=20)

        self.visualization_canvas = tk.Canvas(viz_frame, width=200, height=60, bg='#1F1B24', highlightthickness=0)
        self.visualization_canvas.pack()

    def create_content_area(self):
        """Create the conversation area"""
        content_frame = tk.Frame(self.main_frame, bg='#121212')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Conversation history
        conv_frame = tk.Frame(content_frame, bg='#1E1E1E', bd=0, highlightthickness=0)
        conv_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(conv_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.conversation_text = tk.Text(
            conv_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 11),
            bg='#1E1E1E',
            fg='white',
            padx=15,
            pady=15,
            yscrollcommand=scrollbar.set,
            borderwidth=0,
            highlightthickness=0
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        self.conversation_text.config(state=tk.DISABLED)

        scrollbar.config(command=self.conversation_text.yview)

        # Configure tags for different speakers
        self.conversation_text.tag_config("assistant", foreground="#03DAC6")
        self.conversation_text.tag_config("user", foreground="#BB86FC")
        self.conversation_text.tag_config("system", foreground="#CF6679")

    def create_controls(self):
        """Create control buttons"""
        controls_frame = tk.Frame(self.main_frame, bg='#121212')
        controls_frame.pack(fill=tk.X, pady=(0, 10), padx=10)

        # Start button
        self.start_button = tk.Button(
            controls_frame,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            bg='#6200EE',
            fg='white',
            activebackground='#3700B3',
            activeforeground='white',
            borderwidth=0,
            font=self.button_font,
            padx=20,
            pady=10
        )
        self.start_button.pack(side=tk.LEFT, padx=5, ipadx=20)

        # Clear button
        tk.Button(
            controls_frame,
            text="🗑 Clear",
            command=self.clear_conversation,
            bg='#1E1E1E',
            fg='white',
            activebackground='#2D2D2D',
            borderwidth=0,
            font=self.button_font,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        # Spacer
        tk.Frame(controls_frame, bg='#121212', width=20).pack(side=tk.LEFT, expand=True)

        # Settings button
        tk.Button(
            controls_frame,
            text="⚙ Settings",
            command=self.show_settings,
            bg='#1E1E1E',
            fg='white',
            activebackground='#2D2D2D',
            borderwidth=0,
            font=self.button_font,
            padx=20,
            pady=10
        ).pack(side=tk.RIGHT, padx=5)

        # Help button
        tk.Button(
            controls_frame,
            text="❓ Help",
            command=self.show_help,
            bg='#1E1E1E',
            fg='white',
            activebackground='#2D2D2D',
            borderwidth=0,
            font=self.button_font,
            padx=20,
            pady=10
        ).pack(side=tk.RIGHT, padx=5)

    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.main_frame, bg='#1F1B24')
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.status_label = tk.Label(
            status_frame,
            text="🟢 Ready",
            font=self.subtitle_font,
            bg='#1F1B24',
            fg='white',
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)

        # Battery indicator
        self.battery_label = tk.Label(
            status_frame,
            text="🔋 100%",
            font=self.subtitle_font,
            bg='#1F1B24',
            fg='white',
            anchor=tk.E
        )
        self.battery_label.pack(side=tk.RIGHT, padx=10, pady=5)

    def add_to_conversation(self, speaker, message):
        """Add message to conversation history"""
        self.conversation_text.config(state=tk.NORMAL)

        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        self.conversation_text.insert(tk.END, f"[{timestamp}] ", "system")

        # Add speaker and message
        self.conversation_text.insert(tk.END, f"{speaker}: ", speaker.lower())
        self.conversation_text.insert(tk.END, f"{message}\n\n")

        self.conversation_text.config(state=tk.DISABLED)
        self.conversation_text.see(tk.END)

    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_text.config(state=tk.NORMAL)
        self.conversation_text.delete(1.0, tk.END)
        self.conversation_text.config(state=tk.DISABLED)
        self.add_to_conversation("System", "Conversation cleared")

    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)

    def speak(self, audio):
        """Speak the given text"""
        self.add_to_conversation("Assistant", audio)
        try:
            self.speaker.Speak(audio)
        except Exception as e:
            self.add_to_conversation("System", f"Speech error: {e}")

    def wish_me(self):
        """Greet the user based on time"""
        hour = datetime.now().hour
        if 0 <= hour < 12:
            greeting = "Good Morning!"
        elif 12 <= hour < 18:
            greeting = "Good Afternoon!"
        else:
            greeting = "Good Evening!"

        self.speak(f"{greeting} I am your assistant. Please tell me how may I help you")

    def start_battery_monitor(self):
        """Start battery monitoring thread"""
        def monitor():
            while True:
                try:
                    battery = psutil.sensors_battery()
                    if battery:
                        percent = battery.percent
                        self.battery_label.config(text=f"🔋 {percent}%")

                        if percent <= 20 and not battery.power_plugged:
                            self.speak(f"Warning! Battery is at {percent}%. Please plug in your charger.")
                except:
                    pass
                time.sleep(60)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def toggle_listening(self):
        """Toggle listening state"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        """Start listening for commands"""
        self.is_listening = True
        self.start_button.config(text="🔴 Stop Listening", bg='#CF6679', activebackground='#B00020')
        self.update_status("🔴 Listening...")
        self.add_to_conversation("System", "Assistant is now listening...")

        # Start voice wave animation
        self.animate_voice_wave()

        # Start listening in a separate thread
        threading.Thread(target=self.take_command, daemon=True).start()

    def stop_listening(self):
        """Stop listening for commands"""
        self.is_listening = False
        self.start_button.config(text="🎤 Start Listening", bg='#6200EE', activebackground='#3700B3')
        self.update_status("🟢 Ready")
        self.add_to_conversation("System", "Assistant stopped listening.")

        # Stop voice wave animation
        self.visualization_canvas.delete("wave")

    def animate_voice_wave(self):
        """Animate voice wave visualization"""
        if not self.is_listening:
            return

        self.visualization_canvas.delete("wave")

        width = 200
        height = 60
        center_y = height // 2

        # Generate wave points
        time_val = time.time() * 3
        points = []
        for x in range(0, width + 1, 5):
            y = center_y + math.sin(time_val + x * 0.1) * 15 * (1 if self.is_listening else 0.2)
            points.extend([x, y])

        # Draw the wave
        self.visualization_canvas.create_line(
            points,
            fill="#03DAC6",
            width=2,
            smooth=True,
            tags="wave"
        )

        # Schedule next animation frame
        if self.is_listening:
            self.visualization_canvas.after(50, self.animate_voice_wave)

    def take_command(self):
        """Take voice command from user"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                r.adjust_for_ambient_noise(source, duration=1)
                self.speak("I'm listening...")
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                query = r.recognize_google(audio, language='en-in').lower()

                self.add_to_conversation("You", query)
                self.process_command(query)

            except sr.WaitTimeoutError:
                self.speak("Sorry, I didn't hear anything. Please try again.")
            except sr.UnknownValueError:
                self.speak("Sorry, I couldn't understand what you said.")
            except sr.RequestError as e:
                self.speak("Sorry, I'm having trouble connecting to the speech service.")
                self.add_to_conversation("System", f"Speech recognition error: {e}")
            except Exception as e:
                self.speak("An unexpected error occurred.")
                self.add_to_conversation("System", f"Error: {e}")
            finally:
                self.stop_listening()

    def process_command(self, query):
        """Process the user's command"""
        try:
            # Basic responses
            if 'thanks' in query or 'thank you' in query:
                self.speak("You're welcome! How else can I assist you?")
                return

            if 'exit' in query or 'stop' in query or 'quit' in query:
                self.speak("Goodbye! Have a nice day!")
                self.root.after(1000, self.root.destroy)
                return

            if "tell me about yourself" in query:
                self.speak("I am Deepak AI, your personal voice assistant. I can help with tasks, answer questions, and more!")
                return

            elif "how are you" in query:
                self.speak("I'm just a program, but I'm functioning well. How can I help you?")
                return

            elif "what is your name" in query:
                self.speak("I am Deepak AI, your personal voice assistant!")
                return

            # Time & Date
            if "time" in query:
                current_time = datetime.now().strftime("%I:%M %p")
                self.speak(f"The current time is {current_time}")
                return

            elif "date" in query:
                now = datetime.now()
                self.speak(f"Today is {now.strftime('%B %d, %Y')}")
                return

            # Calculator
            elif any(op in query for op in ['add', 'subtract', 'multiply', 'divide', '+', '-', '*', '/']):
                self.perform_calculation(query)
                return

            # Dictionary
            elif 'define' in query:
                self.define_word(query)
                return

            # Wikipedia Search
            elif 'wikipedia' in query:
                query = query.replace("wikipedia", "").strip()
                if query:
                    try:
                        results = wikipedia.summary(query, sentences=2)
                        self.speak("According to Wikipedia: " + results)
                    except wikipedia.exceptions.DisambiguationError as e:
                        self.speak("There are multiple matches. Please be more specific.")
                    except wikipedia.exceptions.PageError:
                        self.speak("Sorry, I couldn't find information on that topic.")
                    except Exception as e:
                        self.speak("Sorry, I couldn't access Wikipedia right now.")
                else:
                    self.speak("Please specify what to search on Wikipedia.")
                return

            # Open Websites
            elif 'open youtube' in query:
                wb.open("https://youtube.com")
                self.speak("Opening YouTube")
                return

            elif 'open google' in query:
                wb.open("https://google.com")
                self.speak("Opening Google")
                return

            # Weather
            elif 'weather' in query:
                self.get_weather()
                return

            # Play Song
            elif 'play' in query:
                song_name = query.replace('play', '').strip()
                if song_name:
                    self.play_song(song_name)
                else:
                    self.speak("Please specify a song name")
                return

            # Google Search
            elif 'search' in query:
                search_query = query.replace("search", "").strip()
                if search_query:
                    wb.open(f"https://www.google.com/search?q={search_query}")
                    self.speak(f"Here are search results for {search_query}")
                else:
                    self.speak("What would you like me to search for?")
                return

            # Jokes
            elif 'joke' in query:
                self.tell_joke()
                return

            # System Shutdown & Restart
            elif "shutdown" in query:
                self.speak("Shutting down the system, goodbye!")
                os.system("shutdown /s /t 1")
                return

            elif "restart" in query:
                self.speak("Restarting the system, please wait!")
                os.system("shutdown /r /t 1")
                return

            # Timer
            elif "set timer" in query or "timer for" in query:
                self.set_timer(query)
                return

            # Battery Status
            elif "battery" in query or "percentage" in query:
                self.battery_status()
                return


            # If no command matched
            self.speak("I didn't understand that. Can you please repeat?")
        except Exception as e:
            self.speak("Sorry, an error occurred while processing your command.")
            self.add_to_conversation("System", f"Command processing error: {e}")

    def play_song(self, song_name):
        """Play a song on YouTube"""
        try:
            kit.playonyt(song_name)
            self.speak(f"Playing {song_name} on YouTube")
        except Exception as e:
            self.speak("Sorry, I couldn't play the song")
            self.add_to_conversation("System", f"Play song error: {e}")

    def perform_calculation(self, query):
        """Perform a calculation"""
        try:
            # Simple arithmetic operations
            if '+' in query:
                parts = query.split('+')
                result = float(parts[0].strip()) + float(parts[1].strip())
            elif '-' in query:
                parts = query.split('-')
                result = float(parts[0].strip()) - float(parts[1].strip())
            elif '*' in query or 'x' in query:
                parts = query.replace('x', '').split('')
                result = float(parts[0].strip()) * float(parts[1].strip())
            elif '/' in query:
                parts = query.split('/')
                result = float(parts[0].strip()) / float(parts[1].strip())
            else:
                self.speak("Sorry, I couldn't understand the calculation")
                return

            self.speak(f"The result is {result}")
        except Exception as e:
            self.speak("Sorry, I couldn't perform that calculation")
            self.add_to_conversation("System", f"Calculation error: {e}")

    def define_word(self, query):
        """Define a word"""
        word = query.replace("define", "").strip()
        if word:
            try:
                url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
                response = requests.get(url).json()

                if isinstance(response, list):
                    definition = response[0]['meanings'][0]['definitions'][0]['definition']
                    self.speak(f"{word} means {definition}")
                else:
                    self.speak(f"Sorry, I couldn't find the definition for {word}")
            except Exception as e:
                self.speak("Sorry, I couldn't fetch the definition")
                self.add_to_conversation("System", f"Dictionary error: {e}")
        else:
            self.speak("Please specify a word to define")

    def get_weather(self):
        """Get weather information"""
        self.speak("Which city's weather would you like to know?")

        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=5)
                city = r.recognize_google(audio).lower()

                if city:
                    try:
                        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
                        response = requests.get(url).json()

                        if response.get('cod') == 200:
                            temp = response['main']['temp']
                            desc = response['weather'][0]['description']
                            self.speak(f"The weather in {city} is {desc} with a temperature of {temp}°C")
                        else:
                            self.speak("Sorry, I couldn't fetch the weather information")
                    except Exception as e:
                        self.speak("Sorry, I couldn't connect to the weather service")
                        self.add_to_conversation("System", f"Weather API error: {e}")
        except Exception as e:
            self.speak("Sorry, I didn't catch the city name")
            self.add_to_conversation("System", f"Weather input error: {e}")

    def battery_status(self):
        """Check battery status"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                status = "plugged in" if battery.power_plugged else "not charging"
                self.speak(f"Your battery is at {percent}% and is {status}")
            else:
                self.speak("Battery information not available")
        except Exception as e:
            self.speak("Could not check battery status")
            self.add_to_conversation("System", f"Battery error: {e}")

    def send_whatsapp_message(self, query):
        """Send a WhatsApp message"""
        try:
            # Extract contact name
            contact_name = query.replace("send whatsapp message to", "").replace("whatsapp", "").strip().lower()

            if contact_name in self.contacts and self.contacts[contact_name]:
                self.speak(f"What message would you like to send to {contact_name}?")

                try:
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                        audio = r.listen(source, timeout=5)
                        message = r.recognize_google(audio)

                        if message:
                            phone_number = "+91" + self.contacts[contact_name]
                            kit.sendwhatmsg_instantly(phone_number, message)
                            self.speak(f"Message sent to {contact_name}")
                        else:
                            self.speak("No message provided")
                except Exception as e:
                    self.speak("Sorry, I didn't catch the message")
                    self.add_to_conversation("System", f"WhatsApp message error: {e}")
            else:
                self.speak(f"Sorry, I don't have {contact_name}'s contact details")
        except Exception as e:
            self.speak("Sorry, I couldn't send the message")
            self.add_to_conversation("System", f"WhatsApp error: {e}")

    def set_timer(self, query=None):
        """Set a timer"""
        try:
            if query:
                # Extract minutes from query if provided
                numbers = re.findall(r'\d+', query)
                if numbers:
                    minutes = int(numbers[0])
                else:
                    minutes = None
            else:
                minutes = None

            if not minutes:
                self.speak("For how many minutes would you like to set the timer?")
                try:
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                        audio = r.listen(source, timeout=5)
                        minutes = int(re.findall(r'\d+', r.recognize_google(audio))[0])
                except:
                    self.speak("Sorry, I didn't understand the duration")
                    return

            if minutes:
                self.speak(f"Timer set for {minutes} minutes")

                def timer_complete():
                    self.speak("Time's up! Time's up! Time's up!")

                threading.Timer(minutes * 60, timer_complete).start()
        except Exception as e:
            self.speak("Sorry, I couldn't set the timer")
            self.add_to_conversation("System", f"Timer error: {e}")

    def tell_joke(self):
        """Tell a joke"""
        try:
            joke = pyjokes.get_joke()
            self.speak(joke)
        except Exception as e:
            self.speak("Sorry, I couldn't think of a joke right now")
            self.add_to_conversation("System", f"Joke error: {e}")

    def show_settings(self):
        """Show settings dialog"""
        settings = tk.Toplevel(self.root)
        settings.title("Settings")
        settings.geometry("400x300")
        settings.resizable(False, False)
        settings.configure(bg='#1F1B24')

        tk.Label(settings, text="Settings", font=self.title_font, bg='#1F1B24', fg='white').pack(pady=10)

        # Theme selector
        theme_frame = tk.Frame(settings, bg='#1F1B24')
        theme_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(theme_frame, text="Theme:", bg='#1F1B24', fg='white').pack(side=tk.LEFT)

        theme_var = tk.StringVar(value="dark")
        ttk.Radiobutton(theme_frame, text="Dark", variable=theme_var, value="dark").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(theme_frame, text="Light", variable=theme_var, value="light").pack(side=tk.LEFT)

        # Close button
        tk.Button(settings,
                 text="Close",
                 command=settings.destroy,
                 bg='#6200EE',
                 fg='white',
                 borderwidth=0,
                 padx=20,
                 pady=5).pack(pady=20)

    def show_help(self):
        """Show help dialog"""
        help_text = """DEEPAK AI Voice Assistant Help:

Available Commands:
• Play [song name] - Play a song on YouTube
• Wikipedia [topic] - Search Wikipedia
• Open YouTube/Google - Open websites
• Weather [city] - Get weather info
• Time/Date - Current time/date
• Calculate [expression] - Do math calculations
• Define [word] - Get word definitions
• Set timer [minutes] - Set a countdown timer
• Battery status - Check battery level
• Send WhatsApp message - Send message
• Tell a joke - Hear a random joke
• Shutdown/Restart - Control your PC
• Exit - Close the application"""

        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("500x400")
        help_window.resizable(False, False)
        help_window.configure(bg='#1F1B24')

        text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, bg='#1E1E1E', fg='white')
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = VoiceAssistant(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"The application crashed: {e}")
        sys.exit(1)