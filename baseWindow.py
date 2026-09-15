import tkinter as tk

from paths import get_app_icon_png


class BaseWindow:

    def __init__(self):
        self.result = None
        self.app_icon = None

    def show(self):
        self.root.mainloop()
        return self.result

    def close(self, result=None):

        self.result = result

        if self.root:
            self.root.quit()
            self.root.destroy()

    def set_app_icon(self):

        try:

            icon_path = get_app_icon_png()

            if icon_path.exists():

                self.app_icon = tk.PhotoImage(
                    file=str(icon_path)
                )

                self.root.iconphoto(
                    True,
                    self.app_icon
                )

        except Exception as e:
            print("App Icon konnte nicht gesetzt werden:", e)