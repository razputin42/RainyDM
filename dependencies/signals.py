from PyQt5.QtCore import pyqtSignal, QObject


class SignalNexus(QObject):
    attackSignal = pyqtSignal(str, str, name="attackSignal")
    addSpellsSignal = pyqtSignal(list, name="addSpellsSignal")
    encounterDeselectSignal = pyqtSignal(name="encounterDeselctSignal")
    printSignal = pyqtSignal(str, name="printSignal")

sNexus = SignalNexus()