from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QTableWidgetItem, QTextEdit, QVBoxLayout, \
    QHBoxLayout, QTabWidget, QFrame, QSizePolicy, QMainWindow, QWidget
from .monster import Monster

class DBEditor(QWidget):
    def __init__(self, parent, element):
        super().__init__()
        self.vertical_layout = QVBoxLayout()
        if element is Monster:
            print("New Monster")
            edit = False
        else:
            print("Edit element")
            edit = True

        for field in element.database_fields:
            if type(field) is str:
                if edit and hasattr(element, field):
                    horizontal_layout = QHBoxLayout()
                    label = QLabel(field)
                    label.setMinimumWidth(100)
                    line_edit = QLineEdit()
                    line_edit.setText(getattr(element, field))
                    horizontal_layout.addWidget(label)
                    horizontal_layout.addWidget(line_edit)
                    self.vertical_layout.addLayout(horizontal_layout)

            elif type(field) is list:
                horizontal_layout = QHBoxLayout()
                for element in field:
                    label = QLabel(element)
                    line_edit = QLineEdit()
                    horizontal_layout.addWidget(label)
                    horizontal_layout.addWidget(line_edit)
                self.vertical_layout.addLayout(horizontal_layout)
        self.setLayout(self.vertical_layout)