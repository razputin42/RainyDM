from PyQt5 import QtGui
from PyQt5.QtWidgets import QTextBrowser, QPushButton
from dependencies.html_format import monster_dict, spell_dict, sw5e_dict, item_dict, general_head, general_foot, not_srd
from dependencies.auxiliaries import GlobalParameters
from string import Template
from RainyCore import sNexus
from RainyDB import System
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
                name=monster.get_name(),
                size=monster.get_size(),
                type=", ".join(monster.get_type()),
                alignment=monster.get_alignment(),
                armor_class=monster.get_armor_class(),
                hit_points=monster.get_hit_points(),
                speed=monster.get_speed(),
                str=monster.get_strength(),
                str_mod=monster.get_strength_modifier(),
                dex=monster.get_dexterity(),
                dex_mod=monster.get_dexterity_modifier(),
                con=monster.get_constitution(),
                con_mod=monster.get_constitution_modifier(),
                int=monster.get_intelligence(),
                int_mod=monster.get_intelligence_modifier(),
                wis=monster.get_wisdom(),
                wis_mod=monster.get_wisdom_modifier(),
                cha=monster.get_charisma(),
                cha_mod=monster.get_charisma_modifier()
            )
            descriptive_list = [
                ("Saving Throws", monster.get_saving_throws()),
                ("Damage Resistance", monster.get_resistances()),
                ("Damage Immunities", monster.get_immunities()),
                ("Condition Immunities", monster.get_condition_immunities()),
                ("Skills", monster.get_skills()),
                ("Senses", monster.get_senses()),
                ("Languages", monster.get_languages()),
            ]
            for name, value in descriptive_list:
                if value is None:
                    continue
                if isinstance(value, list):
                    value = ", ".join(value)
                template = Template(monster_dict['desc'])
                html = html + template.safe_substitute(
                    name=name,
                    desc=value
                )

            template = Template(monster_dict['cr'])
            html = html + template.safe_substitute(
                cr=monster.get_challenge_rating(),
                xp=monster.get_experience()
            )
            html = html + monster_dict['gradient']

            # add behaviors
            for itt, behavior in enumerate(monster.get_behaviors()):
                template = Template(monster_dict['action_even'])
                html = html + template.safe_substitute(
                    name=behavior.get_name(),
                    text=behavior.get_description().replace("\n", "<br/>")
                )

            # second part of the monster
            template = Template(monster_dict['second'])
            html = html + template.safe_substitute()

            # add each action
            for itt, action in enumerate(monster.get_actions()):
                if itt % 2 == 0:  # even
                    template = Template(monster_dict['action_even'])
                else:
                    template = Template(monster_dict['action_odd'])
                html = html + template.safe_substitute(
                    name=action.get_name(),
                    text=action.get_description()
                )

            # add each legendary action
            if len(list(monster.get_legendary_actions())) != 0:
                html = html + monster_dict['legendary_header']
            for itt, action in enumerate(monster.get_legendary_actions()):
                if itt % 2 == 0:  # even
                    template = Template(monster_dict['action_even'])
                else:
                    template = Template(monster_dict['action_odd'])
                html = html + template.safe_substitute(
                    name=action.get_name(),
                    text=action.get_description()
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
        for action in monster.get_actions():  # second, repopulate
            if not action.is_attack:
                continue
            # button = QPushButton(action.get_name())
            # button.clicked.connect(lambda state, x=action: monster.performAttack(x))
            # button_bar_layout.addWidget(button)

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
            if self._system is System.SW5e:
                template = Template(sw5e_dict['spell'])
                html = template.safe_substitute(
                    name=spell.get_name(),
                    level=self.ordinal(spell.get_level()),
                    time=spell.get_casting_time(),
                    range=spell.get_range(),
                    duration=spell.get_duration(),
                    text=spell.get_description(),
                    classes=', '.join(spell.get_classes())
                )
            elif self._system is System.DnD5e:
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
    def aux_format(self):
        self.setMaximumWidth(53000)  # i.e. as large as it wants

    def draw_view(self, item):
        if not item.is_srd_valid():
            template = Template(not_srd)
            html = template.safe_substitute(
                name=item.name
            )
        else:
            html = item_dict['header']
            template = Template(item_dict["name"])
            html = html + template.safe_substitute(desc=item.get_name())
            html = html + item_dict['gradient']

            template = Template(item_dict["text"])
            html = html + template.safe_substitute(text=item.get_description())

            html = html + item_dict['foot']
        self.setHtml(html)
        self.current_view = item
        sNexus.viewerSelectChanged.emit(GlobalParameters.ITEM_VIEWER_INDEX)
