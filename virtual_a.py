 
import cv2
import numpy as np
import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import os
import playsound
import random
import wikipedia
import time
import threading
import re
import math
import requests
from textblob import TextBlob
from forex_python.converter import CurrencyRates

model_weights = r"C:\Users\Admin\Downloads\MobileNetSSD_deploy.caffemodel"
model_config = r"C:\Users\Admin\Downloads\MobileNetSSD_deploy.prototxt.txt"
labels = ["background", "aeroplane", "bicycle", "bird", "pen", "pencil", "Mobile Phone", "boat", "bottle", "bus",
          "car", "chair", "diningtable", "motorbike", "person", "pottedplant", "sheep","Board","Projector"
          "sofa", "train", "tvmonitor"]

# Load the model
net = cv2.dnn.readNetFromCaffe(model_config, model_weights)

# Initialize text-to-speech engine
engine = pyttsx3.init()
def speak(text):
    print("Assistant said:", text)
    engine.say(text)
    engine.runAndWait()
    return text

# Function to recognize speech
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = r.listen(source, timeout=30)
            command = r.recognize_google(audio)
            print("You said:", command)

            # Check for variations in AM/PM
            command = re.sub(r'\bPM\b', 'p.m.', command, flags=re.IGNORECASE)
            command = re.sub(r'\bAM\b', 'a.m.', command, flags=re.IGNORECASE)
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, could not understand audio.")
            return ""
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            return ""
        except sr.WaitTimeoutError:
            print("User input timeout. Please speak within 30 seconds.")
            return ""


# Function to display available operations
def show_operations():
    print("Here are the operations I can perform:")
    print("Please choose an operation.")
    print("1. Greet me with 'hello' or 'good morning'")
    print("2. Ask for the current time with 'time'")
    print("3. To check weather say, 'Weather")
    print("4. Open a website with 'open website'")
    print("5. To perform stop watch say 'stop watch")
    print("6. Tell me a joke with 'tell me a joke'")
    print("7. To know live information say,'News")
    print("8. If you want to detect some objects,'Can you detect some objects")
    print("9. Ask a question with 'I have a Question for you!'")
    print("10. Set an alarm with 'set alarm'")
    print("11. Perform a math operation with 'calculation'")
    print("12. To convert the currency say,'convert currency")
    print("13. To translate language, 'Translate")
    print("14. Play music with 'play music'")
    print("15. Exit the program with 'exit'")


