from tkinter import *
from tkinter import filedialog

class App:
    def __init__(self):
        self.imported = False

        self.root = Tk()
        self.root.title("Syncopated")
        self.root.geometry("800x600")

        self.import_button = Button(self.root, text="Import songs", command=self.importer)
        self.import_button.pack()

        self.root.mainloop()

    def song_list(self):
        self.songs_list = Listbox(self.root, width=self.root.winfo_width(), height=self.root.winfo_height())

        for self.idx, self.song in enumerate(self.imported):
            self.songs_list.insert(self.idx, self.song)
        
        self.songs_list.pack()

    def importer(self):
        self.dialog = filedialog.askopenfilenames(initialdir="~")
        self.imported = self.dialog
        print(self.imported)
        self.song_list()
App()