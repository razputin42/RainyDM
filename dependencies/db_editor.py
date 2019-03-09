from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QShortcut, QTextEdit, QVBoxLayout, \
    QHBoxLayout, QTabWidget, QFrame, QSizePolicy, QWidget
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt
import os
from .monster import Monster
import time

class DBEditor(QWidget):
    def __init__(self, parent, entry, copy=False):
        super().__init__()
        self.parent = parent
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
        self.tab_widget.addTab(self.attributes_frame, 'Attributes')

        self.old_entries = dict()
        self.line_edit_dict = dict()

        # attributes tab
        for field in self.entry.database_fields:
            if type(field) is str:
                if edit: #and hasattr(self.entry, field):
                    horizontal_layout = QHBoxLayout()
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
        # if hasattr(self.entry, 'action_list') and len(self.entry.action_list) is not 0:
        #     self.action_list = self.add_tab(self.entry.action_list, 'Actions')
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

    def add_tab(self, list, tab_name):
        tab_frame = QFrame()
        full_frame = QFrame()
        tab_layout = QVBoxLayout()
        full_frame.setLayout(tab_layout)
        button_bar_frame = QFrame()
        button_bar_layout = QHBoxLayout()
        button_bar_frame.setLayout(button_bar_layout)
        self.tab_widget.addTab(tab_frame, tab_name)
        return_list = []
        for element in list:
            edit_dict = dict()
            layout = QHBoxLayout()  # horizontal layout
            frame = QFrame()
            frame.setLayout(layout)
            frame.setFrameShadow(1)
            for attr in element.database_fields:  # for each attribute
                if hasattr(element, attr):
                    field_layout = QVBoxLayout()
                    label = QLabel(attr.capitalize())
                    if len(getattr(element, attr)) > 50:
                        edit = QTextEdit()
                    else:
                        edit = QLineEdit()

                    if attr is 'text':
                        edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    else:
                        edit.setMinimumWidth(150)
                        edit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                    # edit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                    edit_dict[attr] = edit
                    edit.setText(getattr(element, attr))
                    field_layout.addWidget(edit)
                    field_layout.addStretch(0)
                    layout.addLayout(field_layout)  # add to horizontal layout
            # action_layout.setStretch(1, 5)
            tab_layout.addWidget(frame)  # add to vertical tab_layout
            return_list.append(edit_dict)
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
                    continue
                self.new_entries[field] = text

        for field, old_value, new_value in zip(
                self.old_entries.keys(),
                self.old_entries.values(),
                self.new_entries.values()):
            if old_value != new_value:
                setattr(self.entry, field, new_value)

        # lists = ['action_list', 'trait_list', 'legendary_list']
        # for list in lists:
        #     if not hasattr(self.entry, list):
        #         continue
        #     entry_list
        #     for action in self.action_list:
        #         # reset entries action list
        #         pass  # save to the entry

        if self.copy:  # either copy the entry, or update the existing
            result = self.parent.copy_entry(self.entry)
            if result is False:
                return
            self.parent.save_entry(self.entry)

        else:
            row = self.parent.table.currentRow()
            self.parent.update_entry(row, self.entry)
            self.parent.save_entry(self.entry, old_name=self.old_entries['name'])

        self.parent.viewer.redraw_view()
        self.close()

    def cancel_handle(self):
        self.close()