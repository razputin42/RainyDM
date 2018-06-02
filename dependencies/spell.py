school_dict = dict(
    A="Abjuration",
    C="Conjuration",
    N="Necromancy",
    EV="Evocation",
    T="Transmutation",
    D="Divinition",
    I="Illusion",
    EN="Enchantment"
)

class Spell:
    def __init__(self, entry, idx):
        self.entry = entry
        self.index = idx
        s = ""
        for attr in entry:
            if attr.tag == "text":
                if attr.text is None:
                    s = s + "<br>"
                else:
                    s = s + attr.text + "<br>"
            elif attr.tag == "school":
                self.school = school_dict[attr.text]
            else:
                setattr(self, attr.tag, attr.text)
        self.text = s

    def __str__(self):
        return self.name


class Spell35(Spell):
    def __init__(self, entry, idx):
        self.entry = entry
        self.index = idx
        for attr in entry:
            if False:
                pass
            else:
                setattr(self, attr.tag, attr.text)

