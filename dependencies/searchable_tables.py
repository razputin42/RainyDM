from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QFrame, QPushButton, QTableWidget, QHeaderView, QMenu, \
    QInputDialog, QTableWidgetItem, QSizePolicy, QTabWidget
from .filter import Filter
import xml.etree.ElementTree as ElementTree
import re


class MyTableWidget(QTableWidget):
    NAME_COLUMN = 0
    COLUMNS = 2

    def __init__(self, parent):
        QTableWidget.__init__(self)
        self.parent = parent
        self.format()

    def format(self):
        columns = self.COLUMNS
        self.setColumnCount(columns)
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(self.NAME_COLUMN, QHeaderView.Stretch)
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.setColumnHidden(1, True)


class SearchableTable(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self)
        self.filter = Filter(self.search_handle)

        self.parent = parent
        self.list = []
        self.search_box = QLineEdit()
        self.search_box.setMaximumWidth(parent.SEARCH_BOX_WIDTH)
        self.filter_button = QPushButton("Filters")

        self.table_layout = QHBoxLayout()
        self.table = MyTableWidget(parent)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_layout.addWidget(self.table)
        self.table_layout.addWidget(self.filter.get_frame())

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.search_box)
        horizontal_layout.addWidget(self.filter_button)
        list_layout = QVBoxLayout()
        list_layout.addLayout(horizontal_layout)
        list_layout.addLayout(self.table_layout)
        self.setLayout(list_layout)

        self.search_box.textChanged.connect(self.search_handle)
        self.filter_button.clicked.connect(self.filter_handle)
        self.format()

    def format(self):
        pass

    def define_filters(self):
        pass

    def load_list(self, s, resource, Class):
        xml = ElementTree.parse(resource)
        root = xml.getroot()
        for itt, entry in enumerate(root.findall(s)):
            self.list.append(Class(entry, itt))

    def fill_table(self):
        self.table.clear()
        self.table.setRowCount(len(self.list))
        for itt, entry in enumerate(self.list):
            self.table.setItem(itt, 0, QTableWidgetItem(str(entry)))
            self.table.setItem(itt, 1, QTableWidgetItem(str(entry.index)))

    def unique_attr(self, attr):
        result = []
        for entry in self.list:
            entry_attr = getattr(entry, attr)
            if entry_attr not in result:
                result.append(entry_attr)
        return result

    def filter_handle(self):
        self.filter.toggle_hidden()

    def search_handle(self):
        s = self.search_box.text()
        p = re.compile('.*{}.*'.format(s), re.IGNORECASE)
        result = []

        for entry in self.list:
            total_cond = True if p.match(entry.name) else False
            total_cond = total_cond and self.filter.evaluate_filter(entry)
            result.append(total_cond)
        self._toggle_table(result)

    def _toggle_table(self, result):
        for itt, cond in enumerate(result):
            self.table.setRowHidden(itt, not cond)

    def extract_subtypes(self, options):
        subtype_dict = dict()
        type_return = []
        for s in options:
            if "(" in s:
                type = s[:s.find("(")].strip()
                if type not in type_return:
                    type_return.append(type)
                subtype_raw = s[s.find("(") + 1:s.find(")")]
                subtype_list = subtype_raw.split(", ")
                for subtype in subtype_list:
                    if type not in subtype_dict.keys():
                        subtype_dict[type] = [subtype]
                    elif subtype not in subtype_dict[type]:
                        subtype_dict[type].append(subtype)
            else:
                if s not in type_return:
                    type_return.append(s)
        return type_return, subtype_dict

    def find_entry(self, attr, value):
        attr = attr.lower()
        value = value.lower()
        for entry in self.list:
            if hasattr(entry, attr):
                if getattr(entry, attr).lower() == value:
                    return entry


