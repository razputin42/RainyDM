from RainyDM import DMTool
import os
import unittest


class Dummy:
    pass


class TestLoadSave(unittest.TestCase):
    def test_load_meta(self):
        cls = Dummy()
        DMTool.load_meta(self=cls)


