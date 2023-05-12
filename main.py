import json
import os
import csv
from tkinter import Tk, Label, Button, filedialog, Entry, StringVar

class SpotifyAnalyzer:
    def __init__(self, master):
        self.master = master
        master.title("Spotify Analyzer")
        self.top_5_labels = []
        self.select_folder_button = Button(master, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        self.process_json_files(folder_path)

    def process_json_files(self, folder_path):
        self.data = {}
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                self.process_json_file(file_path)
        self.display_top_5()

    def process_json_file(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            if "ms_played" in item:
                track_name = item.get("master_metadata_track_name")
                artist_name = item.get("master_metadata_album_artist_name")
                time_played = item.get("ms_played")
                if track_name and artist_name and time_played:
                    if (track_name, artist_name) in self.data:
                        self.data[(track_name, artist_name)] += time_played
                    else:
                        self.data[(track_name, artist_name)] = time_played

    def display_top_5(self):
        for label in self.top_5_labels:
            label.pack_forget()
        self.top_5_labels = []
        top_5 = sorted(self.data.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (track, time_played) in enumerate(top_5):
            track_name, artist_name = track
            label_text = f"{i + 1}. {track_name} - {artist_name}: {round((time_played / 1000))} minutes played"
            label = Label(self.master, text=label_text)
            label.pack()
            self.top_5_labels.append(label)

        date_label = Label(self.master, text="Enter a date (MM/DD/YYYY):")
        date_label.pack()

        self.month_entry = Entry(self.master, width=3)
        self.day_entry = Entry(self.master, width=3)
        self.year_entry = Entry(self.master, width=5)
        self.month_entry.pack(side="left")
        Label(self.master, text="/").pack(side="left")
        self.day_entry.pack(side="left")
        Label(self.master, text="/").pack(side="left")
        self.year_entry.pack(side="left")

        vcmd = self.master.register(self.validate_date)
        self.month_entry.config(validate="key", validatecommand=(vcmd, '%S'))
        self.day_entry.config(validate="key", validatecommand=(vcmd, '%S'))
        self.year_entry.config(validate="key", validatecommand=(vcmd, '%S'))

        save_button = Button(self.master, text="Save to CSV", command=self.save_to_csv)
        save_button.pack(pady=10)
        save_button.pack(side="bottom")

        date_label.pack(pady=10)
        date_label.pack(side="top")
        self.month_entry.pack(padx=10)
        self.day_entry.pack(padx=10)
        self.year_entry.pack(padx=10)
        self.month_entry.pack_configure(side="left")
        self.day_entry.pack_configure(side="left")
        self.year_entry.pack_configure(side="left")
    def validate_date(self, char):
        return char.isdigit()

    def save_to_csv(self):
        month = self.month_entry.get()
        day = self.day_entry.get()
        year = self.year_entry.get()
        date = f"{month}/{day}/{year}"

        top_5 = sorted(self.data.items(), key=lambda x: x[1], reverse=True)[:5]
        track_dict = {}
        for i, (track, time_played) in enumerate(top_5):
            track_name, artist_name = track
            minutes_played = round((time_played / 1000))
            track_dict[f"Track {i + 1}"] = [track_name, artist_name, minutes_played]

        filename = "top5.csv"
        is_empty = os.stat(filename).st_size == 0 if os.path.exists(filename) else True
        with open(filename, "a", newline="") as f:
            writer = csv.writer(f)

            if is_empty:
                writer.writerow(["Date"] + list(track_dict.keys()))

            writer.writerow([date] + [f"{v[0]} - {v[1]} - {v[2]} mins" for v in track_dict.values()])

root = Tk()
app = SpotifyAnalyzer(root)
root.mainloop()