from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QFrame, QPushButton, QTableWidget, QHeaderView, QMenu, \
    QInputDialog, QTableWidgetItem, QSizePolicy
from PyQt5.QtCore import Qt
from .filter import Filter
import xml.etree.ElementTree as ElementTree
import re, os


class MyTableWidget(QTableWidget):
    NAME_COLUMN = 0
    COLUMNS = 2

    def __init__(self, parent):
        QTableWidget.__init__(self)
        self.parent = parent
        self.format()

    def format(self):
        self.setColumnCount(self.COLUMNS)
        # self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(self.NAME_COLUMN, QHeaderView.Stretch)
        self.setShowGrid(False)
        self.verticalHeader().hide()
        # self.setColumnHidden(1, True)


class SearchableTable(QFrame):
    NAME_COLUMN = 0
    INDEX_COLUMN = 1
    HEADERS = ['Name', 'Index']

    def __init__(self, parent):
        self.old_n = None
        self.order = None
        self.COLUMNS = len(self.HEADERS)

        QFrame.__init__(self)
        self.filter = Filter(self.search_handle)

        self.parent = parent
        self.list = []
        self.list_dict = dict()
        self.search_box = QLineEdit()
        self.search_box.setMaximumWidth(parent.SEARCH_BOX_WIDTH)
        self.filter_button = QPushButton("Filters")

        self.table_layout = QHBoxLayout()
        self.table = MyTableWidget(parent)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_columns)
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

    def sort_columns(self, n):
        if self.old_n is n:
            if self.order is Qt.AscendingOrder:
                self.order = Qt.DescendingOrder
            else:
                self.order = Qt.AscendingOrder
        else:
            self.order = Qt.AscendingOrder
        self.table.sortByColumn(n, self.order)
        self.old_n = n

    def define_filters(self):
        pass

    def load_all(self, s, dir, Class):
        self.list = []
        for resource in os.listdir(dir):
            self.load_list(s, dir + resource, Class)
        self.list.sort(key=lambda x: x.name)
        for itt, entry in enumerate(self.list):
            entry.index = itt

    def load_list(self, s, resource, Class):
        xml = ElementTree.parse(resource)
        root = xml.getroot()
        for itt, entry in enumerate(root.findall(s)):
            self.list.append(Class(entry, itt))
        self.list_dict[str(Class)] = self.list

    def fill_table(self):
        self.table.clear()
        self.table.setRowCount(len(self.list))
        for itt, entry in enumerate(self.list):
            self.table.setItem(itt, self.NAME_COLUMN, QTableWidgetItem(str(entry)))
            self.table.setItem(itt, self.INDEX_COLUMN, QTableWidgetItem(str(entry.index)))

    def unique_attr(self, attr):
        result = []
        for entry in self.list:
            if hasattr(entry, attr):
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
            if "(" in s:  # indicates that there is a subtype
                type = s[:s.find("(")].strip()  # find the original type
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

        for key, value in subtype_dict.items():
            value = [option.capitalize() for option in value]
            value = list(set(value))
            value.sort()
            subtype_dict[key] = value

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
    CR_DISPLAY_COLUMN = 3
    CR_COLUMN = 4
    HEADERS = ['Name', 'REFERENCE', 'Type', 'CR', 'FLOAT CR']

    def sort_columns(self, n):
        if n is self.CR_DISPLAY_COLUMN:
            n = self.CR_COLUMN
        super().sort_columns(n)

    def format(self):
        h = self.table.horizontalHeader()
        t = self.table
        t.setColumnCount(self.COLUMNS)
        t.setRowCount(1)
        resize = QHeaderView.ResizeToContents
        stretch = QHeaderView.Stretch
        for column, policy in zip([self.NAME_COLUMN, self.TYPE_COLUMN, self.CR_DISPLAY_COLUMN], [stretch, resize, resize]):
            h.setSectionResizeMode(column, policy)
        t.setShowGrid(False)
        t.setColumnHidden(self.INDEX_COLUMN, True)
        t.setColumnHidden(self.TYPE_COLUMN, True)
        t.setColumnHidden(self.CR_COLUMN, True)

    def fill_table(self):
        self.table.clear()
        self.table.setRowCount(len(self.list))
        for itt, entry in enumerate(self.list):
            self.table.setItem(itt, self.NAME_COLUMN, QTableWidgetItem(str(entry)))
            self.table.setItem(itt, self.INDEX_COLUMN, QTableWidgetItem(str(entry.index)))
            self.table.setItem(itt, self.TYPE_COLUMN, QTableWidgetItem(str(entry.type)))
            if hasattr(entry, "cr"):
                if entry.cr == "00":
                    shown_cr = "-"
                else:
                    shown_cr = str(entry.cr)
                self.table.setItem(itt, self.CR_DISPLAY_COLUMN, QTableWidgetItem(shown_cr))
                cr_item = QTableWidgetItem()
                cr_item.setData(Qt.DisplayRole, eval("float({})".format(entry.cr)))
                self.table.setItem(itt, self.CR_COLUMN, cr_item)
        self.table.setHorizontalHeaderLabels(self.HEADERS)

    def define_filters(self, version):
        if version == "5":
            self.filter.add_dropdown("Type", *self.extract_subtypes(self.unique_attr("type")))
            self.filter.add_dropdown("Size", self.unique_attr("size"))
            self.filter.add_dropdown("Source", self.unique_attr("source"))
            self.filter.add_range("CR")
            # self.filter.add_dropdown("Alignment", self.unique_attr("alignment"))
        elif version == "3.5":
            self.filter.add_dropdown("Type", *self.extract_subtypes(self.unique_attr("type")))
            self.filter.add_dropdown("Size", self.unique_attr("size"))
            # self.filter.add_dropdown("Source", self.unique_attr("source"))
            self.filter.add_range("CR")
        self.search_handle()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        current_row = self.table.currentRow()
        monster_idx = int(self.table.item(current_row, 1).text())
        monster = self.list[monster_idx]

        addAction = menu.addAction("Add to initiative")
        addXAction = menu.addAction("Add X to initiative")
        menu.addSeparator()
        addToolbox = menu.addAction("Add to toolbox")
        if hasattr(monster, "spells"):
            add_spellbook = menu.addAction("Add monster's spells to toolbox")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        if action == addAction:
            self.parent.encounter_table.add_to_encounter(monster, 1)
        elif action == addXAction:
            X, ok = QInputDialog.getInt(self, 'Add Monster', 'How many?')
            if ok and X < 2000:
                self.parent.encounter_table.add_to_encounter(monster, X)
        elif action == addToolbox:
            self.parent.add_to_toolbox(monster)
        elif hasattr(monster, "spells") and action == add_spellbook:
            self.parent.extract_and_add_spellbook(monster)


