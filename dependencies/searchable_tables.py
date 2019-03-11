from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QFrame, QPushButton, QTableWidget, QHeaderView, QMenu, \
    QInputDialog, QTableWidgetItem, QSizePolicy, QMessageBox, QSpacerItem
from PyQt5.QtCore import Qt
from .filter import Filter
import xml.etree.ElementTree as ElementTree
from lxml import etree as ET
import re, os
from dependencies.db_editor import DBEditor
import time


class MyTableWidget(QTableWidget):
    NAME_COLUMN = 0
    INDEX_COLUMN = 1
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
    HEADERS = ['Name', 'REFERENCE']
    EDITABLE = False
    DATABASE_ENTRY_FIELD = 'entry'

    def __init__(self, parent, viewer):
        self.old_n = None
        self.order = None
        self.COLUMNS = len(self.HEADERS)
        self.viewer = viewer

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

        self.button_bar_layout = QHBoxLayout()

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.search_box)
        horizontal_layout.addWidget(self.filter_button)
        list_layout = QVBoxLayout()
        list_layout.addLayout(horizontal_layout)
        list_layout.addLayout(self.table_layout)
        list_layout.addLayout(self.button_bar_layout)
        self.setLayout(list_layout)

        self.search_box.textChanged.connect(self.search_handle)
        self.filter_button.clicked.connect(self.filter_handle)
        self.setup_button_bar()
        self.format()

    def setup_button_bar(self):
        pass

    def format(self):
        pass

    def sort_columns(self, n, order=None):
        if order is not None:
            self.order = order
        elif self.old_n is n:
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
        self.dir = dir
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
            self.update_entry(itt, entry)

        self.table.setHorizontalHeaderLabels(self.HEADERS)

    def update_entry(self, row, entry):
        self.table.setItem(row, self.NAME_COLUMN, QTableWidgetItem(str(entry.name)))
        self.table.setItem(row, self.INDEX_COLUMN, QTableWidgetItem(str(entry.index)))

    def unique_attr(self, attr):
        result = []
        for entry in self.list:
            if hasattr(entry, attr):
                entry_attr = getattr(entry, attr)
                if type(entry_attr) is not list:
                    entry_attr = [entry_attr]
                for _entry_attr in entry_attr:
                    if _entry_attr not in result:
                        result.append(_entry_attr)
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
            idx = int(self.table.item(itt, self.table.INDEX_COLUMN).text())
            self.table.setRowHidden(itt, not result[idx])

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

    # find entry in the instantiated list of whatever is in the table
    def find_entry(self, attr, value):
        attr = attr.lower()
        value = value.lower()
        for entry in self.list:
            if hasattr(entry, attr):
                if getattr(entry, attr).lower() == value:
                    return entry

    def edit_entry(self, entry):
        self.db_editor = DBEditor(self, entry)
        self.db_editor.show()  # the DBEditor calls the copy_entry and save_entry functions defined below

    def copy_entry(self, entry):
        if self.find_entry('name', entry.name) is not None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Entry with name {} already exists'.format(entry.name))
            msg.setWindowTitle("Duplicate Entry")
            msg.exec_()
            return False
        self.list.append(entry)
        entry.index = self.list.index(entry)
        self.table.setRowCount(len(self.list))
        self.update_entry(len(self.list) - 1, entry)
        self.sort_columns(self.NAME_COLUMN, order=Qt.AscendingOrder)

    # find and return the SubElement handle for the first entry with the attribute equal to the value
    def find_db_entry(self, value, root, attr='name'):
        for db_entry in root.findall(self.DATABASE_ENTRY_FIELD):
            for _attr in db_entry:
                if _attr.tag == attr and _attr.text == value:
                    return db_entry

    def save_entry(self, entry, old_name=None):
        flat_fields = []  # list of database fields for the specific entry
        for field in entry.database_fields:
            if type(field) is str:
                flat_fields.append(field)
            else:
                for _field in field:
                    flat_fields.append(_field)
        path = os.path.join(self.dir, 'custom.xml')
        if not os.path.exists(path):
            with open(path, 'w') as f:  # create the file
                pass
            root = ET.Element('compendium')
            root.set('version', '5')
        else:
            parser = ET.XMLParser(remove_blank_text=True)
            root = ET.parse(path, parser).getroot()

        if old_name != None:  # update old entry
            db_entry = self.find_db_entry(value=old_name, root=root, attr='name')
        else:  # new entry
            db_entry = ET.SubElement(root, self.DATABASE_ENTRY_FIELD)

        # for each field
        for field in flat_fields:
            if hasattr(entry, field):
                db_field = db_entry.find(field)
                if db_field is None:
                    db_field = ET.SubElement(db_entry, field)

                db_field.text = str(getattr(entry, field))

        # a few custom fields with content pre-defined
        fields = ['source', 'custom']
        values = ['Custom', None]
        for field, value in zip(fields, values):
            db_field = db_entry.find(field)
            if db_field is None:
                db_field = ET.SubElement(db_entry, field)
            db_field.text = value

        # save lists
        listnames = ['trait_list', 'action_list', 'legendary_list']
        fieldnames = ['trait', 'action', 'legendary']
        subfields_list = [
            ['name', 'text', 'attack'],
            ['name', 'text', 'attack'],
            ['name', 'text', 'attack']
        ]
        for listname, fieldname, subfields in zip(listnames, fieldnames, subfields_list):
            if hasattr(entry, listname):
                for field in getattr(entry, listname):
                    db_field = ET.SubElement(db_entry, fieldname)
                    for subfield in subfields:
                        if hasattr(field, subfield):
                            pieces = getattr(field, subfield).split('<br>')
                            db_subfield = ET.SubElement(db_field, subfield)
                            db_subfield.text = getattr(field, subfield)

        # save actions
        # fields = ['name', 'text', 'attack']
        # if hasattr(entry, 'action_list'):
        #     for action in entry.action_list:
        #         db_action = ET.SubElement(db_entry, 'action')
        #         for field in fields:
        #             if hasattr(action, field):
        #                 # if '<br>' in getattr(trait, field):  # html format break line
        #                 pieces = getattr(action, field).split('<br>')
        #                 for piece in pieces:
        #                     if piece == '':
        #                         continue
        #                     db_field = ET.SubElement(db_trait, field)
        #                     db_field.text = piece

        mydata = ET.tostring(root, encoding="unicode", pretty_print=True)
        myfile = open(path, "w")
        myfile.write(mydata)

    def edit_copy_of_entry(self, entry):
        new_entry = entry.copy()
        new_entry.source = 'custom'
        new_entry.custom = True
        self.db_editor = DBEditor(self, new_entry, copy=True)
        self.db_editor.show()


