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

class Monster:
    class Action:
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
        None

    def __init__(self, entry, idx):
        self.entry = entry
        self.index = idx
        self.action_list = []
        self.trait_list = []
        self.legendary_list = []
        for attr in entry:
            if attr.tag == "trait":
                self._add_trait(attr)
            elif attr.tag == "action":
                self._add_action(attr)
            elif attr.tag == "legendary":
                self._add_legendary(attr)
            elif attr.tag == "type":
                temp_list = attr.text.split(",")
                self.type = ",".join(temp_list[:-1]).strip()
                self.source = temp_list[-1]
                if "(" in self.type:
                    subtype_raw = self.type[self.type.find("(") + 1:self.type.find(")")]
                    subtype_list = subtype_raw.split(", ")
                    self.subtype = []
                    for subtype in subtype_list:
                        self.subtype.append(subtype.strip())
            else:
                setattr(self, attr.tag, attr.text)
        self.xp = xp_dict[self.cr]
        self.initiative = self.calculate_modifier(self.dex)
        i = min(self.hp.find(i) for i in [" ", "("])
        if i is not -1:
            self.hp_no_dice = int(self.hp[0:i])
        else:
            self.hp_no_dice = ""

    @staticmethod
    def calculate_modifier(score, sign=False):
        score = int(score)
        mod = int((score-10)/2)
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
        for trait in self.trait_list:
            if trait.name == "Spellcasting":
                spells = trait.text.split("<br>")
                for line in spells:
                    # new_line = line.replace('\u8226', 'X')
                    if '(at will): ' in line or ' slots):' in line or ' slot):' in line:
                        spells = line.split(':')[1].strip().split(',')
                        spells = [spell.strip().replace('*', '') for spell in spells]
                        return_list = return_list + spells
                return return_list
        return None

    def __str__(self):
        return self.name

