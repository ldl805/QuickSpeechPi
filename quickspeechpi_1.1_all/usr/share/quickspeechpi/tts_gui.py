import os
import sys
import subprocess
import threading
import tempfile
import shutil
import wave
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Optional imports for Google GenAI capabilities
GEMINI_AVAILABLE = False
API_KEY = None

# Attempt to load dotenv if available
try:
    import dotenv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dotenv.load_dotenv(os.path.join(script_dir, ".env"))
    dotenv.load_dotenv(os.path.join(os.path.expanduser("~"), ".env"))
except ImportError:
    pass

# Retrieve API key from environment
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("ANTIGRAVITY_API_KEY")

# Attempt to import google-genai
try:
    from google import genai
    from google.genai import types
    if API_KEY:
        GEMINI_AVAILABLE = True
except ImportError:
    pass

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Text-to-Speech")
        self.root.geometry("520x620")
        
        # State variables
        self.current_process = None
        self.stop_requested = False
        self.gemini_available = GEMINI_AVAILABLE
        self.api_key = API_KEY
        
        # --- Voice Configuration Maps ---
        # espeak variants: m1-m7 (male), f1-f4 (female), croak, whisper
        self.voices = {
            "Male 1": "en+m1", "Male 2": "en+m2", "Male 3": "en+m3", "Male 4": "en+m4",
            "Female 1": "en+f1", "Female 2": "en+f2", "Female 3": "en+f3", "Female 4": "en+f4",
            "Croak": "en+croak", "Whisper": "en+whisper", "Default": "en"
        }
        
        self.gemini_voices = {
            "Kore (Stern Male)": "Kore",
            "Puck (Energetic Male)": "Puck",
            "Fenrir (Deep Male)": "Fenrir",
            "Charon (Narrative Male)": "Charon",
            "Aoede (Narrative Female)": "Aoede"
        }
        
        # --- Configure Modern Dark Style ---
        self._setup_style()
        self.root.configure(bg="#1e1e1e")
        
        # Intercept window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # --- UI Layout ---
        
        # 1. Text Input Area Label
        lbl_text = ttk.Label(root, text="Type your text below:")
        lbl_text.pack(pady=(15, 5))
        
        # Scrolled Text Box Frame
        text_frame = ttk.Frame(root)
        text_frame.pack(padx=20, pady=5, fill="both", expand=True)
        
        self.scrollbar = ttk.Scrollbar(text_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.text_input = tk.Text(
            text_frame,
            height=8,
            width=50,
            font=("Helvetica", 12),
            bg="#2d2d2d",
            fg="#f0f0f0",
            insertbackground="#ffffff", # Caret color
            relief="flat",
            borderwidth=1,
            highlightbackground="#3e3e3e",
            highlightcolor="#3a7ebf",
            yscrollcommand=self.scrollbar.set
        )
        self.text_input.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.text_input.yview)
        
        # Live Stats Label
        self.lbl_stats = ttk.Label(root, text="Characters: 0 | Words: 0", font=("Helvetica", 9))
        self.lbl_stats.pack(padx=25, pady=(2, 5), anchor="w")
        self.text_input.bind("<KeyRelease>", self.update_stats)
        self.text_input.bind("<ButtonRelease-1>", self.update_stats)
        
        # 2. Controls Frame
        controls_frame = ttk.LabelFrame(root, text="Voice Configuration")
        controls_frame.pack(padx=20, pady=10, fill="x")
        
        # Engine Selector Dropdown
        lbl_engine = ttk.Label(controls_frame, text="Engine:")
        lbl_engine.grid(row=0, column=0, padx=10, pady=8, sticky="e")
        
        self.engine_var = tk.StringVar(value="eSpeak (Local)")
        self.engine_combo = ttk.Combobox(controls_frame, textvariable=self.engine_var, state="readonly")
        self.engine_combo['values'] = ["eSpeak (Local)", "Gemini TTS (Cloud)"]
        self.engine_combo.grid(row=0, column=1, padx=10, pady=8, sticky="w")
        self.engine_combo.bind("<<ComboboxSelected>>", self.on_engine_change)
        
        # Voice Variant Dropdown
        lbl_voice = ttk.Label(controls_frame, text="Voice:")
        lbl_voice.grid(row=1, column=0, padx=10, pady=8, sticky="e")
        
        self.voice_var = tk.StringVar(value="Default")
        self.voice_combo = ttk.Combobox(controls_frame, textvariable=self.voice_var, state="readonly")
        self.voice_combo['values'] = list(self.voices.keys())
        self.voice_combo.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        
        # Pitch Slider (0 - 99)
        self.lbl_pitch = ttk.Label(controls_frame, text="Pitch (Tone):")
        self.lbl_pitch.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        
        self.pitch_scale = ttk.Scale(controls_frame, from_=0, to=99, orient="horizontal", length=200)
        self.pitch_scale.set(50)
        self.pitch_scale.grid(row=2, column=1, padx=10, pady=5)
        
        # Speed Slider (80 - 450)
        self.lbl_speed = ttk.Label(controls_frame, text="Speed:")
        self.lbl_speed.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        
        self.speed_scale = ttk.Scale(controls_frame, from_=80, to=400, orient="horizontal", length=200)
        self.speed_scale.set(175)
        self.speed_scale.grid(row=3, column=1, padx=10, pady=5)
        
        # Gemini warning label (initially hidden)
        warning_text = "Gemini TTS Unavailable.\nCheck google-genai install & GEMINI_API_KEY in ~/.env"
        self.lbl_gemini_warning = ttk.Label(
            controls_frame, 
            text=warning_text, 
            foreground="#e53935", 
            font=("Helvetica", 9, "bold"),
            justify="left"
        )
        
        # 3. Action Buttons Frame
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=(15, 20))
        
        self.btn_speak = ttk.Button(btn_frame, text="SPEAK", style="Accent.TButton", command=self.speak_text)
        self.btn_speak.pack(side="left", padx=5)
        
        self.btn_stop = ttk.Button(btn_frame, text="STOP", style="Stop.TButton", command=self.stop_speech)
        self.btn_stop.pack(side="left", padx=5)
        self.btn_stop.config(state="disabled")
        
        self.btn_export = ttk.Button(btn_frame, text="Export WAV", command=self.export_wav)
        self.btn_export.pack(side="left", padx=5)
        
        self.btn_clear = ttk.Button(btn_frame, text="Clear Text", command=self.clear_text)
        self.btn_clear.pack(side="left", padx=5)

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        bg_color = "#1e1e1e"
        fg_color = "#f0f0f0"
        card_bg = "#2d2d2d"
        accent_color = "#3a7ebf"
        accent_active = "#296296"
        stop_color = "#c62828"
        stop_active = "#b71c1c"
        
        style.configure('.', background=bg_color, foreground=fg_color, fieldbackground=card_bg)
        
        # Labels and Frames
        style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Helvetica', 10))
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color, foreground=accent_color, bordercolor='#3e3e3e')
        style.configure('TLabelframe.Label', background=bg_color, foreground=accent_color, font=('Helvetica', 10, 'bold'))
        
        # Combobox styling
        style.configure('TCombobox', fieldbackground=card_bg, background=card_bg, foreground=fg_color, arrowcolor=fg_color)
        style.map('TCombobox', 
            fieldbackground=[('readonly', card_bg)],
            background=[('readonly', card_bg)],
            foreground=[('readonly', fg_color)]
        )
        
        # Scale (Slider) styling
        style.configure('Horizontal.TScale', background=bg_color, troughcolor=card_bg)
        
        # Buttons styling
        style.configure('TButton', background=card_bg, foreground=fg_color, bordercolor='#3e3e3e', focuscolor=accent_color)
        style.map('TButton',
            background=[('active', '#424242'), ('disabled', '#151515')],
            foreground=[('active', '#ffffff'), ('disabled', '#777777')],
            bordercolor=[('disabled', '#252525')]
        )
        
        # Accent button (SPEAK)
        style.configure('Accent.TButton', background=accent_color, foreground='#ffffff', bordercolor=accent_active)
        style.map('Accent.TButton',
            background=[('active', accent_active), ('disabled', '#151515')],
            foreground=[('active', '#ffffff'), ('disabled', '#777777')],
            bordercolor=[('disabled', '#252525')]
        )
        
        # Stop button (STOP)
        style.configure('Stop.TButton', background=stop_color, foreground='#ffffff', bordercolor=stop_active)
        style.map('Stop.TButton',
            background=[('active', stop_active), ('disabled', '#151515')],
            foreground=[('active', '#ffffff'), ('disabled', '#777777')],
            bordercolor=[('disabled', '#252525')]
        )

    def on_engine_change(self, event=None):
        engine = self.engine_var.get()
        if engine == "eSpeak (Local)":
            self.voice_combo['values'] = list(self.voices.keys())
            self.voice_var.set("Default")
            self.pitch_scale.state(["!disabled"])
            self.speed_scale.state(["!disabled"])
            self.lbl_gemini_warning.grid_remove()
            self.btn_speak.config(state="normal")
            self.btn_export.config(state="normal")
        else:
            self.voice_combo['values'] = list(self.gemini_voices.keys())
            self.voice_var.set("Kore (Stern Male)")
            self.pitch_scale.state(["disabled"])
            self.speed_scale.state(["disabled"])
            
            if not self.gemini_available:
                self.lbl_gemini_warning.grid(row=4, column=0, columnspan=2, padx=10, pady=8, sticky="w")
                self.btn_speak.config(state="disabled")
                self.btn_export.config(state="disabled")
            else:
                self.lbl_gemini_warning.grid_remove()
                self.btn_speak.config(state="normal")
                self.btn_export.config(state="normal")

    def update_stats(self, event=None):
        text = self.text_input.get("1.0", tk.END).strip()
        char_count = len(text)
        word_count = len(text.split()) if text else 0
        self.lbl_stats.config(text=f"Characters: {char_count} | Words: {word_count}")

    def speak_text(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            return

        engine = self.engine_var.get()
        voice_name = self.voice_var.get()
        
        self.btn_speak.config(state="disabled")
        self.btn_export.config(state="disabled")
        self.btn_stop.config(state="normal")
        
        self.stop_requested = False
        
        thread = threading.Thread(target=self._run_tts, args=(text, engine, voice_name))
        thread.start()

    def _run_tts(self, text, engine, voice_name):
        try:
            if engine == "eSpeak (Local)":
                voice_code = self.voices.get(voice_name, "en")
                pitch = int(self.pitch_scale.get())
                speed = int(self.speed_scale.get())
                
                if self.stop_requested:
                    return
                    
                self.current_process = subprocess.Popen([
                    "espeak",
                    "-v", voice_code,
                    "-p", str(pitch),
                    "-s", str(speed),
                    text
                ])
                self.current_process.wait()
            else:
                voice_code = self.gemini_voices.get(voice_name, "Kore")
                
                if self.stop_requested:
                    return
                    
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=text,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice_code,
                                )
                            )
                        ),
                    )
                )
                
                if self.stop_requested:
                    return
                    
                data = response.candidates[0].content.parts[0].inline_data.data
                
                # Write to temporary file
                temp_file = os.path.join(tempfile.gettempdir(), "quickspeechpi_temp.wav")
                self.save_wave(temp_file, data)
                
                if self.stop_requested:
                    return
                    
                self.current_process = self.play_wav(temp_file)
                if self.current_process:
                    self.current_process.wait()
                    
        except Exception as e:
            self.root.after(0, lambda err=e: messagebox.showerror("TTS Error", f"Error playing speech: {err}"))
        finally:
            self.current_process = None
            self.root.after(0, self._on_speech_finished)

    def save_wave(self, filename, pcm, channels=1, rate=24000, sample_width=2):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm)

    def play_wav(self, file_path):
        for cmd in ["paplay", "pw-play", "aplay"]:
            try:
                if shutil.which(cmd):
                    return subprocess.Popen([cmd, file_path])
            except Exception:
                continue
        raise FileNotFoundError("No audio utility found (tried paplay, pw-play, aplay)")

    def _on_speech_finished(self):
        self.btn_speak.config(state="normal")
        self.btn_export.config(state="normal")
        self.btn_stop.config(state="disabled")

    def stop_speech(self):
        self.stop_requested = True
        if self.current_process:
            try:
                self.current_process.terminate()
            except Exception:
                pass

    def export_wav(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to export.")
            return

        engine = self.engine_var.get()
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV Audio", "*.wav")],
            title="Export TTS as WAV"
        )
        if not file_path:
            return
            
        self.btn_speak.config(state="disabled")
        self.btn_export.config(state="disabled")
        self.btn_stop.config(state="disabled")
        
        thread = threading.Thread(target=self._run_export, args=(text, engine, file_path))
        thread.start()

    def _run_export(self, text, engine, file_path):
        try:
            if engine == "eSpeak (Local)":
                voice_name = self.voice_var.get()
                voice_code = self.voices.get(voice_name, "en")
                pitch = int(self.pitch_scale.get())
                speed = int(self.speed_scale.get())
                
                subprocess.run([
                    "espeak",
                    "-v", voice_code,
                    "-p", str(pitch),
                    "-s", str(speed),
                    "-w", file_path,
                    text
                ], check=True)
            else:
                voice_name = self.voice_var.get()
                voice_code = self.gemini_voices.get(voice_name, "Kore")
                
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=text,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice_code,
                                )
                            )
                        ),
                    )
                )
                data = response.candidates[0].content.parts[0].inline_data.data
                self.save_wave(file_path, data)
                
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Audio successfully exported to:\n{file_path}"))
        except Exception as e:
            self.root.after(0, lambda err=e: messagebox.showerror("Export Error", f"Failed to export WAV: {err}"))
        finally:
            self.root.after(0, self._on_export_finished)

    def _on_export_finished(self):
        self.btn_speak.config(state="normal")
        self.btn_export.config(state="normal")

    def clear_text(self):
        self.text_input.delete("1.0", tk.END)
        self.update_stats()

    def on_close(self):
        self.stop_speech()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
