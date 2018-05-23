from PyQt5.QtWidgets import QMenu

class Spell:
    def __init__(self, entry, idx):
        self.entry = entry
        self.index = idx
        s = ""
        for attr in entry:
            if attr.tag == "text":
                if attr.text is None:
                    s = s + "<br>"
                else:
                    s = s + attr.text
            else:
                setattr(self, attr.tag, attr.text)
        self.text = s

    def __str__(self):
        return self.name

