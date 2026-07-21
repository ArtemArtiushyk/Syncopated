from tkinter import *
from tkinter import filedialog, messagebox
from mutagen import File
import vlc
import json
import os

SAVE_FILE = "songs_data.json"

CONFIG_FILE = "config.json"

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

        self.config = []

        self.imported   = []
        self.songs_data = []
        self.list_pack  = False
        self.current_index = None

        self.load_config()

        self.root = Tk()
        self.root.title("Syncopated")
        self.root.geometry("800x600")
        self.root.update_idletasks()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.theme = StringVar(value=self.config[0])
        self.volume = IntVar(value=self.config[1])

        # menu
        self.menu_frame = Frame(self.root)
        self.menu_frame.place(relx=0, rely=0, relwidth=1, relheight=0.05)

        self.import_button = Button(self.menu_frame, text="Import", command=self.importer)
        self.import_button.place(relx=0, rely=0, relwidth=0.1, relheight=1)

        self.play_selected_button = Button(self.menu_frame, text="Play Selected", command=self.play_selected)
        self.play_selected_button.place(relx=0.1, rely=0, relwidth=0.1, relheight=1)

        self.clear_button = Button(self.menu_frame, text="Clear List", command=self.clear_list)
        self.clear_button.place(relx=0.2, rely=0, relwidth=0.1, relheight=1)

        self.config_button = Button(self.menu_frame, text="Config", command=self.config_menu)
        self.config_button.place(relx=0.9, rely=0, relwidth=0.1, relheight=1)

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

        self.root.bind("<space>", lambda e: self.toggle_play())

        self.forward_button = Button(self.play_menu_frame, text="⏭", command=self.play_next)
        self.forward_button.place(relx=0.55, rely=0, relwidth=0.1, relheight=1)

        self.volume_scale = Scale(self.play_menu_frame, variable=self.volume, from_=0, to=100, cursor="hand1", orient=HORIZONTAL, command=self.change_volume)
        self.volume_scale.place(relx=0.8, rely=0, relwidth=0.2, relheight=1)
        # load saved songs
        self.load_songs()

        # play next list on end
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.on_end)

        self.root.mainloop()

    def change_volume(self, value):
        self.player.audio_set_volume(int(value))
        self.config[1] = value
        print(self.config[1])

    def apply_config(self):
        self.

    def save_config(self):
        config = {"theme": self.config[0], "volume": self.config[1], "delay": self.config[2]}
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        
        except OSError as e:
            print(f"Could not save config: {e}")


    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            self.config.append("light")
            self.config.append("100")
            self.config.append(1000)
            return
        
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                config = json.load(f)

                theme = config.get("theme", "dark")
                volume = config.get("volume", "100")
                delay = config.get("delay", 1000)

            self.config.append(theme)
            self.config.append(volume)
            self.config.append(delay)

        except (OSError, json.JSONDecodeError) as e:
            print(f"Could not load config: {e}")
            return

    def config_menu(self):
        if not hasattr(self, "config_window") or not self.config_window.winfo_exists():
            self.config_window = Toplevel(self.root)
            self.config_window.geometry("400x300")
            self.config_window.update_idletasks()
            self.config_window.protocol("WM_DELETE_WINDOW", self.config_close)

            self.head1 = Label(self.config_window, text="Configuration menu", font=("Arial", 24), justify=CENTER)
            self.head1.place(relx=0, rely=0, relwidth=1, relheight=0.1)

            self.visual_p = Label(self.config_window, text="Visual", font=("Arial", 16), justify=LEFT)
            self.visual_p.place(x=1, rely=0.1, relwidth=1, relheight=0.05)

            self.theme_p = Label(self.config_window, text="Theme", font=("Arial", 12), justify=CENTER)
            self.theme_p.place(x=1, rely=0.15, relheight=0.05)

            self.theme_rb1 = Radiobutton(self.config_window, text="Light", variable=self.theme, value="light")
            self.theme_rb1.place(x=1, rely=0.2, relheight=0.05)

            self.theme_rb2 = Radiobutton(self.config_window, text="Dark", variable=self.theme, value="dark")
            self.theme_rb2.place(x=100, rely=0.2, relheight=0.05)

            self.delay_p = Label(self.config_window, text="")

        else:
            self.config_window.lift()

    def config_close(self):
        on_close_message = messagebox.askyesnocancel("Save", "Save changes to the configuration?")
        print(on_close_message)

        if on_close_message is None:
            return
        
        elif on_close_message is True:
            self.apply_config()

        self.config_window.destroy()

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
        self.save_config()
        self.root.destroy()

    # import
    def importer(self):
        paths = filedialog.askopenfilenames(initialdir="~/Music", filetypes=SUPPORTED)
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

    def on_end(self, event, _delay=1000):
        self.root.after(_delay, self.play_next)

    def play_prev(self):
        if not self.songs_data:
            return
        
        prev_index = 0 if self.current_index is None else (self.current_index - 1) % len(self.songs_data)
        self.play_index(prev_index)

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