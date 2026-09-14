import tkinter as tk
from tkinter import ttk


class LiveMonitorGUI:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title("Abi Music Monitor")
        self.root.geometry("700x650")
        self.root.attributes("-topmost", True)
        self.root.update_idletasks()
        self.root.update()


        # =====================
        # Variablen
        # =====================

        self.slide_var = tk.StringVar(value="-")
        self.student_var = tk.StringVar(value="-")

        self.song_var = tk.StringVar(value="-")

        self.position_var = tk.StringVar(value="00:00")
        self.remaining_var = tk.StringVar(value="--")
        self.segment_var = tk.StringVar(value="-")

        self.next_slide_var = tk.StringVar(value="-")
        self.next_student_var = tk.StringVar(value="-")
        self.next_song_var = tk.StringVar(value="-")

        self.status_var = tk.StringVar(value="WAITING")

        

        # =====================
        # Titel
        # =====================

        ttk.Label(
            self.root,
            text="ABI CUT LIVE",
            font=("Arial",18,"bold")
        ).pack(pady=(15,5))

        # =====================
        # Status
        # =====================

        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial",14,"bold"),
            fg="orange"
        )

        self.status_label.pack()

        # =====================
        # PowerPoint Status
        # =====================

        self.powerpoint_status_frame = ttk.Frame(
            self.root
        )

        self.powerpoint_status_frame.pack(
            pady=(5, 5)
        )

        self.powerpoint_led = tk.Canvas(
            self.powerpoint_status_frame,
            width=16,
            height=16,
            highlightthickness=0
        )

        self.powerpoint_led.pack(
            side="left",
            padx=(0, 6)
        )

        self.powerpoint_led_circle = (
            self.powerpoint_led.create_oval(
                2,
                2,
                14,
                14,
                fill="red",
                outline=""
            )
        )

        self.powerpoint_status_var = tk.StringVar(
            value="PowerPoint: Nicht verbunden"
        )

        ttk.Label(
            self.powerpoint_status_frame,
            textvariable=self.powerpoint_status_var,
            font=("Arial", 10)
        ).pack(
            side="left"
        )

        # =====================
        # Hauptbereich
        # =====================

        main = ttk.Frame(
            self.root,
            padding=15
        )

        main.pack(
            fill="both",
            expand=True
        )

        # obere Zeile

        top = ttk.Frame(main)
        top.pack(fill="x", pady=(10,20))
 
        #Folie links
        slide_frame = ttk.LabelFrame(
            top,
            text="Folie"
        )

        slide_frame.pack(
            side="left",
            padx=(0,20)
        )

        ttk.Label(
            slide_frame,
            textvariable=self.slide_var,
            font=("Arial",30,"bold")
        ).pack(
            padx=25,
            pady=15
        )

        #Schüler rechts
        student_frame = ttk.LabelFrame(
            top,
            text="Schüler"
        )

        student_frame.pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Label(
            student_frame,
            textvariable=self.student_var,
            font=("Arial",20,"bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(15,5)
        )

        # Song
        song_frame = ttk.LabelFrame(
            main,
            text="Song"
        )

        song_frame.pack(
            fill="x",
            pady=(0,15)
        )

        ttk.Label(
            song_frame,
            textvariable=self.song_var,
            font=("Arial",12)
        ).pack(
            anchor="w",
            padx=15,
            pady=10
        )

        # Segment
        segment_frame = ttk.LabelFrame(
            main,
            text="Segment"
        )

        segment_frame.pack(
            fill="x",
            pady=(0,15)
        )

        ttk.Label(
            segment_frame,
            textvariable=self.segment_var,
            font=("Consolas",12)
        ).pack(
            anchor="center",
            pady=8
        )

        #Fortschritt
        self.progress = ttk.Progressbar(
            main,
            mode="determinate",
            length=380
        )

        self.progress.pack(
            pady=(15,5)
        )

        #Zeit
        bottom = ttk.Frame(main)

        bottom.pack(fill="x")

        #Mitte
        ttk.Label(
            bottom,
            textvariable=self.remaining_var,
            font=("Arial",11,"bold")
        ).pack()

        #Rechts
        self.status_canvas = tk.Canvas(
            bottom,
            width=36,
            height=36,
            highlightthickness=0
        )

        self.status_canvas.pack(side="right")
                        
        #Status LED
        self.led = self.status_canvas.create_oval(
            4,
            4,
            32,
            32,
            fill="orange"
        )

        #nächste Folie
        next_frame = ttk.LabelFrame(
            main,
            text="Nächste Folie",
            padding=12
        )

        next_frame.pack(
            fill="x",
            pady=(20,0)
        )

        #Info
        ttk.Label(
            next_frame,
            text="Folie:"
        ).grid(row=0,column=0,sticky="w")

        ttk.Label(
            next_frame,
            textvariable=self.next_slide_var,
            font=("Arial",11,"bold")
        ).grid(row=0,column=1,sticky="w",padx=10)



        ttk.Label(
            next_frame,
            text="Schüler:"
        ).grid(row=1,column=0,sticky="w")

        ttk.Label(
            next_frame,
            textvariable=self.next_student_var
        ).grid(row=1,column=1,sticky="w",padx=10)



        ttk.Label(
            next_frame,
            text="Song:"
        ).grid(row=2,column=0,sticky="w")

        ttk.Label(
            next_frame,
            textvariable=self.next_song_var
        ).grid(row=2,column=1,sticky="w",padx=10)


    def set_powerpoint_status(self, connected):

        try:

            if connected:

                self.powerpoint_led.itemconfig(
                    self.powerpoint_led_circle,
                    fill="limegreen"
                )

                self.powerpoint_status_var.set(
                    "PowerPoint: Verbunden"
                )

            else:

                self.powerpoint_led.itemconfig(
                    self.powerpoint_led_circle,
                    fill="red"
                )

                self.powerpoint_status_var.set(
                    "PowerPoint: Nicht verbunden"
                )

        except:
            pass


    def update_status(

    self,

    slide=None,
    student=None,
    next_slide=None,
    next_student=None,
    next_song=None,
    song=None,
    status=None,
    position=None,
    segment=None

):

        if slide is not None:
            self.slide_var.set(str(slide))

        if student is not None:
            self.student_var.set(student)

        if next_slide is not None:
            self.next_slide_var.set(str(next_slide))

        if next_student is not None:
            self.next_student_var.set(str(next_student))

        if next_song is not None:
            self.next_song_var.set(str(next_song))

        if song is not None:
            self.song_var.set(song)

        if position is not None:
            self.position_var.set(position)

        if segment is not None:
            self.segment_var.set(segment)

        if status is not None:

            self.status_var.set(status)

    def set_led(self, color):

        try:

            self.status_canvas.itemconfig(
                self.led,
                fill=color
            )

        except:
            pass
    # Alternative Methode, um die Farbe des Status-Labels zu ändern (Schriftfarbe)
    def set_status_color(self, color):

        self.status_label.config(
            fg=color
        )

    def set_progress(self, percent):

        try:

            self.progress["value"] = percent

        except:
            pass
        
    def set_remaining_time(self, seconds):

        try:

            self.remaining_var.set(
                f"{seconds}s"
            )

        except:
            pass
        
    def refresh(self):

        try:
            self.root.update_idletasks()
            self.root.update()

        except:
            pass

    def run(self):
        self.root.mainloop()