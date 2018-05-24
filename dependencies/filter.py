from PyQt5.QtWidgets import QFrame, QComboBox, QVBoxLayout, QSizePolicy, QLabel

class Filter:
    def __init__(self, filter_content):
        self.filter_content = filter_content
        self.filter = dict()
        self.frame = QFrame()
        actual_layout = QVBoxLayout()
        widget_frame = QFrame()
        widget_frame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout = QVBoxLayout()
        widget_frame.setLayout(self.layout)
        actual_layout.addWidget(widget_frame)
        actual_layout.addStretch(1)
        self.filter_names = []
        self.frame.setLayout(actual_layout)
        self.frame.setHidden(True)

    def add_dropdown(self, name, options):
        options.sort()
        combo_box = QComboBox()
        combo_box.addItem("Any")
        combo_box.addItems(options)
        label = QLabel(name)
        self.filter_names.append(name)
        self.layout.addWidget(label)
        self.layout.addWidget(combo_box)
        combo_box.currentIndexChanged.connect(lambda: self.set_filters(name, combo_box))

    def set_filters(self, name, combo_box):
        text = combo_box.currentText()
        name = name.lower()
        if text == "Any" and name in self.filter.keys():
            del self.filter[name]
        else:
            self.filter[name] = combo_box.currentText()
        self.filter_content()

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
