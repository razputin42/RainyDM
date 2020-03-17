from dependencies.auxiliaries import roll_function

class LootTable:
    excludePotions = False
    excludeScrolls = False

    @property
    def chances(self):
        raise NotImplementedError

    def roll_single(self):
        percent_sum = 0
        dice_roll = roll_function("1d100") / 100.0
        for percent, attr in self.chances:
            percent_sum = percent + percent_sum
            if dice_roll <= percent_sum:
                return attr
        print("HERE")

    def roll(self, amount):
        output_list = []
        n = roll_function(amount)
        for i in range(n):
            output_list.append(self.roll_single())
        return output_list


class LootTableA(LootTable):
    chances = [
        (0.6, [("type", "Potion"), ("rarity", "Common")]),
        (0.3, [("type", "Scroll"), ("rarity", "Common")]),
        (0.04, [("type", "Scroll"), ("rarity", "Uncommon")]),
        (0.04, [("type", "Potion"), ("rarity", "Uncommon")]),
        (0.02, [("type", "Wonderous"), ("rarity", "Uncommon")])
        ]


class LootTableB(LootTable):
    chances = [
        (0.6, [("type", "Potion"), ("rarity", "Common")]),
        (0.3, [("type", "Scroll"), ("rarity", "Common")]),
        (0.04, [("type", "Scroll"), ("rarity", "Uncommon")]),
        (0.04, [("type", "Potion"), ("rarity", "Uncommon")]),
        (0.02, [("type", "Wonderous"), ("rarity", "Uncommon")])
        ]

class LootTableC(LootTable):
    chances = []


class LootTableD(LootTable):
    chances = []


class LootTableE(LootTable):
    chances = []


class LootTableF(LootTable):
    chances = []


class LootTableG(LootTable):
    chances = []

