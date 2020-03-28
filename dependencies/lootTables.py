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


def ring(rarity):
    return dict({"type": "Ring", "rarity": rarity})


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
        (0.5, potion("Uncommon")),
        (0.27, wondrous("Uncommon")),
        (0.10, scroll("Uncommon")),
        (0.05, ammunition("Uncommon")),
        (0.03, specific_item("Bag of Holding")),
        (0.02, armor("Uncommon")),
        (0.02, wand("Uncommon")),
        (0.01, ring("Uncommon"))
        ]


class LootTableC(LootTable):
    chances = [
        (0.64, potion("Rare")),
        (0.16, wondrous("Rare")),
        (0.15, scroll("Rare")),
        (0.05, ammunition("Rare"))
        ]


class LootTableD(LootTable):
    chances = [
        (0.64, potion("Very Rare")),
        (0.08, wondrous("Very Rare")),
        (0.23, scroll("Very Rare")),
        (0.05, ammunition("Very Rare"))
        ]


class LootTableE(LootTable):
    chances = [
        (0.40, potion("Very Rare")),
        (0.30, scroll("Very Rare")),
        (0.15, scroll("Legendary")),
        (0.10, wondrous("Legendary")),
        (0.05, ammunition("Very Rare"))
        ]


class LootTableF(LootTable):
    chances = [
        (0.51, wondrous("Uncommon")),
        (0.24, weapon("Uncommon")),
        (0.06, wand("Uncommon")),
        (0.06, shield("Uncommon")),
        (0.04, staff("Uncommon")),
        (0.04, ring("Uncommon")),
        (0.03, armor("Uncommon")),
        (0.02, rod("Uncommon"))
    ]


class LootTableG(LootTable):
    chances = [
        (0.41, wondrous("Rare")),
        (0.28, weapon("Rare")),
        (0.11, armor("Rare")),
        (0.09, ring("Rare")),
        (0.05, staff("Rare")),
        (0.03, shield("Rare")),
        (0.03, rod("Rare"))
    ]


class LootTableH(LootTable):
    chances = [
        (0.34, wondrous("Very Rare")),
        (0.19, weapon("Very Rare")),
        (0.15, armor("Very Rare")),
        (0.10, staff("Very Rare")),
        (0.08, rod("Very Rare")),
        (0.08, wand("Very Rare")),
        (0.06, ring("Very Rare")),
        (0.04, shield("Very Rare"))
    ]


class LootTableI(LootTable):
    chances = [
        (0.26, wondrous("Legendary")),
        (0.26, weapon("Legendary")),
        (0.24, armor("Legendary")),
        (0.03, staff("Legendary")),
        (0.05, rod("Legendary")),
        (0.14, ring("Legendary"))
    ]
