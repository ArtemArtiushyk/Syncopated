from tkinter import *
from tkinter import filedialog, messagebox
from mutagen import File
import vlc
import json
import os

SAVE_FILE = "songs_data.json"

SUPPORTED = (
    ("Audio Files", "*.mp3 *.flac *.wav *.ogg *.aac *.m4a *.wma *.aiff *.ape *.opus"),
    ("MP3",         "*.mp3"),
    ("FLAC",        "*.flac"),
    ("WAV",         "*.wav"),
    ("OGG",         "*.ogg"),
    ("AAC",         "*.aac"),
    ("M4A",         "*.m4a"),
    ("WMA",         "*.wma"),
    ("AIFF",        "*.aiff"),
    ("APE",         "*.ape"),
    ("OPUS",        "*.opus"),
    ("All Files",   "*.*"),
)


class App:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.imported   = []
        self.songs_data = []
        self.list_pack  = False
        self.current_index = None

        self.root = Tk()
        self.root.title("Syncopated")
        self.root.geometry("800x600")
        self.root.update_idletasks()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # menu
        self.menu_frame = Frame(self.root)
        self.menu_frame.place(relx=0, rely=0, relwidth=1, relheight=0.05)

        self.import_button = Button(self.menu_frame, text="Import", command=self.importer)
        self.import_button.pack(side=LEFT, fill=Y)

        self.play_selected_button = Button(self.menu_frame, text="Play Selected", command=self.play_selected)
        self.play_selected_button.pack(side=LEFT, fill=Y)

        self.clear_button = Button(self.menu_frame, text="Clear List", command=self.clear_list)
        self.clear_button.pack(side=LEFT, fill=Y)

        # song list
        self.songs_list = Listbox(self.root, selectmode=SINGLE)
        self.songs_list.place(relx=0, rely=0.05, relwidth=0.5, relheight=0.9)
        self.songs_list.bind("<Double-Button-1>", lambda e: self.play_selected())
        self.list_pack = True

        # player panel
        self.player_frame = Frame(self.root)
        self.player_frame.place(relx=0.5, rely=0.05, relwidth=0.5, relheight=0.9)

        self.song_player_title = Label(self.player_frame, text="No song selected", font=("Arial", 12), wraplength=380, justify=CENTER)
        self.song_player_title.place(relx=0, rely=0.45, relwidth=1, relheight=0.05)

        self.song_player_artist = Label(self.player_frame, text="", font=("Arial", 12))
        self.song_player_artist.place(relx=0, rely=0.5, relwidth=1, relheight=0.05)

        # playback controls
        self.play_menu_frame = Frame(self.root)
        self.play_menu_frame.place(relx=0, rely=0.95, relwidth=1, relheight=0.05)

        self.back_button = Button(self.play_menu_frame, text="⏮", command=self.play_prev)
        self.back_button.place(relx=0.35, rely=0, relwidth=0.1, relheight=1)

        self.play_button = Button(self.play_menu_frame, text="▶", command=self.toggle_play)
        self.play_button.place(relx=0.45, rely=0, relwidth=0.1, relheight=1)

        self.forward_button = Button(self.play_menu_frame, text="⏭", command=self.play_next)
        self.forward_button.place(relx=0.55, rely=0, relwidth=0.1, relheight=1)

        # load saved songs
        self.load_songs()

        # play next list on end

        self.player.event_manager().event_attach(
            vlc.EventType.MediaPlayerEndReached, self.on_end
        )

        self.root.mainloop()

    # persistence
    def save_songs(self):
        data = [{"title": t, "artist": a, "path": p} for t, a, p in self.songs_data]
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            print(f"Could not save song list: {e}")

    def load_songs(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, encoding="utf-8") as f:
                saved = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Could not load song list: {e}")
            return

        missing = 0
        for entry in saved:
            path = entry.get("path", "")
            if not os.path.exists(path):
                missing += 1
                continue
            title  = entry.get("title",  "Unknown")
            artist = entry.get("artist", "Unknown")
            self.songs_data.append((title, artist, path))
            self.songs_list.insert(END, f"{len(self.songs_data)}. {title} - {artist}")

        if missing:
            print(f"{missing} saved file(s) could not be found and were skipped.")

    def on_close(self):
        self.player.stop()
        self.save_songs()
        self.root.destroy()

    # import
    def importer(self):
        paths = filedialog.askopenfilenames(initialdir="~", filetypes=SUPPORTED)
        if not paths:
            return

        existing_paths = {p for _, _, p in self.songs_data}
        new_paths = [p for p in paths if p not in existing_paths]

        if not new_paths:
            messagebox.showinfo("Import", "All selected files are already in the list.")
            return

        self.song_list(new_paths)

    def song_list(self, files):
        for file in files:
            try:
                audio = File(file, easy=True)
                if audio is None:
                    print(f"Unsupported or unreadable file: {file}")
                    continue
                title  = audio.get("title",  [os.path.splitext(os.path.basename(file))[0]])[0]
                artist = audio.get("artist", ["Unknown"])[0]
            except Exception as e:
                print(f"Error reading {file}: {e}")
                title  = os.path.splitext(os.path.basename(file))[0]
                artist = "Unknown"

            self.songs_data.append((title, artist, file))
            self.songs_list.insert(END, f"{len(self.songs_data)}. {title} - {artist}")

    # ── playback ─────────────────────────────────────────────────────────────
    def play_index(self, index):
        if index < 0 or index >= len(self.songs_data):
            return
        title, artist, path = self.songs_data[index]

        if not os.path.exists(path):
            messagebox.showerror("File not found", f"Cannot find:\n{path}")
            return

        self.current_index = index
        
        media = self.instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        self.play_button.config(text="⏸")

        self.song_player_title.config(text=title)
        self.song_player_artist.config(text=artist)

        self.songs_list.selection_clear(0, END)
        self.songs_list.selection_set(index)
        self.songs_list.see(index)

    def play_selected(self):
        selection = self.songs_list.curselection()
        if not selection:
            return
        self.play_index(selection[0])

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_button.config(text="▶")
        else:
            if self.current_index is None:
                if self.songs_data:
                    self.play_index(0)
            else:
                self.player.play()
                self.play_button.config(text="⏸")

    def play_next(self):
        if not self.songs_data:
            return
        next_index = 0 if self.current_index is None else (self.current_index + 1) % len(self.songs_data)
        self.play_index(next_index)

    def on_end(self, event):
        self.root.after(0, self.play_next)

    def play_prev(self):
        if not self.songs_data:
            return
        prev_index = 0 if self.current_index is None else (self.current_index - 1) % len(self.songs_data)
        self.play_index(prev_index)

    # ── list management ──────────────────────────────────────────────────────
    def clear_list(self):
        if not messagebox.askyesno("Clear List", "Remove all songs from the list?"):
            return
        self.player.stop()
        self.play_button.config(text="▶")
        self.songs_data.clear()
        self.songs_list.delete(0, END)
        self.current_index = None
        self.song_player_title.config(text="No song selected")
        self.song_player_artist.config(text="")


App()