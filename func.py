import functools
from functools import reduce
from operator import itemgetter
import operator

class Func:
    def __init__(self,f):
        self.f=isinstance(f,Func) and f.f or callable(f) and f
    def __contains__(self, k):
        return k in self.f
    def __call__(self,*args,**kwargs):
        return self.f(*args,**kwargs)
    def __rmatmul__(self,other):
        return rowtype(other)(map(self,other))
    def __matmul__(self,other):
        return isinstance(other, Func) and Func(compose(self.f,other.f)) or NotImplemented
    def __rmul__(self,other):
        return isinstance(other, Func) and Func(compose(other.f,self.f)) or self(other)
    def __mul__(self,other):
        return isinstance(other, Func) and Func(compose(self.f,other.f)) or NotImplemented
    def __rpow__(self,other):
        return self(*other)
    def __pow__(self,other):
        return isinstance(other, Func) and Func(compose(self.f,star(other.f))) or NotImplemented
    def __rtruediv__(self, other):
        return rowtype(other)(x for x in other if self(x))
    def __ror__(self,f):
        return Func(orr(f,self.f))
    def __or__(self,f):
        return Func(orr(self.f,f))
    def __add__(self, other):
        if isinstance(other, Func):
            return FuncRow((self.f,other.f))
        return NotImplemented
    def __repr__(self):
        return f'{type(self).__name__}({self.f!r})'

class FuncRow(Func):
    def __init__(self, fs):
        self.fs=tuple(fs)
    def __call__(self, other,**kwargs):
        return tuple(f(other[i],**kwargs) for i,f in enumerate(self.fs))
    def __rmul__(self, other):
        return tuple(f(other) for f in self.fs)
    def __radd__(self, other):
        if isinstance(other, Func):
            return FuncRow(((other.f,)+self.fs))
        return NotImplemented
    def __add__(self, other):
        if isinstance(other, FuncRow):
            return FuncRow((self.fs+other.fs))
        if isinstance(other, Func):
            return FuncRow((self.fs+(other.f,)))
        return NotImplemented
    def __repr__(self):
        return f'{type(self).__name__}({self.fs!r})'

class Attr:
    def __init__(self, f):
        self.f=f
    def __call__(self, attr):
        return self.f(attr)
    def __getattr__(self, attr):
        return self.f(attr)
    def __repr__(self):
        return f'{type(self).__name__}({self.f})'

class GetItem:
    def __init__(self,f):
        self.f=f
    def __call__(self, k):
        return self.f(k)
    def __getitem__(self, k):
        return self.f(k)

@Func
def I(x): return x

@Func
def const(x):
    @Func
    def const(y):
        nonlocal x
        return x
    return const

@Attr
class Unique:
    def __init__(self, name=None):
        if name: self.name=name
    def __repr__(self):
        return self.name if hasattr(self, 'name') else super().__repr__()

@Func
def partial(f,*args,**kwargs):
    while isinstance(f,Func): f=f.f
    return F(functools.partial(f,*args,**kwargs))

def getprop(name,object): return getattr(object,name)

@Attr
def prop(name): return partial(getprop,name)

q=Attr(str)

def aslist(f):
    def tolist(f,*args):
        return list(f(*args))
    return partial(tolist,f)

def compose(f,g):
    def compose(*args,**kwargs):
        nonlocal f,g
        return g(f(*args,**kwargs))
    return compose

def apply(f, l,**kwargs):
    return f(*l, **kwargs)

def star(f):
    def star(args,**kwargs):
        nonlocal f
        return f(*args,**kwargs)
    return star

def orr(f,g):
    def orr(*args,**kwargs):
        nonlocal f,g
        try:
            return f(*args,**kwargs)
        except Exception:
            pass
        return g(*args,**kwargs)
    return orr


class RightOp(Func):
    def __rmatmul__(self,x):
        return self.f(x)

class LeftOp(Func):
    def __matmul__(self,x):
        return self.f(x)

e=Unique.e

def span(a,b=None,step=1):
    if isinstance(a,slice): a,b,step=a
    if b is None: a,b=1,a
    return range(1,a+1,step) if b is None else range(a,b+1,step)

def redparts(f,xs):
    f=Binop(f)
    y=f.e
    for x in xs:
        y=Binop(f)(x,y)
        yield y

