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
            else:
                setattr(self, attr.tag, attr.text)
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

    def __str__(self):
        return self.name

