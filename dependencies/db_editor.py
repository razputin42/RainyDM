from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QShortcut, QTextEdit, QVBoxLayout, \
    QHBoxLayout, QTabWidget, QFrame, QSizePolicy, QWidget, QPlainTextEdit
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt
import os
from RainyCore.monster import Monster


class ResizeableTextEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.textChanged.connect(self._resizeToFit)

    def _resizeToFit(self):
        self.setMaximumHeight(72)


class DBEditor(QWidget):
    def __init__(self, parent, entry, copy=False):
        super().__init__()
        self.parent = parent
        self.master_widget = parent.parent
        self.copy = copy
        self.action_list = []
        self.trait_list = []
        self.legendary_list = []

        self.main_layout = QVBoxLayout()
        self.attributes_frame = QFrame()
        self.attributes_layout = QVBoxLayout()
        self.attributes_frame.setLayout(self.attributes_layout)
        self.actions_frame = QFrame()
        self.actions_layout = QVBoxLayout()
        self.actions_frame.setLayout(self.actions_layout)
        self.entry = entry
        self.setWindowTitle('Database editor')
        self.setWindowIcon(QIcon(os.path.join('assets', 'tear.png')))
        if self.entry is Monster:
            edit = False
        else:
            edit = True

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.attributes_frame, "Attributes")
        # self.tab_widget.addTab(self.actions_frame, "Actions")

        self.old_entries = dict()
        self.line_edit_dict = dict()

        # attributes tab
        for field in self.entry.database_fields:
            if type(field) is str:
                if edit: #and hasattr(self.entry, field):
                    horizontal_layout = QHBoxLayout()
                    if field in self.entry.required_database_fields:
                        label = QLabel("{}*".format(field.capitalize()))
                    else:
                        label = QLabel(field.capitalize())
                    label.setMinimumWidth(100)
                    self.old_entries[field] = getattr(self.entry, field) if hasattr(self.entry, field) else None
                    if field == 'text':
                        edit = QTextEdit()
                    else:
                        edit = QLineEdit()
                    edit.setText(getattr(self.entry, field) if hasattr(self.entry, field) else '')
                    self.line_edit_dict[field] = edit
                    horizontal_layout.addWidget(label)
                    horizontal_layout.addWidget(edit)
                    self.attributes_layout.addLayout(horizontal_layout)

            elif type(field) is list:
                horizontal_layout = QHBoxLayout()
                for data in field:
                    label = QLabel(data.capitalize())
                    edit = QLineEdit()
                    self.old_entries[data] = getattr(self.entry, data)
                    edit.setText(str(getattr(self.entry, data)))
                    horizontal_layout.addWidget(label)
                    self.line_edit_dict[data] = edit
                    horizontal_layout.addWidget(edit)
                self.attributes_layout.addLayout(horizontal_layout)

        # actions tab
        if hasattr(self.entry, 'action_list') and len(self.entry.action_list) is not 0:
            self.action_list = self.add_tab(self.entry.action_list, 'Actions')
        #
        # if hasattr(self.entry, 'trait_list') and len(self.entry.trait_list) is not 0:
        #     self.trait_list = self.add_tab(self.entry.trait_list, 'Traits')
        #
        # if hasattr(self.entry, 'legendary_list') and len(self.entry.legendary_list) is not 0:
        #     self.legendary_list = self.add_tab(self.entry.legendary_list, 'Legendary Actions')

        self.new_entries = self.old_entries.copy()
        accept_button = QPushButton('Accept')
        cancel_button = QPushButton('Cancel')
        accept_button.clicked.connect(self.accept_handle)
        cancel_button.clicked.connect(self.cancel_handle)
        button_bar = QFrame()
        button_bar_layout = QHBoxLayout()
        button_bar_layout.addStretch(0)
        button_bar_layout.addWidget(accept_button)
        button_bar_layout.addWidget(cancel_button)
        button_bar.setLayout(button_bar_layout)
        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(button_bar)
        self.setLayout(self.main_layout)

        enter = QShortcut(QKeySequence(Qt.Key_Return), self)
        self.setWindowModality(Qt.ApplicationModal)
        enter.activated.connect(self.accept_handle)

    def add_tab(self, element_list, tab_name):
        tab_frame = QFrame()
        tab_layout = QVBoxLayout()
        tab_frame.setLayout(tab_layout)
        button_bar_frame = QFrame()
        button_bar_layout = QHBoxLayout()
        button_bar_frame.setLayout(button_bar_layout)
        self.tab_widget.addTab(tab_frame, tab_name)
        return_list = []
        for element in element_list:
            edit_dict = dict()
            layout = QHBoxLayout()  # horizontal layout
            frame = QFrame()
            frame.setLayout(layout)
            frame.setFrameShadow(1)
            for attr in element.database_fields:  # for each attribute
                if hasattr(element, attr):
                    field_layout = QVBoxLayout()
                    label = QLabel(attr.capitalize())
                    # if len(getattr(element, attr)) > 50:
                    #     edit = QTextEdit()
                    # else:
                    #     edit = QLineEdit()
                    edit = ResizeableTextEditor()

                    if attr is 'text':
                        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                        sizePolicy.setHorizontalStretch(3)
                    else:
                        # edit.setMinimumWidth(150)
                        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                        sizePolicy.setHorizontalStretch(1)
                        edit.setMaximumWidth(150)
                    edit.setSizePolicy(sizePolicy)
                    # edit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                    edit_dict[attr] = edit
                    edit.setPlainText(getattr(element, attr))
                    field_layout.addWidget(edit)
                    field_layout.addStretch(0)
                    layout.addLayout(field_layout)  # add to horizontal layout
            tab_layout.addWidget(frame)  # add to vertical tab_layout
            return_list.append(edit_dict)
        # tab_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        tab_layout.addWidget(button_bar_frame)
        return return_list

    def accept_handle(self):
        for field in self.entry.database_fields:
            if type(field) is list:
                for _field in field:
                    text = self.line_edit_dict[_field].text()
                    if text == '' or text is None:
                        continue
                    self.new_entries[_field] = text
            elif type(field) is str:
                edit = self.line_edit_dict[field]
                if edit.__class__ is QTextEdit:
                    text = edit.toPlainText()
                else:
                    text = edit.text()
                if text == '' or text is None:
                    if field in self.entry.required_database_fields:
                        self.master_widget.print("Failed; {} must be filled out".format(field))
                        return
                    continue
                self.new_entries[field] = text

        for field, old_value, new_value in zip(
                self.old_entries.keys(),
                self.old_entries.values(),
                self.new_entries.values()):
            if old_value != new_value:
                setattr(self.entry, field, new_value)

        # actions
        if type(self.entry) is Monster:
            lists = ["action_list", "trait_list", "legendary_list"]
            element_classes = [Monster.Action, Monster.Trait, Monster.Action]
            for list_it, element_class in zip(lists, element_classes):
                setattr(self.entry, list_it, [])
                for element in getattr(self, list_it):
                    _element = element_class([])
                    for key, value in element.items():
                        if type(value) is QTextEdit:
                            text = value.toPlainText()
                        elif type(value) is QLineEdit:
                            text = value.text()
                        if not (text is None or text == ""):
                            setattr(_element, key, text)
                    getattr(self.entry, list_it).append(_element)

        if self.copy:  # either copy the entry, or update the existing
            result = self.parent.copy_entry(self.entry)
            if result is False:
                return
            self.parent.save_entry(self.entry)
            self.parent.viewer.draw_view(self.entry)

        else:
            row = self.parent.table.currentRow()
            self.parent.update_entry(row, self.entry)
            self.parent.save_entry(self.entry, old_name=self.old_entries['name'])
            self.parent.viewer.redraw_view()

        self.close()

    def cancel_handle(self):
        self.close()

def create_element_field(element):
    edit_dict = dict()
    layout = QHBoxLayout()  # horizontal layout
    frame = QFrame()
    frame.setLayout(layout)
    frame.setFrameShadow(1)
    frame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
    for attr in element.database_fields:  # for each attribute
        # if hasattr(element, attr):
        field_layout = QVBoxLayout()
        label = QLabel(attr.capitalize())
        if attr is "text":
            edit = QTextEdit()
            edit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
            # edit.setMinimumHeight(100)
        else:
            edit = QLineEdit()
            edit.setMinimumWidth(150)
            edit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # if attr is 'text':
        #     edit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        # else:
        # edit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        edit_dict[attr] = edit
        if hasattr(element, attr):
            edit.setText(getattr(element, attr))
        field_layout.addWidget(label)
        field_layout.addWidget(edit)
        field_layout.addStretch(0)
        layout.addLayout(field_layout)  # add to horizontal layout
    # action_layout.setStretch(1, 5)
    return [frame, edit_dict]