class SpellTableWidget(SearchableTable):
    NAME_COLUMN = 0
    INDEX_COLUMN = 1
    LEVEL_COLUMN = 2
    HEADERS = ['Name', 'REFERENCE', 'Spell Level']

    def fill_table(self):
        self.table.clear()
        self.table.setRowCount(len(self.list))
        for itt, entry in enumerate(self.list):
            self.table.setItem(itt, self.NAME_COLUMN, QTableWidgetItem(str(entry)))
            self.table.setItem(itt, self.INDEX_COLUMN, QTableWidgetItem(str(entry.index)))
            self.table.setItem(itt, self.LEVEL_COLUMN, QTableWidgetItem(str(entry.level)))
        self.table.setHorizontalHeaderLabels(self.HEADERS)

    def format(self):
        t = self.table
        h = self.table.horizontalHeader()
        t.setColumnCount(self.COLUMNS)
        t.setColumnHidden(self.INDEX_COLUMN, True)
        t.setColumnHidden(self.LEVEL_COLUMN, False)

    def define_filters(self, version):
        if version == "5":
            self.filter.add_dropdown("School", self.unique_attr("school"))
            self.filter.add_dropdown("Level", self.unique_attr("level"))
        elif version == "3.5":
            self.filter.add_dropdown("School", self.unique_attr("school"))
            # self.filter.add_dropdown("Level", self.unique_attr("level"))
            # self.filter.add_dropdown("Range", self.unique_attr("range"))

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

    def format(self):
        t = self.table
        h = self.table.horizontalHeader()
        h.hide()
        t.setColumnHidden(self.INDEX_COLUMN, True)

    def define_filters(self, version):
        if version == "5":
            self.filter.add_dropdown("Type", self.unique_attr("type"))
            self.filter.add_dropdown("Magic", self.unique_attr("magic"), default="Yes")
        elif version == "3.5":
            self.filter.add_dropdown("Category", self.unique_attr("category"))
