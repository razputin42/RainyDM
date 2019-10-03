from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QScrollArea, \
    QWidget, QFormLayout, QGroupBox
from PyQt5.QtCore import Qt


class EntryWidget(QFrame):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)


class ListWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        scrollLayout = QVBoxLayout()
        self.scroll_frame = QWidget()
        self.scroll_frame.setLayout(scrollLayout)
        scroll = QScrollArea()
        scroll.setWidget(self.scroll_frame)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        self.setLayout(layout)
        self.m_widgetList = []
        self.widget = QWidget()
        self.widget.setLayout(QVBoxLayout())
        self.scroll_frame.layout().addWidget(self.widget)
        self.scroll_frame.layout().addStretch(1)

    def add(self, widget):
        self.m_widgetList.append(widget)
        self.widget.layout().addWidget(widget)

    def clear(self):
        for i in reversed(range(self.widget.layout().count())):
            self.widget.layout().itemAt(i).widget().setParent(None)
        self.m_widgetList = []

    def sort(self, parameter):
        pass

    def jsonlify(self):
        return []

    def getEntries(self):
        return self.m_widgetList
