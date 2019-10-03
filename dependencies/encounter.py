from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtGui import QFont, QIcon, QPixmap, QIntValidator
from PyQt5.QtCore import Qt
from dependencies.list_widget import ListWidget, EntryWidget
from dependencies.auxiliaries import rollFunction


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
        self.textLabel = QLabel(self.m_maxHP)
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
        return int(self.textLabel.text())


class InitiativeWidget(EntryWidget):
    def __init__(self):
        super().__init__()
        self.layout().setContentsMargins(10, 0, 10, 0)
        self.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.setMinimumHeight(50)


class MonsterWidget(InitiativeWidget):
    def __init__(self, monster, viewer=None, init=None, hp=None, desc=None):
        super().__init__()
        self.setFrameShape(QFrame.Box)
        self.m_health = HealthFrame(hp)
        self.m_initiative = InitiativeFrame("")
        self.monster = monster
        self.viewer = viewer
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


class PlayerWidget(InitiativeWidget):
    pass


class EncounterWidget(ListWidget):
    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer

    def calculate_encounter_xp(self):
        pass

    def format(self):
        pass

    def contextMenuEvent(self, event):
        pass

    def data_changed_handle(self, row, column):
        pass

    def _convert_to_int(self, row, column):
        pass

    def save(self):
        pass

    def load(self, monster_table):
        pass

    def add_to_encounter(self, monster, number=1, init=None, hp=None, desc=None):
        if hp is None:
            hp = monster.hp_no_dice
        for itt in range(number):
            # button = QPushButton("TEST")
            # button.setMinimumHeight(30)
            # self.add(button)
            self.add(MonsterWidget(monster, self.viewer, init, hp, desc))

