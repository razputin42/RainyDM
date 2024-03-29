from PyQt5.QtWidgets import QFrame, QComboBox, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QLineEdit
from PyQt5 import QtCore
import re

class FilterWidget:  ## this will be used to rework how the filtering is handled
    def __init__(self):
        pass

class Filter:
    locks = dict()

    def __init__(self, filter_content):
        self.filter_content = filter_content
        self.filter = dict()
        self.frame = QFrame()
        self.frame.setObjectName("Filter_frame")
        self.frame.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        actual_layout = QVBoxLayout()
        widget_frame = QFrame()
        self.layout = QVBoxLayout()
        widget_frame.setLayout(self.layout)
        actual_layout.addWidget(widget_frame)
        actual_layout.addStretch(1)
        self.filter_names = []
        self.frame.setLayout(actual_layout)
        self.frame.setHidden(True)

    def add_range(self, name, capitalize=False):
        min_input = QLineEdit()
        max_input = QLineEdit()
        min_input.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        min_input.setMaximumWidth(50)
        max_input.setMaximumWidth(50)
        if capitalize:
            name = name.capitalize()
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

    def add_dropdown(self, name, options, suboptions=None, default=None, alphabetical=True):
        if alphabetical:
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
        main = combo_box.currentText().lower()
        sub = sub_combo_box.currentText().lower()
        if sub == "any":
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
                    _suboptions = [subopt for subopt in suboptions[main] if subopt != "Any"]  # remove Any as suboption
                    sub_combo_box.setHidden(False)
                    sub_combo_box.clear()
                    sub_combo_box.addItem("Any")
                    sub_combo_box.addItems(_suboptions)
                else:
                    sub_combo_box.clear()
                    sub_combo_box.setHidden(True)
            self.filter[name] = main + ".*"
        # print(self.filter[name])
        self.filter_content()

    def lock(self, attr, value):
        self.locks[attr] = value

    def get_frame(self):
        return self.frame

    def toggle_hidden(self):
        if self.frame.isHidden():
            self.frame.setHidden(False)
        else:
            self.frame.setHidden(True)

    def evaluate_filter(self, entry):
        cond = True
        for key, arg in self.locks.items():
            if not hasattr(entry, key) or getattr(entry, key) != arg:
                return False
        for key, arg in self.filter.items():
            if not hasattr(entry, key):
                # print("Wrong filter key passed to entry in SearchableTable")
                return False
            attr = getattr(entry, key)
            if type(arg) is str and type(attr) is str:  # single attribute, single argument. Easy as pie
                p = re.compile('{}'.format(arg), re.IGNORECASE)
                cond = cond and (p.match(attr))
            elif type(attr) is list:  # single argument, multiple attributes, eval individually for each element
                p = re.compile('{}'.format(arg), re.IGNORECASE)
                cond = cond and any([p.match(_attr) for _attr in attr])
            elif type(arg) is list:  # numerical range, must be inbetween two values
                if attr is None or None in arg:
                    continue
                attr = eval("float({})".format(attr))
                cond = cond and (arg[0] <= attr <= arg[1])

        return cond

    def clear_filters(self):
        for i in reversed(range(self.layout.count())):
            self.layout.removeItem(self.layout.itemAt(i))
        self.filter = dict()

