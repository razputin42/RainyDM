from PyQt5.QtWidgets import QInputDialog, QTableWidget, QHeaderView, QVBoxLayout, \
    QHBoxLayout, QLineEdit, QTextBrowser, QMenu, QTabWidget, QFrame, QPushButton


class LinkedTableWidget(QTableWidget):
    _NAME_COLUMN = 0
    _INDEX_COLUMN = 1

    def __init__(self, linked_table, parent):
        QTableWidget.__init__(self)
        self.parent = parent
        self.linked_table = linked_table
        self.format()

    def format(self):
        columns = 2
        self.setColumnCount(columns)
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(self._NAME_COLUMN, QHeaderView.Stretch)
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.setColumnHidden(1, True)

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


class LinkedMonsterTable(LinkedTableWidget):
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        add_action = menu.addAction("Add to initiative")
        add_x_action = menu.addAction("Add X to initiative")
        menu.addSeparator()
        remove = menu.addAction("Remove from Toolbox")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        current_row = self.currentRow()
        entry_idx = int(self.item(current_row, 1).text())
        entry = self.linked_table.list[entry_idx]
        if action == add_action:
            self.parent.add_to_encounter(entry, 1)
        if action == add_x_action:
            X, ok = QInputDialog.getInt(self, 'Add Monster', 'How many?')
            if ok:
                self.parent.add_to_encounter(entry, X)
        elif action == remove:
            self.removeRow(current_row)


class LinkedSpellTable(LinkedTableWidget):
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        addToolbox = menu.addAction("Remove from Toolbox")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        current_row = self.currentRow()
        entry_idx = int(self.item(current_row, 1).text())
        entry = self.linked_table.list[entry_idx]
        if action == addToolbox:
            self.removeRow(current_row)


class ToolboxWidget:
    def __init__(self, parent):
        self.parent = parent
        self.frame = QFrame()
        layout = QHBoxLayout()
        self.spell_toolbox = LinkedSpellTable(self.parent.spell_table_widget, self.parent)
        self.monster_toolbox = LinkedMonsterTable(self.parent.monster_table_widget, self.parent)
        self.monster_tabWidget = QTabWidget()
        self.monster_tabWidget.addTab(self.monster_toolbox, "Monster")

        self.spell_tabWidget = QTabWidget()
        self.spell_tabWidget.addTab(self.spell_toolbox, "Spell")

        self.dice_toolbox = QFrame()
        dice_layout = QVBoxLayout()
        for i in range(5):
            dice_layout.addWidget(DiceBox(parent).frame)
        self.dice_toolbox.setLayout(dice_layout)
        self.spell_tabWidget.addTab(self.dice_toolbox, "Dice")

        layout.addWidget(self.monster_tabWidget)
        layout.addWidget(self.spell_tabWidget)
        self.frame.setLayout(layout)

    # def monster_contextMenuEvent(self, event):
    #     menu = QMenu(self.monster_toolbox)
    #     addAction = menu.addAction("Add to initiative")
    #     addXAction = menu.addAction("Add X to initiative")
    #     menu.addSeparator()
    #     removeFromToolbox = menu.addAction("Remove from toolbox")
    #
    #     action = menu.exec_(self.monster_toolbox.mapToGlobal(event.pos()))
    #     if action is None:
    #         return
    #     current_row = self.monster_toolbox.currentRow()
    #     monster_idx = int(self.monster_toolbox.item(current_row, 1).text())
    #     monster = self.parent.monster_table_widget.list[monster_idx]
    #     if action == addAction:
    #         self.parent.add_to_encounter(monster, 1)
    #     if action == addXAction:
    #         X, ok = QInputDialog.getInt(self.parent, 'Add Monster', 'How many?')
    #         if ok:
    #             self.parent.add_to_encounter(monster, X)
    #     elif action == removeFromToolbox:
    #         self.remove_from_toolbox(self.monster_toolbox, current_row)

    @staticmethod
    def remove_from_toolbox(table, row):
        table.remove_row(row)


class DiceBox:
    def __init__(self, parent):
        self.parent = parent
        self.frame = QFrame()
        layout = QHBoxLayout()
        self.button = QPushButton()
        self.input = QLineEdit()
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        self.frame.setLayout(layout)

        def perform_roll(self):
            roll = self.input.text()
            try:
                result = self.parent.roll(roll)
                s = ">> Result of ({}): {}".format(roll, result)
                if type(result) is list:
                    s = s + "({})".format(sum(result))
                self.parent.text_box.append(s)
            except:
                pass
        self.button.clicked.connect(lambda: perform_roll(self))