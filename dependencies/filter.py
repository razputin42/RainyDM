from PyQt5.QtWidgets import QFrame, QComboBox, QVBoxLayout, QSizePolicy, QLabel

class Filter:
    def __init__(self):
        self.filter = dict()
        self.frame = QFrame()
        actual_layout = QVBoxLayout()
        offset_frame = QFrame()
        offset_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        widget_frame = QFrame()
        widget_frame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout = QVBoxLayout()
        widget_frame.setLayout(self.layout)
        actual_layout.addWidget(widget_frame)
        actual_layout.addWidget(offset_frame)
        self.filter_names = []
        self.frame.setLayout(actual_layout)
        self.frame.setHidden(True)

    def add_dropdown(self, name, list):
        combo_box = QComboBox()
        combo_box.addItem("")
        combo_box.addItems(list)
        label = QLabel(name)
        self.filter_names.append(name)
        self.layout.addWidget(label)
        self.layout.addWidget(combo_box)
        combo_box.currentIndexChanged.connect(self.set_filters)

    def set_filters(self):
        pass

    def get_frame(self):
        return self.frame

    def toggle_hidden(self):
        if self.frame.isHidden():
            self.frame.setHidden(False)
        else:
            self.frame.setHidden(True)

    def evaluate_filter(self, entry):
        cond = True
        for key, arg in self.filter.items():
            if not hasattr(entry, key):
                print("Wrong filter key passed to entry in SearchableTable")
                continue
            attr = getattr(entry, key)
            cond = cond and (attr == arg)
        return cond
