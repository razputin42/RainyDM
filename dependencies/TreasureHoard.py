import dependencies.lootTables as LT
import random
from dependencies.auxiliaries import roll_function
from dependencies.encounter import NameLabel
from dependencies.list_widget import ListWidget, EntryWidget, colorDict
from dependencies.signals import sNexus
from dependencies.views import ItemViewer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QLabel
from PyQt5.QtGui import QFont, QMouseEvent

class TreasureHoard:
    @property
    def table(self):
        raise NotImplementedError

    def roll(self):
        percent_sum = 0
        table_roll = roll_function("1d100")
        for percent, amount, lootTable in self.table:
            percent_sum = percent_sum + percent
            if table_roll < percent_sum:
                if lootTable is None or amount is None:
                    return None
                else:
                    return lootTable().roll(amount)


class TreasureHoardLow(TreasureHoard):
    table = [(36, None, None),
            (21, "1d6", LT.LootTableA),
            (15, "1d4", LT.LootTableB),
            (9, "1d4", LT.LootTableA),
            (11, "1d4", LT.LootTableA),
            (3, "1", LT.LootTableA)]


class LootWidget(EntryWidget):
    def __init__(self, item, viewer):
        super().__init__()
        self.color = colorDict["white"]
        self.setLayout(QHBoxLayout())
        name_label = NameLabel(item.name)
        self.layout().addWidget(name_label)
        self.setFrameShape(QFrame.Box)
        self.deselect()

    def mousePressEvent(self, a0: QMouseEvent):
        sNexus.treasureHoardDeselectSignal.emit()
        self.darker_color = [i - 30 for i in self.color]
        self.setStyleSheet("background-color: #{:02X}{:02X}{:02X};".format(*self.darker_color))
        self.setProperty('clicked', True)
        self.redraw()

    def deselect(self):
        self.setStyleSheet("background-color: #{:02X}{:02X}{:02X};".format(*self.color))
        self.setProperty('clicked', False)



class TreasureHoardWidget(ListWidget):
    challengeRatingLow = "0 - 4"

    def __init__(self, item_list):
        super().__init__()
        self.setLayout(QHBoxLayout())
        rollButton = QPushButton("Roll")
        rollButton.clicked.connect(self.rollLoot)
        self.layout().addWidget(rollButton)
        self.item_list = item_list
        sNexus.treasureHoardDeselectSignal.connect(self.deselectAll)

    def readChallengeRating(self):
        return self.challengeRatingLow

    def rollLoot(self):
        challenge_rating = self.readChallengeRating()
        if challenge_rating is self.challengeRatingLow:
            items_attr = TreasureHoardLow().roll()
            if items_attr is None:
                self.set_no_loot()
            else:
                loot = self.acquire_loot(items_attr)
                self.set_loot(loot)

    def set_no_loot(self):
        pass

    def clear_loot_valuables(self):
        pass

    def acquire_loot(self, items_attr):
        output_list = []
        for item_attr in items_attr:
            subset = self.item_list.subset(item_attr)
            output_list.append(random.choice(subset))
        return output_list

    def set_loot(self, loot):
        self.clear()
        for item in loot:
            frame = LootWidget(item)
            self.add(frame)
            print(item.name)

class TreasureHoardTab(QWidget):
    def __init__(self, parent, viewer, item_list):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.item_list = item_list
        self.parent = parent
        self.viewer = viewer
        self.setup()

    def setup(self):
        LootGenerator = TreasureHoardWidget(self.item_list)
        self.layout().addWidget(LootGenerator)
        self.layout().addWidget(self.viewer)
