# Morse_Code_Player
import time
import winsound
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import threading
import numpy as np
import wave
from gtts import gTTS
from playsound import playsound
import pyperclip
import os

# ---------------- Morse Code Dictionaries ----------------
TEXT_TO_MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', ' ': '/'
}
MORSE_TO_TEXT = {v: k for k, v in TEXT_TO_MORSE.items()}

# ---------------- Standard Morse Sound Settings ----------------
DOT_FREQ, DASH_FREQ = 800, 800
DOT_DUR, DASH_DUR = 100, 300  # in milliseconds

# ---------------- Morse Playback Function ----------------
def play_morse_live(message, output_widget):
    message = message.strip()
    is_morse = all(c in ".- /" for c in message)

    output_widget.config(state='normal')

    if is_morse:
        # Morse → Text
        words = message.split(' / ')
        decoded = ''
        for word in words:
            for l in word.split():
                decoded += MORSE_TO_TEXT.get(l, '?')
            decoded += ' '
        output_widget.insert(tk.END, f"📜 Morse → Text: {decoded.strip()}\n", "bold")
    else:
        # Text → Morse
        msg = message.upper()
        morse = " ".join(TEXT_TO_MORSE.get(c, '?') for c in msg)
        output_widget.insert(tk.END, f"💬 Input: {msg}\n", "bold")
        output_widget.insert(tk.END, f"🔹 Morse: {morse}\n\n", "italic")
        output_widget.insert(tk.END, "🎵 Playing live:\n\n")
        output_widget.see(tk.END)
        output_widget.update()

        # ---------------- Optimized Delays ----------------
        intra_symbol_delay = 0.05  # between dot/dash
        inter_letter_delay = 0.1   # between letters
        inter_word_delay = 0.15    # between words

        for char in msg:
            if char in TEXT_TO_MORSE:
                for symbol in TEXT_TO_MORSE[char]:
                    start_index = output_widget.index(tk.END)
                    output_widget.insert(tk.END, symbol + " ")
                    output_widget.see(tk.END)
                    output_widget.update()

                    if symbol == '.':
                        color = "#00BFFF"
                        winsound.Beep(DOT_FREQ, DOT_DUR)
                    elif symbol == '-':
                        color = "#1E90FF"
                        winsound.Beep(DASH_FREQ, DASH_DUR)
                    else:
                        color = "gray"

                    end_index = output_widget.index(tk.END)
                    output_widget.tag_add("active", start_index, end_index)
                    output_widget.tag_config("active", foreground=color, font=("Consolas", 16, "bold"))
                    output_widget.update()
                    time.sleep(intra_symbol_delay)
                    output_widget.tag_remove("active", start_index, end_index)

                output_widget.insert(tk.END, "  ")
                time.sleep(inter_letter_delay)
            elif char == ' ':
                output_widget.insert(tk.END, "/ ")
                output_widget.update()
                time.sleep(inter_word_delay)

        output_widget.insert(tk.END, "\n\n✅ Done!\n", "done")
        output_widget.tag_config("done", foreground="#00FF7F", font=("Arial", 13, "bold"))

    output_widget.config(state='disabled')
    output_widget.see(tk.END)

# ---------------- Morse Audio Generation ----------------
def save_morse_audio(message, filename="morse_output.wav"):
    dot_dur_sec, dash_dur_sec = DOT_DUR / 1000, DASH_DUR / 1000
    sample_rate = 44100
    audio = np.array([], dtype=np.float32)

    for char in message.upper():
        if char in TEXT_TO_MORSE:
            for symbol in TEXT_TO_MORSE[char]:
                if symbol == '.':
                    t = np.linspace(0, dot_dur_sec, int(sample_rate * dot_dur_sec), False)
                    tone = 0.5 * np.sin(DOT_FREQ * 2 * np.pi * t)
                elif symbol == '-':
                    t = np.linspace(0, dash_dur_sec, int(sample_rate * dash_dur_sec), False)
                    tone = 0.5 * np.sin(DASH_FREQ * 2 * np.pi * t)
                else:
                    tone = np.zeros(int(sample_rate * 0.1))
                audio = np.concatenate((audio, tone, np.zeros(int(sample_rate * 0.05))))
            audio = np.concatenate((audio, np.zeros(int(sample_rate * 0.2))))
        elif char == ' ':
            audio = np.concatenate((audio, np.zeros(int(sample_rate * 0.5))))

    audio = np.int16(audio * 32767)
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(audio.tobytes())

