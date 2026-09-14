import win32com.client
import pywintypes


class PowerPointController:

    def __init__(self):

        self.ppt = None
        self.presentation = None

        self.connect()


    def connect(self):

        try:

            self.ppt = win32com.client.Dispatch(
                "PowerPoint.Application"
            )

            try:

                self.presentation = (
                    self.ppt.ActivePresentation
                )

                return True

            except pywintypes.com_error:

                self.presentation = None
                return False

        except Exception:

            self.ppt = None
            self.presentation = None

            return False
    
    import pywintypes


    def get_current_slide(self):

        if self.presentation is None:
            return None

        try:

            if self.ppt.SlideShowWindows.Count > 0:

                window = self.ppt.SlideShowWindows(1)

                return window.View.CurrentShowPosition

            return None

        except pywintypes.com_error:
            return None

        except Exception:
            return None