class Binop(Func):
    def __init__(self, f):
        def binop(x,y):
            nonlocal f
            if y is e:
                return x
            if x is e:
                return y
            return f(x,y)
        self.f=f.f if isinstance(f, Binop) else binop
        self.e=e
    def __rmatmul__(self,a):
        def aop(z):
            nonlocal a
            return self.f(a,z)
        return LeftOp(aop)
    def __matmul__(self,z):
        def opz(a):
            nonlocal z
            return self.f(a,z)
        return RightOp(opz)

class RorFunc(Func):
    def __ror__(self, other):
        return self(other)

F=Func(Func)
K=const
I=F(I)

def callmethod(name,object,*args,**kwargs): return getattr(object,name)(*args,**kwargs)

@Attr
def method(name): return partial(callmethod,name)

@Attr
def meth(name):
    @Func
    def callmeth(*args,**kwargs):
        @Func
        def callmeth(object):
            nonlocal name,args, kwargs
            return callmethod(name,object,*args,**kwargs)
        return callmeth
    return callmeth

def getprop(name,object): return getattr(object,name)

@Attr
def prop(name): return partial(getprop,name)

def unstar(f):
    def unstar(f,*l):
        return f(l)
    return partial(unstar,f)

l=unstar(list)
lmap=aslist(map)
q=Attr(str)

trystr=F(list)*(''.join|I)

def rowtype(o): return (isinstance(o, list) or isinstance(o, tuple) or isinstance(o, FuncRow)) and type(o) or isinstance(o, str) and trystr or list

def aslist(f):
    def tolist(f,*args):
        return list(f(*args))
    return partial(tolist,f)


p=RorFunc(print)

op=Attr(partial(getattr,operator)*F)
li=op.itemgetter

add=Binop(operator.add)
sub=Binop(operator.sub)
pow=Binop(operator.pow)
divide=Binop(operator.truediv)
div=Binop(operator.floordiv)
mul=Binop(operator.mul)

class Lookup(dict,Func):
    def __init__(self,d=()):
        dict.__init__(self,d)
        self.f=self.get
    def __ror__(self,f):
        if isinstance(f, dict):
            d=type(self)(self)
            d.update(f)
            return d
        return Func.__or__(f,self)
    def __or__(self,f):
        if isinstance(f, dict):
            d=type(self)(f)
            d.update(self)
            return d
        return Func.__or__(self,f)
    def get(self,k):
        return super().__getitem__(k)
    def __getitem__(self,kvs):
        if isinstance(kvs, slice): kvs=(kvs,)
        if isinstance(kvs, tuple):
            return self|type(self)(zip((kv.start for kv in kvs), (kv.stop for kv in kvs)))
        return self[k]
    def __repr__(self):
        return f'{type(self)}[{super().__repr__()[1:-1]}]'

Dict=Lookup()

def windows(n,xs):
    l=[]
    for i,x in enumerate(xs):
        l.append(x)
        if i>=n-1:
            yield tuple(l)
            l.pop(0)

