#!/usr/bin/env python3
"""
SimpleDesk - zero-dependency desktop app (Python + Tkinter)
Tabs: Notes, To-Do, Timer, Quick Files
Persistence: ./data/*.json (created automatically)
Run: python app.py
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json, time, threading
from pathlib import Path

APP_NAME = "SimpleDesk"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
NOTES_FILE = DATA_DIR / "notes.json"
TODO_FILE = DATA_DIR / "todos.json"

def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(path, data):
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        messagebox.showerror(APP_NAME, f"Kaydedilemedi:\n{e}")

class SimpleDesk(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_ui()

    def create_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # Notes Tab
        self.notes_text = tk.Text(nb, wrap="word", undo=True)
        nb.add(self.notes_text, text="📝 Notlar")
        self._load_notes()
        self.notes_text.bind("<<Modified>>", self._on_notes_modified)

        # To-Do Tab
        todo_frame = ttk.Frame(nb)
        nb.add(todo_frame, text="✅ Yapılacaklar")
        self.todo_items = load_json(TODO_FILE, [])
        self.todo_list = tk.Listbox(todo_frame, activestyle="dotbox")
        self.todo_list.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        self._refresh_todo_list()
        btns = ttk.Frame(todo_frame)
        btns.pack(side="right", fill="y", padx=4, pady=4)
        self.todo_entry = ttk.Entry(btns, width=24)
        self.todo_entry.pack(pady=(0,6))
        ttk.Button(btns, text="Ekle", command=self._todo_add).pack(fill="x")
        ttk.Button(btns, text="Tamamlandı", command=self._todo_done).pack(fill="x", pady=4)
        ttk.Button(btns, text="Sil", command=self._todo_delete).pack(fill="x")
        ttk.Button(btns, text="Dışa Aktar (txt)", command=self._todo_export).pack(fill="x", pady=(8,0))

        # Timer Tab (Pomodoro basic)
        timer_frame = ttk.Frame(nb)
        nb.add(timer_frame, text="⏱️ Zamanlayıcı")
        self.timer_label = ttk.Label(timer_frame, text="25:00", font=("Segoe UI", 28))
        self.timer_label.pack(pady=12)
        controls = ttk.Frame(timer_frame)
        controls.pack()
        self._timer_seconds = 25*60
        self._timer_running = False
        ttk.Button(controls, text="Başlat", command=self._timer_start).grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(controls, text="Duraklat", command=self._timer_pause).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(controls, text="Sıfırla", command=self._timer_reset).grid(row=0, column=2, padx=4, pady=4)
        ttk.Button(controls, text="25", command=lambda: self._timer_set(25)).grid(row=1, column=0, padx=4, pady=4)
        ttk.Button(controls, text="15", command=lambda: self._timer_set(15)).grid(row=1, column=1, padx=4, pady=4)
        ttk.Button(controls, text="5", command=lambda: self._timer_set(5)).grid(row=1, column=2, padx=4, pady=4)

        # Quick Files Tab
        files_frame = ttk.Frame(nb)
        nb.add(files_frame, text="📂 Hızlı Dosyalar")
        ttk.Label(files_frame, text="Hızlı açmak için dosya ekleyin. Listeye çift tıklayınca açılır.").pack(anchor="w", padx=8, pady=(8,4))
        self.files_list = tk.Listbox(files_frame)
        self.files_list.pack(fill="both", expand=True, padx=8, pady=(0,8))
        self.files_list.bind("<Double-Button-1>", self._open_selected_file)
        ff_btns = ttk.Frame(files_frame)
        ff_btns.pack(fill="x", padx=8, pady=(0,8))
        ttk.Button(ff_btns, text="Ekle", command=self._add_file).pack(side="left")
        ttk.Button(ff_btns, text="Listeden Sil", command=self._remove_file).pack(side="left", padx=6)
        self.quick_files = load_json(DATA_DIR / "quick_files.json", [])
        self._refresh_files()

        # Status bar
        self.status = ttk.Label(self, text="Hazır", anchor="w")
        self.status.pack(fill="x", side="bottom")

        # Menu
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Kaydet (Notlar)", command=self._save_notes)
        filemenu.add_separator()
        filemenu.add_command(label="Çıkış", command=self.master.destroy)
        menubar.add_cascade(label="Dosya", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Hakkında", command=self._about)
        menubar.add_cascade(label="Yardım", menu=helpmenu)

        self.master.config(menu=menubar)

    # Notes
    def _load_notes(self):
        note = load_json(NOTES_FILE, {"text": ""})
        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", note.get("text",""))
        self.notes_text.edit_modified(False)

    def _save_notes(self):
        text = self.notes_text.get("1.0", "end-1c")
        save_json(NOTES_FILE, {"text": text})
        self.status.config(text="Notlar kaydedildi.")

    def _on_notes_modified(self, event):
        if self.notes_text.edit_modified():
            # autosave after idle
            self.master.after(800, self._save_notes)
            self.notes_text.edit_modified(False)

    # To-Do
    def _refresh_todo_list(self):
        self.todo_list.delete(0, "end")
        for item in self.todo_items:
            mark = "✔ " if item.get("done") else "• "
            self.todo_list.insert("end", f"{mark}{item.get('text','')}")

    def _todo_add(self):
        txt = self.todo_entry.get().strip()
        if not txt:
            return
        self.todo_items.append({"text": txt, "done": False})
        save_json(TODO_FILE, self.todo_items)
        self.todo_entry.delete(0, "end")
        self._refresh_todo_list()

    def _todo_done(self):
        i = self.todo_list.curselection()
        if not i:
            return
        idx = i[0]
        self.todo_items[idx]["done"] = True
        save_json(TODO_FILE, self.todo_items)
        self._refresh_todo_list()

    def _todo_delete(self):
        i = self.todo_list.curselection()
        if not i:
            return
        idx = i[0]
        del self.todo_items[idx]
        save_json(TODO_FILE, self.todo_items)
        self._refresh_todo_list()

    def _todo_export(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt")], title="Dışa aktar")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            for item in self.todo_items:
                mark = "[x]" if item.get("done") else "[ ]"
                f.write(f"{mark} {item.get('text','')}\n")
        messagebox.showinfo(APP_NAME, "Txt olarak dışa aktarıldı.")

    # Timer
    def _timer_set(self, minutes):
        self._timer_seconds = int(minutes)*60
        self._update_timer_label()

    def _update_timer_label(self):
        m, s = divmod(self._timer_seconds, 60)
        self.timer_label.config(text=f\"{m:02d}:{s:02d}\")

    def _timer_start(self):
        if self._timer_running:
            return
        self._timer_running = True
        def tick():
            while self._timer_running and self._timer_seconds > 0:
                time.sleep(1)
                self._timer_seconds -= 1
                self.timer_label.after(0, self._update_timer_label)
            if self._timer_running and self._timer_seconds == 0:
                self._timer_running = False
                self.timer_label.after(0, lambda: messagebox.showinfo(APP_NAME, "Süre doldu!"))
        threading.Thread(target=tick, daemon=True).start()

    def _timer_pause(self):
        self._timer_running = False

    def _timer_reset(self):
        self._timer_running = False
        self._timer_seconds = 25*60
        self._update_timer_label()

    # Quick Files
    def _refresh_files(self):
        self.files_list.delete(0, "end")
        for p in self.quick_files:
            self.files_list.insert("end", p)

    def _add_file(self):
        path = filedialog.askopenfilename(title="Dosya ekle")
        if path:
            self.quick_files.append(path)
            save_json(DATA_DIR / "quick_files.json", self.quick_files)
            self._refresh_files()

    def _remove_file(self):
        i = self.files_list.curselection()
        if not i:
            return
        idx = i[0]
        del self.quick_files[idx]
        save_json(DATA_DIR / "quick_files.json", self.quick_files)
        self._refresh_files()

    def _open_selected_file(self, _event=None):
        i = self.files_list.curselection()
        if not i:
            return
        import os, subprocess, sys
        path = self.quick_files[i[0]]
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    def _about(self):
        messagebox.showinfo(APP_NAME, f"{APP_NAME}\nSıfır bağımlılık, hemen çalışır.\nPython + Tkinter")

def main():
    root = tk.Tk()
    root.title(APP_NAME)
    try:
        root.iconbitmap(default=str(Path(__file__).parent / "assets" / "icon.ico"))
    except Exception:
        pass
    # ttk theme
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    SimpleDesk(root)
    root.geometry("900x600")
    root.minsize(720, 480)
    root.mainloop()

if __name__ == "__main__":
    main()
