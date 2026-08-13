import win32com.client


class PowerPointController:

    def __init__(self):

        self.ppt = win32com.client.Dispatch("PowerPoint.Application")
        self.presentation = self.ppt.ActivePresentation

    def get_current_slide(self):

        if self.ppt.SlideShowWindows.Count == 0:
            return None

        slideshow = self.ppt.SlideShowWindows(1).View

        return slideshow.CurrentShowPosition