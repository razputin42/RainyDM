from PyQt5.QtWidgets import QFrame, QVBoxLayout, QScrollArea, \
    QWidget
from PyQt5.Qt import QMouseEvent
from PyQt5.QtCore import Qt
from RainyCore.player import Character

colorDict = dict(
    white=[240, 240, 240],
    green=[0, 240, 0],
    red=[240, 0x00, 0x00],
    blue=[0x00, 0x00, 240],
)


class EntryWidget(QFrame):
    deselect_signal = None

    def __init__(self, entry=None, viewer=None):
        super().__init__()
        self.entry = entry
        self.setFrameShape(QFrame.Box)
        self.setFrameStyle(QFrame.StyledPanel)
        self.viewer = viewer

    def redraw(self):
        self.setStyle(self.style())

    def hide_viewer(self, condition):
        if self.viewer is not None:
            self.viewer.set_hidden(condition)
            return True
        return False

    def mousePressEvent(self, a0: QMouseEvent):
        if self.property('clicked'):  # already clicked
            self.deselect()
        else:
            if self.deselect_signal is not None:
                self.deselect_signal.emit()
            self.select()
            if self.viewer is not None and type(self.entry) is not Character:
                self.viewer.draw_view(self.entry)
        self.redraw()

    def select(self):
        # self.hide_viewer(False)
        self.setProperty('clicked', True)
        if hasattr(self, "button_bar"):
            self.button_bar.setHidden(False)

    def deselect(self):
        # self.hide_viewer(True)
        self.setProperty('clicked', False)
        if hasattr(self, "button_bar"):
            self.button_bar.setHidden(True)


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

    def find(self, target):
        for idx, entry in enumerate(self.m_widgetList):
            if entry is target:
                return idx
        return None

    def getAttrList(self, attr):
        outputList = []
        for entry in self.m_widgetList:
            if hasattr(entry, attr):
                _attr = getattr(entry, attr)
                if callable(_attr):
                    outputList.append(_attr())
                else:
                    outputList.append(_attr)
        return outputList

    def deselectAll(self):
        for entry in self.m_widgetList:
            entry.deselect()
            entry.redraw()