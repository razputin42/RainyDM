from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QInputDialog, QTableWidget, QHeaderView, QVBoxLayout, \
    QHBoxLayout, QLineEdit, QTextBrowser, QMenu, QTabWidget, QFrame, QPushButton
from dependencies.html_format import monster_dict, spell_dict
from string import Template



class MonsterViewer(QTextBrowser):
    def __init__(self):
        QTextBrowser.__init__(self)
        self.horizontalScrollBar().setHidden(True)
        self.setStyleSheet("border-image: url(assets/viewer_background.jpg);")
        self.setMaximumWidth(530)
        self.setMinimumWidth(530)

    def loadResource(self, type, name):
        return QtGui.QPixmap("assets/linear_gradient.png")

    def draw_view(self, monster):
        # this is going to get confusing fast... This is everything before saving throws
        template = Template(monster_dict['first'])
        html = template.safe_substitute(
            name=monster.name,
            size=monster.size,
            type=monster.type,
            alignment=monster.alignment,
            armor_class=monster.ac,
            hit_points=monster.hp,
            speed=monster.speed,
            str=monster.str,
            str_mod=monster.calculate_modifier(monster.str, sign=True),
            dex=monster.dex,
            dex_mod=monster.calculate_modifier(monster.dex, sign=True),
            con = monster.con,
            con_mod=monster.calculate_modifier(monster.con, sign=True),
            int=monster.int,
            int_mod=monster.calculate_modifier(monster.int, sign=True),
            wis=monster.wis,
            wis_mod=monster.calculate_modifier(monster.wis, sign=True),
            cha=monster.cha,
            cha_mod=monster.calculate_modifier(monster.cha, sign=True)
        )
        descriptive = ["save", "skill", "senses", "languages", "cr"]
        name_dict = dict(
            save="Saving Throws",
            skill="Skills",
            senses="Senses",
            languages="Languages",
            cr="Challenge Rating"
        )
        for desc in descriptive:
            if hasattr(monster, desc):
                template = Template(monster_dict['desc'])
                html = html + template.safe_substitute(
                    name=name_dict[desc],
                    desc=getattr(monster, desc))

        html = html + monster_dict['gradient']
        # add traits
        for itt, trait in enumerate(monster.trait_list):
            template = Template(monster_dict['action_even'])
            html = html + template.safe_substitute(
                name=trait.name,
                text=trait.text
            )

        # second part of the monster
        template = Template(monster_dict['second'])
        html = html + template.safe_substitute(
        )

        # add each action
        for itt, action in enumerate(monster.action_list):
            if itt % 2 == 0: # even
                template = Template(monster_dict['action_even'])
            else:
                template = Template(monster_dict['action_odd'])
            html = html + template.safe_substitute(
                name=action.name,
                text=action.text
            )

        # add each legendary action
        if len(monster.legendary_list) != 0:
            html = html + monster_dict['legendary_header']
            for itt, action in enumerate(monster.legendary_list):
                if itt % 2 == 0:  # even
                    template = Template(monster_dict['action_even'])
                else:
                    template = Template(monster_dict['action_odd'])
                html = html + template.safe_substitute(
                    name=action.name,
                    text=action.text
                )

        # rest of the monster
        template = Template(monster_dict['rest'])
        html = html + template.safe_substitute()

        self.setHtml(html)

