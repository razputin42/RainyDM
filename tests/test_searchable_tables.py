from dependencies.searchable_tables import SearchableTable
import os
import unittest


class TestSearchableTables(unittest.TestCase):
    def test_load_meta(self):
        options = [
            'Humanoid', 'Droid', 'Humanoid (any)', 'Beast', 'Construct', 'Swarm of Small Beasts', 'humanoid (any)',
            'Force-wielder (any)', 'humanoid', 'Force-wielder', 'humanoid (gamorrean)', 'humanoid (Twi’lek)',
            'Swarm of Tiny Beasts', 'humanoid (any race)', 'Medium swarm of Tiny beasts', 'humanoid (any species)',
            'droid', 'Starship', 'force-wielder']
        expected_types = ['Humanoid', 'Droid', 'Beast', 'Construct', 'Swarm of small beasts', 'Force-wielder',
                          'Swarm of tiny beasts', 'Medium swarm of tiny beasts', 'Starship']
        expected_subtypes = {'Humanoid': ['Any', 'Any race', 'Any species', 'Gamorrean', 'Twi’lek'],
                             'Force-wielder': ['Any']}
        types, subtypes = SearchableTable.extract_subtypes(options)
        self.assertListEqual(expected_types, types)
        self.assertDictEqual(expected_subtypes, subtypes)
