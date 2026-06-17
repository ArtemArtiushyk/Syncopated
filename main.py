from customtkinter import *
import CTkListbox as l
from tkfilebrowser import askopenfilenames
from mutagen import *
import vlc

class App:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        
        self.imported = False
        self.list_pack = False

        self.songs_data = []

        self.root = CTk()
        self.root.title("Syncopated")
        self.root.geometry("800x600")

        self.root.update_idletasks()

        # menu

        self.menu_frame = CTkFrame(self.root)
        self.menu_frame.place(relx=0, rely=0, relwidth=1, relheight=0.05)

        self.import_button = CTkButton(self.menu_frame, text="Import", command=self.importer)
        self.import_button.pack(side=LEFT, fill=Y)

        self.play_selected_button = CTkButton(self.menu_frame, text="Play Selected", command=self.play_selected)
        self.play_selected_button.pack(side=LEFT, fill=Y)

        # list

        if not self.list_pack:
            self.songs_list = l.CTkListbox(self.root)
            self.songs_list.place(relx=0, rely=0.05, relwidth=0.5, relheight=0.9)
            self.list_pack = True

        # player

        self.player_frame = CTkFrame(self.root)
        self.player_frame.place(relx=0.5, rely=0.05, relwidth=0.5, relheight=0.9)

        self.song_player_title = CTkLabel(self.player_frame, text="Title", font=("Ariel", 24))
        self.song_player_title.place(relx=0, rely=0.5, relwidth=1, relheight=0.03)

        self.song_player_artist = CTkLabel(self.player_frame, text="Artist", font=("Ariel", 12))
        self.song_player_artist.place(relx=0, rely=0.53, relwidth=1, relheight=0.02)

        # play menu

        self.play_menu_frame = CTkFrame(self.root)
        self.play_menu_frame.place(relx=0, rely=0.95, relwidth=1, relheight=0.05)

        self.back_button = CTkButton(self.play_menu_frame, text="⏮️")
        self.back_button.place(relx=0.35, rely=0, relwidth=0.1, relheight=1)

        self.play_button = CTkButton(self.play_menu_frame, text="▶️") #, width=int(self.root.winfo_width() * 0.5)
        # self.import_button.pack(side=LEFT, fill=Y)
        self.play_button.place(relx=0.45, rely=0, relwidth=0.1, relheight=1)

        self.forward_button = CTkButton(self.play_menu_frame, text="⏭️")
        self.forward_button.place(relx=0.55, rely=0, relwidth=0.1, relheight=1)

        self.root.mainloop()

    def play_selected(self):
        self.selected = self.songs_list.curselection()
        if self.selected:
            self.index = self.selected[0]
            self.path = self.songs_data[self.index][3]
            self.media = self.instance.media_new(self.path)
            self.player.set_media(self.media)
            self.player.play()

    def song_list(self):
        for self.idx, self.file in enumerate(self.imported):
            self.audio = File(self.file, easy=True)

            print(self.audio)

            self.title  = self.audio.get("title",  ["Unknown"])[0]
            self.artist = self.audio.get("artist", ["Unknown"])[0]

            # Cover fetching
            self.raw = File(self.file)
            self.cover = False
            for self.tag in self.raw.tags.values():
                if hasattr(self.tag, "data") and hasattr(self.tag, "mime"):
                    self.cover = self.tag.data
                    break
            if self.cover is False and hasattr(self.raw, "pictures") and self.raw.pictures:
                self.cover = self.raw.pictures[0].data
            if self.cover is False and "covr" in self.raw:
                self.cover = bytes(self.raw["covr"][0])

            self.songs_data.append((self.audio, self.title, self.artist, self.file))
        
            self.songs_list.insert(END, f"{len(self.songs_data)}. {self.title} - {self.artist}")

    def importer(self):
        self.dialog = filedialog.askopenfilenames(initialdir="~")
        self.imported = self.dialog
        if self.imported:
            self.song_list()
        return
App()