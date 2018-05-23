class Filter:
    def __init__(self):
        self.filter = dict()

    def add_dropdown(self, name, list):
        pass

    def get_widget(self):
        pass

    def evaluate_filter(self, entry):
        cond = True
        for key, arg in self.filter.items():
            if not hasattr(entry, key):
                print("Wrong filter key passed to entry in SearchableTable")
                continue
            attr = getattr(entry, key)
            cond = cond and (attr == arg)
        return cond

    def add_filter(self, key, value):
        pass