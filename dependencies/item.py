type_dict = {
    "A": "Ammunition",
    "G": "General",
    "HA": "Heavy Armor",
    "LA": "Light Armor",
    "M": "Melee",
    "MA": "Medium Armor",
    "P": "Potions",
    "R": "Ranged",
    "RD": "Rod",
    "RG": "Ring",
    "S": "Shield",
    "SC": "Scroll",
    "ST": "Staff",
    "W": "Wondrous",
    "WD": "Wand",
    "$": "Valuables"
}

magic_dict = {
    "0": "No",
    "1": "Yes"
}


class Item:
    def __init__(self, entry, idx):
        self.entry = entry
        self.index = idx
        s = ""
        for attr in entry:
            if attr.tag == "magic":
                if attr.text is not None:
                    self.magic = magic_dict[attr.text]
                else:
                    self.magic = magic_dict["0"]
            elif attr.tag == "text":
                if attr.text is None:
                    s = s + "<br>"
                else:
                    s = s + attr.text + "<br>"
            elif attr.tag == "type":
                self.type = type_dict[attr.text]
            else:
                setattr(self, attr.tag, attr.text)
        self.text = s

    def __str__(self):
        return self.name


class Item35(Item):
    of_list = ['Scroll', 'Wand']

    def __init__(self, entry, idx):
        self.entry = entry
        self.index = idx
        for attr in entry:
            if attr.tag == 'category' and attr.text in self.of_list:
                self.name = attr.text + ' of ' + self.name
            else:
                setattr(self, attr.tag, attr.text)
