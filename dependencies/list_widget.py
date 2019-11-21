from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QScrollArea, \
    QWidget, QFormLayout, QGroupBox
from PyQt5.QtCore import Qt

colorDict = dict(
    white=[240, 240, 240],
    green=[0, 240, 0],
    red=[240, 0x00, 0x00],
    blue=[0x00, 0x00, 240],
)


class EntryWidget(QFrame):
    def __init__(self):
        super().__init__()
        # self.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.setFrameShape(QFrame.Box)

    def redraw(self):
        self.setStyle(self.style())


class ListWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        scrollLayout = QVBoxLayout()
        self.scroll_frame = QWidget()
        self.scroll_frame.setContentsMargins(0, 0, 0, 0)
        self.scroll_frame.setLayout(scrollLayout)
        scroll = QScrollArea()
        scroll.setWidget(self.scroll_frame)
        scroll.setWidgetResizable(True)

        self.setup_top_button_bar()

        self.layout().addWidget(scroll)
        self.m_widgetList = []
        self.widget = QWidget()
        self.widget.setLayout(QVBoxLayout())
        self.scroll_frame.layout().addWidget(self.widget)
        self.scroll_frame.layout().addStretch(1)
        self.setup_bottom_button_bar()

    def add(self, widget):
        self.m_widgetList.append(widget)
        self.widget.layout().addWidget(widget)

    def setup_bottom_button_bar(self):
        pass

    def setup_top_button_bar(self):
        pass

    def clear(self):
        for i in reversed(range(self.widget.layout().count())):
            self.widget.layout().itemAt(i).widget().setParent(None)
        self.m_widgetList = []

    def refill(self, newList):
        self.clear()
        for entry in newList:
            self.add(entry)

    def sort(self, attribute):
        unsortedList = []
        for entry in self.m_widgetList:
            unsortedList.append((getattr(entry, attribute)(), entry))
        sortedList = sorted(unsortedList, key=lambda x: x[0], reverse=True)
        self.refill([i[1] for i in sortedList])

    def jsonlify(self):
        return_list = []
        for entry in self.m_widgetList:
            return_list.append(entry.jsonlify())
        return return_list

    def getEntries(self):
        return self.m_widgetList

    def remove(self, widget):
        for entry in self.m_widgetList:
            if entry is widget:
                entry.setParent(None)
        try:
            self.m_widgetList.remove(widget)
        except ValueError:
            pass

    def removeCharacter(self, character):
        for entry in self.m_widgetList:
            if entry.getName() == character.getCharName():
                entry.setParent(None)
        try:
            self.m_widgetList.remove(entry)
        except ValueError:
            pass

    def find(self, target):
        for idx, entry in enumerate(self.m_widgetList):
            if entry is target:
                return idx
        return None