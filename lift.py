from func import *

class DelegateBase:
    attrss=dict()
    def __init__(self,attrs=None):
        DelegateBase.attrss[self]=dict()
    def __getattribute__(self, name):
        attrs=DelegateBase.attrss[self]
        return attrs[name]
    def __setattribute__(self, name, value):
        attrs=DelegateBase.attrss[self]
        attrs[name] = value

class Delegate(DelegateBase,int):
    def __getattribute__(self, name):
        #if name=='o': return object.__getattribute__(self)
        s=super(DelegateBase,self)
        return s.__getattribute__(name)

# >>> from lift import *
# >>> d=Delegate()
# >>> d
# 0
# >>> 
# >>> _.o =4
# >>> _.o
# 4
# >>> d=Delegate(3)
# >>> d.__pow__(2)
# 9
# >>> d**2
# 9
# >>> d.__pow__=op.add
# >>> d**2
# 9
# >>> d.a=op.add
# >>> d.a(5)
# <console>:1: TypeError: add expected 2 arguments, got 1
# /home/pi/python/parle/func.py:10: TypeError: add expected 2 arguments, got 1
#     self=Func(<built-in function add>)
#     kwargs={}
#     args=(5,)
# >>> 
# >>> 
# >>> 
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
