from dependencies.monster import Monster
from dependencies.spell import Spell
from dependencies.item import Item
from dependencies.searchable_tables import MonsterTableWidget, SpellTableWidget, ItemTableWidget
from dependencies.toolbox import ToolboxWidget
from dependencies.views import MonsterViewer, SpellViewer, ItemViewer
from dependencies.input_tables import PlayerTable, EncounterTable
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidgetItem, QTextEdit, QVBoxLayout, \
    QHBoxLayout, QTabWidget, QFrame, QSizePolicy
import sys, json, os

from random import randint

class DMTool(QWidget):
    SEARCH_BOX_WIDTH = 200

    def __init__(self):
        super().__init__()
        # self.rh = RequestHandler(addr='http://dnd5eapi.co/api/')
        self._setup_ui()
        self.load_meta()

        # test if all monsters in DB can be interpreted
        # for monster in self.monster_table_widget.list:
        #     print(monster.name, monster.extract_spellbook())

        # test if all the spells in DB can be interpreted
        # for spell in self.spell_table_widget.list:
        #     print(spell.index)
        #     self.spell_viewer.draw_view(spell)

    def _setup_ui(self):
        """
        Layout is a windowLayout with a horizontal box on the left and a tab widget on the right
        :return:
        """
        self.setWindowTitle("RainyDM - Alpha")
        self.setGeometry(100, 100, 1280, 720)
        window_layout = QHBoxLayout()
        # Left side tab
        self.tab_widget = QTabWidget()

        # Viewers
        self.monster_viewer = MonsterViewer()
        spell_viewer_layout = QVBoxLayout()
        self.spell_viewer = SpellViewer()
        self.item_viewer = ItemViewer()

        # Text box
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setFontPointSize(10)
        self.text_box.setMaximumWidth(530)
        self.text_box.setMaximumHeight(250)
        spell_viewer_layout.addWidget(self.spell_viewer)
        # spell_viewer_layout.addWidget(self.item_viewer)
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

        # Item table
        self.item_table_widget = ItemTableWidget(self)
        self.item_table_widget.load_list("./item", "resources/Compendiums/Items Compendium 1.7.0.xml", Item)
        self.item_table_widget.fill_table()
        self.item_table_widget.define_filters()
        self.item_table_widget.layout().addWidget(self.item_viewer)
        # for item in self.item_table_widget.list:
        #     print(item.name)
        #     print(item.type)
        #     print(item.text)

        # inserting tables into tab
        self.tab_widget.addTab(self.monster_table_widget, "Monster")
        self.tab_widget.addTab(self.spell_table_widget, "Spell")
        self.tab_widget.addTab(self.item_table_widget, "Item")

        # Initiative list
        self.encounter_table = EncounterTable(self)

        # encounter buttons - maybe move these to the subclass?
        button_layout = QHBoxLayout()
        top_button_layout = QHBoxLayout()
        self.sort_init_button = QPushButton("Sort Initiative")
        self.roll_init_button = QPushButton("Roll Initiative")
        # self.add_players_button = QPushButton("Add Players")
        self.clear_encounter_button = QPushButton("Clear Encounter")
        self.clear_toolbox_button = QPushButton("Clear Toolbox")
        self.save_encounter_button = QPushButton("Save Encounter")
        self.load_encounter_button = QPushButton("Load Encounter")
        button_layout.addWidget(self.sort_init_button)
        button_layout.addWidget(self.roll_init_button)
        top_button_layout.addWidget(self.save_encounter_button)
        top_button_layout.addWidget(self.load_encounter_button)
        # button_layout.addWidget(self.add_players_button)
        button_layout.addWidget(self.clear_encounter_button)
        button_layout.addWidget(self.clear_toolbox_button)
        top_button_layout.addStretch(0)

        # "{{:<{}}}".format(length) - format or aligning tabs

        # toolbox
        self.toolbox_widget = ToolboxWidget(self)
        toolbox_layout = QVBoxLayout()
        toolbox_layout.addWidget(self.toolbox_widget.frame)

        encounter_frame = QFrame()
        encounter_layout = QVBoxLayout()
        encounter_layout.addLayout(top_button_layout)
        encounter_layout.addWidget(self.encounter_table.frame)
        encounter_layout.addLayout(button_layout)
        encounter_layout.addLayout(toolbox_layout)
        encounter_frame.setLayout(encounter_layout)
        self.tab_widget.addTab(encounter_frame, "Encounter")

        # player tab
        player_table_frame = QFrame()
        player_table_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.add_player_button = QPushButton("Add Player")
        self.add_player_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.player_table_widget = PlayerTable(self)
        button_layout.addWidget(self.add_player_button)
        button_layout.addStretch(0)
        player_table_layout.addWidget(self.player_table_widget)
        player_table_layout.addLayout(button_layout)
        player_table_frame.setLayout(player_table_layout)
        self.tab_widget.addTab(player_table_frame, "Players")

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

        self.encounter_table.itemClicked.connect(
            lambda: self.monster_clicked_handle(self.encounter_table))

        self.item_table_widget.table.itemClicked.connect(
            lambda: self.item_clicked_handle(self.item_table_widget.table))

        # self.add_players_button.clicked.connect(self.add_players_handle)
        self.sort_init_button.clicked.connect(self.sort_init_handle)
        self.roll_init_button.clicked.connect(self.roll_init_handle)
        self.save_encounter_button.clicked.connect(self.encounter_table.save)
        self.load_encounter_button.clicked.connect(lambda: self.encounter_table.load(self.monster_table_widget))
        self.clear_encounter_button.clicked.connect(self.clear_encounter_handle)
        self.clear_toolbox_button.clicked.connect(self.clear_toolbox_handle)

        self.add_player_button.clicked.connect(self.add_player)

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

    def item_clicked_handle(self, table):
        current_row = table.currentRow()
        item_idx = int(table.item(current_row, 1).text())
        item = self.item_table_widget.list[item_idx]
        self.item_viewer.draw_view(item)
        # print(dir(item))
        # print(item.text)
        # self.item_viewer.draw_view(item)

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
            self.toolbox_widget.spell_toolbox.setItem(row_position, 2, QTableWidgetItem(str(spell.level)))

    # def add_to_encounter(self, monster, number=1):
    #     table = self.encounter_table
    #     for itt in range(number):
    #         row_position = table.rowCount()
    #         table.insertRow(row_position)
    # 
    #         if type(monster) == list:
    #             for itt, value in enumerate(monster):
    #                 table.setItem(row_position, itt, QTableWidgetItem(str(value)))
    #         else:
    #             table.setItem(row_position, table.NAME_COLUMN, QTableWidgetItem(str(monster)))
    #             table.setItem(row_position, table.INDEX_COLUMN, QTableWidgetItem(str(monster.index)))
    #             table.setItem(row_position, table.HP_COLUMN, QTableWidgetItem(str(monster.hp_no_dice)))
    #         table.calculate_encounter_xp()

    def add_player(self, player=None):
        table = self.player_table_widget
        row_position = table.rowCount()
        table.insertRow(row_position)
        table.setItem(row_position, 0, QTableWidgetItem(""))  # necessary so that the row isn't picked up in garbage collection
        if type(player) == list:
            for itt, value in enumerate(player):
                table.setItem(row_position, itt, QTableWidgetItem(str(value)))

    def add_players_handle(self):
        encounter_table = self.encounter_table
        encounter_rows = encounter_table.rowCount()
        encounter_names = []
        for itt in range(encounter_rows):
            encounter_names.append(encounter_table.item(itt, encounter_table.NAME_COLUMN).text())

        player_table = self.player_table_widget
        player_rows = player_table.rowCount()
        for itt in range(player_rows):
            item = player_table.item(itt, player_table.NAME_COLUMN)
            if item is None or item.text() == "":
                continue
            name = item.text()
            init = player_table.item(itt, player_table.INITIATIVE_COLUMN)
            if init is None or init.text() == "":
                continue
            if name in encounter_names:
                idx = encounter_names.index(name)
                self.encounter_table.setItem(idx, self.encounter_table.INIT_COLUMN,
                                             QTableWidgetItem(init.text()))
                continue
            else:
                init = player_table.item(itt, player_table.INITIATIVE_COLUMN)
                if init is None:
                    init = ""
                else:
                    init = init.text()
                self.encounter_table.add_to_encounter([name, -1, init, "", "", ""])

    def sort_init_handle(self):
        self.add_players_handle()
        rows = self.encounter_table.rowCount()
        for row in range(rows):
            item = self.encounter_table.item(row, self.encounter_table.INIT_COLUMN)
            try:
                number = int(item.text())
            except:
                number = 0
            new_item = QTableWidgetItem()
            new_item.setData(QtCore.Qt.DisplayRole, number)
            self.encounter_table.setItem(row, self.encounter_table.INIT_COLUMN, new_item)
        self.encounter_table.sortByColumn(self.encounter_table.INIT_COLUMN, 1)

    def roll_init_handle(self):
        encounter_table = self.encounter_table
        encounter_rows = encounter_table.rowCount()
        for itt in range(encounter_rows):
            idx = int(encounter_table.item(itt, encounter_table.INDEX_COLUMN).text())
            if idx is -1:  # entry is a player
                continue
            monster = self.monster_table_widget.list[idx]
            roll = self.roll("1d20")
            encounter_table.setItem(itt, encounter_table.INIT_COLUMN, QTableWidgetItem(str(roll + monster.initiative)))

    def clear_encounter_handle(self):
        self.encounter_table.clear()
        self.encounter_table.setRowCount(0)
        self.encounter_table.format()

    def clear_toolbox_handle(self):
        self.toolbox_widget.monster_toolbox.clear()
        self.toolbox_widget.monster_toolbox.setRowCount(0)
        self.toolbox_widget.spell_toolbox.clear()
        self.toolbox_widget.spell_toolbox.setRowCount(0)

    @staticmethod
    def roll(dice):
        output = []
        split = dice.split("+")
        if len(split) is 1 and "d" not in split[0]:  # in the case of X damage, without a roll
            return int(split[0])
        for itt, each in enumerate(split):
            if "d" in each:
                amount, size = each.split("d")
                rolled = 0
                for i in range(int(amount)):
                    roll = randint(1, int(size))
                    rolled = rolled + roll
                output.append(rolled)
            else:
                if itt is 0:
                    output[0] = int(each)
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
            halved = [max(1, int(dr/2)) for dr in damage_roll]
        else:
            halved = max(1, int(damage_roll/2))
        s = s + "for {} ({} halved)".format(str(damage_roll), str(halved))
        self.text_box.append(s)

    def extract_and_add_spellbook(self, monster):
        spells = monster.extract_spellbook()
        if spells is not None:
            for spell in spells:
                self.add_to_toolbox_spell(self.spell_table_widget.find_entry("name", spell))


    def load_meta(self):
        if not os.path.exists("metadata/"):
            os.mkdir("metadata")
        if os.path.exists("metadata/session.txt"):
            with open("metadata/session.txt", "r") as f:
                meta_dict = eval(f.read())
                for monster_tuple in meta_dict['toolbox_meta']:
                    self.add_to_toolbox(monster_tuple)
                for monster_tuple in meta_dict['initiative_meta']:
                    self.encounter_table.add_to_encounter(monster_tuple)
                for player_tuple in meta_dict['player_meta']:
                    self.add_player(player_tuple)

    def closeEvent(self, event):
        toolbox_meta = self.toolbox_widget.monster_toolbox.jsonlify()
        initiative_meta = self.encounter_table.jsonlify()
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
