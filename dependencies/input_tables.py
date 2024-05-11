from PyQt5.QtWidgets import QTableWidget, QMenu, QVBoxLayout, QFrame, QLabel, QSizePolicy, QLineEdit, QHBoxLayout, \
    QCheckBox
from PyQt5.QtGui import QIntValidator, QFont
from PyQt5.QtCore import Qt
from dependencies.list_widget import ListWidget, EntryWidget
from RainyCore.player import Character
import json


class InputTableWidget(QTableWidget):
    NAME_COLUMN = 0
    INDEX_COLUMN = 1

    def __init__(self, parent):
        QTableWidget.__init__(self)
        self.parent = parent
        self.format()

    def format(self):
        pass

    def contextMenuEvent(self, event):
        pass

    def jsonlify(self):
        rows = self.rowCount()
        cols = self.columnCount()
        output_list = []
        for i in range(rows):
            row = []
            for j in range(cols):
                item = self.item(i, j)
                if item is None:
                    row.append("")
                else:
                    row.append(item.text())
            output_list.append(tuple(row))
        return output_list

    def remove_rows(self):
        items = self.selectedItems()
        for item in items:
            self.removeRow(item.row())


class InputFrame(QFrame):
    def __init__(self, text, type=str, value=None):
        super().__init__()
        self.type = type
        self.setLayout(QVBoxLayout())
        label = QLabel(text)
        font = QFont("Helvetica [Cronyx]", 10)
        font.setCapitalization(QFont.SmallCaps)
        label.setFont(font)
        self.edit = QLineEdit()
        if type is int:
            self.edit.setFixedWidth(30)
        else:
            pass
            # self.edit.setFixedWidth(60)
        if type is int:
            self.edit.setValidator(QIntValidator(-999, 999))
        if value is not None:
            self.edit.setText(str(value))

        self.layout().addWidget(label, Qt.AlignCenter)
        self.layout().addWidget(self.edit, Qt.AlignCenter)
        # self.layout().setAlignment(label, Qt.AlignTop)
        # self.layout().setAlignment(self.edit, Qt.AlignTop)

    def get(self):
        if self.edit.text() == '':
            return None
        elif self.type is int:
            return int(self.edit.text())
        elif self.type is str:
            return self.edit.text()

    def set(self, value):
        self.edit.setText(str(value))

    def setEditSizePolicy(self, policy):
        self.edit.setSizePolicy(policy)


class CustomCheckBox(QCheckBox):
    def __init__(self, isEnabled=False):
        super().__init__()
        self.setChecked(isEnabled)


class PlayerFrame(EntryWidget):
    def __init__(self, parentList, charName=None, playerName=None, init=None, perception=None, insight=None,
                 isEnabled=False):
        super().__init__()
        self.parent = parentList
        self.nameFrame = InputFrame("Character Name", str, value=charName)
        self.nameFrame.setEditSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum))
        self.playerName = InputFrame("Player Name", str, value=playerName)
        self.initFrame = InputFrame("Initiative", int, value=init)
        self.perceptionFrame = InputFrame("Perception", int, value=perception)
        self.insightFrame = InputFrame("Insigt", int, value=insight)
        self.checkBox = CustomCheckBox(isEnabled)

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(20, 0, 20, 0)
        topFrame = QFrame()
        botFrame = QFrame()
        topFrame.setLayout(QHBoxLayout())
        topFrame.layout().setContentsMargins(0, 0, 0, 0)
        topFrame.layout().addWidget(self.nameFrame)
        topFrame.layout().addWidget(self.playerName)
        topFrame.layout().addWidget(self.initFrame)
        topFrame.layout().addWidget(self.perceptionFrame)
        topFrame.layout().addWidget(self.insightFrame)
        topFrame.layout().addStretch(1)
        topFrame.layout().addWidget(self.checkBox)
        botFrame.setLayout(QHBoxLayout())
        botFrame.layout().setContentsMargins(0, 0, 0, 0)
        # botFrame.layout().addWidget(self.initFrame)
        # botFrame.layout().addWidget(self.perceptionFrame)
        # botFrame.layout().addWidget(self.insightFrame)
        # botFrame.layout().addStretch(1)
        self.layout().addWidget(topFrame)
        # self.layout().addWidget(botFrame)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.setObjectName("PlayerFrame")

    def getCharacter(self):
        return Character(self.nameFrame.get(), self.playerName.get(), self.initFrame.get(), True)

    def contextMenuEvent(self, event):
        menu = QMenu()
        removeAction = menu.addAction("Remove")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        elif action == removeAction:
            self.parent.remove(self)

    def isEnabled(self):
        return self.checkBox.isChecked()

    def jsonlify(self):
        output = dict(
            characterName=self.nameFrame.get(),
            playerName=self.playerName.get(),
            initiative=self.initFrame.get(),
            perception=self.perceptionFrame.get(),
            insight=self.insightFrame.get(),
            isEnabled=self.checkBox.isChecked()
        )
        return json.dumps(output)

    def select(self):
        pass

    def deselect(self):
        pass


class PlayerTable(ListWidget):
    def __init__(self):
        super().__init__()

    def findCharacterByName(self, name):
        for entry in self.m_widgetList:
            if entry.getCharacter().getCharName() == name:
                return entry.getCharacter()

# class PlayerTable(InputTableWidget):
#     PLAYER_COLUMN = 1
#     INITIATIVE_COLUMN = 2
#     PASSIVE_PERCEPTION_COLUMN = 3
#     PASSIVE_INSIGHT_COLUMN = 4
#
#     def contextMenuEvent(self, event):
#         menu = QMenu(self)
#         addAction = menu.addAction("Add player")
#         removeAction = menu.addAction("Remove player")
#
#         action = menu.exec_(self.mapToGlobal(event.pos()))
#         if action is None:
#             return
#         current_row = self.currentRow()
#         if action == addAction:
#             self.parent.add_player()
#         elif action == removeAction:
#             self.remove_rows()
#
#     def format(self):
#         columns = 5
#         self.setColumnCount(columns)
#         self.setHorizontalHeaderLabels(["Name", "Player", "Initiative", "Passive Insight",
#                                         "Passive Perception", "Inactive"])
#         self.setShowGrid(True)
#         for i in range(columns):
#             self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
#         self.setColumnWidth(self.NAME_COLUMN, 150)
#         self.verticalHeader().hide()
