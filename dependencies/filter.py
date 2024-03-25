import logging
import re

from PyQt5 import QtCore
from PyQt5.QtWidgets import QFrame, QComboBox, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QLineEdit


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

    def add_range(self, name, attribute=None, capitalize=False):
        if attribute is None:
            attribute = name
        min_input = QLineEdit()
        max_input = QLineEdit()
        min_input.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        min_input.setMaximumWidth(50)
        max_input.setMaximumWidth(50)
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
        self.layout.addWidget(title)
        self.layout.addWidget(frame)

        min_input.textChanged.connect(lambda: self.set_range_filter(attribute, min_input, max_input))
        max_input.textChanged.connect(lambda: self.set_range_filter(attribute, min_input, max_input))

    def set_range_filter(self, attribute, min_input, max_input):
        try:
            minimum = int(min_input.text())
        except:
            minimum = -9001
        try:
            maximum = int(max_input.text())
        except:
            maximum = 9001

        if minimum == -9001 and maximum == 9001:
            if attribute in self.filter.keys():
                del self.filter[attribute]
        else:
            self.filter[attribute] = [minimum, maximum]
        self.filter_content()

    def add_dropdown(
            self,
            name,
            options,
            attribute=None,
            suboptions=None,
            default=None,
            alphabetical=True
    ):
        if attribute is None:
            attribute = name.lower()
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
        self.filter_names.append(attribute)
        self.layout.addWidget(label)
        self.layout.addWidget(combo_box)
        if suboptions is not None:
            self.layout.addWidget(sub_combo_box)
            sub_combo_box.currentIndexChanged.connect(
                lambda: self.set_sub_filters(
                    attribute,
                    combo_box,
                    sub_combo_box
                )
            )
        combo_box.currentIndexChanged.connect(
            lambda: self.set_filters(attribute, combo_box, sub_combo_box, suboptions)
        )

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

    def set_filters(self, attribute, combo_box, sub_combo_box=None, suboptions=None):
        selection = combo_box.currentText()
        sub_cond = sub_combo_box is not None
        if sub_cond:
            sub = sub_combo_box.currentText()

        attribute = attribute.lower()
        if selection == "Any" and attribute in self.filter.keys():
            del self.filter[attribute]
            if sub_cond:
                sub_combo_box.setHidden(True)
        else:
            if sub_cond:
                if selection in suboptions.keys():
                    _suboptions = [subopt for subopt in suboptions[selection] if subopt != "Any"]  # remove Any as suboption
                    sub_combo_box.setHidden(False)
                    sub_combo_box.clear()
                    sub_combo_box.addItem("Any")
                    sub_combo_box.addItems(_suboptions)
                else:
                    sub_combo_box.clear()
                    sub_combo_box.setHidden(True)
            self.filter[attribute] = selection + ".*"
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
        for key, value in self.locks.items():
            if not hasattr(entry, key) or getattr(entry, key) != value:
                return False
        for key, value in self.filter.items():
            attribute = entry.get_attributes().get(key, None)
            if attribute is None:
                logging.warning("Wrong filter key passed to entry in SearchableTable")
                return False
            if type(value) is str and type(attribute) is str:  # single attribute, single argument. Easy as pie
                p = re.compile('{}'.format(value), re.IGNORECASE)
                cond = cond and (p.match(attribute))
            elif type(attribute) is list:  # single argument, multiple attributes, eval individually for each element
                p = re.compile('{}'.format(value), re.IGNORECASE)
                cond = cond and any([p.match(_attr) for _attr in attribute])
            elif type(value) is list:  # numerical range, must be inbetween two values
                if attribute is None or None in value:
                    continue
                if attribute == "CR":
                    logging.warning(entry.get_name())
                attribute = eval(f"float({attribute})")  # necessary for values such as 1/8
                cond = cond and (value[0] <= attribute <= value[1])
        return cond

    def clear_filters(self):
        for i in reversed(range(self.layout.count())):
            self.layout.removeItem(self.layout.itemAt(i))
        self.filter = dict()