class MonsterTableWidget(SearchableTable):
    NAME_COLUMN = 0
    INDEX_COLUMN = 1
    TYPE_COLUMN = 2
    CR_DISPLAY_COLUMN = 3
    CR_COLUMN = 4
    HEADERS = ['Name', 'REFERENCE', 'Type', 'CR', 'FLOAT CR']
    DATABASE_ENTRY_FIELD = 'monster'
    EDITABLE = True

    def sort_columns(self, n, order=None):
        if n is self.CR_DISPLAY_COLUMN:
            n = self.CR_COLUMN
        super().sort_columns(n, order=order)

    def setup_button_bar(self):
        #  find current selected monster
        current_row = self.table.currentRow()

        add_enc_button = QPushButton("Add to initiative")
        add_enc_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        add_enc_button.clicked.connect(lambda state, x=1: self.add_monster_to_encounter(x))
        add_x_enc_button = QPushButton("Add more to initiative")
        add_x_enc_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        add_x_enc_button.clicked.connect(self.add_monster_to_encounter)
        add_tool_button = QPushButton("Add to toolkit")
        add_tool_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        hspacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.button_bar_layout.addWidget(add_enc_button)
        self.button_bar_layout.addWidget(add_x_enc_button)
        self.button_bar_layout.addWidget(add_tool_button)
        self.button_bar_layout.addItem(hspacer)

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
        self.sort_columns(self.NAME_COLUMN)

    def update_entry(self, row, entry):
        self.table.setItem(row, self.NAME_COLUMN, QTableWidgetItem(str(entry.name)))
        self.table.setItem(row, self.INDEX_COLUMN, QTableWidgetItem(str(entry.index)))
        self.table.setItem(row, self.TYPE_COLUMN, QTableWidgetItem(str(entry.type)))
        if hasattr(entry, "cr"):
            if entry.cr == "00":
                shown_cr = "-"
            else:
                shown_cr = str(entry.cr)
            self.table.setItem(row, self.CR_DISPLAY_COLUMN, QTableWidgetItem(shown_cr))
            cr_item = QTableWidgetItem()
            cr_item.setData(Qt.DisplayRole, eval("float({})".format(entry.cr)))
            self.table.setItem(row, self.CR_COLUMN, cr_item)

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

    def add_monster_to_encounter(self, number=False):

        current_row = self.table.currentRow()
        if current_row == -1:
            return False
        monster_idx = int(self.table.item(current_row, 1).text())
        monster = self.list[monster_idx]
        if number is False:
            number, ok = QInputDialog.getInt(self, 'Add Monster', 'How many?')
            if not (ok and number < 2000):
                return False
        self.parent.encounter_table.add_to_encounter(monster, number)

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

        edit_entry = None
        edit_copy_entry = None
        if self.EDITABLE:
            menu.addSeparator()
            if hasattr(monster, 'custom'):
                edit_entry = menu.addAction("Edit entry")
            edit_copy_entry = menu.addAction('Edit copy of entry')

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
        elif hasattr(monster, "spells") and action is add_spellbook:
            self.parent.extract_and_add_spellbook(monster)
        elif self.EDITABLE and action is edit_entry:
            self.edit_entry(monster)
        elif self.EDITABLE and action is edit_copy_entry:
            self.edit_copy_of_entry(monster)


