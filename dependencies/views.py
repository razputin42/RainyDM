from PyQt5 import QtGui
from PyQt5.QtWidgets import QTextBrowser, QPushButton
from dependencies.html_format import monster_dict, spell_dict, sw5e_dict, item_dict, general_head, general_foot, not_srd
from dependencies.auxiliaries import GlobalParameters
from string import Template
from RainyCore import System, sNexus
from abc import abstractmethod as abstract


class Viewer(QTextBrowser):
    current_view = None

    def __init__(self, system):
        QTextBrowser.__init__(self)
        self._system = system
        self.horizontalScrollBar().setHidden(True)
        self.aux_format()

    def aux_format(self):
        pass

    def loadResource(self, type, name):
        return QtGui.QPixmap("assets/linear_gradient.png")

    @abstract
    def draw_view(self, entry):
        pass

    def redraw_view(self):
        self.draw_view(self.current_view)

    def set_hidden(self, condition):
        self.setHidden(condition)

    def is_hidden(self):
        return self.isHidden()


class MonsterViewer(Viewer):
    def __init__(self, button_bar, system):
        super().__init__(system)
        self.button_bar = button_bar
        self.button_bar.setContentsMargins(0, 0, 0, 0)

    def draw_view(self, monster):
        if not monster.is_srd_valid():
            # What to display is monster is not SRD valid
            template = Template(not_srd)
            html = template.safe_substitute(
                name=monster.name
            )

        else:
            # this is going to get confusing fast... This is everything before saving throws
            template = Template(monster_dict['first'])
            html = template.safe_substitute(
                name=monster.name,
                size=monster.size,
                type=monster.type,
                alignment=monster.alignment,
                armor_class=monster.ac,
                hit_points=monster.hp,
                speed=monster.speed,
                str=monster.str,
                str_mod=monster.calculate_modifier(monster.str, sign=True),
                dex=monster.dex,
                dex_mod=monster.calculate_modifier(monster.dex, sign=True),
                con=monster.con,
                con_mod=monster.calculate_modifier(monster.con, sign=True),
                int=monster.int,
                int_mod=monster.calculate_modifier(monster.int, sign=True),
                wis=monster.wis,
                wis_mod=monster.calculate_modifier(monster.wis, sign=True),
                cha=monster.cha,
                cha_mod=monster.calculate_modifier(monster.cha, sign=True)
            )
            descriptive = ["save", "resist", "immune", "conditionImmune", "skill", "senses", "languages"]
            name_dict = dict(
                save="Saving Throws",
                resist="Damage Resistance",
                immune="Damage Immunities",
                conditionImmune="Condition Immunities",
                skill="Skills",
                senses="Senses",
                languages="Languages",
                cr="Challenge Rating"
            )
            for desc in descriptive:
                if hasattr(monster, desc) and getattr(monster, desc) is not None:
                    template = Template(monster_dict['desc'])
                    html = html + template.safe_substitute(
                        name=name_dict[desc],
                        desc=getattr(monster, desc))

            if hasattr(monster, "cr"):
                template = Template(monster_dict['cr'])
                html = html + template.safe_substitute(
                    cr=monster.cr,
                    xp=monster.xp
                )
            html = html + monster_dict['gradient']

            # add traits
            for itt, trait in enumerate(monster.trait_list):
                template = Template(monster_dict['action_even'])
                html = html + template.safe_substitute(
                    name=trait.name if hasattr(trait, "name") else "",
                    text=trait.text.replace("\n", "<br/>")
                )

            # second part of the monster
            template = Template(monster_dict['second'])
            html = html + template.safe_substitute(
            )

            # add each action
            for itt, action in enumerate(monster.action_list):
                if itt % 2 == 0:  # even
                    template = Template(monster_dict['action_even'])
                else:
                    template = Template(monster_dict['action_odd'])
                html = html + template.safe_substitute(
                    name=action.name if hasattr(action, "name") else "",
                    text=action.text
                )

            # add each legendary action
            if len(monster.legendary_list) != 0:
                html = html + monster_dict['legendary_header']
                for itt, action in enumerate(monster.legendary_list):
                    if itt % 2 == 0:  # even
                        template = Template(monster_dict['action_even'])
                    else:
                        template = Template(monster_dict['action_odd'])
                    html = html + template.safe_substitute(
                        name=action.name if hasattr(action, "name") else "",
                        text=action.text
                    )

            self.update_button_bar(monster)
        # rest of the monster
        template = Template(monster_dict['rest'])
        html = html + template.safe_substitute()
        self.html = html
        self.setHtml(html)
        self.current_view = monster
        sNexus.viewerSelectChanged.emit(GlobalParameters.MONSTER_VIEWER_INDEX)

    def update_button_bar(self, monster):
        button_bar_layout = self.button_bar.layout()
        for i in reversed(range(button_bar_layout.count())):  # first, clear layout
            button_bar_layout.itemAt(i).widget().setParent(None)
        for action in monster.action_list:  # second, repopulate
            if not hasattr(action, "attack"):
                continue
            button = QPushButton(action.name)
            button.clicked.connect(lambda state, x=action: monster.performAttack(x))
            button_bar_layout.addWidget(button)

    def set_hidden(self, condition):
        self.setHidden(condition)
        self.button_bar.setHidden(condition)


