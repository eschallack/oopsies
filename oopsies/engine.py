import random

class OopsStrategy:
    def apply(self, series):
        raise NotImplementedError()

class NullifyStrategy(OopsStrategy):
    def apply(self, series):
        return [None] * len(series)

class CorruptIntStrategy(OopsStrategy):
    def apply(self, series):
        return ["oops"] * len(series)

class CorruptDateStrategy(OopsStrategy):
    def apply(self, series):
        bad_dates = ["", "2025-99-99", "1500-01-01", "", None]
        return [random.choice(bad_dates) for i in range(len(series))]

class StrategyRegistry:
    def __init__(self):
        self.registry = {}

    def register(self, db_type:str, nullable, strategy):
        self.registry[(db_type.upper(), nullable)] = strategy

    def get(self, db_type:str, nullable, index:int=None):
        return self.registry.get((db_type.upper(), nullable), None)
        
    
registry = StrategyRegistry()
registry.register("INTEGER", False, NullifyStrategy())
registry.register("DOUBLE", True, CorruptIntStrategy())
registry.register("DATE", False, CorruptDateStrategy())

# add more as needed