class SpellViewer(MonsterViewer):
    def draw_view(self, spell):
        template = Template(spell_dict['entire'])
        html = template.safe_substitute(
            name=spell.name,
            level=self.ordinal(spell.level),
            school=spell.school,
            time=spell.time,
            range=spell.range,
            components=spell.components,
            duration=spell.duration,
            text=spell.text
        )
        self.setHtml(html)

    @staticmethod
    def ordinal(n):
        n = int(n)
        if n == 0:
            return "Cantrip"
        return "{}{}-level".format(n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


class MonsterTableWidget(QTableWidget):
    _NAME_COLUMN = 0
    _INDEX_COLUMN = 1
    _INIT_COLUMN = 2
    _HP_COLUMN = 3
    _DAMAGE_COLUMN = 4
    _DESCRIPTION_COLUMN = 5

    def __init__(self, parent):
        QTableWidget.__init__(self)
        self.parent = parent
        self.format()

    def format(self):
        columns = 2
        self.setColumnCount(columns)
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(self._NAME_COLUMN, QHeaderView.Stretch)
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.setColumnHidden(1, True)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        addAction = menu.addAction("Add to initiative")
        addXAction = menu.addAction("Add X to initiative")
        menu.addSeparator()
        addToolbox = menu.addAction("Add to toolbox")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        current_row = self.currentRow()
        monster_idx = int(self.item(current_row, 1).text())
        monster = self.parent.monster_table_widget.list[monster_idx]
        if action == addAction:
            self.parent.add_to_encounter(monster, 1)
        if action == addXAction:
            X, ok = QInputDialog.getInt(self, 'Add Monster', 'How many?')
            if ok:
                self.parent.add_to_encounter(monster, X)
        elif action == addToolbox:
            self.parent.add_to_toolbox(monster)

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

    def remove_row(self, row):
        self.removeRow(row)

    def spellContextEvent(self, event):
        menu = QMenu(self)
        addToolbox = menu.addAction("Add to toolbox")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        current_row = self.currentRow()
        idx = int(self.item(current_row, 1).text())
        spell = self.parent.spell_table_widget.list[idx]
        if action == addToolbox:
            self.parent.add_to_toolbox_spell(spell)


class InitiativeTableWidget(MonsterTableWidget):
    def __init__(self, parent):
        MonsterTableWidget.__init__(self, parent)
        self.cellChanged.connect(self.data_changed_handle)

    def format(self):
        columns = 6
        self.setColumnCount(columns)
        self.setHorizontalHeaderLabels(["Name", "_index", "Initiative", "HP", "Damage Input", "Description"])
        self.horizontalHeader().setSectionResizeMode(self._DESCRIPTION_COLUMN, QHeaderView.Stretch)
        self.setShowGrid(True)
        self.setColumnWidth(self._NAME_COLUMN, 150)
        self.verticalHeader().hide()
        self.setColumnHidden(1, True)

    def contextMenuEvent(self, event):
        current_row = self.currentRow()
        if current_row == -1:  # empty table
            return None
        monster_idx = int(self.item(current_row, 1).text())

        action_indexes = []
        action_menu_handles = []
        menu = QMenu(self)
        if monster_idx is not -1:
            monster = self.parent.monster_table_widget.list[monster_idx]
            for itt, action in enumerate(monster.action_list):
                if hasattr(action, "attack"):
                    action_indexes.append(itt)
                    action_menu_handles.append(menu.addAction(action.name))

        menu.addSeparator()
        removeAction = menu.addAction("Remove from initiative")
        addToolbox = menu.addAction("Add to toolbox")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        elif action == addToolbox:
            if monster_idx == 0:  # monster is a player
                return
            monster = self.parent.monster_table_widget.list[monster_idx]
            self.parent.add_to_toolbox(monster)
        elif action == removeAction:
            self.remove_row(current_row)
        elif action in action_menu_handles:
            idx = action_menu_handles.index(action)
            attack = monster.action_list[action_indexes[idx]]
            if hasattr(attack, "attack"):
                self.parent.print_attack(monster, attack.attack)

    def data_changed_handle(self, row, column):
        if column == self._DAMAGE_COLUMN:
            damage = -self._convert_to_int(row, column)
            hp = self._convert_to_int(row, self._HP_COLUMN)
            if damage is False or hp is False:
                pass
            else:
                monster = self.parent.monster_table_widget.list[int(self.item(row, self._INDEX_COLUMN).text())]
                self.item(row, self._HP_COLUMN).setText(str(min(hp + damage, int(monster.hp_no_dice))))
            self.item(row, column).setText("")

    def _convert_to_int(self, row, column):
        value = self.item(row, column).text()
        if value == "" or value is None:
            return False
        try:
            return int(value)
        except:
            return False


class PlayerTableWidget(MonsterTableWidget):
    _NAME_COLUMN = 0
    _PLAYER_COLUMN = 1
    _INITIATIVE_COLUMN = 2
    _PASSIVE_PERCEPTION_COLUMN = 3
    _PASSIVE_INSIGHT_COLUMN = 4

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
            self.remove_row(current_row)

    def format(self):
        columns = 5
        self.setColumnCount(columns)
        self.setHorizontalHeaderLabels(["Name", "Player", "Initiative", "Passive Insight",
                                        "Passive Perception", "Inactive"])
        self.setShowGrid(True)
        for i in range(columns):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        self.setColumnWidth(self._NAME_COLUMN, 150)
        self.verticalHeader().hide()


class ToolboxWidget:
    def __init__(self, parent):
        self.parent = parent
        self.frame = QFrame()
        layout = QHBoxLayout()
        self.spell_toolbox = MonsterTableWidget(self.parent)
        self.monster_toolbox = MonsterTableWidget(self.parent)
        self.monster_toolbox.contextMenuEvent = self.monster_contextMenuEvent
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

    def monster_contextMenuEvent(self, event):
        menu = QMenu(self.monster_toolbox)
        addAction = menu.addAction("Add to initiative")
        addXAction = menu.addAction("Add X to initiative")
        menu.addSeparator()
        removeFromToolbox = menu.addAction("Remove from toolbox")

        action = menu.exec_(self.monster_toolbox.mapToGlobal(event.pos()))
        if action is None:
            return
        current_row = self.monster_toolbox.currentRow()
        monster_idx = int(self.monster_toolbox.item(current_row, 1).text())
        monster = self.parent.monster_table_widget.list[monster_idx]
        if action == addAction:
            self.parent.add_to_encounter(monster, 1)
        if action == addXAction:
            X, ok = QInputDialog.getInt(self.parent, 'Add Monster', 'How many?')
            if ok:
                self.parent.add_to_encounter(monster, X)
        elif action == removeFromToolbox:
            self.remove_from_toolbox(self.monster_toolbox, current_row)

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

