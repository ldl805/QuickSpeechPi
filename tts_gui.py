import tkinter as tk
from tkinter import ttk
import subprocess
import threading

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Text-to-Speech")
        self.root.geometry("500x450")

        # --- Voice Configuration Maps ---
        # espeak variants: m1-m7 (male), f1-f4 (female), croak, whisper
        self.voices = {
            "Male 1": "en+m1", "Male 2": "en+m2", "Male 3": "en+m3", "Male 4": "en+m4",
            "Female 1": "en+f1", "Female 2": "en+f2", "Female 3": "en+f3", "Female 4": "en+f4",
            "Croak": "en+croak", "Whisper": "en+whisper", "Default": "en"
        }

        # --- UI Layout ---

        # 1. Text Input Area
        lbl_text = ttk.Label(root, text="Type your text below:")
        lbl_text.pack(pady=(10, 5))

        self.text_input = tk.Text(root, height=8, width=50, font=("Helvetica", 12))
        self.text_input.pack(padx=20, pady=5)

        # 2. Controls Frame
        controls_frame = ttk.LabelFrame(root, text="Voice Settings")
        controls_frame.pack(padx=20, pady=10, fill="x")

        # Voice Variant Dropdown
        lbl_voice = ttk.Label(controls_frame, text="Voice:")
        lbl_voice.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.voice_var = tk.StringVar(value="Default")
        self.voice_combo = ttk.Combobox(controls_frame, textvariable=self.voice_var, state="readonly")
        self.voice_combo['values'] = list(self.voices.keys())
        self.voice_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Pitch Slider (0 - 99)
        lbl_pitch = ttk.Label(controls_frame, text="Pitch (Tone):")
        lbl_pitch.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        
        self.pitch_scale = ttk.Scale(controls_frame, from_=0, to=99, orient="horizontal", length=200)
        self.pitch_scale.set(50) # Default pitch
        self.pitch_scale.grid(row=1, column=1, padx=10, pady=5)

        # Speed Slider (80 - 450)
        lbl_speed = ttk.Label(controls_frame, text="Speed:")
        lbl_speed.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        
        self.speed_scale = ttk.Scale(controls_frame, from_=80, to=400, orient="horizontal", length=200)
        self.speed_scale.set(175) # Default speed
        self.speed_scale.grid(row=2, column=1, padx=10, pady=5)

        # 3. Action Buttons
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=20)

        self.btn_speak = ttk.Button(btn_frame, text="SPEAK", command=self.speak_text)
        self.btn_speak.pack(side="left", padx=10)

        self.btn_clear = ttk.Button(btn_frame, text="Clear Text", command=self.clear_text)
        self.btn_clear.pack(side="left", padx=10)

    def speak_text(self):
        # Get text from box
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            return

        # Get settings
        voice_name = self.voice_var.get()
        voice_code = self.voices.get(voice_name, "en")
        pitch = int(self.pitch_scale.get())
        speed = int(self.speed_scale.get())

        # Disable button briefly
        self.btn_speak.config(state="disabled")

        # Run in a separate thread to avoid freezing GUI
        thread = threading.Thread(target=self._run_espeak, args=(text, voice_code, pitch, speed))
        thread.start()

    def _run_espeak(self, text, voice, pitch, speed):
        try:
            # Construct command: espeak -v <voice> -p <pitch> -s <speed> "text"
            # We use --stdout | paplay for better audio compatibility on some Linux distros,
            # or just run espeak directly. Let's try direct first, it's simpler.
            subprocess.run([
                "espeak",
                "-v", voice,
                "-p", str(pitch),
                "-s", str(speed),
                text
            ])
        except Exception as e:
            print(f"Error speaking: {e}")
        finally:
            # Re-enable button
            self.root.after(0, lambda: self.btn_speak.config(state="normal"))

    def clear_text(self):
        self.text_input.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
