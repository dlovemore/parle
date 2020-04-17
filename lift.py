from func import *

class DelegateBase:
    def __init__(self,o):
        self.o=o
    def f(self): return super(DelegateBase,self).o

class Delegate(DelegateBase):
    def __init__(self,o):
        super().__init__(o)
    def __getattribute__(self, name):
        #if name=='o': return object.__getattribute__(self)
        s=super(DelegateBase,self)
        # r=s.__getattribute__(s,name)
        return object.__getattribute__(self,'f')()

# >>> from lift import *
# >>> DelegateBase(dict)
# <lift.DelegateBase object at 0xb66d85b0>
# >>> _.o
# <class 'dict'>
# >>> d=Delegate(dict)
# >>> d
# <lift.Delegate object at 0xb66d85b0>
# >>> DelegateBase.f
# <function DelegateBase.f at 0xb65c46a8>
# >>> d.o
# <console>:1: AttributeError: 'super' object has no attribute 'o'
# /home/pi/python/parle/lift.py:15: AttributeError: 'super' object has no attribute 'o'
#     self=<lift.Delegate object at 0xb66d85b0>
#     name=o
#     s=<super: <class 'DelegateBase'>, <Delegate object>>
# /home/pi/python/parle/lift.py:6: AttributeError: 'super' object has no attribute 'o'
#     self=<lift.Delegate object at 0xb66d85b0>
# >>> 
# >>> 
# >>> 
# >>> dir(set())
# ['__and__', '__class__', '__contains__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__iand__', '__init__', '__init_subclass__', '__ior__', '__isub__', '__iter__', '__ixor__', '__le__', '__len__', '__lt__', '__ne__', '__new__', '__or__', '__rand__', '__reduce__', '__reduce_ex__', '__repr__', '__ror__', '__rsub__', '__rxor__', '__setattr__', '__sizeof__', '__str__', '__sub__', '__subclasshook__', '__xor__', 'add', 'clear', 'copy', 'difference', 'difference_update', 'discard', 'intersection', 'intersection_update', 'isdisjoint', 'issubset', 'issuperset', 'pop', 'remove', 'symmetric_difference', 'symmetric_difference_update', 'union', 'update']
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> d=Delegate('fred')
# <console>:1: AttributeError: 'super' object has no attribute 'o'
# /home/pi/python/parle/lift.py:5: AttributeError: 'super' object has no attribute 'o'
#     o=fred
#     self=<lift.Delegate object at 0xb64fe730>
# >>> d.__dict__
# <console>:1: NameError: name 'd' is not defined
# >>> 
# >>> 
# >>> d
# <lift.Delegate object at 0xb6561a10>
# >>> 
# >>> 
