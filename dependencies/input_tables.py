from PyQt5.QtWidgets import QTableWidget, QHeaderView, QMenu, QVBoxLayout, QFrame, QLabel, QTableWidgetItem, \
    QInputDialog, QFileDialog
import os


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

class EncounterTable(InputTableWidget):
    INIT_COLUMN = 2
    HP_COLUMN = 3
    DAMAGE_COLUMN = 4
    DESCRIPTION_COLUMN = 5
    PLAYER_INDEX = -1
    xp_string = "Total XP: "

    def __init__(self, parent):
        super().__init__(parent)
        self.cellChanged.connect(self.data_changed_handle)
        self.layout = QVBoxLayout()
        self.frame = QFrame()
        self.xp_label = QLabel(self.xp_string)
        self.layout.addWidget(self)
        self.layout.addWidget(self.xp_label)
        self.frame.setLayout(self.layout)

    def format(self):
        columns = 6
        self.setColumnCount(columns)
        self.setHorizontalHeaderLabels(["Name", "_index", "Initiative", "HP", "Damage Taken", "Description"])
        self.horizontalHeader().setSectionResizeMode(self.DESCRIPTION_COLUMN, QHeaderView.Stretch)
        self.setShowGrid(True)
        self.setColumnWidth(self.NAME_COLUMN, 150)
        self.verticalHeader().hide()
        self.setColumnHidden(1, True)

    def contextMenuEvent(self, event):
        current_row = self.currentRow()
        addToolbox = None
        add_spellbook = None

        if current_row == -1:  # empty table
            return None
        monster_idx = int(self.item(current_row, 1).text())

        action_indexes = []
        action_menu_handles = []
        menu = QMenu(self)
        if monster_idx is not -1:
            monster = self.parent.monster_table_widget.list[monster_idx]
            if hasattr(monster, "action_list"):
                for itt, action in enumerate(monster.action_list):
                    if hasattr(action, "attack"):
                        action_indexes.append(itt)
                        action_menu_handles.append(menu.addAction(action.name))

        menu.addSeparator()
        removeAction = menu.addAction("Remove from initiative")

        if monster_idx is not -1:
            addToolbox = menu.addAction("Add to toolbox")
            add_spellbook = menu.addAction("Add monster's spells to toolbox")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        elif action == addToolbox:
            if monster_idx == -1:  # monster is a player
                return
            monster = self.parent.monster_table_widget.list[monster_idx]
            self.parent.add_to_toolbox(monster)
        elif action == removeAction:
            self.remove_rows()
            self.calculate_encounter_xp()
        elif action in action_menu_handles:
            idx = action_menu_handles.index(action)
            attack = monster.action_list[action_indexes[idx]]
            if hasattr(attack, "attack"):
                self.parent.print_attack(monster, attack.attack)
        elif action is add_spellbook:
            if monster_idx is not -1:
                self.parent.extract_and_add_spellbook(monster)

    def data_changed_handle(self, row, column):
        if column == self.DAMAGE_COLUMN:
            damage = -self._convert_to_int(row, column)
            hp = self._convert_to_int(row, self.HP_COLUMN)
            if damage is False or hp is False:
                pass
            else:
                monster = self.parent.monster_table_widget.list[int(self.item(row, self.INDEX_COLUMN).text())]
                self.item(row, self.HP_COLUMN).setText(str(min(hp + damage, int(monster.hp_no_dice))))
            self.item(row, column).setText("")

    def _convert_to_int(self, row, column):
        value = self.item(row, column).text()
        if value == "" or value is None:
            return False
        try:
            return int(value)
        except:
            return False

    def calculate_encounter_xp(self):
        if self.parent.version == "3.5":
            return '-'
        total_xp = 0
        monsters = 0
        players = 0
        player_modifier = 0
        monster_modifier = 1
        multipliers = [0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
        rows = self.rowCount()
        for row in range(rows):
            item = self.item(row, self.INDEX_COLUMN)
            if item is None:
                continue
            idx = int(item.text())
            if idx is self.PLAYER_INDEX:  # entry is a player
                players = players + 1
                continue
            monster = self.parent.monster_table_widget.list[idx]
            total_xp = total_xp + monster.xp
            monsters = monsters + 1
        if players < 3:
            player_modifier = 1
        elif players > 5:
            player_modifier = -1
        if monsters == 2:
            monster_modifier = 2
        elif monsters < 7:
            monster_modifier = 3
        elif monsters < 10:
            monster_modifier = 4
        elif monsters < 15:
            monster_modifier = 5
        else:
            monster_modifier = 6
        modifier = multipliers[monster_modifier + player_modifier]
        # print("dependencies.input_tables.calculate_encounter_xp:", total_xp * modifier)
        self.xp_label.setText(self.xp_string + str(total_xp * modifier))
        return total_xp * modifier

    def save(self):
        if not os.path.exists("encounters"):
            os.mkdir("encounters")
        rows = self.rowCount()
        names = []
        inits = []
        lives = []
        descs = []
        for row in range(rows):
            item = self.item(row, self.INDEX_COLUMN)
            if item is None:
                continue
            idx = int(item.text())
            if idx is self.PLAYER_INDEX:  # entry is a player
                continue
            names.append(self.item(row, self.NAME_COLUMN).text())
            init = self.item(row, self.INIT_COLUMN)
            if init is not None:
                inits.append(init.text())
            else:
                inits.append("")
            lives.append(self.item(row, self.HP_COLUMN).text())
            desc = self.item(row, self.DESCRIPTION_COLUMN)
            if desc is not None:
                descs.append(desc.text())
            else:
                descs.append("")

        if len(names) is 0:
            return
        f = "{{:<{}}} | {{:<{}}} | {{:<{}}} | {{:<{}}}\n".format(
            len(max(names, key=len)),
            len(max(inits, key=len)),
            len(max(lives, key=len)),
            len(max(descs, key=len))
        )
        encounter_name, ok = QInputDialog.getText(self, "Save", "Encounter Name:")
        if not ok or encounter_name.strip() == "":
            return
        elif encounter_name[-4:] != ".txt":
            encounter_name = encounter_name + ".txt"

        with open("encounters/" + encounter_name, 'w') as file:
            for name, init, hp, desc in zip(names, inits, lives, descs):
                file.write(f.format(name, init, hp, desc))

    def load(self, monster_table):
        filename, _ = QFileDialog.getOpenFileName(self, "Select encounter", "encounters", "Text files (*.txt)")
        if filename and os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f.readlines():
                    split = line.split('|')
                    name = split[0].strip()
                    init = split[1].strip()
                    hp = split[2].strip()
                    desc = split[3].strip()
                    monster = monster_table.find_entry("name", name)
                    if monster:
                        self.add_to_encounter(monster, init=init, hp=hp, desc=desc)

    def add_to_encounter(self, monster, number=1, init=None, hp=None, desc=None):
        for itt in range(number):
            row_position = self.rowCount()
            self.insertRow(row_position)

            if type(monster) == list:
                for itt, value in enumerate(monster):
                    self.setItem(row_position, itt, QTableWidgetItem(str(value)))
            else:
                self.setItem(row_position, self.NAME_COLUMN, QTableWidgetItem(str(monster)))
                self.setItem(row_position, self.INDEX_COLUMN, QTableWidgetItem(str(monster.index)))
                if hp is not None:
                    self.setItem(row_position, self.HP_COLUMN, QTableWidgetItem(str(hp)))
                else:
                    self.setItem(row_position, self.HP_COLUMN, QTableWidgetItem(str(monster.hp_no_dice)))
                if init is not None:
                    self.setItem(row_position, self.INIT_COLUMN, QTableWidgetItem(str(init)))
                if desc is not None:
                    self.setItem(row_position, self.DESCRIPTION_COLUMN, QTableWidgetItem(str(desc)))

            self.calculate_encounter_xp()

class PlayerTable(InputTableWidget):
    PLAYER_COLUMN = 1
    INITIATIVE_COLUMN = 2
    PASSIVE_PERCEPTION_COLUMN = 3
    PASSIVE_INSIGHT_COLUMN = 4

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        addAction = menu.addAction("Add player")
        removeAction = menu.addAction("Remove player")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        current_row = self.currentRow()
        if action == addAction:
            self.parent.add_player()
        elif action == removeAction:
            self.remove_rows()

    def format(self):
        columns = 5
        self.setColumnCount(columns)
        self.setHorizontalHeaderLabels(["Name", "Player", "Initiative", "Passive Insight",
                                        "Passive Perception", "Inactive"])
        self.setShowGrid(True)
        for i in range(columns):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        self.setColumnWidth(self.NAME_COLUMN, 150)
        self.verticalHeader().hide()
