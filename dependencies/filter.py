from PyQt5.QtWidgets import QFrame, QComboBox, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QLineEdit
from PyQt5 import QtCore
import re


class Filter:
    def __init__(self, filter_content):
        self.filter_content = filter_content
        self.filter = dict()
        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        actual_layout = QVBoxLayout()
        widget_frame = QFrame()
        # widget_frame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout = QVBoxLayout()
        widget_frame.setLayout(self.layout)
        actual_layout.addWidget(widget_frame)
        actual_layout.addStretch(1)
        self.filter_names = []
        self.frame.setLayout(actual_layout)
        self.frame.setHidden(True)

    def add_range(self, name):
        min_input = QLineEdit()
        max_input = QLineEdit()
        min_input.setMaximumWidth(30)
        max_input.setMaximumWidth(30)
        title = QLabel(name)
        dash = QLabel("-")
        frame = QFrame()
        layout = QHBoxLayout()
        layout.addWidget(min_input)
        layout.addStretch(0)
        layout.addWidget(dash)
        layout.addStretch(0)
        layout.addWidget(max_input)
        frame.setLayout(layout)
        # frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(title)
        self.layout.addWidget(frame)

        min_input.textChanged.connect(lambda: self.set_range_filter(name, min_input, max_input))
        max_input.textChanged.connect(lambda: self.set_range_filter(name, min_input, max_input))

    def set_range_filter(self, name, min_input, max_input):
        name = name.lower()
        minimum = -9001
        maximum = 9001
        try: minimum = int(min_input.text())
        except: pass
        try: maximum = int(max_input.text())
        except: pass

        if minimum == -9001 and maximum == 9001:
            if name in self.filter.keys():
                del self.filter[name]
        else:
            self.filter[name] = [minimum, maximum]
        self.filter_content()

    def add_dropdown(self, name, options, suboptions=None, default=None):
        options.sort()
        combo_box = QComboBox()
        combo_box.addItem("Any")
        combo_box.addItems(options)
        if suboptions is not None:
            sub_combo_box = QComboBox()
            sub_combo_box.setHidden(True)
        else:
            sub_combo_box = None
        label = QLabel(name)
        self.filter_names.append(name)
        self.layout.addWidget(label)
        self.layout.addWidget(combo_box)
        if suboptions is not None:
            self.layout.addWidget(sub_combo_box)
            sub_combo_box.currentIndexChanged.connect(lambda: self.set_sub_filters(name, combo_box,
                                                                                   sub_combo_box))
        combo_box.currentIndexChanged.connect(lambda: self.set_filters(name, combo_box, sub_combo_box, suboptions))

        if default is not None:
            index = combo_box.findText(default, QtCore.Qt.MatchFixedString)
            if index >= 0:
                combo_box.setCurrentIndex(index)

    def set_sub_filters(self, name, combo_box, sub_combo_box):
        name = name.lower()
        main = combo_box.currentText()
        sub = sub_combo_box.currentText()
        print("\""+sub+"\"")
        if sub == "Any":
            self.filter[name] = main + ".*"
        else:
            self.filter[name] = main + ".*(\ \(|\,\ )(" + sub + ").*"
        self.filter_content()

    def set_filters(self, name, combo_box, sub_combo_box=None, suboptions=None):
        main = combo_box.currentText()
        sub_cond = sub_combo_box is not None
        if sub_cond:
            sub = sub_combo_box.currentText()

        name = name.lower()
        if main == "Any" and name in self.filter.keys():
            del self.filter[name]
            if sub_cond:
                sub_combo_box.setHidden(True)
        else:
            if sub_cond:
                if main in suboptions.keys():
                    sub_combo_box.setHidden(False)
                    sub_combo_box.clear()
                    sub_combo_box.addItem("Any")
                    sub_combo_box.addItems(suboptions[main])
                else:
                    sub_combo_box.clear()
                    sub_combo_box.setHidden(True)
            self.filter[name] = main + ".*"
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
            if type(arg) is str:
                p = re.compile('{}'.format(arg), re.IGNORECASE)
                cond = cond and (p.match(attr))
            elif type(arg) is list:  # numerical range
                cond = cond and (arg[0] <= attr <= arg[1])
        return cond
