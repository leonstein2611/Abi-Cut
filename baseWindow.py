class BaseWindow:

    def __init__(self):
        self.result = None

    def show(self):
        self.root.mainloop()
        return self.result

    def close(self, result=None):

        self.result = result

        if self.root:
            self.root.quit()
            self.root.destroy()