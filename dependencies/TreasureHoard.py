import dependencies.lootTables as LT
import random
from dependencies.auxiliaries import roll_function
from dependencies.encounter import NameLabel
from dependencies.list_widget import ListWidget, EntryWidget, colorDict
from dependencies.signals import sNexus
from dependencies.views import ItemViewer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QComboBox, QSpacerItem
from PyQt5.QtGui import QFont, QMouseEvent
import os

class TreasureHoard:
    @property
    def table(self):
        raise NotImplementedError

    def roll(self):
        percent_sum = 0
        table_roll = roll_function("1d100")
        for percent, table_sets in self.table:
            percent_sum = percent_sum + percent
            if table_roll < percent_sum:
                if table_sets is None:
                    return None
                else:
                    rolled_items = None
                    for amount, loot_table in table_sets:
                        if rolled_items is None:
                            rolled_items = loot_table().roll(amount)
                        else:
                            rolled_items.append(loot_table().roll(amount))
                    return rolled_items


class TreasureHoardLow(TreasureHoard):
    table = [(36, None),
            (22,    [("1d6",  LT.LootTableA)]),
            (16,    [("1d4",  LT.LootTableB)]),
            (10,     [("1d4",  LT.LootTableA)]),
            (12,    [("1d4",  LT.LootTableA)]),
            (4,     [("1",    LT.LootTableA)])
    ]


class TreasureHoardMidLow(TreasureHoard):
    table = [(28, None),
             (16,   [("1d6",  LT.LootTableA)]),
             (19,   [("1d4",  LT.LootTableB)]),
             (11,   [("1d4",  LT.LootTableC)]),
             (6,    [("1",    LT.LootTableD)]),
             (14,   [("1d4",  LT.LootTableF)]),
             (4,    [("1d4",  LT.LootTableG)]),
             (2,    [("1",    LT.LootTableH)])
    ]


class TreasureHoardMidHigh(TreasureHoard):
    table = [(28, None),
             (16,   [("1d6",  LT.LootTableA)]),
             (19,   [("1d4",  LT.LootTableB)]),
             (11,   [("1d4",  LT.LootTableC)]),
             (6,    [("1",    LT.LootTableD)]),
             (14,   [("1d4",  LT.LootTableF)]),
             (4,    [("1d4",  LT.LootTableG)]),
             (2,    [("1",    LT.LootTableH)])
    ]


class TreasureHoardHigh(TreasureHoard):
    table = [(2, None),
             (12,   [("1d8", LT.LootTableC)]),
             (32,   [("1d6", LT.LootTableD)]),
             (22,   [("1d6", LT.LootTableE)]),
             (4,    [("1d4", LT.LootTableG)]),
             (8,    [("1d4", LT.LootTableH)]),
             (20,   [("1d4", LT.LootTableI)])
    ]


class RerollButton(QPushButton):
    def __init__(self):
        super().__init__("")


