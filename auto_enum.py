from enum import Enum


class AutoEnum(Enum):
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return repr(self.value)
    
    def __eq__(self, other):
        return self.value == other
    
    def __hash__(self):
        return hash(self.value)

