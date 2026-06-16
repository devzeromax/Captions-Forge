"""
╔══════════════════════════════════════════════════════════════╗
║            Captions Forge v2.0 — Free Subtitle Generator        ║
║   Auto-installs · GPU Accelerated · Open Source (MIT)        ║
║   GitHub: https://github.com/YOUR_USERNAME/captions-forge       ║
╚══════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────────────────────
#  BOOTSTRAP — runs BEFORE any imports
#  Checks & auto-installs: pip, torch, openai-whisper, ffmpeg-python
# ─────────────────────────────────────────────────────────────
import sys
import subprocess
import importlib
import threading
import time
import traceback
import os

# True when running as PyInstaller EXE (not python script)
IS_FROZEN = getattr(sys, "frozen", False)

REQUIRED_PACKAGES = {
    "whisper":       "openai-whisper",
    "torch":         "torch",
    "torchaudio":    "torchaudio",
    "torchvision":   "torchvision",
}

def _pip_install(pkg_name: str, extra_args: list = None):
    cmd = [sys.executable, "-m", "pip", "install", pkg_name,
           "--quiet", "--no-warn-script-location"]
    if extra_args:
        cmd += extra_args
    subprocess.check_call(cmd)

def bootstrap_check(log_fn=print):
    """
    Called on app start.
    1. Checks each required package.
    2. If torch missing → installs CUDA version first, falls back to CPU.
    3. Installs any other missing package silently.
    Returns True when everything is ready.
    """
    # EXE already bundles everything — skip slow imports and pip on every launch
    if IS_FROZEN:
        log_fn("Application ready.")
        return True

    missing = []
    for mod, pkg in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append((mod, pkg))

    if not missing:
        log_fn("All requirements satisfied.")
        return True

    log_fn(f"Missing packages: {[p for _, p in missing]}")
    log_fn("Installing dependencies. Please wait.\n")

    for mod, pkg in missing:
        log_fn(f"  Installing {pkg}…")
        try:
            if mod in ("torch", "torchaudio", "torchvision"):
                # Try CUDA first
                try:
                    _pip_install(pkg, ["--index-url", "https://download.pytorch.org/whl/cu118"])
                    log_fn(f"  {pkg} (CUDA) installed")
                except Exception:
                    _pip_install(pkg)
                    log_fn(f"  {pkg} (CPU fallback) installed")
            else:
                _pip_install(pkg)
                log_fn(f"  {pkg} installed")
        except Exception as e:
            log_fn(f"  Failed to install {pkg}: {e}")
            return False

    log_fn("\nAll packages ready.\n")
    return True


# ─────────────────────────────────────────────────────────────
#  Main GUI imports (safe after bootstrap)
# ─────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Lazy globals
whisper_mod = None
torch_mod   = None

def _load_libs():
    global whisper_mod, torch_mod
    if whisper_mod is None:
        import whisper as w;  whisper_mod = w
    if torch_mod is None:
        import torch as t;    torch_mod   = t

# ─────────────────────────────────────────────────────────────
#  Colour + Font tokens
# ─────────────────────────────────────────────────────────────
BG           = "#f3f3f3"
PANEL        = "#ffffff"
PANEL2       = "#fafafa"
ACCENT       = "#0078d4"
ACCENT_DARK  = "#005a9e"
ACCENT_HOVER = "#106ebe"
SUCCESS      = "#107c10"
WARNING      = "#ca5010"
ERROR        = "#c42b1c"
TEXT         = "#1a1a1a"
TEXT_DIM     = "#605e5c"
BORDER       = "#d1d1d1"
HDR_BG       = "#ffffff"
LOG_BG       = "#fafafa"
LOG_FG       = "#323130"

FT           = ("Segoe UI", 10)
FT_BOLD      = ("Segoe UI", 10, "bold")
FT_TITLE     = ("Segoe UI", 16, "bold")
FT_SMALL     = ("Segoe UI",  9)
FT_MONO      = ("Consolas",  9)
FT_SECTION   = ("Segoe UI",  9, "bold")


# ═════════════════════════════════════════════════════════════
#  Splash / Setup Window  (shown on first launch)
# ═════════════════════════════════════════════════════════════
class SetupWindow(tk.Toplevel):
    def __init__(self, parent, on_done):
        super().__init__(parent)
        self.title("Captions Forge — Setup")
        self.geometry("560x420")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.on_done = on_done
        self._build()
        self.after(300, self._run)

    def _build(self):
        tk.Label(self, text="Captions Forge", font=FT_TITLE,
                 bg=BG, fg=TEXT).pack(pady=(28, 4))
        tk.Label(self, text="Checking and installing required packages",
                 font=FT, bg=BG, fg=TEXT_DIM).pack()

        self.log = scrolledtext.ScrolledText(
            self, height=14, bg=LOG_BG, fg=LOG_FG,
            relief="flat", font=FT_MONO, wrap="word",
            highlightthickness=1, highlightbackground=BORDER)
        self.log.pack(fill="both", expand=True, padx=20, pady=16)
        self.log.configure(state="disabled")

        self.bar = ttk.Progressbar(self, mode="indeterminate")
        self.bar.pack(fill="x", padx=20, pady=(0, 8))
        self._style_bar()
        self.bar.start(10)

        self.btn = tk.Button(self, text="Continue", state="disabled",
                             bg=ACCENT, fg="white", relief="flat",
                             font=FT_BOLD, padx=24, pady=8,
                             activebackground=ACCENT_DARK,
                             command=self._continue)
        self.btn.pack(pady=(0, 20))

    def _style_bar(self):
        s = ttk.Style(self)
        s.theme_use("default")
        s.configure("Horizontal.TProgressbar", troughcolor=PANEL,
                    background=ACCENT, thickness=6)

    def _log(self, msg):
        def _do():
            self.log.configure(state="normal")
            self.log.insert("end", msg + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.after(0, _do)

    def _run(self):
        def worker():
            ok = bootstrap_check(self._log)
            self.bar.stop()
            if ok:
                self._log("\nSetup complete. Click Continue.")
                self.after(0, lambda: self.btn.configure(state="normal"))
            else:
                self._log("\nSetup failed. Check your internet connection and retry.")
                self.after(0, lambda: self.btn.configure(
                    text="Close", state="normal",
                    command=self.destroy, bg=ERROR))
        threading.Thread(target=worker, daemon=True).start()

    def _continue(self):
        self.destroy()
        self.on_done()


# ═════════════════════════════════════════════════════════════
#  Main Application Window
# ═════════════════════════════════════════════════════════════
class CaptionsForgeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Captions Forge — Subtitle Generator")
        self.geometry("880x720")
        self.minsize(780, 640)
        self.configure(bg=BG)
        if not IS_FROZEN:
            self.withdraw()       # hidden until setup done (Python mode only)

        # State variables
        self.input_path  = tk.StringVar()
        self.output_dir  = tk.StringVar()
        self.model_var   = tk.StringVar(value="medium")
        self.task_var    = tk.StringVar(value="translate")
        self.lang_var    = tk.StringVar(value="auto")
        self.burn_var    = tk.BooleanVar(value=False)
        self.is_running  = False

        self._build_ui()

        if IS_FROZEN:
            self._after_setup()   # EXE: open main window immediately
        else:
            SetupWindow(self, self._after_setup)

    # ── After setup completes ────────────────────────────
    def _after_setup(self):
        self.deiconify()
        self._check_gpu()

    # ─────────────────────────────────────────────────────
    #  UI Construction
    # ─────────────────────────────────────────────────────
    def _build_ui(self):

        # ── Top header bar ──
        hdr = tk.Frame(self, bg=HDR_BG, highlightthickness=1,
                       highlightbackground=BORDER)
        hdr.pack(fill="x")

        hdr_inner = tk.Frame(hdr, bg=HDR_BG)
        hdr_inner.pack(fill="x", padx=20, pady=14)

        title_col = tk.Frame(hdr_inner, bg=HDR_BG)
        title_col.pack(side="left")
        tk.Label(title_col, text="Captions Forge",
                 font=FT_TITLE, bg=HDR_BG, fg=TEXT).pack(anchor="w")
        tk.Label(title_col, text="Speech-to-text subtitle generation",
                 font=FT_SMALL, bg=HDR_BG, fg=TEXT_DIM).pack(anchor="w")

        self.gpu_badge = tk.Label(hdr_inner, text="Detecting GPU…",
                                  font=FT_SMALL, bg=PANEL2, fg=TEXT_DIM,
                                  padx=10, pady=4,
                                  highlightthickness=1,
                                  highlightbackground=BORDER)
        self.gpu_badge.pack(side="right")

        # ── Tab strip ──
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)
        self._style_notebook()

        main_tab    = tk.Frame(self.notebook, bg=BG)
        about_tab   = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(main_tab,  text="  Generate  ")
        self.notebook.add(about_tab, text="  About  ")

        self._build_main_tab(main_tab)
        self._build_about_tab(about_tab)

    # ── Main tab ─────────────────────────────────────────
    def _build_main_tab(self, parent):
        # scrollable canvas
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0,0), window=inner, anchor="nw")

        def _resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=e.width)
        inner.bind("<Configure>", _resize)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))

        padx = 20

        # ── INPUT FILE ──
        self._section(inner, "Input File", padx)
        row1 = tk.Frame(inner, bg=BG)
        row1.pack(fill="x", padx=padx, pady=(0, 6))
        tk.Entry(row1, textvariable=self.input_path,
                 bg=PANEL, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=FT,
                 highlightthickness=1,
                 highlightcolor=ACCENT,
                 highlightbackground=BORDER).pack(
                     side="left", fill="x", expand=True, ipady=7, padx=(0, 8))
        self._small_btn(row1, "Browse", self._browse_input).pack(side="left")
        tk.Label(inner,
                 text="Supported: MP3, WAV, M4A, AAC, OGG, FLAC, MP4, MKV, AVI, MOV, WEBM",
                 font=FT_SMALL, bg=BG, fg=TEXT_DIM).pack(anchor="w", padx=padx, pady=(0, 12))

        # ── OUTPUT FOLDER ──
        self._section(inner, "Output Folder", padx)
        row2 = tk.Frame(inner, bg=BG)
        row2.pack(fill="x", padx=padx, pady=(0, 16))
        tk.Entry(row2, textvariable=self.output_dir,
                 bg=PANEL, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=FT,
                 highlightthickness=1,
                 highlightcolor=ACCENT,
                 highlightbackground=BORDER).pack(
                     side="left", fill="x", expand=True, ipady=7, padx=(0, 8))
        self._small_btn(row2, "Browse", self._browse_output).pack(side="left")

        # ── MODEL + LANGUAGE ──
        self._section(inner, "Model and Language", padx)
        opts = tk.Frame(inner, bg=PANEL, highlightthickness=1,
                        highlightbackground=BORDER)
        opts.pack(fill="x", padx=padx, pady=(0, 6), ipady=10, ipadx=12)

        tk.Label(opts, text="Model", font=FT, bg=PANEL,
                 fg=TEXT_DIM).grid(row=0, column=0, sticky="w", padx=(0, 8))
        model_cb = ttk.Combobox(opts, textvariable=self.model_var,
                                values=["tiny", "base", "small", "medium", "large"],
                                state="readonly", width=12, font=FT)
        model_cb.grid(row=0, column=1, padx=(0, 32))

        tk.Label(opts, text="Source language", font=FT, bg=PANEL,
                 fg=TEXT_DIM).grid(row=0, column=2, sticky="w", padx=(0, 8))
        langs = ["auto","af","ar","az","be","bg","bn","ca","cs","cy","da","de",
                 "el","en","es","et","fa","fi","fr","gl","gu","he","hi","hr",
                 "hu","hy","id","is","it","ja","ka","kk","km","kn","ko","lt",
                 "lv","mk","ml","mn","mr","ms","my","ne","nl","no","pa","pl",
                 "pt","ro","ru","sk","sl","sq","sr","su","sv","sw","ta","te",
                 "tg","th","tk","tl","tr","tt","uk","ur","uz","vi","yi","yo","zh"]
        lang_cb = ttk.Combobox(opts, textvariable=self.lang_var,
                               values=langs, state="readonly", width=12, font=FT)
        lang_cb.grid(row=0, column=3)

        tk.Label(inner,
                 text="tiny: fastest  |  small: balanced  |  medium: recommended  |  large: highest accuracy",
                 font=FT_SMALL, bg=BG, fg=TEXT_DIM).pack(anchor="w", padx=padx, pady=(0, 14))

        # ── SUBTITLE MODE ──
        self._section(inner, "Subtitle Mode", padx)
        modes_frame = tk.Frame(inner, bg=BG)
        modes_frame.pack(fill="x", padx=padx, pady=(0, 14))

        modes = [
            ("translate", "Translate to English",
             "Detects the spoken language and outputs English subtitles."),
            ("transcribe", "Transcribe (original language)",
             "Outputs subtitles in the same language as the source audio."),
        ]
        for i, (val, label, hint) in enumerate(modes):
            card = tk.Frame(modes_frame, bg=PANEL,
                            highlightthickness=1, highlightbackground=BORDER)
            card.pack(side="left", fill="both", expand=True,
                      padx=(0, 10 if i == 0 else 0), pady=0, ipadx=12, ipady=10)
            tk.Radiobutton(card, text=label, variable=self.task_var, value=val,
                           bg=PANEL, fg=TEXT, selectcolor=PANEL,
                           activebackground=PANEL, activeforeground=TEXT,
                           font=FT_BOLD).pack(anchor="w")
            tk.Label(card, text=hint, font=FT_SMALL,
                     bg=PANEL, fg=TEXT_DIM,
                     justify="left").pack(anchor="w", padx=22, pady=(4, 0))

        # ── EXTRA OPTIONS ──
        self._section(inner, "Options", padx)
        extras = tk.Frame(inner, bg=PANEL, highlightthickness=1,
                           highlightbackground=BORDER)
        extras.pack(fill="x", padx=padx, pady=(0, 16), ipadx=12, ipady=10)
        tk.Checkbutton(extras,
                       text="Burn subtitles into video (requires video input and FFmpeg)",
                       variable=self.burn_var,
                       bg=PANEL, fg=TEXT, selectcolor=PANEL,
                       activebackground=PANEL, font=FT).pack(anchor="w")

        # ── RUN BUTTON ──
        run_frame = tk.Frame(inner, bg=BG)
        run_frame.pack(fill="x", padx=padx, pady=(0, 10))
        self.run_btn = tk.Button(run_frame,
                                 text="Generate Subtitles",
                                 command=self._start,
                                 bg=ACCENT, fg="white", relief="flat",
                                 font=FT_BOLD,
                                 padx=20, pady=10,
                                 activebackground=ACCENT_DARK,
                                 activeforeground="white",
                                 cursor="hand2")
        self.run_btn.pack(fill="x")

        # ── PROGRESS ──
        prog_row = tk.Frame(inner, bg=BG)
        prog_row.pack(fill="x", padx=padx, pady=(4, 4))
        tk.Label(prog_row, text="Status", font=FT_SMALL,
                 bg=BG, fg=TEXT_DIM).pack(side="left")
        self.status_lbl = tk.Label(prog_row, text="Ready",
                                   font=FT_SMALL, bg=BG, fg=TEXT_DIM)
        self.status_lbl.pack(side="left", padx=(8, 0))

        self.progress = ttk.Progressbar(inner, mode="indeterminate",
                                        style="W.Horizontal.TProgressbar")
        self.progress.pack(fill="x", padx=padx, pady=(0, 12))

        # ── LOG ──
        self._section(inner, "Output Log", padx)
        self.log = scrolledtext.ScrolledText(
            inner, height=11,
            bg=LOG_BG, fg=LOG_FG,
            relief="flat", font=FT_MONO, wrap="word",
            highlightthickness=1, highlightbackground=BORDER)
        self.log.pack(fill="both", expand=True, padx=padx, pady=(0, 20))
        self.log.configure(state="disabled")

    # ── About tab ────────────────────────────────────────
    def _build_about_tab(self, parent):
        tk.Label(parent, text="Captions Forge",
                 font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT).pack(pady=(40, 4))
        tk.Label(parent, text="Version 2.0",
                 font=FT_SMALL, bg=BG, fg=TEXT_DIM).pack()
        tk.Label(parent,
                 text="Local speech recognition and subtitle generation",
                 font=FT, bg=BG, fg=TEXT_DIM).pack(pady=(4, 24))

        info = [
            ("Engine",       "OpenAI Whisper (local inference)"),
            ("Languages",    "Automatic detection, 99+ supported"),
            ("Acceleration", "NVIDIA CUDA when available"),
            ("Output",       "SRT subtitle files"),
            ("Burn-in",      "Optional hard-coded subtitles via FFmpeg"),
            ("Dependencies", "openai-whisper, PyTorch, FFmpeg"),
            ("License",      "MIT"),
        ]

        frame = tk.Frame(parent, bg=PANEL, highlightthickness=1,
                         highlightbackground=BORDER)
        frame.pack(padx=48, pady=8, fill="x")
        for label, val in info:
            row = tk.Frame(frame, bg=PANEL)
            row.pack(fill="x", padx=16, pady=6)
            tk.Label(row, text=label, font=FT_BOLD,
                     bg=PANEL, fg=TEXT_DIM, width=14,
                     anchor="w").pack(side="left")
            tk.Label(row, text=val, font=FT,
                     bg=PANEL, fg=TEXT).pack(side="left")

        tk.Label(parent,
                 text="https://github.com/YOUR_USERNAME/captions-forge",
                 font=FT_SMALL, bg=BG, fg=TEXT_DIM).pack(pady=(20, 0))

    # ── Style helpers ─────────────────────────────────────
    def _style_notebook(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=PANEL, foreground=TEXT_DIM,
                    padding=[16, 8], font=FT)
        s.map("TNotebook.Tab",
              background=[("selected", PANEL)],
              foreground=[("selected", ACCENT)])
        s.configure("TCombobox", fieldbackground=PANEL, background=PANEL)
        s.configure("W.Horizontal.TProgressbar",
                    troughcolor=PANEL, background=ACCENT, thickness=4)

    def _section(self, parent, title, padx):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", pady=(14, 6), padx=padx)
        tk.Label(f, text=title.upper(), font=FT_SECTION, bg=BG,
                 fg=TEXT_DIM).pack(anchor="w")

    def _small_btn(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd,
                         bg=PANEL, fg=TEXT, relief="flat",
                         font=FT, padx=14, pady=7,
                         activebackground=PANEL2,
                         activeforeground=TEXT,
                         cursor="hand2",
                         highlightthickness=1,
                         highlightbackground=BORDER)

    # ── GPU detection ─────────────────────────────────────
    def _check_gpu(self):
        def _do():
            try:
                _load_libs()
                if torch_mod.cuda.is_available():
                    dev_name = torch_mod.cuda.get_device_name(0)
                    self.gpu_badge.configure(text=f"GPU: {dev_name}", fg=SUCCESS, bg="#deffde")
                else:
                    self.gpu_badge.configure(text="GPU: Not detected (CPU mode)", fg=TEXT_DIM, bg=PANEL2)
            except Exception as e:
                self.gpu_badge.configure(text="GPU check failed", fg=ERROR, bg="#fde7e9")
                self._log(f"GPU check error: {e}")
        threading.Thread(target=_do, daemon=True).start()

    # ── File browsing ─────────────────────────────────────
    def _browse_input(self):
        p = filedialog.askopenfilename(
            title="Select audio or video file",
            filetypes=[("Media files",
                        "*.mp3 *.wav *.m4a *.aac *.ogg *.flac "
                        "*.mp4 *.mkv *.avi *.mov *.webm"),
                       ("All files","*.*")])
        if p:
            self.input_path.set(p)
            if not self.output_dir.get():
                self.output_dir.set(os.path.dirname(p))

    def _browse_output(self):
        p = filedialog.askdirectory(title="Select output folder")
        if p:
            self.output_dir.set(p)

    # ── Logging ───────────────────────────────────────────
    def _log(self, msg):
        def _do():
            self.log.configure(state="normal")
            ts = time.strftime("%H:%M:%S")
            self.log.insert("end", f"[{ts}]  {msg}\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.after(0, _do)

    def _status(self, msg, color=TEXT_DIM):
        self.after(0, lambda: self.status_lbl.configure(text=msg, fg=color))

    # ── Start processing ──────────────────────────────────
    def _start(self):
        if self.is_running:
            return
        inp = self.input_path.get().strip()
        out = self.output_dir.get().strip()
        if not inp:
            messagebox.showerror("No file selected", "Please select an audio or video file.")
            return
        if not os.path.exists(inp):
            messagebox.showerror("File not found", f"Cannot find:\n{inp}")
            return
        if not out:
            messagebox.showerror("No output folder", "Please select an output folder.")
            return

        self.is_running = True
        self.run_btn.configure(text="Processing…", state="disabled", bg=TEXT_DIM)
        self._status("Processing…", ACCENT)
        self.progress.start(12)
        threading.Thread(target=self._process, daemon=True).start()

    def _done(self, ok=True):
        self.is_running = False
        self.after(0, self.progress.stop)
        self.after(0, lambda: self.run_btn.configure(
            text="Generate Subtitles", state="normal", bg=ACCENT))
        if ok:
            self._status("Complete", SUCCESS)
        else:
            self._status("Failed — see log", ERROR)

    # ── Core Whisper processing ───────────────────────────
    def _process(self):
        try:
            inp        = self.input_path.get().strip()
            out_dir    = self.output_dir.get().strip()
            model_size = self.model_var.get()
            task       = self.task_var.get()
            lang       = self.lang_var.get()
            burn       = self.burn_var.get()

            _load_libs()

            # Device
            device = "cuda" if torch_mod.cuda.is_available() else "cpu"
            self._log(f"Device: {device.upper()}")

            # Load model
            self._status(f"Loading {model_size} model…")
            self._log(f"Loading Whisper model: {model_size}")
            model = whisper_mod.load_model(model_size, device=device)
            self._log("Model loaded.")

            # Auto-detect language
            if lang == "auto":
                self._status("Detecting language…")
                self._log("Detecting source language from audio…")
                clip = whisper_mod.pad_or_trim(whisper_mod.load_audio(inp))
                mel  = whisper_mod.log_mel_spectrogram(
                           clip, n_mels=model.dims.n_mels).to(device)
                _, probs    = model.detect_language(mel)
                detected    = max(probs, key=probs.get)
                conf        = round(probs[detected]*100, 1)
                self._log(f"Detected language: {detected.upper()} (confidence: {conf}%)")
                transcribe_lang = detected
            else:
                transcribe_lang = lang
                self._log(f"Language set manually: {lang.upper()}")

            # Task info
            if task == "translate":
                self._log("Mode: Translate to English")
            else:
                self._log(f"Mode: Transcribe ({transcribe_lang.upper()})")

            # Transcribe
            self._status("Transcribing audio…")
            self._log("Processing audio. This may take a while for long files.")

            kwargs = dict(task=task, verbose=False, fp16=(device=="cuda"))
            if lang != "auto":
                kwargs["language"] = lang

            result = whisper_mod.transcribe(model, inp, **kwargs)
            segs   = result["segments"]
            self._log(f"Transcription complete: {len(segs)} segments.")

            # Save SRT
            base     = os.path.splitext(os.path.basename(inp))[0]
            suffix   = "_en" if task == "translate" else f"_{transcribe_lang}"
            srt_path = os.path.join(out_dir, f"{base}{suffix}.srt")
            self._save_srt(segs, srt_path)
            self._log(f"SRT saved: {srt_path}")

            # Optional burn-in
            if burn:
                self._status("Burning subtitles into video…")
                out_vid = os.path.join(out_dir, f"{base}_subtitled.mp4")
                self._burn(inp, srt_path, out_vid)

            # Success
            self._log("Processing finished.")
            self._log(f"Output: {srt_path}")
            self.after(0, lambda: messagebox.showinfo(
                "Complete", f"Subtitles generated successfully.\n\n{srt_path}"))
            self._done(True)

        except Exception as e:
            self._log(traceback.format_exc())
            self._log(f"ERROR: {e}\n{traceback.format_exc()}")
            self._done(False)

    # ── SRT helper ────────────────────────────────────────
    def _save_srt(self, segments, path):
        def fmt(s):
            h,m,sc,ms = int(s//3600), int((s%3600)//60), int(s%60), int((s%1)*1000)
            return f"{h:02}:{m:02}:{sc:02},{ms:03}"
        with open(path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segments, 1):
                f.write(f"{i}\n{fmt(seg['start'])} --> {fmt(seg['end'])}\n{seg['text'].strip()}\n\n")

    # ── Burn-in helper ────────────────────────────────────
    def _burn(self, video, srt, output):
        srt_esc = srt.replace("\\","/").replace(":","\\:")
        cmd = ["ffmpeg","-y","-i",video,
               "-vf",f"subtitles='{srt_esc}'",
               "-c:a","copy", output]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            self._log(f"FFmpeg error: {r.stderr[-400:]}")
        else:
            self._log(f"Burned video saved: {output}")


# ═════════════════════════════════════════════════════════════
#  Entry point
# ═════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = CaptionsForgeApp()
    app.mainloop()