# ---------------- Text-to-Speech ----------------
def speak_text():
    msg = entry.get().strip()
    if not msg:
        messagebox.showwarning("Warning", "Enter a message first!")
        return
    tts = gTTS(text=msg, lang='en')
    tmp_file = "tts_temp.mp3"
    tts.save(tmp_file)
    threading.Thread(target=playsound, args=(tmp_file,), daemon=True).start()

# ---------------- Copy Output ----------------
def copy_output():
    msg = entry.get().strip()
    if not msg:
        messagebox.showwarning("Warning", "Enter a message first!")
        return
    morse_text = " ".join(TEXT_TO_MORSE.get(c.upper(), '?') for c in msg)
    pyperclip.copy(morse_text)
    messagebox.showinfo("Copied", "Morse code copied to clipboard!")

# ---------------- GUI Handlers ----------------
def on_play(event=None):
    msg = entry.get()
    if msg.strip():
        threading.Thread(target=play_morse_live, args=(msg, output), daemon=True).start()

def clear_all():
    entry.delete(0, tk.END)
    output.config(state='normal')
    output.delete("1.0", tk.END)
    output.config(state='disabled')

def on_download():
    msg = entry.get().strip()
    if not msg:
        messagebox.showwarning("Warning", "Enter a message first!")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV Audio", "*.wav")])
    if file_path:
        save_morse_audio(msg, filename=file_path)
        messagebox.showinfo("Saved", f"Morse audio saved to {file_path}")

def decode_morse_audio():
    messagebox.showinfo("Info", "Audio decoding to text is not yet implemented.")

# ---------------- GUI Setup ----------------
root = tk.Tk()
root.title("🎵 Morse Code Player + TTS + Copy")
root.geometry("1050x780")
root.config(bg="black")
root.rowconfigure(2, weight=1)
root.columnconfigure(0, weight=1)

# Label
tk.Label(root, text="💬 Enter message or Morse code (. - /):",
         font=("Arial", 18, "bold"), bg="black", fg="#1E90FF", pady=10).grid(row=0, column=0, sticky="ew")

# Entry
entry = tk.Entry(root, width=60, font=("Consolas", 20), justify="center", bg="#111", fg="#00BFFF",
                 insertbackground="#00BFFF")
entry.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
entry.focus_set()
entry.bind("<Return>", on_play)

# Output
output = scrolledtext.ScrolledText(root, width=100, height=32, font=("Consolas", 13), bg="#000", fg="#00FFFF",
                                   insertbackground="#00BFFF")
output.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
output.config(state='disabled')

# Buttons
btn_frame = tk.Frame(root, bg="black")
btn_frame.grid(row=3, column=0, sticky="ew", pady=10)
btn_frame.columnconfigure([0, 1, 2, 3, 4, 5], weight=1)

tk.Button(btn_frame, text="▶ Play / Translate", command=on_play, font=("Arial", 16, "bold"), bg="#1E90FF",
          fg="white").grid(row=0, column=0, padx=5, sticky="ew")
tk.Button(btn_frame, text="🗑 Clear", command=clear_all, font=("Arial", 16, "bold"), bg="#FF4500", fg="white").grid(
    row=0, column=1, padx=5, sticky="ew")
tk.Button(btn_frame, text="🔊 Speak Text", command=speak_text, font=("Arial", 16, "bold"), bg="#FF69B4",
          fg="white").grid(row=0, column=2, padx=5, sticky="ew")
tk.Button(btn_frame, text="📂 Decode Audio → Text", command=decode_morse_audio, font=("Arial", 16, "bold"), bg="#FFD700",
          fg="black").grid(row=0, column=3, padx=5, sticky="ew")
tk.Button(btn_frame, text="💾 Download Morse Audio", command=on_download, font=("Arial", 16, "bold"), bg="#32CD32",
          fg="white").grid(row=0, column=4, padx=5, sticky="ew")
tk.Button(btn_frame, text="📋 Copy Output", command=copy_output, font=("Arial", 16, "bold"), bg="#30CD30",
          fg="white").grid(row=0, column=5,padx=5, sticky="ew")

root.mainloop()