# Function to handle virtual assistant commands
def assistant(command):
    result_text = ""
    if any(
            greeting in command for greeting in
            ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        result_text = speak("Hello sir! How can I assist you today?")
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak("The current time is " + current_time)
        result_text = "Showing the current time."
    elif "open website" in command:
        speak("Sure, which website would you like me to open?")
        website = listen()
        webbrowser.open("http://" + website + ".com")
        result_text = f"Opening {website} website."
    elif "play music" in command:
        music_dir = r'C:\Users\Admin\Music\\'
        songs = os.listdir(music_dir)
        if songs:
            random_song = random.choice(songs)
            music_file = os.path.join(music_dir, random_song)
            playsound.playsound(music_file)
            result_text = f"Now playing {random_song}."
        else:
            result_text = speak("No music files found in the specified directory.")
            
    elif "set alarm" in command:
        speak("What time should I set the alarm for?")
        alarm_time = listen()
        new_alarm_thread = set_alarm(alarm_time)
        result_text = "Setting the alarm."

    elif "calculation" in command:
        speak("Sure, what mathematical operation would you like me to perform?")
        expression = listen()
        try:
            # Replace "X" with "*" for multiplication
            expression = expression.replace("X", "*")
            result = evaluate_expression(expression)
            result_text = speak("The result is: " + str(result))
        except Exception as e:
            result_text = speak("Sorry, I couldn't perform the operation. Please try again.")

    elif "i have a question for you" in command:
        speak("Sure, what question would you like me to answer?")
        user_question = listen()
        try:
            wikipedia_result = wikipedia.summary(user_question, sentences=2)
            result_text = speak("According to Wikipedia, " + wikipedia_result)
        except wikipedia.exceptions.DisambiguationError as e:
            result_text = speak("There are multiple possible results for this query. Please be more specific.")
        except wikipedia.exceptions.PageError as e:
            result_text = speak("Sorry, I couldn't find information on that topic.")
            
    elif "stopwatch" in command:
        result_text = speak("Starting stopwatch.")
        stopwatch()
    elif "tell me a joke" in command:
        joke = get_joke()
        speak(joke)
        result_text = "Here's a joke for you."
    elif "translate" in command:
        translate_text()
        result_text = "Performing language translation."
    elif "weather" in command:
        speak("Sure, which city's weather information would you like to check?")
        city = listen()
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=819125530a2924dc43faffa7454e233a"
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            weather_info = data["weather"][0]["description"]
            temperature = round(data["main"]["temp"] - 273.15, 1)
            humidity = data["main"]["humidity"]
            result_text = speak(f"The weather in {city} is currently {weather_info}. The temperature is {temperature} degrees Celsius and the humidity is {humidity}%.")
        else:
            result_text = speak(f"Could not find weather information for {city}.")    

    elif "convert currency" in command:
        convert_currency()
        result_text = "Performing currency conversion."

    elif "news" in command:
        speak("Sure, what categories of news would you like? You can choose from categories like business, entertainment, health, science, sports, or technology.")
    
        # Listen for the user's input regarding the news category
        categories = listen()
    
        # Convert the user's input to lowercase for easier comparison
        categories = categories.lower()
    
        # Map user-friendly category names to API-compatible category names
        category_mapping = {
            'business': 'business',
            'entertainment': 'entertainment',
            'health': 'health',
            'science': 'science',
            'sports': 'sports',
            'technology': 'technology'
        }
    
        # Check if the user's chosen category is valid
        if categories in category_mapping:
            # Get the corresponding API-compatible category name
            api_category = category_mapping[categories]
        
            # Construct the URL for fetching news based on the chosen category
            url = f"https://newsapi.org/v2/top-headlines?country=us&category={api_category}&apiKey=593d9f94fdba4a368bf9b16ab573744c"
        
            # Make the API request
            response = requests.get(url)
            data = response.json()

            if data["status"] == "ok":
                articles = data["articles"]
                if articles:
                    for index, article in enumerate(articles):
                        title = article["title"]
                        description = article["description"]
                        if index < 5:
                            speak(f"{index+1}. {title}. {description}")
                else:
                    speak("No news articles found.")
            else:
                speak("Could not find news information.")
        else:
            speak("Invalid news category. Please choose from the available categories.")
    elif "can you detect some objects" in command:
        speak("Sure!")
        detect_objects()
    
    elif "exit" in command:
        result_text = speak("Thank You! If you need anything else, just let me know. have a nice day sir!")
        exit()
    elif "thank you" in command or "thanks" in command:
        result_text = speak("You're welcome! If you need anything else, just let me know.")
        exit()
    else:
        result_text = speak("I'm sorry, I don't understand that command.")
    return result_text
# speak(mood_feedback)

def detect_objects():
    # Open a video capture object
    cap = cv2.VideoCapture(0)

    detected_objects = set()
    start_time = time.time()
    detection_duration = 10  # seconds

    while (time.time() - start_time) < detection_duration:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Resize frame to 300x300 pixels for the model
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

        # Pass the blob through the network and obtain the detections
        net.setInput(blob)
        detections = net.forward()

        # Loop over the detections
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            # If confidence is above 0.5, consider it as a valid detection
            if confidence > 0.5:
                # Get the index of the label from the 'detections'
                idx = int(detections[0, 0, i, 1])
                object_label = labels[idx]

                # Add the detected object to the set of detected objects
                detected_objects.add(object_label)

                # Speak the detected object label
                # speak(object_label)

        # Break out of the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()

    print("Objects Detected:")
    for obj in detected_objects:
        print(obj)
        speak(obj)


def set_alarm(alarm_time):
    time_formats = ["%H:%M", "%H %M", "%I:%M %p", "%I %p", "%I:%M%p", "%I%p"]
    for format_str in time_formats:
        try:
            alarm_time_obj = datetime.datetime.strptime(alarm_time, format_str)
            break
        except ValueError:
            alarm_time_obj = None

    if alarm_time_obj is not None:
        alarm_thread = threading.Thread(target=alarm_clock, args=(alarm_time_obj,))
        alarm_thread.start()
        return alarm_thread
    else:
        speak("Invalid time format. Please provide the valid time format.")
def translate_text():
    speak("Sure, please provide the text you want to translate.")
    text_to_translate = listen()
    speak("Please specify the target language.")
    target_language = listen()
    try:
        source_lang = TextBlob(text_to_translate).detect_language()
        translated_text = TextBlob(text_to_translate).translate(to=target_language)
        speak(f"The translated text in {target_language} is: {translated_text}")
    except Exception as e:
        speak("Sorry, I couldn't translate the text. Please try again.")

# Function to simulate the alarm clock
def alarm_clock(alarm_time_obj):
    try:
        current_time = datetime.datetime.now()
        while current_time < alarm_time_obj:
            time.sleep(1)
            current_time = datetime.datetime.now()
        speak("Wake up! It's time.")
    except ValueError:
        speak("Invalid time format. Please provide the valid time format.")


# Function to evaluate mathematical expressions
def evaluate_expression(expression):
    if "square root of" in expression:
        number_str = expression.replace("square root of", "").strip()
        number = float(number_str)
        result = math.sqrt(number)
    else:
        result = eval(expression)

    return result
def analyze_sentiment(command):
    blob = TextBlob(command)
    sentiment_score = blob.sentiment.polarity
    if sentiment_score > 0.5:
        return "positive"
    elif sentiment_score < -0.5:
        return "negative"
    else:
        return "neutral"

# Function to provide response based on user's mood
def mood_response(sentiment):
    if sentiment == "positive":
        return "It sounds like you're feeling great! Keep up the good vibes!"
    elif sentiment == "negative":
        return "I'm sorry to hear that. Remember, tough times don't last, but tough people do."
    else:
        return "Seems like a neutral mood. Is there anything specific you'd like to do or talk about?"



def stopwatch():
    speak("Say 'start' to begin the stopwatch.")
    start_time = None
    while True:
        command = listen()
        if "start" in command and start_time is None:
            start_time = time.time()
            speak("Stopwatch started.")
        elif "stop" in command and start_time is not None:
            elapsed_time = time.time() - start_time
            speak(f"Stopwatch stopped. Elapsed time: {round(elapsed_time, 2)} seconds.")
            start_time = None
        elif "stop" in command and start_time is None:
            speak("Stopwatch is not running.")
        elif "exit" in command:
            speak("Exiting stopwatch.")
            break
        else:
            speak("Command not recognized.")


def get_joke():
    url = "https://v2.jokeapi.dev/joke/Any?type=single"
    response = requests.get(url)
    data = response.json()
    joke = data['joke']
    return joke

def convert_currency():
        speak("Please enter the amount to convert:")
        amount = float(input("Enter the amount: "))

        speak("Please enter the source currency:")
        source_currency = input("Enter the source currency: ").upper()

        speak("Please enter the target currency:")
        target_currency = input("Enter the target currency: ").upper()

        try:
            # Initialize CurrencyRates object
            currency_rates = CurrencyRates()

            # Perform the currency conversion
            converted_amount = currency_rates.convert(source_currency, target_currency, amount)

            speak(f"{amount} {source_currency} is equal to {converted_amount} {target_currency}.")
        except Exception as e:
            speak("Sorry, there was an error performing the currency conversion. Please try again.")

# Main loop
show_operations()
while True:
    command = listen()
    result = assistant(command)
    # if "translate" in command:
    #     translate_text()
