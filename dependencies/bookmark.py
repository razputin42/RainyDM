from PyQt5.QtWidgets import QInputDialog, QTableWidget, QHeaderView, QVBoxLayout, \
    QHBoxLayout, QLineEdit, QSizePolicy, QMenu, QTabWidget, QFrame, QPushButton, QTableWidgetItem
import dependencies.auxiliaries as aux
from RainyCore.signals import sNexus

class LinkedTableWidget(QTableWidget):
    _NAME_COLUMN = 0
    _INDEX_COLUMN = 1
    prev_entry = None

    def __init__(self, table, viewer):
        QTableWidget.__init__(self)
        self.table = table
        self.viewer = viewer
        self.format()
        self.clicked.connect(self.selection_change_handle)

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

    def selection_change_handle(self):
        current_entry = self.get_current_selection()
        if self.prev_entry is current_entry:
            self.set_hidden(not self.viewer.isHidden())
        else:
            self.prev_entry = current_entry
            self.set_hidden(False)
            self.viewer.draw_view(current_entry)

    def get_current_selection(self):
        current_row = self.currentRow()
        entry_idx = int(self.item(current_row, 1).text())
        return self.table.list[entry_idx]

    def set_hidden(self, condition):
        self.viewer.set_hidden(condition)


class LinkedMonsterTable(LinkedTableWidget):
    def contextMenuEvent(self, event):
        entry = self.get_current_selection()

        menu = QMenu(self)
        add_action = menu.addAction("Add to initiative")
        add_x_action = menu.addAction("Add X to initiative")
        if hasattr(entry, "spells"):
            menu.addSeparator()
            add_spellbook = menu.addAction("Add monster's spells to bookmark")
        else:
            add_spellbook = None
        menu.addSeparator()
        remove = menu.addAction("Remove from Bookmark")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        if action == add_action:
            entry.add_to_encounter()
        if action == add_x_action:
            x, ok = QInputDialog.getInt(self, 'Add Monster', 'How many?')
            if ok:
                entry.add_to_encounter(x)
        elif action == remove:
            self.remove_rows()
        elif action == add_spellbook:
            entry.addSpells()

    def set_hidden(self, condition):
        self.viewer.set_hidden(condition)
        self.viewer.button_bar.setHidden(condition)


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
        remove_bookmark = menu.addAction("Remove from bookmark")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        if action == remove_bookmark:
            self.remove_rows()


class BookmarkWidget(QFrame):
    SPELL_TAB = 0
    DICE_TAB = 1

    def __init__(self, monster_table, monster_viewer, spell_table, spell_viewer):
        super().__init__()
        self.monster_table = monster_table
        self.spell_table = spell_table
        self.monster_viewer = monster_viewer
        self.spell_viewer = spell_viewer
        self.bookmark_frame = QFrame()
        self.bookmark_frame.setMaximumHeight(300)
        self.button_bar = QFrame()
        self.button_bar.setLayout(QHBoxLayout())
        bookmark_layout = QHBoxLayout()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum))

        self.spell_bookmark = LinkedSpellTable(self.spell_table, self.spell_viewer)
        self.monster_bookmark = LinkedMonsterTable(self.monster_table, self.monster_viewer)
        self.monster_tabWidget = QTabWidget()
        self.monster_tabWidget.addTab(self.monster_bookmark, "Monster")

        self.spell_tabWidget = QTabWidget()
        self.spell_tabWidget.addTab(self.spell_bookmark, "Spell")

        self.dice_bookmark = QFrame()
        dice_layout = QVBoxLayout()
        for i in range(5):
            dice_layout.addWidget(DiceBox().frame)
        dice_help_button = QPushButton("Help")
        dice_help_button.clicked.connect(self.dice_instructions)
        dice_layout.addWidget(dice_help_button)
        self.dice_bookmark.setLayout(dice_layout)
        self.spell_tabWidget.addTab(self.dice_bookmark, "Dice")

        bookmark_layout.addWidget(self.monster_tabWidget)
        bookmark_layout.addWidget(self.spell_tabWidget)
        self.bookmark_frame.setLayout(bookmark_layout)

        self.clear_bookmark_button = QPushButton("Clear Bookmark")
        self.toggle_bookmark_button = QPushButton("Toggle Bookmark")
        self.button_bar.layout().setContentsMargins(0, 0, 0, 0)
        self.button_bar.layout().addWidget(self.clear_bookmark_button)
        self.button_bar.layout().addWidget(self.toggle_bookmark_button)

        self.layout().addWidget(self.bookmark_frame)
        self.layout().addWidget(self.button_bar)

        self.bookmark_frame.setHidden(True)
        self.hidden = True

    def dice_instructions(self):
        sNexus.printSignal.emit("\nEither input diceroll in format xdy+z, AttackBonus|DamageRoll, or"
                                    " AttackBonus, DamageRoll\nExample: 1d20+6\n5|2d6+3\n5, 2d6+3\n")
    def toggle_hide(self):
        self.hidden = not self.hidden
        self.bookmark_frame.setHidden(self.hidden)


class DiceBox:
    def __init__(self):
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
                    bonus, dmg_dice = roll.split("|")
                    dmg = aux.roll_function(dmg_dice)
                    atk_roll = aux.\
                        roll_function("1d20")
                    atk = atk_roll + int(bonus)
                    sNexus.printSignal.emit("Dice rolls ({}): {}[{}], {} damage".format(roll, atk, atk_roll, dmg))
                else:
                    result = aux.roll_function(roll)
                    sNexus.printSignal.emit("Dice rolls ({}): {}".format(roll, result[0]))
            except:
                sNexus.printSignal.emit("Invalid dice format\nPress help for info")
        self.button.clicked.connect(lambda: perform_roll(self))