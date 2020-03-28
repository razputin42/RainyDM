from dependencies.auxiliaries import roll_function


def potion(rarity):
    return dict({"type": "Potion", "rarity": rarity})


def scroll(rarity):
    return dict({"type": "Scroll", "rarity": rarity})


def specific_item(name):
    return dict({"name": name})


def wondrous(rarity):
    return dict({"type": "Wondrous", "rarity": rarity})


def ammunition(rarity):
    return dict({"type": "Ammunition", "rarity": rarity})


def armor(rarity):
    return dict({"type": "Armor", "rarity": rarity})


def weapon(rarity):
    return dict({"type": "Weapon", "rarity": rarity})


def shield(rarity):
    return dict({"type": "Shield", "rarity": rarity})


def staff(rarity):
    return dict({"type": "Staff", "rarity": rarity})


def wand(rarity):
    return dict({"type": "Wand", "rarity": rarity})


def rod(rarity):
    return dict({"type": "Rod", "rarity": rarity})


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

    def roll(self, amount):
        output_list = []
        n = roll_function(amount)
        for i in range(n):
            output_list.append(self.roll_single())
        return output_list


class LootTableA(LootTable):
    chances = [
        (0.6, potion("Common")),
        (0.3, scroll("Common")),
        (0.04, scroll("Uncommon")),
        (0.04, potion("Uncommon")),
        (0.01, specific_item("Bag of Holding")),
        (0.01, wondrous("Uncommon"))
        ]

    # chances = [
    #     (0.6, [("type", "Potion"), ("rarity", "Common")]),
    #     (0.3, [("type", "Scroll"), ("rarity", "Common")]),
    #     (0.04, [("type", "Scroll"), ("rarity", "Uncommon")]),
    #     (0.04, [("type", "Potion"), ("rarity", "Uncommon")]),
    #     (0.01, [("name", "Bag of Holding")]),
    #     (0.01, [("type", "Wondrous"), ("rarity", "Uncommon")])
    #     ]


class LootTableB(LootTable):
    chances = [
        (0.5, [("type", "Potion"), ("rarity", "Uncommon")]),
        (0.27, [("type", "Wondrous"), ("rarity", "Uncommon")]),
        (0.10, [("type", "Scroll"), ("rarity", "Uncommon")]),
        (0.05, [("type", "Ammunition"), ("rarity", "Uncommon")]),
        (0.03, [("name", "Bag of Holding")]),
        (0.02, [("type", "Armor"), ("rarity", "Uncommon")]),
        (0.02, [("type", "Wand"), ("rarity", "Uncommon")]),
        (0.01, [("type", "Ring"), ("rarity", "Uncommon")])
        ]


class LootTableC(LootTable):
    chances = [
        (0.64, [("type", "Potion"), ("rarity", "Rare")]),
        (0.16, [("type", "Wondrous"), ("rarity", "Rare")]),
        (0.15, [("type", "Scroll"), ("rarity", "Rare")]),
        (0.05, [("type", "Ammunition"), ("rarity", "Rare")])
        ]


class LootTableD(LootTable):
    chances = [
        (0.64, [("type", "Potion"), ("rarity", "Very Rare")]),
        (0.08, [("type", "Wondrous"), ("rarity", "Very Rare")]),
        (0.23, [("type", "Scroll"), ("rarity", "Very Rare")]),
        (0.05, [("type", "Ammunition"), ("rarity", "Very Rare")])
        ]


class LootTableE(LootTable):
    chances = [
        (0.40, [("type", "Potion"), ("rarity", "Very Rare")]),
        (0.30, [("type", "Scroll"), ("rarity", "Very Rare")]),
        (0.15, [("type", "Scroll"), ("rarity", "Legendary")]),
        (0.10, [("type", "Wondrous"), ("rarity", "Legendary")]),
        (0.05, [("type", "Ammunition"), ("rarity", "Very Rare")])
        ]


class LootTableF(LootTable):
    chances = [
        (0.51, [("type", "Wondrous"), ("rarity", "Uncommon")]),
        (0.24, [("type", "Weapon"), ("rarity", "Uncommon")]),
        (0.06, [("type", "Wand"), ("rarity", "Uncommon")]),
        (0.06, [("type", "Shield"), ("rarity", "Uncommon")]),
        (0.04, [("type", "Staff"), ("rarity", "Uncommon")]),
        (0.04, [("type", "Ring"), ("rarity", "Uncommon")]),
        (0.03, [("type", "Armor"), ("rarity", "Uncommon")]),
        (0.02, [("type", "Rod"), ("rarity", "Uncommon")])
    ]


class LootTableG(LootTable):
    chances = [
        (0.41, [("type", "Wondrous"), ("rarity", "Rare")]),
        (0.28, [("type", "Weapon"), ("rarity", "Rare")]),
        (0.11, [("type", "Armor"), ("rarity", "Rare")]),
        (0.09, [("type", "Ring"), ("rarity", "Rare")]),
        (0.05, [("type", "Staff"), ("rarity", "Rare")]),
        (0.03, [("type", "Shield"), ("rarity", "Rare")]),
        (0.03, [("type", "Rod"), ("rarity", "Rare")])
    ]


class LootTableH(LootTable):
    chances = [
        (0.34, [("type", "Wondrous"), ("rarity", "Very Rare")]),
        (0.19, [("type", "Weapon"), ("rarity", "Very Rare")]),
        (0.15, [("type", "Armor"), ("rarity", "Very Rare")]),
        (0.10, [("type", "Staff"), ("rarity", "Very Rare")]),
        (0.08, [("type", "Rod"), ("rarity", "Very Rare")]),
        (0.08, [("type", "Wand"), ("rarity", "Very Rare")]),
        (0.06, [("type", "Ring"), ("rarity", "Very Rare")]),
        (0.04, [("type", "Shield"), ("rarity", "Very Rare")])
    ]


class LootTableH(LootTable):
    chances = [
        (0.26, [("type", "Wondrous"), ("rarity", "Legendary")]),
        (0.26, [("type", "Weapon"), ("rarity", "Legendary")]),
        (0.24, [("type", "Armor"), ("rarity", "Legendary")]),
        (0.03, [("type", "Staff"), ("rarity", "Legendary")]),
        (0.05, [("type", "Rod"), ("rarity", "Legendary")]),
        (0.14, [("type", "Ring"), ("rarity", "Legendary")])
    ]
