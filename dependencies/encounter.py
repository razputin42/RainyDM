from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, \
    QLabel, QLineEdit, QMenu, QInputDialog, QFileDialog
from PyQt5.QtGui import QFont, QIcon, QPixmap, QIntValidator
from PyQt5.QtCore import Qt
from dependencies.list_widget import ListWidget, EntryWidget
from dependencies.auxiliaries import rollFunction
import os, json


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

    def __init__(self, health):
        super().__init__()
        self.m_maxHP = health

        self.setLayout(QHBoxLayout())
        iconLabel = QLabel()
        iconSize = [self.ratio*self.height, self.height]
        iconLabel.setFixedSize(*iconSize)
        iconLabel.setScaledContents(True)
        iconLabel.setPixmap(QPixmap(self.iconPath))
        self.textLabel = QLabel(str(self.m_maxHP))
        self.textLabel.setFixedWidth(30)
        self.textLabel.setFont(QFont("Helvetica [Cronyx]", 12))
        self.layout().addWidget(iconLabel)
        self.layout().addWidget(self.textLabel)
        self.layout().setAlignment(Qt.AlignLeft)

    def set(self, value):
        self.textLabel.setText(str(value))

    def get(self):
        return int(self.textLabel.text())

    def max(self):
        return int(self.m_maxHP)


class DamageInputFrame(QFrame):
    height = 30
    ratio = 0.67
    iconPath = "assets/icons/sword_icon.png"

    def __init__(self, healthWidget):
        super().__init__()
        self.m_health = healthWidget
        self.setLayout(QHBoxLayout())
        iconLabel = QLabel()
        iconSize = [self.ratio*self.height, self.height]
        iconLabel.setFixedSize(*iconSize)
        iconLabel.setScaledContents(True)
        iconLabel.setPixmap(QPixmap(self.iconPath))
        self.damageEdit = QLineEdit()
        self.damageEdit.setFixedWidth(30)
        self.damageEdit.returnPressed.connect(self.returnPressedHandle)
        self.damageEdit.setValidator(QIntValidator(-999, 999))

        self.layout().addWidget(iconLabel)
        self.layout().addWidget(self.damageEdit)
        self.layout().setAlignment(Qt.AlignLeft)

    def returnPressedHandle(self):
        damage = int(self.damageEdit.text())
        newHealth = self.m_health.get() - damage
        if newHealth < 0:
            newHealth = 0
        if newHealth > self.m_health.max():
            newHealth = self.m_health.max()
        self.m_health.set(newHealth)
        self.damageEdit.clear()


class InitiativeFrame(QFrame):
    height = 30
    ratio = 0.56
    iconPath = "assets/icons/initiative_icon.png"

    def __init__(self, initiative):
        super().__init__()
        self.setLayout(QHBoxLayout())
        iconLabel = QLabel()
        iconSize = [self.ratio*self.height, self.height]
        iconLabel.setFixedSize(*iconSize)
        iconLabel.setScaledContents(True)
        iconLabel.setPixmap(QPixmap(self.iconPath))
        self.textLabel = QLabel(initiative)
        self.textLabel.setFixedWidth(30)
        self.textLabel.setFont(QFont("Helvetica [Cronyx]", 12))
        self.layout().addWidget(iconLabel)
        self.layout().addWidget(self.textLabel)
        self.layout().setAlignment(Qt.AlignLeft)

    def set(self, value):
        self.textLabel.setText(str(value))

    def get(self):
        try:
            return int(self.textLabel.text())
        except ValueError:
            return 0


class InitiativeWidget(EntryWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(10, 0, 10, 0)
        self.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.setMinimumHeight(50)
        self.setFrameShape(QFrame.Box)

    def getInitiative(self):
        return self.m_initiative.get()


class MonsterWidget(InitiativeWidget):
    def __init__(self, monster, parentList, viewer=None, init=None, hp=None, desc=None):
        super().__init__()
        self.m_health = HealthFrame(hp)
        self.m_initiative = InitiativeFrame("")
        self.monster = monster
        self.viewer = viewer
        self.parent = parentList
        self.layout().addWidget(NameLabel(monster.name))
        self.layout().addWidget(self.m_health)
        self.layout().addWidget(DamageInputFrame(self.m_health))
        self.layout().addWidget(self.m_initiative)

    def rollInitiative(self):
        self.m_initiative.set(rollFunction("1d20") + self.monster.initiative)

    def mouseReleaseEvent(self, event):
        if self.viewer is None:
            return
        self.viewer.draw_view(self.monster)

    def contextMenuEvent(self, event):
        menu = QMenu()
        removeAction = menu.addAction("Remove from Initiative")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        elif action == removeAction:
            self.parent.remove(self)

    def jsonlify(self):
        output = dict(
            type="Monster",
            monster=self.monster.name,
            hp=self.m_health.get(),
            init=self.m_initiative.get()
        )
        return json.dumps(output)


class PlayerWidget(InitiativeWidget):
    def __init__(self, character):
        self.m_initiative = InitiativeFrame("")
        self.m_character = character
        self.layout().addWidget(self.m_initiative)

    def getCharName(self):
        return self.m_character.getCharName()

    def jsonlify(self):
        output = dict(
            type="Player",
            name=self.getCharName(),
            init=self.m_initiative.get()
        )
        return json.dumps(output)

class EncounterWidget(ListWidget):
    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer

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
        self.add_players_button = QPushButton("Add Players")
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
                self.addToEncounter(monster, init=entry["init"], hp=entry["hp"])

    def getCharacterNames(self):
        charNameList = []
        for entry in self.m_widgetList:
            if type(entry) is PlayerWidget:
                if entry.getCharName() not in charNameList:
                    charNameList.append(entry.getCharName())
        return charNameList

    def updateCharacterInitiative(self, character):
        pass

    def sortInitiative(self):
        unsortedList = []
        for entry in self.m_widgetList:
            unsortedList.append((entry.getInitiative(), entry))
        sortedList = sorted(unsortedList, key=lambda x: x[0], reverse=True)
        self.clear()
        for itt, entry in sortedList:
            self.add(entry)

    def rollInitiative(self):
        for entry in self.m_widgetList:
            if type(entry) is MonsterWidget:
                entry.rollInitiative()

    def addToEncounter(self, monster, number=1, init=None, hp=None, desc=None):
        if hp is None:
            hp = monster.hp_no_dice
        for itt in range(number):
            self.add(MonsterWidget(monster, self, self.viewer, init, hp, desc))

