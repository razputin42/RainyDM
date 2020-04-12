import re
import copy
from PyQt5.QtCore import pyqtSignal, QObject
from dependencies.signals import sNexus
import math

xp_dict = {
    "00": 0,
    "0": 10,
    "1/8": 25,
    "1/4": 50,
    "1/2": 100,
    "1": 200,
    "2": 450,
    "3": 700,
    "4": 1100,
    "5": 1800,
    "6": 2300,
    "7": 2900,
    "8": 3900,
    "9": 5500,
    "10": 5900,
    "11": 7200,
    "12": 8400,
    "13": 10000,
    "14": 11500,
    "15": 13000,
    "16": 15000,
    "17": 18000,
    "18": 20000,
    "19": 22000,
    "20": 25000,
    "21": 33000,
    "22": 41000,
    "23": 50000,
    "24": 62000,
    "25": 75000,
    "26": 90000,
    "27": 105000,
    "28": 120000,
    "29": 135000,
    "30": 155000
}

size_dict = dict(
    T="Tiny",
    S="Small",
    M="Medium",
    L="Large",
    H="Huge",
    G="Gargantuan",
    A="Medium"
)


class Monster (QObject):
    database_fields = [
        'name', 'size', 'type', 'alignment', 'ac', 'hp', 'speed',
        ['str', 'dex', 'con', 'int', 'wis', 'cha'],
        'save', 'resist', 'immune', 'conditionImmune', 'skill', 'senses', 'languages', 'passive', 'cr', 'spells'
    ]
    required_database_fields = ['name',
                                'str', 'dex', 'con', 'int', 'wis', 'cha',
                                ]

    class Action:
        database_fields = ['name', 'text', 'attack']

        def __init__(self, attr):
            s = ""
            for itt, _attr in enumerate(attr):
                if _attr.tag == "text":
                    if _attr.text is None:
                        s = s + "<br>"
                    else:
                        s = s + _attr.text
                        if itt != 0 and itt != len(attr) - 1:
                            s = s + "<br>"
                else:
                    setattr(self, _attr.tag, _attr.text)
            self.text = s

        def __str__(self):
            return self.name + ": " + self.text

    class Trait(Action):
        pass

    def __init__(self, entry, idx):
        super().__init__()
        self.entry = entry
        self.index = idx
        self.action_list = []
        self.trait_list = []
        self.legendary_list = []
        if entry is not None:
            for attr in entry:
                # print(attr.tag, attr.text)
                if attr.text is None:
                    setattr(self, attr.tag, attr.text)
                elif attr.tag == "trait":
                    self._add_trait(attr)
                elif attr.tag == "action":
                    self._add_action(attr)
                elif attr.tag == "legendary":
                    self._add_legendary(attr)
                elif attr.tag == "size":
                    size = attr.text.upper()
                    if size in size_dict.keys():
                        self.size = size_dict[size]
                    else:
                        self.size = attr.text
                elif attr.tag == "type" and attr.text is not None and ',' in attr.text:
                    temp_list = attr.text.split(",")
                    self.type = ",".join(temp_list[:-1]).strip()
                    if 'swarm' in self.type.lower():
                        self.type = 'Swarm'
                    self.source = temp_list[-1]
                    if "(" in self.type:
                        subtype_raw = self.type[self.type.find("(") + 1:self.type.find(")")]
                        subtype_list = subtype_raw.split(", ")
                        self.subtype = []
                        for subtype in subtype_list:
                            self.subtype.append(subtype.strip())
                else:
                    setattr(self, attr.tag, attr.text)
            if hasattr(self, 'cr') and self.cr is not None:
                self.xp = xp_dict[self.cr]
            else:
                self.xp = 0
            if hasattr(self, 'dex') and self.dex is not None:
                self.initiative = self.calculate_modifier(self.dex)
            if hasattr(self, 'hp') and self.hp is not None:
                self.hp_no_dice, self.HD = self.extract_hp(self.hp)
        else:
            self.name = ""
            self.size = ""
            self.type = ""
            self.alignment = ""
            self.ac = ""
            self.hp = ""
            self.speed = ""
            self.str = 0
            self.dex = 0
            self.con = 0
            self.wis = 0
            self.int = 0
            self.cha = 0
            self.cr = ""
            self.xp = 0

    @staticmethod
    def extract_hp(hp):
        if hp is None:
            return "", ""
        i = hp.find("(")
        if i is not -1:
            j = hp.find(")")
            hp_no_dice = hp[0:i]
            HD = hp[i+1:j]
        else:
            hp_no_dice = ""
            HD = ""
        return hp_no_dice, HD

    @staticmethod
    def calculate_modifier(score, sign=False):
        if score is None:
            return 0
        score = int(score)
        mod = math.floor((score-10)/2)
        if sign:
            if mod > 0:
                return "+" + str(mod)
        return mod

    def _add_action(self, attr):
        action = self.Action(attr)
        self.action_list.append(action)

    def _add_trait(self, attr):
        trait = self.Trait(attr)
        self.trait_list.append(trait)

    def _add_legendary(self, attr):
        legendary = self.Action(attr)
        self.legendary_list.append(legendary)

    def extract_spellbook(self):
        return_list = []
        if hasattr(self, "spells") and self.spells is not None:
            for s in self.spells.split(","):
                return_list.append(s.strip().replace('*', ''))
            return return_list
        else:
            return None

    def addSpells(self):
        sNexus.addSpellsSignal.emit(self.extract_spellbook())

    def add_to_encounter(self, n=1):
        sNexus.addMonstersToEncounter.emit(self, n)

    def copy(self):
        return copy.deepcopy(self)

    def performAttack(self, attack):
        sNexus.attackSignal.emit(self.name, attack.attack)


class Monster35(Monster):
    def __init__(self, entry, idx):
        self.entry = entry
        self.index = idx
        for attr in entry:
            if attr.tag == "hit_dice":
                HD, hp_no_dice = self.extract_hp(attr.text)
                hp_no_dice = hp_no_dice.replace(' hp', '')
                self.HD = HD
                self.hp_no_dice = hp_no_dice
            elif attr.tag == "challenge_rating":
                self.cr = re.sub("[^,;0-9/]+", "", attr.text)
            # elif attr.tag == "abilities":
                # for ability in attr.text.split(", "):
                #     temp = ability.split(" ")
                #     setattr(self, temp[0].lower(), int(temp[1]))
            elif attr.tag == "initiative":
                self.initiative = int(attr.text.split(" ")[0])
            else:
                setattr(self, attr.tag, attr.text)