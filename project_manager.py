import os
import json
import datetime
import tkinter as tk
from tkinter import ttk

import shutil

from tkinter import messagebox
from tkinter import simpledialog

from project_controller import set_current_project
from project_controller import get_current_project
from project_controller import clear_current_project

from baseWindow import BaseWindow


class ProjectManager(BaseWindow):

    def __init__(self):

        super().__init__()

        self.root = tk.Tk()

        self.root.title("Projektmanager")
        self.root.geometry("820x520")

        # Verhalten beim Schließen des Fensters
        self.root.protocol(
            "WM_DELETE_WINDOW",
            lambda: self.close("menu")
        )

        self.project_paths = []

        self.create_widgets()
        self.load_projects()


    def create_widgets(self):

        ttk.Label(

            self.root,

            text="Projektmanager",

            font=("Arial",18,"bold")

        ).pack(pady=15)

        frame = ttk.Frame(self.root)

        frame.pack(fill="both", expand=True, padx=20, pady=15)

        self.project_list = tk.Listbox(

            frame,

            width=40,

            height=20

        )

        self.project_list.pack(

            side="left",

            fill="y"

        )

        self.info_frame = ttk.LabelFrame(
            frame,
            text="Projektinformationen",
            padding=15
        )

        self.info_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(20, 0)
        )

        self.menu = tk.Menu(
            self.root,
            tearoff=False
        )

        self.menu.add_command(
            label="📂 Projekt öffnen",
            command=self.open_project
        )

        self.menu.add_command(
            label="▶ Live starten",
            command=self.live_project
        )

        self.menu.add_separator()

        self.menu.add_command(
            label="✏ Umbenennen",
            command=self.rename_project
        )

        self.menu.add_command(
            label="📄 Duplizieren",
            command=self.duplicate_project
        )

        self.menu.add_command(
            label="🗑 Löschen",
            command=self.delete_project
        )

        self.project_list.bind(
            "<Button-3>",
            self.show_context_menu
        )

        self.project_list.bind(

            "<Double-Button-1>",

            lambda e: self.open_project()

        )

        self.project_list.bind(
            "<<ListboxSelect>>",
            lambda e: self.update_project_info()
        )

        scroll = ttk.Scrollbar(

            frame,

            orient="vertical",

            command=self.project_list.yview

        )

        scroll.pack(side="left", fill="y")

        self.project_list.configure(

            yscrollcommand=scroll.set

        )

    def load_projects(self):

        self.project_list.delete(0, tk.END)

        self.project_paths.clear()

        if not os.path.exists("projects"):
            return

        for folder in sorted(os.listdir("projects")):

            config = os.path.join(
                "projects",
                folder,
                "config.json"
            )

            if os.path.exists(config):

                self.project_paths.append(config)

                self.project_list.insert(
                    tk.END,
                    f"🎓 {folder}"
                )

        if self.project_list.size() > 0:

            self.project_list.selection_set(0)

            self.update_project_info()

    def show_context_menu(self, event):

        index = self.project_list.nearest(event.y)

        self.project_list.selection_clear(0, tk.END)

        self.project_list.selection_set(index)

        self.menu.post(
            event.x_root,
            event.y_root
        )

    def open_project(self):

        selection = self.project_list.curselection()

        if not selection:
            return

        path = self.project_paths[selection[0]]

        set_current_project(path)

        self.close(("editor", path))

    def live_project(self):

        selection = self.project_list.curselection()

        if not selection:
            return

        path = self.project_paths[selection[0]]

        set_current_project(path)

        self.close(("live", path))

    def rename_project(self):

        selection = self.project_list.curselection()

        if not selection:
            return

        old_path = self.project_paths[selection[0]]

        old_folder = os.path.dirname(old_path)

        if not os.path.exists(old_folder):

            messagebox.showerror(

                "AbiCut",

                "Das Projekt existiert nicht mehr."

            )

            self.load_projects()

            return

        old_name = os.path.basename(old_folder)

        new_name = simpledialog.askstring(

            "Projekt umbenennen",

            "Neuer Projektname:",

            initialvalue=old_name,

            parent=self.root

        )

        if not new_name:
            return

        new_folder = os.path.join(

            "projects",

            new_name

        )

        os.rename(

            old_folder,

            new_folder

        )

        config_path = os.path.join(
            new_folder,
            "config.json"
            )

        current = get_current_project()
                
        if current == old_path:
                
            set_current_project(config_path)

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        config["project"]["name"] = new_name

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(
                config,
                f,
                indent=4,
                ensure_ascii=False
            )

        self.load_projects()
        self.update_project_info()
        

    def duplicate_project(self):

        selection = self.project_list.curselection()

        if not selection:
            return

        source = os.path.dirname(
            self.project_paths[selection[0]]
        )

        name = os.path.basename(source)

        target = os.path.join(

            "projects",

            name + " (Kopie)"

        )

        counter = 2

        while os.path.exists(target):

            target = os.path.join(

                "projects",

                f"{name} (Kopie){counter}"

            )

            counter += 1

        shutil.copytree(

            source,

            target

        )

        config_path = os.path.join(
            target,
            "config.json"
        )

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        config["project"]["created"] = datetime.datetime.now().strftime("%d.%m.%Y")

        config["project"]["name"] = os.path.basename(target)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(
                config,
                f,
                indent=4,
                ensure_ascii=False
            )

        self.load_projects()

        self.project_list.selection_clear(0, tk.END)

        last = self.project_list.size()-1

        self.project_list.selection_set(last)

        self.update_project_info()

    def delete_project(self):

        selection = self.project_list.curselection()

        if not selection:
            return

        path = self.project_paths[selection[0]]

        answer = messagebox.askyesno(
            "Projekt löschen",
            "Projekt wirklich löschen?"
        )

        if not answer:
            return

        current = get_current_project()

        if current == path:
            clear_current_project()

        folder = os.path.dirname(path)

        shutil.rmtree(folder)

        self.load_projects()

        self.update_project_info()

       
        
    def update_project_info(self):

        for widget in self.info_frame.winfo_children():
            widget.destroy()

        selection = self.project_list.curselection()

        if not selection:

            ttk.Label(
                self.info_frame,
                text="Kein Projekt ausgewählt."
            ).pack()

            return

        path = self.project_paths[selection[0]]

        from project_statistics import load_project_statistics

        stats = load_project_statistics(path)

        if not stats:
            return

        progress = stats["progress"]

        from project_statistics import create_progress_bar

        bar = create_progress_bar(progress)

        text = (

            f"🎓 {stats['project_name']}\n\n"

            f"Fortschritt\n"

            f"{bar}   {progress}%\n\n"

            f"👨‍🎓 Schüler:      {stats['total']}\n"

            f"🎵 Songs:         {stats['songs']}\n"

            f"✅ Bestätigt:     {stats['confirmed']}\n\n"

            f"Erstellt: {stats['created']}"

        )

        ttk.Label(

            self.info_frame,

            text=text,

            justify="left",

            font=("Consolas", 10)

        ).pack(anchor="w")

        ttk.Separator(
            self.info_frame,
            orient="horizontal"
        ).pack(
            fill="x",
            pady=15
        )

        button_frame = ttk.Frame(self.info_frame)
        button_frame.pack(
            anchor="w",
            pady=(20,0)
        )
    
        ttk.Button(
            button_frame,
            text="📂 Projekt öffnen",
            width=22,
            command=self.open_project
        ).pack()
    
        ttk.Button(
            button_frame,
            text="▶ Live starten",
            width=22,
            command=self.live_project
        ).pack(pady=(8,0))

if __name__ == "__main__":
    manager = ProjectManager()
    manager.show()