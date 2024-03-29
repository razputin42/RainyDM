from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton, \
    QLabel, QLineEdit, QMenu, QInputDialog, QFileDialog
from PyQt5.QtGui import QFont, QPixmap, QIntValidator
from PyQt5.QtCore import Qt
from dependencies.list_widget import ListWidget, EntryWidget, colorDict
from dependencies.auxiliaries import roll_function
from RainyCore.signals import sNexus
import os, json


class NumberInput(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(30)
        self.setValidator(QIntValidator(-999, 999))


class NameLabel(QLabel):
    def __init__(self, name):
        super().__init__(name)
        font = QFont("Helvetica [Cronyx]", 12)
        font.setCapitalization(QFont.SmallCaps)
        self.setFont(font)


class HealthFrame(QFrame):
    height = 22
    ratio = 1
    iconPath = "assets/icons/heart_icon.png"

    def __init__(self, health, srd_valid):
        super().__init__()
        self.m_maxHP = health

        self.setLayout(QHBoxLayout())
        iconLabel = QLabel()
        iconSize = [self.ratio*self.height, self.height]
        iconLabel.setFixedSize(*iconSize)
        iconLabel.setScaledContents(True)
        iconLabel.setPixmap(QPixmap(self.iconPath))
        if srd_valid:
            self.health = QLabel(str(self.m_maxHP))
            self.health.setFixedWidth(30)
            self.health.setFont(QFont("Helvetica [Cronyx]", 12))
        else:
            self.health = NumberInput()
            # self.health.returnPressed.connect(self.return_pressed_handle)
        self.layout().addWidget(iconLabel)
        self.layout().addWidget(self.health)
        self.layout().setAlignment(Qt.AlignLeft)

    def set(self, value):
        self.health.setText(str(value))

    def get(self):
        try:
            return int(self.health.text())
        except ValueError:
            return 0

    def max(self):
        return int(self.m_maxHP)


class DamageInputFrame(QFrame):
    height = 30
    ratio = 0.67
    iconPath = "assets/icons/sword_icon.png"

    def __init__(self, healthWidget, srd_valid):
        super().__init__()
        self.m_health = healthWidget
        self.srd_valid = srd_valid
        self.setLayout(QHBoxLayout())
        iconLabel = QLabel()
        iconSize = [self.ratio*self.height, self.height]
        iconLabel.setFixedSize(*iconSize)
        iconLabel.setScaledContents(True)
        iconLabel.setPixmap(QPixmap(self.iconPath))
        self.damageEdit = NumberInput()
        self.damageEdit.returnPressed.connect(self.returnPressedHandle)

        self.layout().addWidget(iconLabel)
        self.layout().addWidget(self.damageEdit)
        self.layout().setAlignment(Qt.AlignLeft)

    def returnPressedHandle(self):
        damage = int(self.damageEdit.text())
        newHealth = self.m_health.get() - damage
        print(damage, self.m_health.get())
        if newHealth < 0:
            newHealth = 0
        if self.srd_valid and newHealth > self.m_health.max():
            newHealth = self.m_health.max()
        self.m_health.set(newHealth)
        self.damageEdit.clear()


class InitiativeFrame(QFrame):
    height = 30
    ratio = 0.56
    iconPath = "assets/icons/initiative_icon.png"

    def __init__(self, initiative, srd_valid=True):
        super().__init__()
        self.setLayout(QHBoxLayout())
        iconLabel = QLabel()
        iconSize = [self.ratio*self.height, self.height]
        iconLabel.setFixedSize(*iconSize)
        iconLabel.setScaledContents(True)
        iconLabel.setPixmap(QPixmap(self.iconPath))
        if srd_valid:
            self.initiative = QLabel(initiative)
            self.initiative.setFixedWidth(30)
            self.initiative.setFont(QFont("Helvetica [Cronyx]", 12))
        else:
            self.initiative = NumberInput()
        self.layout().addWidget(iconLabel)
        self.layout().addWidget(self.initiative)
        self.layout().setAlignment(Qt.AlignLeft)

    def set(self, value):
        self.initiative.setText(str(value))

    def get(self):
        try:
            return int(self.initiative.text())
        except ValueError:
            return 0


class InitiativeWidget(EntryWidget):
    deselect_signal = sNexus.encounterDeselectSignal

    def __init__(self, entry):
        super().__init__(entry)
        self.color = colorDict["white"]
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(10, 0, 10, 0)
        # self.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.setMinimumHeight(50)
        self.setFrameShape(QFrame.Box)
        self.deselect()
        # self.color = colorDict['green']

    def getInitiative(self):
        return self.m_initiative.get()


class MonsterWidget(InitiativeWidget):
    def __init__(self, monster, parentList, viewer=None, init=None, hp=None, desc=None):
        self.monster = monster
        super().__init__(monster)
        self.m_health = HealthFrame(hp, monster.is_srd_valid())
        self.m_initiative = InitiativeFrame(str(init), monster.is_srd_valid())
        self.viewer = viewer
        self.parent = parentList
        self.m_name = NameLabel(monster.name)
        self.layout().addWidget(self.m_name)
        self.layout().addStretch(1)
        self.layout().addWidget(self.m_health)
        self.layout().addWidget(DamageInputFrame(self.m_health, monster.is_srd_valid()))
        self.layout().addWidget(self.m_initiative)

    def rollInitiative(self):
        self.m_initiative.set(roll_function("1d20") + self.monster.initiative)

    # def mouseReleaseEvent(self, event):
    #     if self.viewer is None:
    #         return
    #     self.viewer.draw_view(self.monster)

    def getHp(self):
        return self.m_health.get()

    def getName(self):
        return self.m_name.text()

    def contextMenuEvent(self, event):
        menu = QMenu()
        moveUpAction = menu.addAction("Move Up")
        moveDownAction = menu.addAction("Move Down")
        menu.addSeparator()
        removeAction = menu.addAction("Remove from Initiative")

        actionMenuHandles = []
        if len(self.monster.action_list) is not 0:
            menu.addSeparator()
            for attack in self.monster.action_list:
                if hasattr(attack, "attack"):
                    actionMenuHandles.append((menu.addAction(attack.name), attack))

        if hasattr(self.monster, 'spells'):
            menu.addSeparator()
            addSpells = menu.addAction("Add monster's spells to bookmark")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        elif action is removeAction:
            self.parent.remove(self)
        elif action is moveUpAction:
            self.parent.moveEntry(self, -1)
        elif action is moveDownAction:
            self.parent.moveEntry(self, 1)
        elif action in [i[0] for i in actionMenuHandles]:
            for _action, attack in actionMenuHandles:
                if action is _action:
                    self.monster.performAttack(attack)
        elif action is addSpells:
            self.monster.addSpells()

    def jsonlify(self):
        output = dict(
            type="Monster",
            monster=self.monster.name,
            hp=self.m_health.get(),
            init=self.m_initiative.get()
        )
        return json.dumps(output)


class PlayerWidget(InitiativeWidget):
    def __init__(self, parentList, character):
        super().__init__(character)
        self.m_initiative = InitiativeFrame(str(character.getInit()))
        self.m_character = character
        self.name = NameLabel(character.getCharName())
        self.layout().addWidget(self.name)
        self.layout().addStretch(1)
        self.layout().addWidget(self.m_initiative)
        self.parent = parentList

    def set_name(self, name):
        self.name.setText(name)

    def set_initiative(self, initiative):
        self.m_initiative.set(initiative)

    def getName(self):
        return self.m_character.getCharName()

    def jsonlify(self):
        output = dict(
            type="Player",
            name=self.getName(),
            init=self.m_initiative.get()
        )
        return json.dumps(output)

    def contextMenuEvent(self, event):
        menu = QMenu()
        moveUpAction = menu.addAction("Move Up")
        moveDownAction = menu.addAction("Move Down")
        menu.addSeparator()
        removeAction = menu.addAction("Remove from Initiative")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        elif action == removeAction:
            self.parent.remove(self)
        elif action == moveUpAction:
            self.parent.moveEntry(self, -1)
        elif action == moveDownAction:
            self.parent.moveEntry(self, 1)


class EncounterWidget(ListWidget):
    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.setObjectName("EncounterWidget")
        self.scroll_frame.setObjectName("EncounterWidgetScrollArea")
        sNexus.encounterDeselctSignal.connect(self.deselectAll)

    def calculate_encounter_xp(self):
        pass

    def format(self):
        pass

    def setup_top_button_bar(self):
        button_frame = QFrame()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_frame.setLayout(button_layout)

        self.save_encounter_button = QPushButton("Save Encounter")
        self.load_encounter_button = QPushButton("Load Encounter")
        button_layout.addWidget(self.save_encounter_button)
        button_layout.addWidget(self.load_encounter_button)
        button_layout.addStretch(0)
        self.layout().addWidget(button_frame)

    def setup_bottom_button_bar(self):
        button_frame = QFrame()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_frame.setLayout(button_layout)

        self.sort_init_button = QPushButton("Sort Initiative")
        self.roll_init_button = QPushButton("Roll Initiative")
        self.add_players_button = QPushButton("Update Players")
        self.clear_encounter_button = QPushButton("Clear Encounter")
        button_layout.addWidget(self.sort_init_button)
        button_layout.addWidget(self.roll_init_button)
        button_layout.addWidget(self.add_players_button)
        button_layout.addWidget(self.clear_encounter_button)
        button_layout.addStretch(0)
        self.layout().addWidget(button_frame)

    def contextMenuEvent(self, event):
        pass

    def data_changed_handle(self, row, column):
        pass

    def _convert_to_int(self, row, column):
        pass

    def save(self):
        if not os.path.exists("encounters"):
            os.mkdir("encounters")
        output = []
        for entry in self.m_widgetList:
            if type(entry) is MonsterWidget:
                output.append(entry.jsonlify())

        encounter_name, ok = QInputDialog.getText(self, "Save", "Encounter Name:")
        if not ok or encounter_name.strip() == "":
            return
        elif encounter_name[-4:] != ".txt":
            encounter_name = encounter_name + ".txt"
        with open("encounters/" + encounter_name, 'w') as file:
            file.write(json.dumps(output))

    def load(self, monsterList):
        filename, _ = QFileDialog.getOpenFileName(self, "Select encounter", "encounters", "Text files (*.txt)")
        if filename and os.path.exists(filename):
            self.clear()
            with open(filename, 'r') as f:
                encounter = json.load(f)
            for jsonEntry in encounter:
                entry = json.loads(jsonEntry)
                monster = monsterList.find_entry("name", entry["monster"])
                self.addMonsterToEncounter(monster, init=entry["init"], hp=entry["hp"])

    def getCharacterNames(self):
        charNameList = []
        for entry in self.m_widgetList:
            if type(entry) is PlayerWidget:
                if entry.getName() not in charNameList:
                    charNameList.append(entry.getName())
        return charNameList

    def updateCharacterInitiative(self, character):
        pass

    def sortInitiative(self):
        self.sort('getInitiative')

    def rollInitiative(self):
        for entry in self.m_widgetList:
            if type(entry) is MonsterWidget and entry.monster.is_srd_valid():
                entry.rollInitiative()

    def addMonsterToEncounter(self, monster, number=1, init=None, hp=None, desc=None):
        if hp is None:
            hp = monster.hp_no_dice
        for itt in range(number):
            self.add(MonsterWidget(monster, self, self.viewer, init, hp, desc))

    def addPlayerToEncounter(self, character):
        self.add(PlayerWidget(self, character))

    def find_PC(self, character):
        for entry in self.m_widgetList:
            if entry.getName() == character.getCharName():
                return entry

    def remove_character(self, character):
        entry = self.find_PC(character)
        if entry is None:
            return
        self.remove(entry)

    def update_character(self, character):
        entry = self.find_PC(character)
        if entry is None:
            return
        entry.set_name(character.getCharName())
        entry.set_initiative(character.getInit())

    def moveEntry(self, entry, move):
        newList = self.m_widgetList
        idx = self.find(entry)
        if idx is None:
            return
        if idx + move > len(newList)-1 or idx + move < 0:
            return
        newList[idx], newList[idx+move] = newList[idx+move], newList[idx]
        self.refill(newList)


    def jsonlify(self):
        return_list = []
        for entry in self.m_widgetList:
            return_list.append(entry.jsonlify())
        return return_list
