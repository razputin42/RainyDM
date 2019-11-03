from PyQt5.QtCore import pyqtSignal, QObject


class SignalNexus(QObject):
    attackSignal = pyqtSignal(str, str, name="attackSignal")


sNexus = SignalNexus()