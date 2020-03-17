from PyQt5.QtCore import pyqtSignal, QObject


class SignalNexus(QObject):
    attackSignal = pyqtSignal(str, str, name="attackSignal")
    addSpellsSignal = pyqtSignal(list, name="addSpellsSignal")
    encounterDeselectSignal = pyqtSignal(name="encounterDeselctSignal")
    treasureHoardDeselectSignal = pyqtSignal(name="treasureHoardDeselectSignal")
    printSignal = pyqtSignal(str, name="printSignal")

sNexus = SignalNexus()