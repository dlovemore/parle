from parle.sym import *

class Map:
    def __init__(self):
        self.keys = []
        self.values = []
    def __setitem__(self, key, value):
        if key in self.keys:
            i = self.keys.index(key)
            del self.keys[i]
            del self.values[i]
        self.keys = [key] + self.keys
        self.values = [value] + self.values

class Table(Map):
    def __getitem__(self, key):
        i = self.keys.index(key)
        return self.values[i]

def match(pat, e):
    not implemented
    def unify(pat, e, env):
        pass
        

class Fun(Map):
    def __getitem__(self, key):
        not implemented
        for i, pat in enumerate(self.keys):
            if match(pat, key):
                pass
        return self.values[i]

# >>> from fun import *
# >>> f = Fun()
# >>> 
# >>> f=Table()
# >>> f[3]=4
# >>> f[3]
# 4
# >>> try: f[7]
# ... except ValueError as e: print(e)
# ... 
# 7 is not in list
# >>> f[7]=6
# >>> f[7]
# 6
# >>> f[3]
# 4
# >>> f.keys
# [7, 3]
# >>> f.values
# [6, 4]
# >>> f[3]=8
# >>> f[3]
# 8
# >>> f.keys
# [3, 7]
# >>> f.values
# [8, 6]
# >>> f[1]=2
# >>> f[1]
# 2
# >>> f[3]
# 8
# >>> 
