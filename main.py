from customtkinter import *
import CTkListbox as l
from tkfilebrowser import askopenfilenames
from mutagen import *


class App:
    def __init__(self):
        self.imported = False
        self.list_pack = False

        self.root = CTk()
        self.root.title("Syncopated")
        self.root.geometry("800x600")

        self.root.update_idletasks()

        # menu

        self.menu_frame = CTkFrame(self.root)
        self.menu_frame.place(relx=0, rely=0, relwidth=1, relheight=0.05)

        self.import_button = CTkButton(self.menu_frame, text="Import", command=self.importer)
        self.import_button.pack(side=LEFT, fill=Y)

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

    def song_list(self):
            # self.songs_list = l.CTkListbox(self.root, width=self.root.winfo_width() // 2, height=self.root.winfo_height() - self.menu.winfo_height())
        self.songs_data = []

        for self.idx, self.file in enumerate(self.imported):
            self.audio = File(self.file, easy=True)

            self.title = self.audio.get("title", ["Unknown"])[0]
            self.artist = self.audio.get("artist", ["Unknown"])[0]
        
            self.raw = File(self.file)
            self.cover = None
            for self.tag in self.raw.tags.values():
                if hasattr(self.tag, "data") and hasattr(self.tag, "mime"):
                    self.cover = self.tag.data
                    break

            self.songs_data.append((self.title, self.artist, self.cover))

            print(self.songs_data[self.idx][2])

        for i in range(len(self.songs_data)):
            self.songs_list.insert(len(self.songs_data)+i, f"{self.songs_data[i-1][0]} - {self.songs_data[i-1][1]}", )

    

    def importer(self):
        self.dialog = filedialog.askopenfilenames(initialdir="~")
        self.imported = self.dialog
        if self.imported:
            self.song_list()
        return
App()