class LootWidget(EntryWidget):
    def __init__(self, item, item_list, viewer):
        super().__init__(item, viewer)
        self.setObjectName("LootWidget")
        self.item = item
        self.item_list = item_list
        self.viewer = viewer

        name_frame = QFrame()
        name_frame.setContentsMargins(0, 0, 0, 0)
        name_frame.setLayout(QHBoxLayout())
        self.name_label = NameLabel(item.name)
        self.name_label.setObjectName("LootWidget_name")
        name_frame.layout().addWidget(self.name_label)
        name_frame.layout().addStretch(1)

        self.reroll_button = RerollButton()
        self.reroll_button.clicked.connect(self.reroll_item)

        self.button_bar = QFrame()
        self.button_bar.setContentsMargins(0, 0, 0, 0)
        self.button_bar.setLayout(QHBoxLayout())

        self.button_bar.setHidden(True)
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItem("Any")
        self.type_dropdown.addItem("Weapon")
        self.type_dropdown.addItem("Armor")
        self.type_dropdown.addItems(self.item_list.unique_attr("type"))
        if self.item.type in ["Staff", "Melee", "Ranged", "Rod"]:
            self.type_dropdown.setCurrentText("Weapon")
        elif self.item.type in ["Light Armor, Medium Armor, Heavy Armor"]:
            self.type_dropdown.setCurrentText("Armor")
        else:
            self.type_dropdown.setCurrentText(self.item.type)

        self.rarity_dropdown = QComboBox()
        self.rarity_dropdown.addItems(self.item_list.unique_attr("rarity"))
        self.rarity_dropdown.setCurrentText(self.item.rarity)

        self.button_bar.layout().addWidget(self.type_dropdown)
        self.button_bar.layout().addWidget(self.rarity_dropdown)
        self.button_bar.layout().addStretch(1)
        self.button_bar.layout().addWidget(self.reroll_button)

        self.setLayout(QVBoxLayout())
        QSpacerItem(50, 10)
        self.layout().setContentsMargins(20, 5, 10, 10)
        self.layout().addWidget(name_frame)
        self.layout().addWidget(self.button_bar)
        self.setFrameShape(QFrame.Box)

    def reroll_item(self):
        item_dict = dict({"type": self.type_dropdown.currentText(), "rarity": self.rarity_dropdown.currentText()})
        subset = self.item_list.subset(item_dict)
        if len(subset) is 0:
            sNexus.printSignal.emit(
                "There is no {} {} in the database.".format(item_dict["rarity"], item_dict["type"]))
            return
        self.item = random.choice(subset)
        self.name_label.setText(self.item.name)
        self.viewer.draw_view(self.item)

    def mousePressEvent(self, a0: QMouseEvent):
        if self.property('clicked'):  # already clicked
            self.deselect()
        else:
            sNexus.treasureHoardDeselectSignal.emit()
            self.select()
            self.viewer.draw_view(self.item)
        self.redraw()


class TreasureHoardWidget(ListWidget):
    challengeRatingLow = "0 - 4"
    challengeRatingMidLow = "5 - 10"
    challengeRatingMidHigh = "11 - 16"
    challengeRatingHigh = "17+"

    def __init__(self, item_list, viewer):
        self.challenge_rating_combo_box = QComboBox()
        self.challenge_rating_combo_box.addItems([
            self.challengeRatingLow,
            self.challengeRatingMidLow,
            self.challengeRatingMidHigh,
            self.challengeRatingHigh])
        super().__init__()
        self.viewer = viewer
        rollButton = QPushButton("Roll")
        rollButton.clicked.connect(self.roll_loot)
        bottom_bar = QFrame()
        bottom_bar.setLayout(QHBoxLayout())
        bottom_bar.layout().addStretch(1)
        bottom_bar.layout().addWidget(self.challenge_rating_combo_box)
        bottom_bar.layout().addWidget(rollButton)
        self.layout().addWidget(bottom_bar)
        self.item_list = item_list
        sNexus.treasureHoardDeselectSignal.connect(self.deselectAll)

    def read_challenge_rating(self):
        return self.challenge_rating_combo_box.currentText()

    def roll_loot(self):
        challenge_rating = self.read_challenge_rating()
        if challenge_rating == self.challengeRatingLow:
            items_dict = TreasureHoardLow().roll()
        elif challenge_rating == self.challengeRatingMidLow:
            items_dict = TreasureHoardMidLow().roll()
        elif challenge_rating == self.challengeRatingMidHigh:
            items_dict = TreasureHoardMidHigh().roll()
        elif challenge_rating == self.challengeRatingHigh:
            items_dict = TreasureHoardHigh().roll()

        if items_dict is None:
            self.set_no_loot()
        else:
            loot = self.acquire_loot(items_dict)
            self.set_loot(loot)

    def set_no_loot(self):
        self.clear()
        sNexus.printSignal.emit("Treasure hoard yielded no loot")

    def clear_loot_valuables(self):
        pass

    def acquire_loot(self, items_dict):
        output_list = []
        for item_dict in items_dict:
            subset = self.item_list.subset(item_dict)
            output_list.append(random.choice(subset))
        return output_list

    def set_loot(self, loot):
        self.clear()
        for item in loot:
            frame = LootWidget(item, self.item_list, self.viewer)
            self.add(frame)


class TreasureHoardTab(QWidget):
    def __init__(self, parent, viewer, item_list):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.item_list = item_list
        self.parent = parent
        self.viewer = viewer
        self.setup()

    def setup(self):
        LootGenerator = TreasureHoardWidget(self.item_list, self.viewer)
        self.layout().addWidget(LootGenerator)
        self.layout().addWidget(self.viewer)
