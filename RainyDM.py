from dependencies.monster import Monster, Monster35
from dependencies.spell import Spell, Spell35
from dependencies.item import Item, Item35
from dependencies.searchable_tables import MonsterTableWidget, SpellTableWidget, ItemTableWidget
from dependencies.toolbox import ToolboxWidget
from dependencies.encounter import MonsterWidget
from dependencies.views import MonsterViewer, SpellViewer, ItemViewer
from dependencies.input_tables import PlayerTable, PlayerFrame
from dependencies.encounter import EncounterWidget
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QAction, QPushButton, QTableWidgetItem, QTextEdit, QVBoxLayout, \
    QHBoxLayout, QTabWidget, QFrame, QSizePolicy, QMainWindow, QLabel, QMessageBox, QSpacerItem
import sys, json, os
import html2text
import pyperclip
import time
from dependencies.auxiliaries import rollFunction

MONSTER_TAB = 0
SPELL_TAB = 1

class DMTool(QMainWindow):
    SEARCH_BOX_WIDTH = 200

    def __init__(self):
        super().__init__()

        self.load_meta()
        self._setup_ui()
        self._setup_menu()
        self.bind_signals()
        self.load_session()
        self._display_ui()
        # self.db_editor = DBEditor(self, self.monster_table_widget.list[0])
        # self.db_editor.show()

        # for monster in self.monster_table_widget.list:
            # monster.extract_spellbook()
            # if monster.size == "LARGE":
            #     print(monster.name, monster.source)

        # for spell in self.spell_table_widget.list:
        #     print(spell.index)
        #     self.spell_viewer.draw_view(spell)

    def _setup_ui(self):
        """
        Layout is a windowLayout with a horizontal box on the left and a tab widget on the right
        :return:
        """
        self.setWindowIcon(QIcon(os.path.join('assets', 'tear.png')))
        self.setWindowTitle("RainyDM")
        self.setGeometry(100, 100, 1280, 720)
        self.window_frame = QFrame()
        self.window_layout = QHBoxLayout()
        # Left side tab
        self.tab_widget = QTabWidget()

        # Viewers
        self.monster_viewer = MonsterViewer()
        spell_viewer_layout = QVBoxLayout()
        self.spell_frame = QFrame()
        self.spell_frame.setLayout(spell_viewer_layout)
        self.spell_frame.setContentsMargins(0, 0, 0, 0)
        self.spell_frame.setFrameStyle(0)
        self.spell_viewer = SpellViewer()
        self.item_viewer = ItemViewer()

        # Text box
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setFontPointSize(10)
        # self.text_box.setMaximumWidth(530)
        # self.text_box.setMaximumHeight(250)
        spell_viewer_layout.addWidget(self.spell_viewer)
        spell_viewer_layout.addWidget(self.text_box)
        spell_viewer_layout.setStretch(1, 1)
        spell_viewer_layout.setStretch(0, 2)


        ## Tables
        # Spell Table
        self.spell_table_widget = SpellTableWidget(self, self.spell_viewer)

        # Monster table
        self.monster_table_widget = MonsterTableWidget(self, self.monster_viewer)

        # Item table
        self.item_table_widget = ItemTableWidget(self, self.item_viewer)
        self.item_table_widget.layout().addWidget(self.item_viewer)

        self.load_resources()

        # inserting tables into tab
        self.tab_widget.addTab(self.monster_table_widget, "Monster")
        self.tab_widget.addTab(self.spell_table_widget, "Spell")
        self.tab_widget.addTab(self.item_table_widget, "Item")

        # Initiative list
        self.encounterWidget = EncounterWidget(self.monster_viewer)

        # encounter buttons - maybe move these to the subclass?
        # encounter_button_layout = QHBoxLayout()
        # top_button_layout = QHBoxLayout()
        # self.sort_init_button = QPushButton("Sort Initiative")
        # self.roll_init_button = QPushButton("Roll Initiative")
        # # self.add_players_button = QPushButton("Add Players")
        # self.clear_encounter_button = QPushButton("Clear Encounter")
        # self.save_encounter_button = QPushButton("Save Encounter")
        # self.load_encounter_button = QPushButton("Load Encounter")
        # encounter_button_layout.addWidget(self.sort_init_button)
        # encounter_button_layout.addWidget(self.roll_init_button)
        # top_button_layout.addWidget(self.save_encounter_button)
        # top_button_layout.addWidget(self.load_encounter_button)
        # # button_layout.addWidget(self.add_players_button)
        # encounter_button_layout.addWidget(self.clear_encounter_button)
        # top_button_layout.addStretch(0)

        # Toolbox buttons
        toolbox_button_layout = QHBoxLayout()
        self.clear_toolbox_button = QPushButton("Clear Toolbox")
        self.toggle_toolbox_button = QPushButton("Toggle Toolbox")
        toolbox_button_layout.addWidget(self.clear_toolbox_button)
        toolbox_button_layout.addWidget(self.toggle_toolbox_button)

        # toolbox
        self.toolbox_widget = ToolboxWidget(self)

        encounter_frame = QFrame()
        encounter_layout = QVBoxLayout()
        # encounter_layout.addLayout(top_button_layout)
        encounter_layout.addWidget(self.encounterWidget)
        # encounter_layout.addLayout(encounter_button_layout)
        encounter_layout.addWidget(self.toolbox_widget)
        encounter_frame.setLayout(encounter_layout)
        self.tab_widget.addTab(encounter_frame, "Encounter")

        # player tab
        player_table_frame = QFrame()
        player_table_layout = QVBoxLayout()
        encounter_button_layout = QHBoxLayout()
        self.add_player_button = QPushButton("Add Player")
        self.add_player_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.playerWidget = PlayerTable()
        encounter_button_layout.addWidget(self.add_player_button)
        encounter_button_layout.addStretch(0)
        player_table_layout.addWidget(self.playerWidget)
        player_table_layout.addLayout(encounter_button_layout)
        player_table_frame.setLayout(player_table_layout)
        self.tab_widget.addTab(player_table_frame, "Players")

        # monster_view_frame = QFrame()
        monster_view_layout = QVBoxLayout()
        self.monster_view_frame = QFrame()
        self.monster_view_frame.setLayout(monster_view_layout)
        # monster_view_frame.setLayout(monster_view_layout)
        self.monster_viewer_bar = QFrame()
        layout = QHBoxLayout()
        monster_plaintext_button = QPushButton("Copy plaintext to clipboard")
        monster_plaintext_button.clicked.connect(self.copy_plaintext_monster_to_clipboard)
        layout.addWidget(monster_plaintext_button)
        self.monster_viewer_bar.setLayout(layout)

        monster_view_layout.addWidget(self.monster_viewer)
        monster_view_layout.addWidget(self.monster_viewer_bar)
        monster_view_layout.setStretch(0, 2)

        self.window_layout.addWidget(self.tab_widget)
        self.window_layout.addWidget(self.monster_view_frame)
        self.window_layout.addWidget(self.spell_frame)
        self.window_layout.setStretch(0, 6)
        self.window_layout.setStretch(1, 5)
        self.window_layout.setStretch(2, 5)

        self.monster_viewer_bar.setHidden(True)

        self.window_frame.setLayout(self.window_layout)

    def _setup_menu(self):
        ### Menubar
        menu = self.menuBar()
        version = menu.addMenu("Version")
        button_3_5 = QAction("3.5 Edition", self)
        button_3_5.setStatusTip("3.5 Edition")
        version.addAction(button_3_5)
        button_5 = QAction("5th Edition", self)
        button_5.setStatusTip("5th Edition")
        version.addAction(button_5)
        button_5.triggered.connect(lambda: self.change_version("5"))
        button_3_5.triggered.connect(lambda: self.change_version("3.5"))

        experimental = menu.addMenu("Experimental")
        button_plain_text = QAction("Plain text monsters", self, checkable=True)
        button_plain_text.setStatusTip("Plain text monsters")
        button_plain_text.triggered.connect(self.toggle_monster_bar)
        self.edit_entries_action = QAction("Edit Entries", self, checkable=True)
        self.edit_entries_action.setStatusTip("Enable edit data entries")
        # development
        self.edit_entries_action.setChecked(True)  # default ON
        self.enable_edit_data_entries()
        ##
        self.edit_entries_action.triggered.connect(self.enable_edit_data_entries)

        experimental.addAction(button_plain_text)
        experimental.addAction(self.edit_entries_action)

        tools = menu.addMenu("Tools")
        self.button_hide_spells = QAction("Spells", tools, checkable=True)
        self.button_hide_spells.setChecked(True)
        self.button_hide_spells.setStatusTip("Spells")
        self.button_hide_spells.triggered.connect(self.toggle_spells)

        tools.addAction(self.button_hide_spells)

        self.window_frame.setLayout(self.window_layout)

    def enable_edit_data_entries(self):
        cond = self.edit_entries_action.isChecked()
        self.monster_table_widget.EDITABLE = cond
        self.spell_table_widget.EDITABLE = cond
        self.item_table_widget.EDITABLE = cond

    def bind_signals(self):
        self.spell_table_widget.table.selectionModel().selectionChanged.connect(
            lambda: self.spell_clicked_handle(self.spell_table_widget.table))

        self.toolbox_widget.spell_toolbox.selectionModel().selectionChanged.connect(
            lambda: self.spell_clicked_handle(self.toolbox_widget.spell_toolbox))

        self.monster_table_widget.table.selectionModel().selectionChanged.connect(
            lambda: self.monster_clicked_handle(self.monster_table_widget.table))

        self.toolbox_widget.monster_toolbox.selectionModel().selectionChanged.connect(
            lambda: self.monster_clicked_handle(self.toolbox_widget.monster_toolbox))

        self.item_table_widget.table.selectionModel().selectionChanged.connect(
            lambda: self.item_clicked_handle(self.item_table_widget.table))

        self.encounterWidget.add_players_button.clicked.connect(self.addPlayersToCombat)
        self.encounterWidget.sort_init_button.clicked.connect(self.sort_init_handle)
        self.encounterWidget.roll_init_button.clicked.connect(self.roll_init_handle)
        self.encounterWidget.save_encounter_button.clicked.connect(self.encounterWidget.save)
        self.encounterWidget.load_encounter_button.clicked.connect(lambda: self.encounterWidget.load(self.monster_table_widget))
        self.encounterWidget.clear_encounter_button.clicked.connect(self.clear_encounter_handle)
        self.toolbox_widget.clear_toolbox_button.clicked.connect(self.clear_toolbox_handle)
        self.toolbox_widget.toggle_toolbox_button.clicked.connect(self.toggle_toolbox_handle)

        self.add_player_button.clicked.connect(self.add_player)

    def _display_ui(self):
        self.setCentralWidget(self.window_frame)

    def toggle_monster_bar(self):
        if self.monster_viewer_bar.isHidden():
            self.monster_viewer_bar.setHidden(False)
        else:
            self.monster_viewer_bar.setHidden(True)

    def toggle_spells(self):
        if self.button_hide_spells.isChecked():
            cond = True
        else:
            cond = False
        self.spell_frame.setHidden(not cond)
        self.tab_widget.setTabEnabled(SPELL_TAB, cond)
        self.toolbox_widget.spell_tabWidget.setTabEnabled(self.toolbox_widget.SPELL_TAB, cond)
        self.text_box.setLayout = None
        if not cond:
            self.monster_view_frame.layout().addWidget(self.text_box)
            self.window_layout.setStretch(0, 4)
        else:
            self.spell_frame.layout().addWidget(self.text_box)
            self.window_layout.setStretch(0, 6)
        self.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")

    def copy_plaintext_monster_to_clipboard(self):
        # print(self.monster_viewer.toPlainText())
        pyperclip.copy(html2text.html2text(self.monster_viewer.html))

    def change_version(self, version):
        if self.version == version:
            return
        self.version = version
        self.clear_toolbox_handle()
        self.clear_encounter_handle()

        self.monster_table_widget.table.clear()
        self.spell_table_widget.table.clear()
        self.item_table_widget.table.clear()

        self.monster_table_widget.filter.clear_filters()

        self.load_resources()
        # self.monster_table_widget.load_all("./monster", "resources/3.5/Bestiary/", Monster35)
        # self.monster_table_widget.fill_table()

        # self.spell_table_widget.load_all("./spell", "resources/3.5/Spells/", Spell35)
        # self.spell_table_widget.fill_table()
        # self.spell_table_widget.define_filters()

        # self.item_table_widget.load_all("./item", "resources/3.5/Items/", Item35)
        # self.item_table_widget.fill_table()
        # self.item_table_widget.define_filters()

    def spell_clicked_handle(self, table):
        current_row = table.currentRow()
        if current_row is -1:
            return
        itext = table.item(current_row, 1)
        if itext is None or itext.text() == '':
            return
        spell_idx = int(itext.text())
        spell = self.spell_table_widget.list[spell_idx]
        self.spell_viewer.draw_view(spell)

    def monster_clicked_handle(self, table):
        current_row = table.currentRow()
        if current_row is -1:
            return
        monster_idx = int(table.item(current_row, 1).text())
        if monster_idx == -1:  # monster is a player character
            return
        monster = self.monster_table_widget.list[monster_idx]
        self.monster_viewer.draw_view(monster)

    def item_clicked_handle(self, table):
        current_row = table.currentRow()
        if current_row is -1:
            return
        item_idx = int(table.item(current_row, 1).text())
        item = self.item_table_widget.list[item_idx]
        self.item_viewer.draw_view(item)

    # def spell_search_handle(self):
    #     self.spell_viewer.draw_view()

    def _fill_monster_table(self, monster_list):
        self.monster_table_widget.table_widget.clear()
        self.monster_table_widget.table_widget.setRowCount(len(monster_list))
        for itt, monster in enumerate(monster_list):
            self.monster_table_widget.table_widget.setItem(itt, 0, QTableWidgetItem(str(monster.name)))
            self.monster_table_widget.table_widget.setItem(itt, 1, QTableWidgetItem(str(monster.index)))

    def add_to_toolbox(self, monster):
        row_position = self.toolbox_widget.monster_toolbox.rowCount()
        self.toolbox_widget.monster_toolbox.insertRow(row_position)
        if type(monster) == list:
            for itt, value in enumerate(monster):
                self.toolbox_widget.monster_toolbox.setItem(row_position, itt, QTableWidgetItem(str(value)))
        else:
            self.toolbox_widget.monster_toolbox.setItem(row_position, 0, QTableWidgetItem(str(monster.name)))
            self.toolbox_widget.monster_toolbox.setItem(row_position, 1, QTableWidgetItem(str(monster.index)))

    def add_to_toolbox_spell(self, spell):
        row_position = self.toolbox_widget.spell_toolbox.rowCount()
        self.toolbox_widget.spell_toolbox.insertRow(row_position)
        if type(spell) == list:
            for itt, value in enumerate(spell):
                self.toolbox_widget.spell_toolbox.setItem(row_position, itt, QTableWidgetItem(str(value)))
        elif spell is not None:
            self.toolbox_widget.spell_toolbox.setItem(row_position, 0, QTableWidgetItem(str(spell.name)))
            self.toolbox_widget.spell_toolbox.setItem(row_position, 1, QTableWidgetItem(str(spell.index)))
            self.toolbox_widget.spell_toolbox.setItem(row_position, 2, QTableWidgetItem(str(spell.level)))

    def load_resources(self):
        if self.version == "5":
            item_cls = Item
            monster_cls = Monster
            spell_cls = Spell
        elif self.version == "3.5":
            item_cls = Item35
            monster_cls = Monster35
            spell_cls = Spell35
        self.item_table_widget.load_all("./item", "resources/{}/Items/".format(self.version), item_cls)
        self.item_table_widget.fill_table()
        self.item_table_widget.define_filters(self.version)
        self.monster_table_widget.load_all("./monster", "resources/{}/Bestiary/".format(self.version), monster_cls)
        self.monster_table_widget.fill_table()
        self.monster_table_widget.define_filters(self.version)
        self.spell_table_widget.load_all("./spell", "resources/{}/Spells/".format(self.version), spell_cls)
        self.spell_table_widget.fill_table()
        self.spell_table_widget.define_filters(self.version)

    def add_player(self, player=None):
        self.playerWidget.add(PlayerFrame(self.playerWidget))
        # table = self.playerWidget
        # row_position = table.rowCount()
        # table.insertRow(row_position)
        # table.setItem(row_position, 0, QTableWidgetItem(""))  # necessary so that the row isn't picked up in garbage collection
        # if type(player) is list:
        #     for itt, value in enumerate(player):
        #         table.setItem(row_position, itt, QTableWidgetItem(str(value)))

    def addPlayersToCombat(self):
        encounterWidget = self.encounterWidget
        characterNames = encounterWidget.getCharacterNames()

        # Get active players
        playerWidget = self.playerWidget

        for entry in self.playerWidget.m_widgetList:
            # character in encounter, but shouldn't be
            if entry.getCharacter().getCharName() in characterNames and not entry.isEnabled():
                pass

            # character not in encounter, but should be
            elif entry.getCharacter().getCharName() not in characterNames and entry.isEnabled():
                pass

            # character not in encounter, but shouldn't be
            else:
                pass

        # for itt in range(player_rows):
        #     item = playerWidget.item(itt, playerWidget.NAME_COLUMN)
        #     if item is None or item.text() == "":
        #         continue
        #     name = item.text()
        #     init = playerWidget.item(itt, playerWidget.INITIATIVE_COLUMN)
        #     if init is None or init.text() == "":
        #         continue
        #     if name in character_names:
        #         idx = character_names.index(name)
        #         self.encounterWidget.setItem(idx, self.encounterWidget.INIT_COLUMN,
        #                                      QTableWidgetItem(init.text()))
        #         continue
        #     else:
        #         init = playerWidget.item(itt, playerWidget.INITIATIVE_COLUMN)
        #         if init is None:
        #             init = ""
        #         else:
        #             init = init.text()
        #         self.encounterWidget.addToEncounter([name, -1, init, "", "", ""])

    def sort_init_handle(self):
        self.encounterWidget.sortInitiative()

    def roll_init_handle(self):
        self.encounterWidget.rollInitiative()

    def clear_encounter_handle(self):
        self.encounterWidget.clear()

    def clear_toolbox_handle(self):
        self.toolbox_widget.monster_toolbox.clear()
        self.toolbox_widget.monster_toolbox.setRowCount(0)
        self.toolbox_widget.spell_toolbox.clear()
        self.toolbox_widget.spell_toolbox.setRowCount(0)

    def toggle_toolbox_handle(self):
        self.toolbox_widget.toggle_hide()

    def print(self, s):
        self.text_box.append(s)

    def print_attack(self, monster, attack):
        comp = attack.split("|")
        if monster is not None:
            s = "{} uses {} -- ".format(monster.name, comp[0])
        else:
            s = "Roll -- "
        if comp[1] not in ["", " "]:  # this means there's an attack roll and a damage roll
            attack_roll = rollFunction("1d20+"+comp[1])
            s = s + "{}({}) to hit -- ".format(attack_roll, attack_roll-int(comp[1]))

        damage_roll = rollFunction(comp[2])
        if type(damage_roll) is list:
            halved = [max(1, int(dr/2)) for dr in damage_roll]
        else:
            halved = max(1, int(damage_roll/2))
        s = s + "for {} ({} halved)".format(str(damage_roll), str(halved))
        self.print(s)

    def extract_and_add_spellbook(self, monster):
        spells = monster.extract_spellbook()
        if spells is not None:
            for spell in spells:
                spell_entry = self.spell_table_widget.find_entry("name", spell)
                if spell_entry is not None:
                    self.add_to_toolbox_spell(spell_entry)
                else:
                    print("Failed to locate spell for", monster.name, "with spellname {}".format(spell))

    def load_meta(self):
        if not os.path.exists("metadata/"):
            os.mkdir("metadata")
        self.version = "5"
        if os.path.exists("metadata/meta.txt"):
            try:
                with open("metadata/meta.txt", "r") as f:
                    meta_dict = eval(f.read())
                    if 'version' in meta_dict.keys():
                        self.version = meta_dict['version']
            except:
                None

    def load_session(self):
        if not os.path.exists("metadata/"):
            os.mkdir("metadata")
        if os.path.exists("metadata/session.txt"):
            with open("metadata/session.txt", "r") as f:
                meta_dict = eval(f.read())
                for monster_tuple in meta_dict['toolbox_meta']:
                    self.add_to_toolbox(monster_tuple)
                for monster_tuple in meta_dict['initiative_meta']:
                    self.encounterWidget.addToEncounter(monster_tuple)
                for player_tuple in meta_dict['player_meta']:
                    self.add_player(player_tuple)

    def closeEvent(self, event):
        toolbox_meta = self.toolbox_widget.monster_toolbox.jsonlify()
        initiative_meta = self.encounterWidget.jsonlify()
        player_meta = self.playerWidget.jsonlify()

        with open("metadata/session.txt", "w") as f:
            json.dump(dict(
                toolbox_meta=toolbox_meta,
                initiative_meta=initiative_meta,
                player_meta=player_meta
            ), f)

        with open("metadata/meta.txt", "w") as f:
            json.dump(dict(
                version=self.version
            ), f)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    # app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    form = DMTool()  # We set the form to be our ExampleApp (design)

    form.show()  # Show the form
    sys.exit(app.exec_())  # and execute the app
