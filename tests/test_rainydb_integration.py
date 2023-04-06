import unittest

from RainyDB import RainyDatabase, EntryType, System
from RainyCore import MonsterSW5e, Power, ItemSW5e


class TestRainyDBIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db = RainyDatabase(
            system=System.SW5e,
            system_entry_classes=dict({
                EntryType.Monster: MonsterSW5e,
                EntryType.Power: Power,
                EntryType.Item: ItemSW5e
            })
        )

    def test_content(self):
        self.assertNotEqual(0, self.db.length(EntryType.Monster))
        self.assertNotEqual(0, self.db.length(EntryType.Power))
        self.assertNotEqual(0, self.db.length(EntryType.Item))