def failas(f,failresult=None,exc=None):
    def failsafe2(f,failresult,*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except:
            return failresult
    def failsafe3(f,failresult,exc,*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except exc:
            return failresult
    return partial(failsafe3,f,failresult,exc) if exc else partial(failsafe2,f,failresult)

@aslist
def inks(k,l):
    for i in range(0,len(l),k):
        yield tuple(l[i:i+k])

pairs=partial(windows,2)
twos=partial(inks,2)
threes=partial(inks,3)

@aslist
def withoutrepeats(xs):
    y=Unique()
    for x in xs:
        if x!=y:
            yield x
        y=x

def splitat(poss, xs):
    return [xs[x:y] for x,y in pairs(poss+[len(xs)])]

def positions(bs):
    return [i for i,b in enumerate(bs) if b]

def perm(*ks):
    assert sorted(ks)==list(range(len(ks)))
    permuter=li(*ks)
    nks=len(ks)
    def perm(l):
        nonlocal nks,permuter
        return type(l)(permuter(l))+l[nks:]
    return perm

def select(*ks):
    pass



def permargs(*ks):
    def permargs(f):
        nonlocal ks
        return compose(unstar(perm(*ks)),star(f))
    return permargs

def fggf(fg):
    def gf(*args1,**kwargs1):
        def f(*args,**kwargs):
            nonlocal args1,kwargs1,fg
            return fg(*args,**kwargs)(*args1,**kwargs1)
        return f
    return gf

swap=unstar(perm(1,0))
swapargs=permargs(1,0)

# >>> from auto import *
# >>> from func import *
# >>> 
# >>> 
# >>> 
# >>> 
# >>> method.join
# Func(functools.partial(<function callmethod at 0xb6452228>, 'join'))
# >>> method.join(',','abc')
# 'a,b,c'
# >>> meth.startswith('a')
# Func(<function meth.<locals>.callmeth.<locals>.callmeth at 0xb6452db0>)
# >>> _('a'),_('b')
# (True, False)
# >>> 
# >>> 
# >>> 
# >>> ap=Attr(print)
# >>> ap
# Attr(<built-in function print>)
# >>> ap.abc
# abc
# >>> pairs('abcdefg')
# <generator object windows at 0xb64d6f30>
# >>> list(_)
# [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'f'), ('f', 'g')]
# >>> 
# >>> l(1,2,3)
# [1, 2, 3]
# >>> 
# >>> F(list)
# Func(<class 'list'>)
# >>> _([1,2,3])
# [1, 2, 3]
# >>> 
# >>> unstar(li(2,1,3))(4,5,6,7)
# (6, 5, 7)
# >>> swap(0,1)
# (1, 0)
# >>> 
# >>> (2,3)**F(swap)
# (3, 2)
# >>> (2,3)**F(op.pow)
# 8
# >>> ((2,3)**F(swap))**F(op.pow)
# 9
# >>> (2,3)**(F(swap)**F(op.pow))
# 9
# >>> (2,3)**F(swap)**F(op.pow)
# 9
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> swap(1,2,3)
# (2, 1, 3)
# >>> 
# >>> swap(2,3)
# (3, 2)
# >>> isinstance(*swap(int, 3))
# True
# >>> 
# >>> star(isinstance)(swap(int, 3))
# True
# >>> partial(compose(swap,star(isinstance)),int)
# Func(functools.partial(<function compose.<locals>.compose at 0xb6452e40>, <class 'int'>))
# >>> _(9),_(True),_('aa'),_((1,2))
# (True, True, False, False)
# >>> 
# >>> 
# >>> 
# >>> partial(compose(swap,partial(apply,isinstance)),int)
# Func(functools.partial(<function compose.<locals>.compose at 0xb67227c8>, <class 'int'>))
# >>> _('a'),_(3)
# (False, True)
# >>> 
# >>> 
# >>> 
# >>> swap(1,2,3,4)
# (2, 1, 3, 4)
# >>> perm(1,0)([1,2,3,4])
# [2, 1, 3, 4]
# >>> perm(1,0)([1,2,3,4])
# [2, 1, 3, 4]
# >>> compose(unstar(perm(1,0)),star(l))(1,2,3,4)
# [2, 1, 3, 4]
# >>> 
# >>> 
# >>> 
# >>> permargs(2,0,1)(l)(1,2,3,4)
# [3, 1, 2, 4]
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> swapargs(l)(1,2,3)
# [2, 1, 3]
# >>> Dict[3:4](3)
# 4
# >>> Dict[3:4,5:6]
# <class 'func.Lookup'>[3: 4, 5: 6]
# >>> _(5)
# 6
# >>> Dict[3:4,5:6][7:8]
# <class 'func.Lookup'>[7: 8, 3: 4, 5: 6]
# >>> Dict[3:4,5:6][7:8][3:-3]
# <class 'func.Lookup'>[3: 4, 7: 8, 5: 6]
# >>> p(_(3))
# 4
# >>> {3:-3}|Dict[3:4,5:6][7:8]
# <class 'func.Lookup'>[7: 8, 3: -3, 5: 6]
# >>> p(_(3))
# -3
# >>> {1:2}|{3:4}
# <console>:1: TypeError: unsupported operand type(s) for |: 'dict' and 'dict'
# >>> 
# >>> rowtype([])
# <class 'list'>
# >>> rowtype(())
# <class 'tuple'>
# >>> rowtype(2)
# <class 'list'>
# >>> rowtype('abc')
# Func(<function compose.<locals>.compose at 0xb6452540>)
# >>> rowtype('abc')('def')
# 'def'
# >>> 
# >>> f=Dict|{1:2, 3:4}|K(7)
# >>> [f(x) for x in range(1,6)]
# [2, 7, 4, 7, 7]
# >>> span(5)@f
# [2, 7, 4, 7, 7]
# >>> 
# >>> meth.join(map(str,range(10)))(', ')
# '0, 1, 2, 3, 4, 5, 6, 7, 8, 9'
# >>> 
# >>> fggf(meth.join)(',')(map(str,[1,2,3]))
# '1,2,3'
# >>> 
# >>> 
# >>> 
# >>> aslist(map)(op.neg,[1,2,3])
# [-1, -2, -3]
# >>> op.neg
# Func(<built-in function neg>)
# >>> 
# >>> [1,2,3]@op.neg
# [-1, -2, -3]
# >>> 
# >>> callable(F)
# True
# >>> F(list)@F(map)
# Func(<function compose.<locals>.compose at 0xb6452db0>)
# >>> F(list)
# Func(<class 'list'>)
# >>> type(_)
# <class 'func.Func'>
# >>> (I|l)(1,2,3)
# [1, 2, 3]
# >>> Dict['a':'b']|I
# Func(<function orr.<locals>.orr at 0xb6452db0>)
# >>> 
# >>> p(_('c'),_('a'))
# c b
# >>> 1|p
# 1
# >>> 
# >>> span(3)*F(sum)
# 6
# >>> 3|I
# Func(<function orr.<locals>.orr at 0xb6452db0>)
# >>> (''.join|I)(['a','b','d'])
# 'abd'
# >>> (''.join|I)(['a','b','d',1])
# ['a', 'b', 'd', 1]
# >>> list
# <class 'list'>
# >>> list('bcd')
# ['b', 'c', 'd']
# >>> 
# >>> (list*(''.join|I))(['a','b','d'])
# ['a', 'b', 'd']
# >>> trystr('abc')
# 'abc'
# >>> 
# >>> 'abc123'/method.isdigit
# '123'
# >>> ['1',2]/(method.isdigit|K(False))
# ['1']
# >>> 
# >>> partial(l,0)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb6452468>, <class 'list'>, 0))
# >>> partial(partial(partial(l,0),1),2)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb6452468>, <class 'list'>, 0, 1, 2))
# >>> partial(partial(partial(partial(l,0),1),2),3)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb6452468>, <class 'list'>, 0, 1, 2, 3))
# >>> dir(_)|p
# ['__add__', '__call__', '__class__', '__contains__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__matmul__', '__module__', '__mul__', '__ne__', '__new__', '__or__', '__pow__', '__reduce__', '__reduce_ex__', '__repr__', '__rmatmul__', '__rmul__', '__ror__', '__rpow__', '__rtruediv__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'f']
# >>> _.f,args,_.func
# <console>:1: NameError: name 'args' is not defined
# >>> 
# >>> 
# >>> 
# >>> 
# >>> span(10)**l@l
# [[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]]
# >>> 
# >>> len(span(10))
# 10
# >>> 
# >>> span(10)[0]
# 1
# >>> 
# >>> isinstance(range(10),collections.Sequence)
# True
# >>> 'abcd'@method.isdigit
# [False, False, False, False]
# >>> 
# >>> 
# >>> type(partial(I))
# <class 'func.Func'>
# >>> type(functools.partial(I))
# <class 'functools.partial'>
# >>> I
# Func(<function I at 0xb64e4588>)
# >>> _(3)
# 3
# >>> K
# Func(<function const at 0xb64e4db0>)
# >>> 
# >>> K(9)
# Func(<function const.<locals>.const at 0xb6465078>)
# >>> _(9)
# 9
# >>> 
# >>> 
# >>> I+K(9)
# FuncRow((<function I at 0xb64e4588>, <function const.<locals>.const at 0xb6465078>))
# >>> 3*_
# (3, 9)
# >>> meth.add
# Func(<function meth.<locals>.callmeth at 0xb64e4198>)
# >>> 
