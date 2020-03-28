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
    pass


class RerollButton(QPushButton):
    def __init__(self):
        super().__init__("Reroll Type")


class LootWidget(EntryWidget):
    def __init__(self, item, item_dict, item_list, viewer):
        super().__init__(item, viewer)
        self.setObjectName("LootWidget")
        self.item = item
        self.item_dict = item_dict
        self.item_list = item_list
        self.viewer = viewer

        self.setLayout(QHBoxLayout())
        self.name_label = NameLabel(item.name)
        self.reroll_button = RerollButton()
        self.reroll_button.clicked.connect(self.reroll_item_from_set)
        self.layout().addWidget(self.name_label)
        self.layout().addStretch(1)
        self.layout().addWidget(self.reroll_button)
        self.setFrameShape(QFrame.Box)

    def reroll_item_from_set(self):
        subset = self.item_list.subset(self.item_dict)
        self.item = random.choice(subset)
        self.name_label.setText(self.item.name)
        self.viewer.draw_view(self.item)

    def reroll_item(self):
        pass

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
    challengeRatingMidLow = "5 - 8"
    challengeRatingMidHigh = "9 - 12"
    challengeRatingHigh = "13 - 16"

    def __init__(self, item_list, viewer):
        super().__init__()
        self.viewer = viewer
        # self.setLayout(QHBoxLayout())
        rollButton = QPushButton("Roll")
        rollButton.clicked.connect(self.roll_loot)
        self.layout().addWidget(rollButton)
        self.item_list = item_list
        sNexus.treasureHoardDeselectSignal.connect(self.deselectAll)

    def read_challenge_rating(self):
        return self.challengeRatingLow

    def roll_loot(self):
        challenge_rating = self.read_challenge_rating()
        if challenge_rating is self.challengeRatingLow:
            items_dict = TreasureHoardLow().roll()
        elif challenge_rating is self.challengeRatingMidLow:
            items_dict = TreasureHoardMidLow().roll()
        elif challenge_rating is self.challengeRatingMidHigh:
            items_dict = TreasureHoardMidHigh().roll()
        elif challenge_rating is self.challengeRatingHigh:
            items_dict = TreasureHoardHigh().roll()

        print(items_dict)

        if items_dict is None:
            self.set_no_loot()
        else:
            loot = self.acquire_loot(items_dict)
            self.set_loot(loot)

    def set_no_loot(self):
        pass

    def clear_loot_valuables(self):
        pass

    def acquire_loot(self, items_dict):
        output_list = []
        for item_dict in items_dict:
            subset = self.item_list.subset(item_dict)
            output_list.append((random.choice(subset), item_dict))
        return output_list

    def set_loot(self, loot):
        self.clear()
        for item, item_dict in loot:
            frame = LootWidget(item, item_dict, self.item_list, self.viewer)
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