class SpellViewer(Viewer):
    def draw_view(self, spell):
        if hasattr(spell, "srd") and spell.srd == "no":
            template = Template(not_srd)
            html = template.safe_substitute(
                name=spell.name
            )
            html = html + general_foot
        else:
            # if isinstance(spell, Spell35):
            #     html = general_head + spell.full_text + general_foot
            if self._system == System.SW5e:
                template = Template(sw5e_dict['spell'])
                html = template.safe_substitute(
                    name=spell.name,
                    level=self.ordinal(spell.level),
                    time=spell.time,
                    range=spell.range,
                    duration=spell.duration,
                    text=spell.text,
                    classes=', '.join(spell.classes) if hasattr(spell, "classes") else ""
                )
            elif self._system == System.DnD5e:
                template = Template(spell_dict['entire'])
                html = template.safe_substitute(
                    name=spell.name,
                    level=self.ordinal(spell.level),
                    school=spell.school,
                    time=spell.time,
                    range=spell.range,
                    components=spell.components,
                    duration=spell.duration,
                    text=spell.text,
                    classes=', '.join(spell.classes) if hasattr(spell, "classes") else ""
                )
        self.setHtml(html)
        self.current_view = spell
        sNexus.viewerSelectChanged.emit(GlobalParameters.SPELL_VIEWER_INDEX)

    @staticmethod
    def ordinal(n):
        n = int(n)
        if n == 0:
            return "Cantrip"
        return "{}{}-level".format(n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

    def set_hidden(self, condition):
        super().set_hidden(condition)
        if condition is True:
            sNexus.setWidgetStretch.emit(GlobalParameters.MIDDLE_FRAME_POSITION, 0)
        else:
            sNexus.setWidgetStretch.emit(GlobalParameters.MIDDLE_FRAME_POSITION, GlobalParameters.MIDDLE_FRAME_STRETCH)


class ItemViewer(Viewer):
    item_keyname_dict = dict(
        dmg1="Damage",
        ac="AC",
        range="Range",
        weight="Weight",
        value="Value"
    )

    def aux_format(self):
        self.setMaximumWidth(53000)  # i.e. as large as it wants

    def draw_view(self, item):
        if not item.is_srd_valid():
            template = Template(not_srd)
            html = template.safe_substitute(
                name=item.name
            )
        else:
            if self._system.is_DnD5e() or self._system.is_SW5e():  # 5e item
                html = item_dict['header']
                template = Template(item_dict["name"])
                html = html + template.safe_substitute(desc=item.name)
                html = html + item_dict['gradient']

                for desc in ["ac", "dmg1", "range", "weight", "value"]:
                    if desc in self.item_keyname_dict.keys():
                        name = self.item_keyname_dict[desc]
                    else:
                        name = desc.capitalize()

                    if hasattr(item, desc):  # exceptions first, then the general case
                        if desc == "dmg1":
                            if hasattr(item, "dmg2"):  # has two dmg dice (for example with versatile weapons)
                                template = Template(item_dict['dmg_vers'])
                                html = html + template.safe_substitute(
                                    name=name,
                                    dmg1=getattr(item, "dmg1"),
                                    dmg2=getattr(item, "dmg2"),
                                    dmgType=item.damage_type_dict[getattr(item, "dmgType")]
                                    if hasattr(item, "dmgType") else "None"
                                )
                            else:  # has only one damage dice
                                template = Template(item_dict['dmg'])
                                html = html + template.safe_substitute(
                                    name=name,
                                    dmg1=getattr(item, "dmg1"),
                                    dmgType=item.damage_type_dict[getattr(item, "dmgType")]
                                    if hasattr(item, "dmgType") else "None"
                                )
                        else:  # general case
                            template = Template(item_dict['desc'])
                            html = html + template.safe_substitute(
                                name=name,
                                desc=getattr(item, desc)
                            )

                template = Template(item_dict["text"])
                html = html + template.safe_substitute(text=item.text)

            html = html + item_dict['foot']
        self.setHtml(html)
        self.current_view = item
        sNexus.viewerSelectChanged.emit(GlobalParameters.ITEM_VIEWER_INDEX)
