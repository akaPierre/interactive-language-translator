import tkinter as tk
from ttkbootstrap import Style
from tkinter import messagebox, filedialog
from googletrans import Translator
import threading
import time
import os
from gtts import gTTS
import speech_recognition as sr

# Initialize the translator
translator = Translator()

# Create the main window with a ttkbootstrap theme
style = Style(theme="solar")  # Example: solar theme
root = style.master
root.title("Interactive Language Translator")
root.geometry("800x640")
root.minsize(800,640)
root.maxsize(800,640)

# Set window icon
root.iconbitmap("assets/translator_icon.ico")  # Make sure you have this ico file in assets/

# Set a default font
FONT = ("Arial", 12)

# A global variable to store the last input time
last_input_time = 0
debounce_time = 0.5  # Half-second debounce time

# Function to perform the actual translation in a separate thread
def translate_in_thread(source_text, source_language, target_language, retry_count=3):
    try:
        # Initialize the translator
        translator = Translator()
        
        # Perform the translation
        translation = translator.translate(source_text, src=source_language, dest=target_language)
        
        # Update the output text in the main thread
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, translation.text)

        # Update translation history
        update_history(source_text, translation.text, source_language, target_language)

    except Exception as e:
        # Handle exceptions
        messagebox.showerror("Translation Error", f"An error occurred: {str(e)}")

# Function to debounce the translation and trigger it when the user stops typing
def debounce_translate():
    global last_input_time
    while True:
        current_time = time.time()
        # If the user hasn't typed in the last debounce_time seconds, trigger translation
        if current_time - last_input_time >= debounce_time:
            source_text = text_input.get("1.0", tk.END).strip()
            if source_text:
                source_language = languages[source_lang_var.get()]
                target_language = languages[target_lang_var.get()]
                # Run translation in a separate thread
                threading.Thread(target=translate_in_thread, args=(source_text, source_language, target_language)).start()
            break
        time.sleep(0.1)  # Sleep for 100 ms and check again

# Event handler when text input is modified
def on_text_change(event):
    global last_input_time
    text_input.edit_modified(False)  # Reset modified flag
    last_input_time = time.time()  # Record the current time as the last input time
    threading.Thread(target=debounce_translate).start()  # Start debounce translation in a new thread

# Function to swap languages
def swap_languages():
    source = source_lang_var.get()
    target = target_lang_var.get()

    source_lang_var.set(target)
    target_lang_var.set(source)

    # Re-translate after swapping
    source_text = text_input.get("1.0", tk.END).strip()
    if source_text:
        source_language = languages[source_lang_var.get()]
        target_language = languages[target_lang_var.get()]
        threading.Thread(target=translate_in_thread, args=(source_text, source_language, target_language)).start()

# Function to save translation to a file
def save_translation():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(f"Source: {text_input.get('1.0', tk.END)}\n")
            file.write(f"Translation: {text_output.get('1.0', tk.END)}\n\n")

# Function to translate into multiple languages
def translate_multiple_languages():
    source_text = text_input.get("1.0", tk.END).strip()
    source_language = languages[source_lang_var.get()]

    if source_text:
        for lang in languages.values():
            threading.Thread(target=translate_in_thread, args=(source_text, source_language, lang)).start()

# Function to handle speech-to-text input
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        # Recognize speech using Google Speech Recognition
        recognized_text = recognizer.recognize_google(audio)
        text_input.delete("1.0", tk.END)
        text_input.insert(tk.END, recognized_text)
    except sr.UnknownValueError:
        messagebox.showerror("Error", "Could not understand audio.")
    except sr.RequestError as e:
        messagebox.showerror("Error", f"Could not request results; {e}")

# Function to speak the translated text
def speak_translated_text():
    translated_text = text_output.get("1.0", tk.END).strip()
    target_language = languages[target_lang_var.get()]

    if translated_text:
        tts = gTTS(text=translated_text, lang=target_language)
        tts.save("output.mp3")
        os.system("start output.mp3")  # On Windows, adjust for other OS

# Function to update translation history
def update_history(source_text, translated_text, source_language, target_language):
    history_text = f"{source_lang_var.get()} ({source_language}) -> {target_lang_var.get()} ({target_language}):\n{source_text}\n\nTranslation:\n{translated_text}\n\n"
    history_box.insert(tk.END, history_text)

# Language selection dropdowns
languages = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh-cn",
    "Japanese": "ja",
    "Russian": "ru",
    "Portuguese": "pt",
    "Hindi": "hi"
}

source_lang_var = tk.StringVar(value="English")
target_lang_var = tk.StringVar(value="Spanish")

source_lang_label = tk.Label(root, text="Source Language:", font=FONT)
source_lang_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

source_lang_menu = tk.OptionMenu(root, source_lang_var, *languages.keys())
source_lang_menu.grid(row=0, column=1, padx=10, pady=10)

target_lang_label = tk.Label(root, text="Target Language:", font=FONT)
target_lang_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")

target_lang_menu = tk.OptionMenu(root, target_lang_var, *languages.keys())
target_lang_menu.grid(row=0, column=3, padx=10, pady=10)

# Swap languages button
swap_button = tk.Button(root, text="Swap", command=swap_languages)
swap_button.grid(row=0, column=4, padx=10, pady=10)

# Input Text
input_label = tk.Label(root, text="Enter Text:", font=FONT)
input_label.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

text_input = tk.Text(root, height=8, width=35, font=FONT)
text_input.grid(row=1, column=1, padx=10, pady=10, sticky="nsew", columnspan=2)
text_input.bind('<<Modified>>', on_text_change)

# Output Text
output_label = tk.Label(root, text="Translated Text:", font=FONT)
output_label.grid(row=2, column=0, padx=10, pady=10, sticky="nw")

text_output = tk.Text(root, height=8, width=35, font=FONT)
text_output.grid(row=2, column=1, padx=10, pady=10, sticky="nsew", columnspan=2)

# Translation history
history_label = tk.Label(root, text="Translation History:", font=FONT)
history_label.grid(row=3, column=0, padx=10, pady=10, sticky="nw")

history_box = tk.Text(root, height=8, width=60, font=FONT)
history_box.grid(row=3, column=1, padx=10, pady=10, columnspan=3)

# Speech to Text button
speech_button = tk.Button(root, text="Speak", command=speech_to_text)
speech_button.grid(row=4, column=0, padx=10, pady=10)

# Speak Translated Text button
tts_button = tk.Button(root, text="Speak Translation", command=speak_translated_text)
tts_button.grid(row=4, column=1, padx=10, pady=10)

# Save translation button
save_button = tk.Button(root, text="Save Translation", command=save_translation)
save_button.grid(row=4, column=2, padx=10, pady=10)

# Run the app
root.mainloop()