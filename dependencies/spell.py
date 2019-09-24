import copy


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
    required_database_fields = ["name"]
    database_fields = [
        'name', 'level', 'school', 'time', 'range', 'components', 'duration', 'text'
    ]

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
            elif attr.tag == 'classes':
                self.classes = attr.text.split(', ')
            else:
                setattr(self, attr.tag, attr.text)
        self.text = s

    def __str__(self):
        return self.name

    def copy(self):
        return copy.deepcopy(self)

class Spell35(Spell):
    def __init__(self, entry, idx):
        self.entry = entry
        self.index = idx
        for attr in entry:
            if False:
                pass
            else:
                setattr(self, attr.tag, attr.text)

