class Character:
    def __init__(self, charName="", playerName="", init=0, enabled=False):
        self.m_charName = charName
        self.m_playerName = playerName
        self.m_init = init
        self.m_enabled = enabled

    def getCharName(self):
        return self.m_charName

    def getInit(self):
        return self.m_init

    @property
    def isEnabled(self):
        return self.m_enabled
