import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import yt_dlp
import threading
import os

class YouTubeDownloaderYTDLP:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader (yt-dlp)")
        self.root.geometry("500x360")
        self.url_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.format_var = tk.StringVar()
        self.available_formats = []

        # ----------- URL and "Paste" Button -----------
        frame_url = tk.Frame(root)
        frame_url.pack(pady=5)
        tk.Label(frame_url, text="YouTube URL:").grid(row=0, column=0, sticky="w")
        self.entry_url = tk.Entry(frame_url, textvariable=self.url_var, width=50)
        self.entry_url.grid(row=1, column=0, padx=5)

        # "Paste" button
        paste_btn = tk.Button(frame_url, text="Paste", command=self.paste_from_clipboard)
        paste_btn.grid(row=1, column=1)

        # ----------- Fetch Formats Button -----------
        tk.Button(root, text="Get Formats", command=self.fetch_formats).pack(pady=5)

        # ----------- Format Combobox -----------
        tk.Label(root, text="Select Format:").pack()
        self.format_combo = ttk.Combobox(root, textvariable=self.format_var, width=60, state='readonly')
        self.format_combo.pack(pady=5)

        # ----------- Select Save Path -----------
        tk.Button(root, text="Choose Save Folder", command=self.select_path).pack(pady=5)
        tk.Label(root, textvariable=self.path_var, fg="blue").pack()

        # ----------- Download Button -----------
        tk.Button(root, text="Download", command=self.start_download).pack(pady=10)

        # ----------- Progress Bar -----------
        self.progress = ttk.Progressbar(root, length=400, mode='indeterminate')
        self.progress.pack(pady=10)

    # Paste from clipboard
    def paste_from_clipboard(self):
        try:
            text = self.root.clipboard_get()
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(0, text)
        except tk.TclError:
            pass

    def fetch_formats(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('height')]

                self.available_formats = video_formats
                format_list = [
                    f"{f['format_id']} - {f.get('format_note', '')} - {f['ext']} - {f.get('resolution', str(f.get('height')) + 'p')}"
                    for f in video_formats
                ]

                self.format_combo['values'] = format_list
                if format_list:
                    self.format_var.set(format_list[0])
                else:
                    messagebox.showwarning("No Formats Found", "No suitable video formats found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch formats:\n{e}")

    def select_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def start_download(self):
        threading.Thread(target=self.download_video).start()

    def download_video(self):
        url = self.url_var.get().strip()
        path = self.path_var.get().strip()
        format_string = self.format_var.get()

        if not url or not path or not format_string:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        format_id = format_string.split(" - ")[0]

        ydl_opts = {
            'format': f"{format_id}+bestaudio/best",
            'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'progress_hooks': [self.yt_progress_hook],
            'quiet': True,
        }

        self.progress.start()
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.progress.stop()
            messagebox.showinfo("Success", "Video downloaded successfully!")
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Download Error", str(e))

    def yt_progress_hook(self, d):
        if d['status'] == 'finished':
            self.progress.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderYTDLP(root)
    root.mainloop()