class SpellTableWidget(SearchableTable):
    NAME_COLUMN = 0
    INDEX_COLUMN = 1
    LEVEL_COLUMN = 2
    HEADERS = ['Name', 'REFERENCE', 'Spell Level']
    DATABASE_ENTRY_FIELD = 'spell'
    EDITABLE = True

    def update_entry(self, row, entry):
        self.table.setItem(row, self.NAME_COLUMN, QTableWidgetItem(str(entry.name)))
        self.table.setItem(row, self.INDEX_COLUMN, QTableWidgetItem(str(entry.index)))
        self.table.setItem(row, self.LEVEL_COLUMN, QTableWidgetItem(str(entry.level)))

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
            self.filter.add_dropdown('Classes', *self.extract_subtypes(self.unique_attr('classes')))
        elif version == "3.5":
            self.filter.add_dropdown("School", self.unique_attr("school"))
            # self.filter.add_dropdown("Level", self.unique_attr("level"))
            # self.filter.add_dropdown("Range", self.unique_attr("range"))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        add_toolbox = menu.addAction("Add to toolbox")

        current_row = self.table.currentRow()
        idx = int(self.table.item(current_row, 1).text())
        spell = self.list[idx]

        menu.addSeparator()
        if self.EDITABLE and hasattr(spell, 'custom'):
            edit_entry = menu.addAction("Edit entry")
        else:
            edit_entry = None
        edit_copy_entry = menu.addAction('Edit copy of entry')

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return

        if action == add_toolbox:
            self.parent.add_to_toolbox_spell(spell)
        elif self.EDITABLE and action is edit_entry:
            self.edit_entry(spell)
        elif self.EDITABLE and action is edit_copy_entry:
            self.edit_copy_of_entry(spell)


class ItemTableWidget(SearchableTable):
    NAME_COLUMN = 0
    INDEX_COLUMN = 1
    DATABASE_ENTRY_FIELD = 'item'
    EDITABLE = True

    def format(self):
        t = self.table
        h = self.table.horizontalHeader()
        h.hide()
        t.setColumnHidden(self.INDEX_COLUMN, True)

    def define_filters(self, version):
        if version == "5":
            self.filter.add_dropdown("Type", self.unique_attr("type"))
            self.filter.add_dropdown("Magic", self.unique_attr("magic"), default="Any")
        elif version == "3.5":
            self.filter.add_dropdown("Category", self.unique_attr("category"))

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        current_row = self.table.currentRow()
        idx = int(self.table.item(current_row, 1).text())
        item = self.list[idx]

        if self.EDITABLE and hasattr(item, 'custom'):
            edit_entry = menu.addAction("Edit entry")
        else:
            edit_entry = None
        edit_copy_entry = menu.addAction('Edit copy of entry')

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return

        if self.EDITABLE and action is edit_entry:
            self.edit_entry(item)
        elif self.EDITABLE and action is edit_copy_entry:
            self.edit_copy_of_entry(item)
