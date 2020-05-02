import functools
import operator

class Func:
    def __init__(self,f):
        self.f=fun(f)
    def __xcontains__(self, k):
        return k in self.f
    def __call__(self,*args,**kwargs):
        return self.f(*args,**kwargs)
    def __rmatmul__(self,left):
        return dmap(self,left)
    def __matmul__(self,right):
        return Fun(right) and compose(self,partial(dmap,right)) or NotImplemented
    def __rmul__(self,left):
        return Fun(left) and compose(left,self) or self(left)
    def __mul__(self,right):
        return Fun(right) and compose(self,right) or NotImplemented
    def __rpow__(self,left):
        return Fun(left) and compose(left, star(self)) or self(*left)
    def __pow__(self,right):
        return Fun(right) and compose(self,star(right)) or NotImplemented
    def __rtruediv__(self, other):
        return rowtype(other)(x for x in other if self(x))
    def __rand__(self,l):
        return Fun(l) and then(l,self) or self(l)
    def __ror__(self,l):
        return Fun(l) and orr(l,self) or NotImplemented
    def __or__(self,r):
        return Fun(r) and orr(self,r) or NotImplemented
    def __add__(self, other):
        if isinstance(other, Func):
            return FuncRow((self.f,other.f))
        return NotImplemented
    def __repr__(self):
        return f'{type(self).__name__}({self.f})'

def fun(f):
    if isinstance(f,Func):
        while isinstance(f,Func):
            f=f.f
        return f
    else:
        return callable(f) and f

def Fun(f): return fun(f) and Func(f)

class FuncRow(Func):
    def __init__(self, fs):
        self.fs=tuple(fs)
        self.f=self.__call__
    def __call__(self, other,**kwargs):
        return tuple(f(other,**kwargs) for f in self.fs)
    def __rmul__(self, left):
        return tuple(f(left) for f in self.fs)
    def __radd__(self, left):
        if isinstance(left, Func):
            return FuncRow(((left.f,)+self.fs))
        return NotImplemented
    def __add__(self, other):
        if isinstance(other, FuncRow):
            return FuncRow((self.fs+other.fs))
        if isinstance(other, Func):
            return FuncRow((self.fs+(other.f,)))
        return NotImplemented
    def __repr__(self):
        return f'{type(self).__name__}({self.fs!r})'

def dmap(f,l):
    f=fun(f)
    return rowtype(l)(map(f,l))

def pmap(f,l):
    f=fun(f)
    return FuncRow([partial(f,x) for x in l])

class DataRow(tuple):
    def __mul__(self,right):
        return isinstance(right,Func) and NotImplemented or self*Func(right)
    def __pow__(self,right):
        return isinstance(right,Func) and NotImplemented or self**Func(right)
    def __add__(self,right):
        return isinstance(right,Func) and NotImplemented or self+Func(right)
    def __truediv(self,right):
        return isinstance(right,Func) and NotImplemented or self/Func(right)

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

def getitem(k):
    return meth.__getitem__(k)

@Func
def I(x): return x

@Func
def const(x):
    @Func
    def const(*y,**kwargs):
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
    f=fun(f)
    return F(functools.partial(f,*args,**kwargs))

@Func
def compose(f,g):
    while isinstance(f,Func): f=f.f
    while isinstance(g,Func): g=g.f
    @Func
    def compose(*args,**kwargs):
        nonlocal f,g
        return g(f(*args,**kwargs))
    return compose

reduce=Func(functools.reduce)

def getprop(name,object): return getattr(object,name)

@Attr
def prop(name): return partial(getprop,name)

def aslist(f):
    def tolist(f,*args):
        return list(f(*args))
    return partial(tolist,f)

@Func
def apply(f, l,**kwargs):
    return f(*l, **kwargs)

@Func
def star(f):
    f=fun(f)
    @Func
    def star(args,**kwargs):
        nonlocal f
        return f(*args,**kwargs)
    return star

