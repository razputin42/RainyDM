from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QInputDialog, QTableWidget, QHeaderView, QVBoxLayout, \
    QHBoxLayout, QLineEdit, QTextBrowser, QMenu, QTabWidget, QFrame, QPushButton
from dependencies.html_format import monster_dict, monster_dict35, spell_dict, item_dict, general_desc
from string import Template
from .monster import Monster35, Monster


class Viewer(QTextBrowser):
    def __init__(self):
        QTextBrowser.__init__(self)
        self.horizontalScrollBar().setHidden(True)
        self.setStyleSheet("border-image: url(assets/viewer_background.jpg);")
        self.setMaximumWidth(530)
        self.setMinimumWidth(530)
        self.aux_format()

    def aux_format(self):
        pass

    def loadResource(self, type, name):
        return QtGui.QPixmap("assets/linear_gradient.png")


class MonsterViewer(Viewer):
    def draw_view(self, monster):
        # this is going to get confusing fast... This is everything before saving throws
        if isinstance(monster, Monster35):
            html = monster_dict35['head'] + monster.full_text + monster_dict35['foot']
        else:
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
                con = monster.con,
                con_mod=monster.calculate_modifier(monster.con, sign=True),
                int=monster.int,
                int_mod=monster.calculate_modifier(monster.int, sign=True),
                wis=monster.wis,
                wis_mod=monster.calculate_modifier(monster.wis, sign=True),
                cha=monster.cha,
                cha_mod=monster.calculate_modifier(monster.cha, sign=True)
            )
            descriptive = ["save", "skill", "senses", "languages"]
            name_dict = dict(
                save="Saving Throws",
                skill="Skills",
                senses="Senses",
                languages="Languages",
                cr="Challenge Rating"
            )
            for desc in descriptive:
                if hasattr(monster, desc):
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
                    name=trait.name,
                    text=trait.text
                )

            # second part of the monster
            template = Template(monster_dict['second'])
            html = html + template.safe_substitute(
            )

            # add each action
            for itt, action in enumerate(monster.action_list):
                if itt % 2 == 0: # even
                    template = Template(monster_dict['action_even'])
                else:
                    template = Template(monster_dict['action_odd'])
                html = html + template.safe_substitute(
                    name=action.name,
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
                        name=action.name,
                        text=action.text
                    )

            # rest of the monster
            template = Template(monster_dict['rest'])
            html = html + template.safe_substitute()

        self.setHtml(html)


class SpellViewer(Viewer):
    def draw_view(self, spell):
        template = Template(spell_dict['entire'])
        html = template.safe_substitute(
            name=spell.name,
            level=self.ordinal(spell.level),
            school=spell.school,
            time=spell.time,
            range=spell.range,
            components=spell.components,
            duration=spell.duration,
            text=spell.text
        )
        self.setHtml(html)

    @staticmethod
    def ordinal(n):
        n = int(n)
        if n == 0:
            return "Cantrip"
        return "{}{}-level".format(n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


class ItemViewer(Viewer):
    def aux_format(self):
        self.setMaximumWidth(53000)  # i.e. as large as it wants

    def draw_view(self, item):
        html = item_dict['header']
        template = Template(item_dict["name"])
        html = html + template.safe_substitute(desc=item.name)
        html = html + item_dict['gradient']

        for desc in ["ac", "weight", "value"]:  # also add dmg1 and dmgType, with a dicionary instead of capitalize...
            if hasattr(item, desc):
                template = Template(general_desc)
                html = html + template.safe_substitute(
                    name=desc.capitalize(),
                    desc=getattr(item, desc)
                )

        template = Template(item_dict["text"])
        html = html + template.safe_substitute(desc=item.text)

        html = html + item_dict['foot']
        self.setHtml(html)
