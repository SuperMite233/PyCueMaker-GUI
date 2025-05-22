import tkinter as tk
from tkinter import filedialog, messagebox
import os


class MusicEntry:
    def __init__(self, parent, index, remove_callback, move_callback):
        self.frame = tk.Frame(parent, bd=2, relief=tk.RIDGE, padx=5, pady=5)
        self.parent = parent
        self.index = index
        self.remove_callback = remove_callback
        self.move_callback = move_callback

        tk.Label(self.frame, text=f"音乐标题 {index + 1}:").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(self.frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(self.frame, text="作者:").grid(row=0, column=2, sticky="w")
        self.artist_entry = tk.Entry(self.frame, width=20)
        self.artist_entry.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(self.frame, text="音乐文件:").grid(row=1, column=0, sticky="w")
        self.file_entry = tk.Entry(self.frame, width=25)
        self.file_entry.grid(row=1, column=1, padx=5, pady=2)
        self.browse_btn = tk.Button(self.frame, text="浏览...", command=self.browse_file)
        self.browse_btn.grid(row=1, column=2, padx=5)

        self.remove_btn = tk.Button(self.frame, text="×", command=self.remove)
        self.remove_btn.grid(row=0, column=4, rowspan=2, padx=5, sticky="ns")

        self.frame.bind("<Button-1>", self.on_press)
        self.frame.bind("<B1-Motion>", self.on_drag)
        self.frame.bind("<ButtonRelease-1>", self.on_release)

        self.drag_start_y = 0
        self.dragging = False

    def browse_file(self):
        filepath = filedialog.askopenfilename(
            title="选择音乐文件",
            filetypes=[("音频文件", "*.mp3 *.wav *.flac *.ogg *.aac"), ("所有文件", "*.*")]
        )
        if filepath:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filepath)

    def remove(self):
        self.remove_callback(self.index)

    def on_press(self, event):
        self.drag_start_y = event.y_root
        self.dragging = False

    def on_drag(self, event):
        if not self.dragging and abs(event.y_root - self.drag_start_y) > 5:
            self.dragging = True
            self.frame.lift()
        if self.dragging:
            self.frame.place(y=event.y_root - self.drag_start_y + self.frame.winfo_y())

    def on_release(self, event):
        if self.dragging:
            self.dragging = False
            self.move_callback(self.index, event.y_root)
        self.frame.place_forget()

    def get_data(self):
        return {
            "title": self.title_entry.get(),
            "artist": self.artist_entry.get(),
            "file": self.file_entry.get()
        }


class CueGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("PYCueMaker")

        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.album_frame = tk.LabelFrame(self.main_frame, text="专辑信息", padx=5, pady=5)
        self.album_frame.pack(fill=tk.X, pady=5)

        tk.Label(self.album_frame, text="专辑名:").grid(row=0, column=0, sticky="w")
        self.album_title_entry = tk.Entry(self.album_frame, width=40)
        self.album_title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        tk.Label(self.album_frame, text="专辑作者:").grid(row=1, column=0, sticky="w")
        self.album_artist_entry = tk.Entry(self.album_frame, width=40)
        self.album_artist_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        self.entries_frame = tk.Frame(self.main_frame)
        self.entries_frame.pack(fill=tk.BOTH, expand=True)

        self.add_btn = tk.Button(self.main_frame, text="+ 添加音乐条目", command=self.add_entry)
        self.add_btn.pack(pady=5)

        self.generate_btn = tk.Button(self.main_frame, text="生成CUE文件", command=self.generate_cue)
        self.generate_btn.pack(pady=10)

        self.status_label = tk.Label(self.main_frame, text="", fg="green")
        self.status_label.pack()

        self.entries = []

        self.add_entry()

    def add_entry(self):
        index = len(self.entries)
        entry = MusicEntry(
            self.entries_frame,
            index,
            self.remove_entry,
            self.move_entry
        )
        entry.frame.pack(fill=tk.X, pady=5)
        self.entries.append(entry)
        self.update_indexes()

    def remove_entry(self, index):
        if len(self.entries) <= 1:
            self.status_label.config(text="至少需要保留一个条目", fg="red")
            return

        self.entries[index].frame.destroy()
        del self.entries[index]
        self.update_indexes()

    def move_entry(self, index, y_pos):
        for i, entry in enumerate(self.entries):
            entry_y = entry.frame.winfo_rooty()
            entry_height = entry.frame.winfo_height()

            if i != index and y_pos > entry_y and y_pos < entry_y + entry_height:
                if i < index:
                    self.entries.insert(i, self.entries.pop(index))
                else:
                    self.entries.insert(i + 1, self.entries.pop(index))

                for entry in self.entries:
                    entry.frame.pack_forget()
                for entry in self.entries:
                    entry.frame.pack(fill=tk.X, pady=5)

                self.update_indexes()
                break

    def update_indexes(self):
        for i, entry in enumerate(self.entries):
            entry.index = i
            entry.title_entry.config(textvariable=tk.StringVar(value=f"音乐标题 {i + 1}:"))

    def generate_cue(self):
        album_title = self.album_title_entry.get().strip()
        album_artist = self.album_artist_entry.get().strip()

        if not album_title:
            messagebox.showerror("错误", "请输入专辑名")
            return

        tracks = []
        for entry in self.entries:
            data = entry.get_data()
            if not data["title"] or not data["file"]:
                self.status_label.config(text="请填写所有条目的标题和文件路径", fg="red")
                return
            tracks.append(data)

        save_path = filedialog.asksaveasfilename(
            title="保存CUE文件",
            defaultextension=".cue",
            filetypes=[("CUE文件", "*.cue"), ("所有文件", "*.*")]
        )

        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(f'PERFORMER "{album_artist if album_artist else "Unknown"}"\n')
                f.write(f'TITLE "{album_title}"\n')

                for i, track in enumerate(tracks):
                    filename = os.path.basename(track["file"])
                    f.write(f'FILE "{filename}" WAVE\n')
                    f.write(f'  TRACK {i + 1:02d} AUDIO\n')
                    f.write(f'    TITLE "{track["title"]}"\n')
                    f.write(
                        f'    PERFORMER "{track["artist"] if track["artist"] else (album_artist if album_artist else "Unknown")}"\n')
                    f.write('    INDEX 01 00:00:00\n')

            self.status_label.config(text=f"CUE文件已成功生成: {save_path}", fg="green")
            messagebox.showinfo("成功", "CUE文件已成功生成！")
        except Exception as e:
            self.status_label.config(text=f"生成CUE文件时出错: {str(e)}", fg="red")
            messagebox.showerror("错误", f"生成CUE文件时出错:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x600")
    app = CueGeneratorApp(root)
    root.mainloop()