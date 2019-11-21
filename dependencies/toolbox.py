from PyQt5.QtWidgets import QInputDialog, QTableWidget, QHeaderView, QVBoxLayout, \
    QHBoxLayout, QLineEdit, QSizePolicy, QMenu, QTabWidget, QFrame, QPushButton


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

    def remove_rows(self):
        items = self.selectedItems()
        for item in items:
            self.removeRow(item.row())


class LinkedMonsterTable(LinkedTableWidget):
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        add_action = menu.addAction("Add to initiative")
        add_x_action = menu.addAction("Add X to initiative")
        menu.addSeparator()
        add_spellbook = menu.addAction("Add monster's spells to toolbox")
        menu.addSeparator()
        remove = menu.addAction("Remove from Toolbox")


        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        current_row = self.currentRow()
        entry_idx = int(self.item(current_row, 1).text())
        entry = self.linked_table.list[entry_idx]
        if action == add_action:
            self.parent.encounter_table.addMonsterToEncounter(entry, 1)
        if action == add_x_action:
            X, ok = QInputDialog.getInt(self, 'Add Monster', 'How many?')
            if ok:
                self.parent.encounter_table.addMonsterToEncounter(entry, X)
        elif action == remove:
            self.remove_rows()
        elif action == add_spellbook:
            self.parent.extract_and_add_spellbook(entry)


class LinkedSpellTable(LinkedTableWidget):
    _SPELL_LEVEL_COLUMN = 2

    def format(self):
        columns = 3
        self.setColumnCount(columns)
        header = self.horizontalHeader()
        header.hide()
        header.setSectionResizeMode(self._NAME_COLUMN, QHeaderView.Stretch)
        header.setSectionResizeMode(self._SPELL_LEVEL_COLUMN, QHeaderView.ResizeToContents)
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.setColumnHidden(1, True)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        remove_toolbox = menu.addAction("Remove from toolbox")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        current_row = self.currentRow()
        entry_idx = int(self.item(current_row, 1).text())
        entry = self.linked_table.list[entry_idx]
        if action == remove_toolbox:
            self.remove_rows()


class ToolboxWidget(QFrame):
    SPELL_TAB = 0
    DICE_TAB = 1

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.toolbox_frame = QFrame()
        self.toolbox_frame.setMaximumHeight(300)
        self.button_bar = QFrame()
        self.button_bar.setLayout(QHBoxLayout())
        toolbox_layout = QHBoxLayout()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum))

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
        dice_help_button = QPushButton("Help")
        dice_help_button.clicked.connect(self.dice_instructions)
        dice_layout.addWidget(dice_help_button)
        self.dice_toolbox.setLayout(dice_layout)
        self.spell_tabWidget.addTab(self.dice_toolbox, "Dice")

        toolbox_layout.addWidget(self.monster_tabWidget)
        toolbox_layout.addWidget(self.spell_tabWidget)
        self.toolbox_frame.setLayout(toolbox_layout)

        self.clear_toolbox_button = QPushButton("Clear Toolbox")
        self.toggle_toolbox_button = QPushButton("Toggle Toolbox")
        self.button_bar.layout().setContentsMargins(0, 0, 0, 0)
        self.button_bar.layout().addWidget(self.clear_toolbox_button)
        self.button_bar.layout().addWidget(self.toggle_toolbox_button)

        self.layout().addWidget(self.toolbox_frame)
        self.layout().addWidget(self.button_bar)

        self.hidden = False

    def dice_instructions(self):
        self.parent.text_box.append("\nEither input diceroll in format xdy+z, AttackBonus|DamageRoll, or"
                                    " AttackBonus, DamageRoll\nExample: 1d20+6\n5|2d6+3\n5, 2d6+3\n")
    def toggle_hide(self):
        self.hidden = not self.hidden
        self.toolbox_frame.setHidden(self.hidden)
    # @staticmethod
    # def remove_from_toolbox(table, row):
    #     table.remove_row(row)


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
                roll.replace(" ", "")
                if "," in roll:
                    roll = roll.replace(",", "|")
                if "|" in roll:
                    self.parent.print_attack(None, "|" + roll)
                else:
                    result = self.parent.roll(roll)
                    s = ">> Result of ({}): {}".format(roll, result)
                    if type(result) is list:
                        s = s + "({})".format(sum(result))
                    self.parent.text_box.append(s)
            except:
                self.parent.text_box.append("Invalid dice format\nPress help for info")
        self.button.clicked.connect(lambda: perform_roll(self))