@Func
def orr(f,g):
    f,g=fun(f),fun(g)
    @Func
    def orr(*args,**kwargs):
        nonlocal f,g
        try:
            return f(*args,**kwargs)
        except Exception:
            pass
        return g(*args,**kwargs)
    return orr


class LeftOp(Func):
    def __mul__(self,x):
        return self(x)
    def __matmul__(self,x):
        return dmap(self,x)

class RightOp(Func):
    def __rmatmul__(self,x):
        return self(x)

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
    def __rmul__(self,a):
       return Fun(a) and NotImplemented or LeftOp(partial(self,a))
    def __mul__(self,z):
       return Fun(z) and NotImplemented or partial(swapargs(self.f),z)
    def __rmatmul__(self,a):
        return Fun(a) and NotImplemented or LeftOp(pmap(self,a))
        def aop(z):
            nonlocal a
            return self.f(a,z)
    def __matmul__(self,z):
        return Fun(z) and NotImplemented or FuncRow(lmap(self,partial(swapargs(self.f),z)))
        def opz(a):
            nonlocal z
            return self.f(a,z)
        return RightOp(opz)

F=Func(Func)
FR=Func(FuncRow)
K=const

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
L=Func(list)
lmap=aslist(map)
q=Attr(str)

trystr=F(list)*(''.join|I)

def rowtype(o): return (isinstance(o, list) or isinstance(o, tuple) or isinstance(o, FuncRow)) and type(o) or isinstance(o, str) and trystr or list

def aslist(f):
    def tolist(f,*args):
        return list(f(*args))
    return partial(tolist,f)

X=GetItem(meth.__getitem__)

p=Func(print)

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
        return super().__getitem__(kvs)
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

class qstr(str):
    def __getattr__(self,w):
        return qstr(' '.join((self,w)))

q=Attr(qstr)

@I(aslist*F)
def firstn(n,g):
    for i,x in enumerate(g):
        if i==n: break
        yield x

@Func
def first(g):
    for x in g:
        return x