class MonsterTableWidget(SearchableTable):
    NAME_COLUMN = 0
    INDEX_COLUMN = 1
    TYPE_COLUMN = 2
    CR_COLUMN = 3
    COLUMNS = 4

    def format(self):
        columns = self.COLUMNS
        h = self.table.horizontalHeader()
        t = self.table
        t.setColumnCount(columns)
        resize = QHeaderView.ResizeToContents
        stretch = QHeaderView.Stretch
        for column, policy in zip([self.NAME_COLUMN, self.TYPE_COLUMN, self.CR_COLUMN], [stretch, resize, resize]):
            h.setSectionResizeMode(column, policy)
        t.setShowGrid(False)
        t.verticalHeader().hide()
        t.setColumnHidden(self.INDEX_COLUMN, True)
        t.setColumnHidden(self.TYPE_COLUMN, True)

    def fill_table(self):
        self.table.clear()
        self.table.setRowCount(len(self.list))
        for itt, entry in enumerate(self.list):
            self.table.setItem(itt, self.NAME_COLUMN, QTableWidgetItem(str(entry)))
            self.table.setItem(itt, self.INDEX_COLUMN, QTableWidgetItem(str(entry.index)))
            self.table.setItem(itt, self.TYPE_COLUMN, QTableWidgetItem(str(entry.type)))
            self.table.setItem(itt, self.CR_COLUMN, QTableWidgetItem(str(entry.cr)))

    def format(self):
        columns = self.COLUMNS
        h = self.table.horizontalHeader()
        t = self.table
        t.setColumnCount(columns)
        resize = QHeaderView.ResizeToContents
        stretch = QHeaderView.Stretch
        for column, policy in zip([self.NAME_COLUMN, self.TYPE_COLUMN, self.CR_COLUMN], [stretch, resize, resize]):
            h.setSectionResizeMode(column, policy)
        t.setShowGrid(False)
        t.verticalHeader().hide()
        t.setColumnHidden(self.INDEX_COLUMN, True)
        t.setColumnHidden(self.TYPE_COLUMN, True)

    def fill_table(self):
        self.table.clear()
        self.table.setRowCount(len(self.list))
        for itt, entry in enumerate(self.list):
            self.table.setItem(itt, self.NAME_COLUMN, QTableWidgetItem(str(entry)))
            self.table.setItem(itt, self.INDEX_COLUMN, QTableWidgetItem(str(entry.index)))
            self.table.setItem(itt, self.TYPE_COLUMN, QTableWidgetItem(str(entry.type)))
            self.table.setItem(itt, self.CR_COLUMN, QTableWidgetItem(str(entry.cr)))

    def define_filters(self):
        self.filter.add_dropdown("Type", *self.extract_subtypes(self.unique_attr("type")))
        self.filter.add_dropdown("Size", self.unique_attr("size"))
        self.filter.add_dropdown("Source", self.unique_attr("source"))
        self.filter.add_range("CR")
        # self.filter.add_dropdown("Alignment", self.unique_attr("alignment"))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        addAction = menu.addAction("Add to initiative")
        addXAction = menu.addAction("Add X to initiative")
        menu.addSeparator()
        addToolbox = menu.addAction("Add to toolbox")
        add_spellbook = menu.addAction("Add monster's spells to toolbox")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        current_row = self.table.currentRow()
        monster_idx = int(self.table.item(current_row, 1).text())
        monster = self.list[monster_idx]
        if action == addAction:
            self.parent.add_to_encounter(monster, 1)
        elif action == addXAction:
            X, ok = QInputDialog.getInt(self, 'Add Monster', 'How many?')
            if ok:
                self.parent.add_to_encounter(monster, X)
        elif action == addToolbox:
            self.parent.add_to_toolbox(monster)
        elif action == add_spellbook:
            self.parent.extract_and_add_spellbook(monster)


class SpellTableWidget(SearchableTable):
    NAME_COLUMN = 0
    INDEX_COLUMN = 1

    def define_filters(self):
        self.filter.add_dropdown("School", self.unique_attr("school"))
        self.filter.add_dropdown("Level", self.unique_attr("level"))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        add_toolbox = menu.addAction("Add to toolbox")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        current_row = self.table.currentRow()
        idx = int(self.table.item(current_row, 1).text())
        spell = self.list[idx]
        if action == add_toolbox:
            self.parent.add_to_toolbox_spell(spell)


class ItemTableWidget(SearchableTable):
    NAME_COLUMN = 0
    INDEX_COLUMN = 1

    def define_filters(self):
        self.filter.add_dropdown("Type", self.unique_attr("type"))
        self.filter.add_dropdown("Magic", self.unique_attr("magic"), default="1")
