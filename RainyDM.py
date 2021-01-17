from dependencies.auxiliaries import roll_function, GlobalParameters
from dependencies.custom_widgets import RainyButton
from dependencies.encounter import EncounterWidget, MonsterWidget, PlayerWidget
from dependencies.input_tables import PlayerTable, PlayerFrame
from dependencies.TreasureHoard import TreasureHoardTab
from dependencies.searchable_tables import MonsterTableWidget, SpellTableWidget, ItemTableWidget
from RainyCore.signals import sNexus
from dependencies.bookmark import BookmarkWidget
from dependencies.views import MonsterViewer, SpellViewer, ItemViewer
from RainyCore.item import Item, Item35
from RainyCore.monster import Monster, Monster35
from RainyCore.spell import Spell, Spell35
from RainyDB.RainyDatabase import RainyDatabase
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QAction, QPushButton, QTableWidgetItem, QTextEdit, QVBoxLayout, \
    QHBoxLayout, QTabWidget, QFrame, QSizePolicy, QMainWindow, QMessageBox, QSpacerItem
import sys, json, os, traceback
import html2text
import pyperclip

MONSTER_TAB = 0
SPELL_TAB = 1

old_excepthook = sys.excepthook

class DMTool(QMainWindow):
    SEARCH_BOX_WIDTH = 200

    def __init__(self, db_path):
        super().__init__()
        sys.excepthook = self.excepthook
        self.settings = dict({"query_srd": True})
        self.load_meta()
        self._setup_ui(db_path)
        self._setup_menu()
        self.bind_signals()
        self.load_session()
        self._display_ui()
        # for monster in self.db[str(Monster)].values():
        #     print(monster.name)
        #     self.monster_viewer.draw_view(monster)
        #     if hasattr(monster, "action_list"):
        #         for action in monster.action_list:
        #             if hasattr(action, "attack"):
        #                 monster.performAttack(action)

    def _setup_ui(self, db_path):
        """
        Layout is a windowLayout with a horizontal box on the left and a tab widget on the right
        :return:
        """
        self.setStyleSheet(open(os.path.join("assets", "styles", "default.css")).read())
        self.setWindowIcon(QIcon(os.path.join('assets', 'tear.png')))
        self.setWindowTitle("RainyDM")
        self.setGeometry(100, 100, 1280, 720)
        self.window_frame = QFrame()
        self.window_layout = QHBoxLayout()
        # Left side tab
        self.tab_widget = QTabWidget()

        # Viewers
        # - monster viewer
        monster_button_bar = QFrame()
        monster_button_bar_layout = QHBoxLayout()
        monster_button_bar.setLayout(monster_button_bar_layout)
        self.monster_viewer = MonsterViewer(monster_button_bar)
        monster_viewer_frame_layout = QVBoxLayout()
        self.monster_viewer_frame = QFrame()
        self.monster_viewer_frame.setLayout(monster_viewer_frame_layout)
        self.monster_viewer_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.monster_viewer_frame.setFrameStyle(0)

        # - spell viewer
        self.spell_viewer = SpellViewer()

        # - item viewer
        self.item_viewer = ItemViewer()

        # Text box
        self.text_box = QTextEdit()
        self.text_box.setObjectName("OutputField")
        self.text_box.setReadOnly(True)
        self.text_box.setFontPointSize(10)

        ## Tables
        # Spell Table
        self.spell_table_widget = SpellTableWidget(self, self.spell_viewer)

        # Monster table
        self.monster_table_widget = MonsterTableWidget(self, self.monster_viewer)

        # Item table
        self.item_table_widget = ItemTableWidget(self, self.item_viewer)
        self.item_table_widget.layout().addWidget(self.item_viewer)

        self.load_resources(db_path)

        # Loot Generator Widget
        self.lootViewer = ItemViewer()
        self.loot_widget = TreasureHoardTab(self, self.item_viewer, self.item_table_widget)

        # Initiative list
        self.encounterWidget = EncounterWidget(self.monster_viewer)

        # bookmark
        self.bookmark_widget = BookmarkWidget(self.monster_table_widget,
                                            self.monster_viewer,
                                            self.spell_table_widget,
                                            self.spell_viewer)

        encounter_frame = QFrame()
        encounter_layout = QVBoxLayout()
        encounter_layout.addWidget(self.encounterWidget)
        encounter_layout.addWidget(self.bookmark_widget)
        encounter_frame.setLayout(encounter_layout)

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

        self.monster_viewer_bar = QFrame()
        self.monster_viewer_bar.setContentsMargins(0, 0, 0, 0)

        monster_viewer_frame_layout.addWidget(self.monster_viewer)
        monster_viewer_frame_layout.addWidget(monster_button_bar)
        monster_viewer_frame_layout.addWidget(self.monster_viewer_bar)
        monster_viewer_frame_layout.setStretch(3, 1)
        monster_viewer_frame_layout.setStretch(0, 2)

        middle_frame_layout = QVBoxLayout()
        self.middle_frame = QTabWidget()
        self.middle_frame.setLayout(middle_frame_layout)
        self.middle_frame.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        monster_plaintext_button = QPushButton("Copy plaintext to clipboard")
        monster_plaintext_button.clicked.connect(self.copy_plaintext_monster_to_clipboard)
        layout.addWidget(monster_plaintext_button)
        self.monster_viewer_bar.setLayout(layout)

        # middle_frame_layout.addWidget(self.spell_viewer)
        middle_frame_layout.setStretch(0, 2)
        middle_frame_layout.setContentsMargins(0, 0, 0, 0)

        # Leftmost tab
        self.tab_widget.addTab(encounter_frame, "Encounter")
        self.tab_widget.addTab(player_table_frame, "Players")
        self.tab_widget.addTab(self.loot_widget, "Loot")

        # Center tab
        self.middle_frame.addTab(self.monster_table_widget, "Monster")
        self.middle_frame.addTab(self.spell_table_widget, "Spell")
        self.middle_frame.addTab(self.item_table_widget, "Item")
        self.middle_frame.addTab(self.text_box, "Text Box")

        # Right frame
        self.right_tab = QTabWidget()
        self.right_tab.addTab(self.monster_viewer_frame, "Monster")
        self.right_tab.addTab(self.spell_viewer, "Spell")
        self.right_tab.addTab(self.item_viewer, "Item")

        self.window_layout.addWidget(self.tab_widget)
        self.window_layout.addWidget(self.middle_frame)
        self.window_layout.addWidget(self.right_tab)
        self._set_widget_stretch(GlobalParameters.MAIN_TOOL_POSITION, GlobalParameters.MAIN_TOOL_STRETCH)
        self._set_widget_stretch(GlobalParameters.MIDDLE_FRAME_POSITION, 0)
        self._set_widget_stretch(GlobalParameters.RIGHT_FRAME_POSITION, GlobalParameters.RIGHT_FRAME_STRETCH)

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
        # raise_exception = QAction("Raise Exception", self)
        # raise_exception.setStatusTip("Raise an Exception")
        # raise_exception.triggered.connect(self.raise_exception)
        self.edit_entries_action = QAction("Edit Entries", self, checkable=True)
        self.edit_entries_action.setStatusTip("Enable edit data entries")
        # development
        self.edit_entries_action.setChecked(True)  # default ON
        self.enable_edit_data_entries()
        ##
        self.edit_entries_action.triggered.connect(self.enable_edit_data_entries)

        experimental.addAction(button_plain_text)
        experimental.addAction(self.edit_entries_action)
        # experimental.addAction(raise_exception)

        self.window_frame.setLayout(self.window_layout)

    # def raise_exception(self):
    #     raise EnvironmentError("Forced an exception")

    def enable_edit_data_entries(self):
        cond = self.edit_entries_action.isChecked()
        self.monster_table_widget.EDITABLE = False # not for monsters
        self.spell_table_widget.EDITABLE = cond
        self.item_table_widget.EDITABLE = cond

    def bind_signals(self):
        self.encounterWidget.add_players_button.clicked.connect(self.addPlayersToCombat)
        self.encounterWidget.sort_init_button.clicked.connect(self.sort_init_handle)
        self.encounterWidget.roll_init_button.clicked.connect(self.roll_init_handle)
        self.encounterWidget.save_encounter_button.clicked.connect(self.encounterWidget.save)
        self.encounterWidget.load_encounter_button.clicked.connect(lambda: self.encounterWidget.load(self.monster_table_widget))
        self.encounterWidget.clear_encounter_button.clicked.connect(self.clear_encounter_handle)
        self.bookmark_widget.clear_bookmark_button.clicked.connect(self.clear_bookmark_handle)
        self.bookmark_widget.toggle_bookmark_button.clicked.connect(self.toggle_bookmark_handle)

        self.add_player_button.clicked.connect(self.add_player)
        sNexus.attackSignal.connect(self.attackSlot)
        sNexus.addSpellsSignal.connect(self.addSpellsToBookmark)
        sNexus.printSignal.connect(self.print)
        sNexus.addMonstersToEncounter.connect(self.encounterWidget.addMonsterToEncounter)
        sNexus.setWidgetStretch.connect(self._set_widget_stretch)
        sNexus.viewerSelectChanged.connect(self.viewer_select_changed)

    def _display_ui(self):
        self.setCentralWidget(self.window_frame)

    def _set_widget_stretch(self, widget, stretch):
        self.window_layout.setStretch(widget, stretch)

    def toggle_monster_bar(self):
        if self.monster_viewer_bar.isHidden():
            self.monster_viewer_bar.setHidden(False)
        else:
            self.monster_viewer_bar.setHidden(True)

    def copy_plaintext_monster_to_clipboard(self):
        pyperclip.copy(html2text.html2text(self.monster_viewer.html))

    def viewer_select_changed(self, idx):
        self.right_tab.setCurrentIndex(idx)

    def change_version(self, version):
        if self.version == version:
            return
        self.version = version
        self.clear_bookmark_handle()
        self.clear_encounter_handle()

        self.monster_table_widget.table.clear()
        self.spell_table_widget.table.clear()
        self.item_table_widget.table.clear()

        self.monster_table_widget.filter.clear_filters()

        self.load_resources()

    def addMonsterToBookmark(self, monster):
        row_position = self.bookmark_widget.monster_bookmark.rowCount()
        self.bookmark_widget.monster_bookmark.insertRow(row_position)
        if type(monster) == list:
            for itt, value in enumerate(monster):
                self.bookmark_widget.monster_bookmark.setItem(row_position, itt, QTableWidgetItem(str(value)))
        else:
            self.bookmark_widget.monster_bookmark.setItem(row_position, 0, QTableWidgetItem(str(monster.name)))
            self.bookmark_widget.monster_bookmark.setItem(row_position, 1, QTableWidgetItem(str(monster.index)))

    def addSpellsToBookmark(self, spells):
        for spell in spells:
            _spell = self.spell_table_widget.find_entry('name', spell)
            self.add_to_bookmark_spell(_spell)

    def add_to_bookmark_spell(self, spell):
        row_position = self.bookmark_widget.spell_bookmark.rowCount()
        self.bookmark_widget.spell_bookmark.insertRow(row_position)
        if type(spell) == list:
            for itt, value in enumerate(spell):
                self.bookmark_widget.spell_bookmark.setItem(row_position, itt, QTableWidgetItem(str(value)))
        elif spell is not None:
            self.bookmark_widget.spell_bookmark.setItem(row_position, 0, QTableWidgetItem(str(spell.name)))
            self.bookmark_widget.spell_bookmark.setItem(row_position, 1, QTableWidgetItem(str(spell.index)))
            self.bookmark_widget.spell_bookmark.setItem(row_position, 2, QTableWidgetItem(str(spell.level)))

    def load_resources(self, resource_path):
        if self.version == "5":
            item_cls = Item
            monster_cls = Monster
            spell_cls = Spell
        elif self.version == "3.5":
            item_cls = Item35
            monster_cls = Monster35
            spell_cls = Spell35
        self.db = RainyDatabase(resource_path)
        self.item_table_widget.set_database(self.db)
        self.item_table_widget.fill_table()
        self.item_table_widget.define_filters(self.version)
        self.monster_table_widget.set_database(self.db)
        self.monster_table_widget.fill_table()
        self.monster_table_widget.define_filters(self.version)
        # self.spell_table_widget.load_all("./spell", "{}/{}/Spells/".format(resource_path, self.version), spell_cls)
        self.spell_table_widget.set_database(self.db)
        self.spell_table_widget.fill_table()
        self.spell_table_widget.define_filters(self.version)

    def add_player(self, player=None):
        self.playerWidget.add(PlayerFrame(self.playerWidget))

    def addPlayersToCombat(self):
        encounterWidget = self.encounterWidget
        characterNames = encounterWidget.getCharacterNames()
        # Get active players

        for entry in self.playerWidget.m_widgetList:
            # character in encounter, and should be
            if entry.getCharacter().getCharName() in characterNames and entry.isEnabled():
                # print("Character in encounter, and should be")
                encounterWidget.update_character(entry.getCharacter())

            # character in encounter, but shouldn't be
            elif entry.getCharacter().getCharName() in characterNames and not entry.isEnabled():
                # print("Character in enocunter, shouldn't be")
                # print(entry.getCharacter().getCharName(), entry.isEnabled())
                encounterWidget.remove_character(entry.getCharacter())

            # character not in encounter, but should be
            elif entry.getCharacter().getCharName() not in characterNames and entry.isEnabled():
                # print("Character not in encounter, should be")
                encounterWidget.addPlayerToEncounter(entry.getCharacter())

            # character not in encounter, and shouldn't be
            else:
                pass

    def sort_init_handle(self):
        self.encounterWidget.sortInitiative()

    def roll_init_handle(self):
        self.encounterWidget.rollInitiative()

    def clear_encounter_handle(self):
        self.encounterWidget.clear()

    def clear_bookmark_handle(self):
        self.bookmark_widget.monster_bookmark.clear()
        self.bookmark_widget.monster_bookmark.setRowCount(0)
        self.bookmark_widget.spell_bookmark.clear()
        self.bookmark_widget.spell_bookmark.setRowCount(0)

    def toggle_bookmark_handle(self):
        self.bookmark_widget.toggle_hide()

    def print(self, s):
        self.middle_frame.setCurrentIndex(GlobalParameters.TEXT_BOX_INDEX)
        self.text_box.append(s)

    def print_attack(self, monster_name, attack):
        attack = attack.strip(" ")
        comp = attack.split("|")
        if attack == "":
            s = "{} used an action".format(monster_name)
        else:
            s = "{} uses {} -- ".format(monster_name, comp[0])

            if comp[1] not in ["", " "]:  # this means there's an attack roll and a damage roll
                attack_roll = roll_function("1d20+" + comp[1])
                s = s + "{}({}) to hit".format(attack_roll, attack_roll-int(comp[1]))
            damage_roll = roll_function(comp[2])
            if damage_roll is not None:
                if type(damage_roll) is list:
                    halved = [max(1, int(dr/2)) for dr in damage_roll]
                else:
                    # print("\trainydm - print_attack: \"{}\"".format(damage_roll))
                    halved = max(1, int(damage_roll/2))
                s = s + " -- for {} ({} halved)".format(str(damage_roll), str(halved))
        self.print(s)

    def extract_and_add_spellbook(self, monster):
        spells = monster.extract_spellbook()
        if spells is not None:
            for spell in spells:
                spell_entry = self.spell_table_widget.find_entry("name", spell)
                if spell_entry is not None:
                    self.add_to_bookmark_spell(spell_entry)
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
                        self.settings = meta_dict['settings']
            except:
                None

    def load_session(self):
        if not os.path.exists("metadata/"):
            os.mkdir("metadata")
        if os.path.exists("metadata/session.txt"):
            with open("metadata/session.txt", "r") as f:
                meta_dict = eval(f.read())
                for monster_tuple in meta_dict['bookmark_meta']:
                    self.addMonsterToBookmark(monster_tuple)

                for player in meta_dict['player_meta']:
                    player_dict = json.loads(player)
                    self.playerWidget.add(PlayerFrame(
                        self.playerWidget,
                        charName=player_dict["characterName"],
                        playerName=player_dict["playerName"],
                        init=player_dict["initiative"],
                        perception=player_dict["perception"],
                        insight=player_dict["insight"],
                        isEnabled=player_dict["isEnabled"]
                        )
                    )

                for entry in meta_dict['initiative_meta']:
                    entry_dict = json.loads(entry)
                    if entry_dict["type"] == "Monster":
                        self.encounterWidget.add(MonsterWidget(
                            self.monster_table_widget.find_entry("name", entry_dict["monster"]),
                            self.encounterWidget,
                            viewer=self.monster_viewer,
                            init=entry_dict["init"],
                            hp=entry_dict["hp"]
                        ))
                    elif entry_dict["type"] == "Player":
                        self.encounterWidget.add(PlayerWidget(
                            self.encounterWidget,
                            self.playerWidget.findCharacterByName(entry_dict["name"])
                        ))

    def closeEvent(self, event):
        bookmark_meta = self.bookmark_widget.monster_bookmark.jsonlify()
        initiative_meta = self.encounterWidget.jsonlify()
        player_meta = self.playerWidget.jsonlify()

        with open("metadata/session.txt", "w") as f:
            json.dump(dict(
                bookmark_meta=bookmark_meta,
                initiative_meta=initiative_meta,
                player_meta=player_meta
            ), f)

        with open("metadata/meta.txt", "w") as f:
            json.dump(dict(
                version=self.version,
                settings=self.settings
            ), f)

    # SLOTS
    @pyqtSlot(str, str)
    def attackSlot(self, name, attack):
        self.print_attack(name, attack)
        self.middle_frame.setCurrentIndex(GlobalParameters.TEXT_BOX_INDEX)

    def excepthook(self, type, value, tb):
        box = QMessageBox()
        box.setWindowTitle("Oof!")
        box.setText("RainyDM has crashed!")
        box.setIcon(QMessageBox.Critical)
        details = "".join(traceback.format_exception(type, value, tb))
        box.setDetailedText(details)

        spacer = QSpacerItem(500, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        box.layout().addItem(spacer, box.layout().rowCount(), 0, 1, box.layout().columnCount())

        box.exec_()
        old_excepthook(type, value, tb)
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    form = DMTool(os.path.join(os.getcwd(), "RainyDB"))

    form.show()  # Show the form
    sys.exit(app.exec_())  # and execute the app