# >>> from auto import *
# >>> from func import *
# >>> 
# >>> method.join
# Func(functools.partial(<function callmethod at 0xb6487c00>, 'join'))
# >>> method.join(',','abc')
# 'a,b,c'
# >>> meth.startswith('a')
# Func(<function meth.<locals>.callmeth.<locals>.callmeth at 0xb6518b28>)
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
# <generator object windows at 0xb6508f70>
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
# >>> (I**swap)((0,1))
# (1, 0)
# >>> swapargs(op.truediv)(2,3)
# 1.5
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> swap(1,2,3)
# (2, 1, 3)
# >>> 
# >>> 
# >>> swap(2,3)
# (3, 2)
# >>> isinstance(*swap(int, 3))
# True
# >>> 
# >>> star(isinstance)(swap(int, 3))
# True
# >>> partial(compose(swap,star(isinstance)),int)
# Func(functools.partial(<function compose.<locals>.compose at 0xb649a978>, <class 'int'>))
# >>> _(9),_(True),_('aa'),_((1,2))
# (True, True, False, False)
# >>> 
# >>> 
# >>> 
# >>> partial(compose(swap,partial(apply,isinstance)),int)
# Func(functools.partial(<function compose.<locals>.compose at 0xb6518468>, <class 'int'>))
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
# <81>:1: TypeError: unsupported operand type(s) for |: 'dict' and 'dict'
# >>> 
# >>> rowtype([])
# <class 'list'>
# >>> rowtype(())
# <class 'tuple'>
# >>> rowtype(2)
# <class 'list'>
# >>> o='abc'
# >>> isinstance(o, list)
# False
# >>> isinstance(o, tuple)
# False
# >>> FuncRow
# <class 'func.FuncRow'>
# >>> 
# >>> isinstance(o, FuncRow)
# False
# >>> isinstance(o, list) or isinstance(o, tuple) or isinstance(o, FuncRow)
# False
# >>> rowtype('abc')
# Func(<function compose.<locals>.compose at 0xb6487f60>)
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
# Func(<function compose.<locals>.compose at 0xb649aa98>)
# >>> F(list)
# Func(<class 'list'>)
# >>> type(_)
# <class 'func.Func'>
# >>> (I|l)(1,2,3)
# [1, 2, 3]
# >>> Dict['a':'b']|I
# Func(<function orr.<locals>.orr at 0xb649aa98>)
# >>> 
# >>> p(_('c'),_('a'))
# c b
# >>> 1&p
# 1
# >>> 
# >>> span(3)*F(sum)
# 6
# >>> 3&I
# 3
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
# 'abd'
# >>> trystr('abc')
# 'abc'
# >>> 
# >>> 'abc123'/method.isdigit
# '123'
# >>> ['1',2]/(method.isdigit|K(False))
# ['1']
# >>> 
# >>> partial(l,0)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb6487e88>, <class 'list'>, 0))
# >>> partial(partial(partial(l,0),1),2)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb6487e88>, <class 'list'>, 0, 1, 2))
# >>> partial(partial(partial(partial(l,0),1),2),3)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb6487e88>, <class 'list'>, 0, 1, 2, 3))
# >>> _.f.args
# (<class 'list'>, 0, 1, 2, 3)
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
# Func(<function I at 0xb6487738>)
# >>> _(3)
# 3
# >>> K
# Func(<function const at 0xb6487780>)
# >>> 
# >>> K(9)
# Func(<function const.<locals>.const at 0xb649aa08>)
# >>> _(9)
# 9
# >>> 
# >>> 
# >>> I+K(9)
# FuncRow((<function I at 0xb6487738>, <function const.<locals>.const at 0xb649aa08>))
# >>> 3*_,_(4)
# ((3, 9), (4, 9))
# >>> 
# >>> meth.add
# Func(<function meth.<locals>.callmeth at 0xb6518a50>)
# >>> m=Attr(((K(callmethod)+I)**partial*(I+K(I)))**partial)
# >>> 
# >>> 'join'
# 'join'
# >>> _*(K(callmethod)+I)
# (<function callmethod at 0xb6487c00>, 'join')
# >>> _**partial
# Func(functools.partial(<function callmethod at 0xb6487c00>, 'join'))
# >>> _*(I*K+K(I))
# (Func(<function const.<locals>.const at 0xb649ad68>), Func(<function I at 0xb6487738>))
# >>> _*FuncRow
# <172>:1: TypeError: can't multiply sequence by non-int of type 'type'
# >>> (',')*_
# <173>:1: TypeError: can't multiply sequence by non-int of type 'tuple'
# >>> 
# >>> _**apply
# <175>:1: TypeError: Func object argument after * must be an iterable, not Func
# /home/pi/python/parle/func.py:20: TypeError: Func object argument after * must be an iterable, not Func
#   __rpow__(
#     self=Func(<function apply at 0xb64879c0>)
#     left=(Func(<function const.<locals>.const at 0xb649ad68>), Func(<...
#   )
# /home/pi/python/parle/func.py:10: TypeError: Func object argument after * must be an iterable, not Func
#   __call__(self=Func(<function apply at 0xb64879c0>))
#     args=(Func(<function const.<locals>.const at 0xb649ad68>), Func(<...
#     kwargs={}
# /home/pi/python/parle/func.py:155: TypeError: Func object argument after * must be an iterable, not Func
#   apply(
#     f=Func(<function const.<locals>.const at 0xb649ad68>)
#     l=Func(<function I at 0xb6487738>)
#   )
#     kwargs={}
# >>> 
# >>> 
# >>> 
# >>> 
# >>> meth.join(['1','2','3'])(',')
# '1,2,3'
# >>> 
# >>> (2,(1,2,3))*(X[1]@mul*X[0])
# <182>:1: TypeError: binop() missing 1 required positional argument: 'y'
# /home/pi/python/parle/func.py:16: TypeError: binop() missing 1 required positional argument: 'y'
#   __rmul__(
#     self=Func(<function compose.<locals>.compose at 0xb6518420>)
#     left=(2, (1, 2, 3))
#   )
# /home/pi/python/parle/func.py:10: TypeError: binop() missing 1 required positional argument: 'y'
#   __call__(self=Func(<function compose.<locals>.compose at 0xb6518420...
#     args=((2, (1, 2, 3)),)
#     kwargs={}
# /home/pi/python/parle/func.py:138: TypeError: binop() missing 1 required positional argument: 'y'
#   compose()
#     args=((2, (1, 2, 3)),)
#     kwargs={}
#     f=<function compose.<locals>.compose at 0xb65186f0>
#     g=<function meth.<locals>.callmeth.<locals>.callmeth at 0xb65183d...
# /home/pi/python/parle/func.py:138: TypeError: binop() missing 1 required positional argument: 'y'
#   compose()
#     args=((2, (1, 2, 3)),)
#     kwargs={}
#     f=<function meth.<locals>.callmeth.<locals>.callmeth at 0xb67577c...
#     g=functools.partial(<function dmap at 0xb6487198>, Binop(<functio...
# /home/pi/python/parle/func.py:71: TypeError: binop() missing 1 required positional argument: 'y'
#   dmap(
#     f=<function Binop.__init__.<locals>.binop at 0xb649a228>
#     l=(1, 2, 3)
#   )
# >>> 
# >>> X[3](range(5))
# 3
# >>> 
# >>> q.the.name
# 'the name'
# >>> 
# >>> [1,2]&p
# [1, 2]
# >>> 
# >>> first(range(10))
# 0
# >>> firstn(3,range(10))
# [0, 1, 2]
# >>> span(100)*partial(firstn,10)
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# >>> 
# >>> K(11)(1,2,3)
# 11
# >>> K('good')()
# 'good'
# >>> K('good')(a=1)
# 'good'
# >>> 
# >>> add
# Binop(<function Binop.__init__.<locals>.binop at 0xb649a0c0>)
# >>> add(2,2)
# 4
# >>> sub(2,3)
# -1
# >>> 2*sub
# LeftOp(functools.partial(<function Binop.__init__.<locals>.binop at 0xb649a108>, 2))
# >>> _(3)
# -1
# >>> sub*2
# Func(functools.partial(<function compose.<locals>.compose at 0xb65183d8>, 2))
# >>> _(3)
# 1
# >>> 2*sub*3
# -1
# >>> (2,3,4)@(sub*1)
# (1, 2, 3)
# >>> (1*sub)*2
# -1
# >>> (1*sub)@(1,2,3)
# (0, -1, -2)
# >>> (1,2,3)@sub
# LeftOp(<bound method FuncRow.__call__ of FuncRow((Func(functools.partial(<function Binop.__init__.<locals>.binop at 0xb649a108>, 1)), Func(functools.partial(<function Binop.__init__.<locals>.binop at 0xb649a108>, 2)), Func(functools.partial(<function Binop.__init__.<locals>.binop at 0xb649a108>, 3))))>)
# >>> _(1)&p
# (0, 1, 2)
# >>> _(2)&p
# (-1, 0, 1)
# >>> _@(1,2,3)
# ((0, 1, 2), (-1, 0, 1), (-2, -1, 0))
# >>> chr(0x2580)
# '▀'
# >>> span(0x2580,0x259f)@F(chr)*F(''.join)
# '▀▁▂▃▄▅▆▇█▉▊▋▌▍▎▏▐░▒▓▔▕▖▗▘▙▚▛▜▝▞▟'
# >>> span(0x2500,0x257f)@F(chr)*F(''.join)
# '─━│┃┄┅┆┇┈┉┊┋┌┍┎┏┐┑┒┓└┕┖┗┘┙┚┛├┝┞┟┠┡┢┣┤┥┦┧┨┩┪┫┬┭┮┯┰┱┲┳┴┵┶┷┸┹┺┻┼┽┾┿╀╁╂╃╄╅╆╇╈╉╊╋╌╍╎╏═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬╭╮╯╰╱╲╳╴╵╶╷╸╹╺╻╼╽╾╿'
# >>> ▏
# invalid character in identifier (<216>, line 1)
# >>> chr(0x2062)&p
# ⁢
# >>> p('‗​‌')
# ‗​‌
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
