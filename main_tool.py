from dependencies.monster import Monster
from dependencies.spell import Spell
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidgetItem, QTextEdit, QVBoxLayout, \
    QHBoxLayout, QTabWidget, QFrame
import sys, json, os
from subclasses import MonsterViewer, ToolboxWidget, PlayerTableWidget, \
    InitiativeTableWidget, SpellViewer
from dependencies.searchable_tables import MonsterTableWidget, SpellTableWidget
from random import randint

class DMTool(QWidget):
    SEARCH_BOX_WIDTH = 200

    def __init__(self):
        super().__init__()
        # self.rh = RequestHandler(addr='http://dnd5eapi.co/api/')
        self._setup_ui()
        self.load_meta()

        # test if all monsters in DB can be interpreted
        # for monster in self.monster_list:
        #     print(monster.index)
        #     self.draw_view(monster)

        # test if all the spells in DB can be interpreted
        # for spell in self.spell_table_widget.list:
        #     print(spell.index)
        #     self.spell_viewer.draw_view(spell)

    def _setup_ui(self):
        """
        Layout is a windowLayout with a horizontal box on the left and a tab widget on the right
        :return:
        """
        self.setWindowTitle("Test")
        self.setGeometry(100, 100, 1280, 720)
        window_layout = QHBoxLayout()
        # Left side tab
        self.tab_widget = QTabWidget()

        # Monster viewer
        self.monster_viewer = MonsterViewer()

        # Spell viewer
        spell_viewer_layout = QVBoxLayout()
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setFontPointSize(10)
        self.text_box.setMaximumWidth(530)
        self.text_box.setMaximumHeight(250)
        self.spell_viewer = SpellViewer()
        spell_viewer_layout.addWidget(self.spell_viewer)
        spell_viewer_layout.addWidget(self.text_box)

        ## Tables
        # Spell Table
        self.spell_table_widget = SpellTableWidget(self)
        self.spell_table_widget.load_list("./spell", "resources/Compendiums/Spells Compendium 1.3.0.xml", Spell)
        self.spell_table_widget.fill_table()
        self.spell_table_widget.define_filters()

        # Monster table
        self.monster_table_widget = MonsterTableWidget(self)
        self.monster_table_widget.load_list("./monster", "resources/Compendiums/Bestiary Compendium 2.1.0.xml", Monster)
        self.monster_table_widget.fill_table()
        self.monster_table_widget.define_filters()

        self.tab_widget.addTab(self.monster_table_widget, "Monster")
        self.tab_widget.addTab(self.spell_table_widget, "Spell")

        # Initiative list
        self.initiative_table_widget = InitiativeTableWidget(self)

        # encounter buttons
        button_layout = QHBoxLayout()
        self.sort_init_button = QPushButton("Sort Initiative")
        self.roll_init_button = QPushButton("Roll Initiative")
        self.add_players_button = QPushButton("Add Players")
        self.clear_encounter_button = QPushButton("Clear Encounter")
        self.clear_toolbox_button = QPushButton("Clear Toolbox")
        button_layout.addWidget(self.sort_init_button)
        button_layout.addWidget(self.roll_init_button)
        button_layout.addWidget(self.add_players_button)
        button_layout.addWidget(self.clear_encounter_button)
        button_layout.addWidget(self.clear_toolbox_button)

        # toolbox
        self.toolbox_widget = ToolboxWidget(self)
        toolbox_layout = QVBoxLayout()
        toolbox_layout.addWidget(self.toolbox_widget.frame)

        encounter_frame = QFrame()
        encounter_layout = QVBoxLayout()
        encounter_layout.addWidget(self.initiative_table_widget)
        encounter_layout.addLayout(button_layout)
        encounter_layout.addLayout(toolbox_layout)
        encounter_frame.setLayout(encounter_layout)
        self.tab_widget.addTab(encounter_frame, "Encounter")

        # player tab
        self.player_table_widget = PlayerTableWidget(self)
        self.tab_widget.addTab(self.player_table_widget, "Players")

        window_layout.addWidget(self.tab_widget)
        window_layout.addWidget(self.monster_viewer)
        window_layout.addLayout(spell_viewer_layout)

        self.bind_signals()

        self.setLayout(window_layout)

    def bind_signals(self):
        self.spell_table_widget.table.itemClicked.connect(
            lambda: self.spell_clicked_handle(self.spell_table_widget.table))

        self.toolbox_widget.spell_toolbox.itemClicked.connect(
            lambda: self.spell_clicked_handle(self.toolbox_widget.spell_toolbox))

        self.monster_table_widget.table.itemClicked.connect(
            lambda: self.monster_clicked_handle(self.monster_table_widget.table))

        self.toolbox_widget.monster_toolbox.itemClicked.connect(
            lambda: self.monster_clicked_handle(self.toolbox_widget.monster_toolbox))

        self.initiative_table_widget.itemClicked.connect(
            lambda: self.monster_clicked_handle(self.initiative_table_widget))

        self.add_players_button.clicked.connect(self.add_players_handle)
        self.sort_init_button.clicked.connect(self.sort_init_handle)
        self.roll_init_button.clicked.connect(self.roll_init_handle)
        self.clear_encounter_button.clicked.connect(self.clear_encounter_handle)
        self.clear_toolbox_button.clicked.connect(self.clear_toolbox_handle)

    def spell_clicked_handle(self, table):
        current_row = table.currentRow()
        spell_idx = int(table.item(current_row, 1).text())
        spell = self.spell_table_widget.list[spell_idx]
        self.spell_viewer.draw_view(spell)

    def monster_clicked_handle(self, table):
        current_row = table.currentRow()
        monster_idx = int(table.item(current_row, 1).text())
        if monster_idx == -1:  # monster is a player character
            return
        monster = self.monster_table_widget.list[monster_idx]
        self.monster_viewer.draw_view(monster)

    def spell_search_handle(self):
        self.spell_viewer.draw_view()

    def _fill_monster_table(self, monster_list):
        self.monster_table_widget.table_widget.clear()
        self.monster_table_widget.table_widget.setRowCount(len(monster_list))
        for itt, monster in enumerate(monster_list):
            self.monster_table_widget.table_widget.setItem(itt, 0, QTableWidgetItem(str(monster)))
            self.monster_table_widget.table_widget.setItem(itt, 1, QTableWidgetItem(str(monster.index)))

    def add_to_toolbox(self, monster):
        row_position = self.toolbox_widget.monster_toolbox.rowCount()
        self.toolbox_widget.monster_toolbox.insertRow(row_position)
        if type(monster) == list:
            for itt, value in enumerate(monster):
                self.toolbox_widget.monster_toolbox.setItem(row_position, itt, QTableWidgetItem(str(value)))
        else:
            self.toolbox_widget.monster_toolbox.setItem(row_position, 0, QTableWidgetItem(str(monster)))
            self.toolbox_widget.monster_toolbox.setItem(row_position, 1, QTableWidgetItem(str(monster.index)))

    def add_to_toolbox_spell(self, spell):
        row_position = self.toolbox_widget.spell_toolbox.rowCount()
        self.toolbox_widget.spell_toolbox.insertRow(row_position)
        if type(spell) == list:
            for itt, value in enumerate(spell):
                self.toolbox_widget.spell_toolbox.setItem(row_position, itt, QTableWidgetItem(str(value)))
        else:
            self.toolbox_widget.spell_toolbox.setItem(row_position, 0, QTableWidgetItem(str(spell)))
            self.toolbox_widget.spell_toolbox.setItem(row_position, 1, QTableWidgetItem(str(spell.index)))

    def add_to_encounter(self, monster, number=1):
        table = self.initiative_table_widget
        for itt in range(number):
            row_position = table.rowCount()
            table.insertRow(row_position)

            if type(monster) == list:
                for itt, value in enumerate(monster):
                    table.setItem(row_position, itt, QTableWidgetItem(str(value)))
            else:
                table.setItem(row_position, table._NAME_COLUMN, QTableWidgetItem(str(monster)))
                table.setItem(row_position, table._INDEX_COLUMN, QTableWidgetItem(str(monster.index)))
                table.setItem(row_position, table._HP_COLUMN, QTableWidgetItem(str(monster.hp_no_dice)))

    def add_player(self, player=None):
        table = self.player_table_widget
        row_position = table.rowCount()
        table.insertRow(row_position)
        if type(player) == list:
            for itt, value in enumerate(player):
                table.setItem(row_position, itt, QTableWidgetItem(str(value)))

    def add_players_handle(self):
        encounter_table = self.initiative_table_widget
        encounter_rows = encounter_table.rowCount()
        encounter_names = []
        for itt in range(encounter_rows):
            encounter_names.append(encounter_table.item(itt, encounter_table._NAME_COLUMN).text())

        player_table = self.player_table_widget
        player_rows = player_table.rowCount()
        for itt in range(player_rows):
            item = player_table.item(itt, player_table._NAME_COLUMN)
            if item is None:
                continue
            name = item.text()
            init = player_table.item(itt, player_table._INITIATIVE_COLUMN)
            if init is None:
                init = ""
            if name in encounter_names:
                idx = encounter_names.index(name)
                self.initiative_table_widget.setItem(idx, self.initiative_table_widget._INIT_COLUMN,
                                                     QTableWidgetItem(init.text()))
                continue
            else:
                init = player_table.item(itt, player_table._INITIATIVE_COLUMN)
                if init is None:
                    init = ""
                else:
                    init = init.text()
                self.add_to_encounter([name, -1, init, "", "", ""])

    def sort_init_handle(self):
        rows = self.initiative_table_widget.rowCount()
        for row in range(rows):
            item = self.initiative_table_widget.item(row, self.initiative_table_widget._INIT_COLUMN)
            try:
                number = int(item.text())
            except:
                number = 0
            new_item = QTableWidgetItem()
            new_item.setData(QtCore.Qt.DisplayRole, number)
            self.initiative_table_widget.setItem(row, self.initiative_table_widget._INIT_COLUMN, new_item)
        self.initiative_table_widget.sortByColumn(self.initiative_table_widget._INIT_COLUMN, 1)

    def roll_init_handle(self):
        encounter_table = self.initiative_table_widget
        encounter_rows = encounter_table.rowCount()
        for itt in range(encounter_rows):
            idx = int(encounter_table.item(itt, encounter_table._INDEX_COLUMN).text())
            if idx is -1:  # entry is a player
                continue
            monster = self.monster_table_widget.list[idx]
            roll = self.roll("1d20")
            encounter_table.setItem(itt, encounter_table._INIT_COLUMN, QTableWidgetItem(str(roll + monster.initiative)))

    def clear_encounter_handle(self):
        self.initiative_table_widget.clear()
        self.initiative_table_widget.setRowCount(0)
        self.initiative_table_widget.format()

    def clear_toolbox_handle(self):
        self.toolbox_widget.monster_toolbox.clear()
        self.toolbox_widget.monster_toolbox.setRowCount(0)
        self.toolbox_widget.spell_toolbox.clear()
        self.toolbox_widget.spell_toolbox.setRowCount(0)

    @staticmethod
    def roll(dice):
        output = []
        split = dice.split("+")
        for itt, each in enumerate(split):
            if "d" in each:
                amount, size = each.split("d")
                rolled = 0
                for i in range(int(amount)):
                    roll = randint(1, int(size))
                    rolled = rolled + roll
                output.append(rolled)
            else:
                output[itt-1] = output[itt-1] + int(each)
        if len(output) == 1:
            return output[0]
        return output

    def print_attack(self, monster, attack):
        comp = attack.split("|")
        s = "{} uses {} -- ".format(monster.name, comp[0])
        if comp[1] not in ["", " "]:  # this means there's an attack roll and a damage roll
            attack_roll = self.roll("1d20+"+comp[1])
            s = s + "{}({}) to hit -- ".format(attack_roll, attack_roll-int(comp[1]))

        damage_roll = self.roll(comp[2])
        if type(damage_roll) is list:
            halved = [int(dr/2) for dr in damage_roll]
        else:
            halved = int(damage_roll/2)
        s = s + "for {} ({} halved)".format(str(damage_roll), str(halved))
        self.text_box.append(s)

    def load_meta(self):
        if not os.path.exists("metadata/"):
            os.mkdir("metadata")
        if os.path.exists("metadata/session.txt"):
            with open("metadata/session.txt", "r") as f:
                meta_dict = eval(f.read())
                for monster_tuple in meta_dict['toolbox_meta']:
                    self.add_to_toolbox(monster_tuple)
                for monster_tuple in meta_dict['initiative_meta']:
                    self.add_to_encounter(monster_tuple)
                for player_tuple in meta_dict['player_meta']:
                    self.add_player(player_tuple)

    def closeEvent(self, event):
        toolbox_meta = self.toolbox_widget.monster_toolbox.jsonlify()
        initiative_meta = self.initiative_table_widget.jsonlify()
        player_meta = self.player_table_widget.jsonlify()

        with open("metadata/session.txt", "w") as f:
            json.dump(dict(
                toolbox_meta=toolbox_meta,
                initiative_meta=initiative_meta,
                player_meta=player_meta
            ), f)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    form = DMTool()  # We set the form to be our ExampleApp (design)

    form.show()  # Show the form
    sys.exit(app.exec_())  # and execute the app
