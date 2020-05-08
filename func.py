import functools
import builtins
import operator

class Func:
    def __init__(self,f):
        self.f=fun(f)
    def __xcontains__(self, k):
        return k in self.f
    def __call__(self,*args,**kwargs):
        if args and args[-1]==...: return partial(self,*args[:-1],**kwargs)
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
    def __truediv__(self, right):
        return Fun(right) and compose(self,partial(filter,right)) or NotImplemented
    def __rtruediv__(self, left):
        return Fun(left) and compose(left,partial(filter,self)) or filter(self,left)
    def __rand__(self,l):
        return Fun(l) and then(l,self) or self(l)
    def __ror__(self,l):
        return Fun(l) and orr(l,self) or NotImplemented
    def __or__(self,r):
        return Fun(r) and orr(self,r) or NotImplemented
    def __add__(self, other):
        if isinstance(other, Func):
            return FuncRow((self,other))
        return NotImplemented
    def __invert__(self): return compose(self,op.not_)
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
    def __call__(self, *args,**kwargs):
        return tuple(f(*args,**kwargs) for f in self.fs)
    def __rmul__(self, left):
        return tuple(f(left) for f in self.fs)
    def __radd__(self, left):
        if isinstance(left, FuncRow):
            return FuncRow(left.fs+self.fs)
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

def dmap(f,l):
    f=fun(f)
    return rowtype(l)(map(f,l))

def pmap(f,l):
    f=fun(f)
    return FuncRow([partial(f,x) for x in l])

def getitem(k):
    return meth.__getitem__(k)

@Func
def filter(f,xs):
    return rowtype(xs)(builtins.filter(f,xs))

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
def delay(f):
    @Func
    def call(*args, **kwargs):
        nonlocal f
        return f(*args, **kwargs)
    return call

@Func
def push(x):
    pass

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

@Func
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
       return Fun(z) and NotImplemented or partial(unstar(swap)**self,z)
    def __rmatmul__(self,a):
        return Fun(a) and NotImplemented or LeftOp(pmap(self,a))
        def aop(z):
            nonlocal a
            return self.f(a,z)
    def __matmul__(self,z):
        return Fun(z) and NotImplemented or FuncRow(lmap(self,partial(swap*self,z)))
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
mod=Binop(operator.mod)
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
    rt=rowtype(xs)
    l=[]
    for i,x in enumerate(xs):
        l.append(x)
        if i>=n-1:
            yield rt(l)
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

@Func
def perm(*ks):
    assert sorted(ks)==list(range(len(ks)))
    permuter=li(*ks)
    nks=len(ks)
    @Func
    def perm(l):
        nonlocal nks,permuter
        return type(l)(permuter(l))+l[nks:]
    return perm

@Func
def permargs(*ks):
    @Func
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

swap=perm(1,0)
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
# Func(functools.partial(<function callmethod at 0xb6473db0>, 'join'))
# >>> method.join(',','abc')
# 'a,b,c'
# >>> meth.startswith('a')
# Func(<function meth.<locals>.callmeth.<locals>.callmeth at 0xb6503b70>)
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
# <generator object windows at 0xb6603f30>
# >>> list(_)
# ['ab', 'bc', 'cd', 'de', 'ef', 'fg']
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
# >>> swap((0,1))
# (1, 0)
# >>> 
# >>> (2,3)*swap
# (3, 2)
# >>> (2,3)**F(op.pow)
# 8
# >>> (2,3)*swap**F(op.pow)
# 9
# >>> 
# >>> (I**l)((0,1))
# [0, 1]
# >>> swapargs(op.truediv)(2,3)
# 1.5
# >>> 
# >>> (1,2,3)*swap
# (2, 1, 3)
# >>> 
# >>> unstar(swap)(2,3)
# (3, 2)
# >>> isinstance(*(int, 3)*swap)
# True
# >>> (int, 3)*swap**isinstance
# True
# >>> (int, 3)*(swap**isinstance)
# True
# >>> 
# >>> star(isinstance)(swap((int, 3)))
# True
# >>> partial(compose(unstar(swap),star(isinstance)),int)
# Func(functools.partial(<function compose.<locals>.compose at 0xb6484b28>, <class 'int'>))
# >>> _(9),_('ab')
# (True, False)
# >>> push=(K(I)+l*tuple*K)*FuncRow*
# invalid syntax (<42>, line 1)
# >>> push(3)
# >>> (1,2)*push(3)
# <44>:1: TypeError: can't multiply sequence by non-int of type 'NoneType'
# >>> 
# >>> _*push(4)
# <46>:1: TypeError: can't multiply sequence by non-int of type 'NoneType'
# >>> 
# >>> _(9),_(True),_('aa'),_((1,2))
# <48>:1: TypeError: 'tuple' object is not callable
# >>> 
# >>> 
# >>> 
# >>> 
# >>> swap((1,2,3,4))
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
# <75>:1: TypeError: unsupported operand type(s) for |: 'dict' and 'dict'
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
# Func(<function compose.<locals>.compose at 0xb6484150>)
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
# Func(<function compose.<locals>.compose at 0xb6484b70>)
# >>> F(list)
# Func(<class 'list'>)
# >>> type(_)
# <class 'func.Func'>
# >>> (I|l)(1,2,3)
# [1, 2, 3]
# >>> Dict['a':'b']|I
# Func(<function orr.<locals>.orr at 0xb6484b70>)
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
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb6484078>, <class 'list'>, 0))
# >>> partial(partial(partial(l,0),1),2)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb6484078>, <class 'list'>, 0, 1, 2))
# >>> partial(partial(partial(partial(l,0),1),2),3)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb6484078>, <class 'list'>, 0, 1, 2, 3))
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
# Func(<function I at 0xb6473858>)
# >>> _(3)
# 3
# >>> K
# Func(<function const at 0xb64738a0>)
# >>> 
# >>> K(9)
# Func(<function const.<locals>.const at 0xb6484b28>)
# >>> _(9)
# 9
# >>> 
# >>> 
# >>> I+K(9)
# FuncRow((Func(<function I at 0xb6473858>), Func(<function const.<locals>.const at 0xb6484b28>)))
# >>> 3*_,_(4)
# ((3, 9), (4, 9))
# >>> 
# >>> meth.add
# Func(<function meth.<locals>.callmeth at 0xb6503a98>)
# >>> m=Attr(((K(callmethod)+I)**partial*(I+K(I)))**partial)
# >>> 
# >>> 'join'
# 'join'
# >>> _*(K(callmethod)+I)
# (<function callmethod at 0xb6473db0>, 'join')
# >>> _**partial
# Func(functools.partial(<function callmethod at 0xb6473db0>, 'join'))
# >>> _*(I*K+K(I))
# (Func(<function const.<locals>.const at 0xb6484f60>), Func(<function I at 0xb6473858>))
# >>> _*FuncRow
# <164>:1: TypeError: can't multiply sequence by non-int of type 'type'
# >>> (',')*_
# <165>:1: TypeError: can't multiply sequence by non-int of type 'tuple'
# >>> 
# >>> _**apply
# <167>:1: TypeError: Func object argument after * must be an iterable, not Func
# /home/pi/python/parle/func.py:22: TypeError: Func object argument after * must be an iterable, not Func
#   __rpow__(
#     self=Func(<function apply at 0xb6473ae0>)
#     left=(Func(<function const.<locals>.const at 0xb6484f60>), Func(<...
#   )
# /home/pi/python/parle/func.py:12: TypeError: Func object argument after * must be an iterable, not Func
#   __call__(self=Func(<function apply at 0xb6473ae0>))
#     args=(Func(<function const.<locals>.const at 0xb6484f60>), Func(<...
#     kwargs={}
# /home/pi/python/parle/func.py:166: TypeError: Func object argument after * must be an iterable, not Func
#   apply(
#     f=Func(<function const.<locals>.const at 0xb6484f60>)
#     l=Func(<function I at 0xb6473858>)
#   )
#     kwargs={}
# >>> 
# >>> 
# >>> 
# >>> 
# >>> meth.join(['1','2','3'])(',')
# '1,2,3'
# >>> 
# >>> (2,(1,2,3))*(X[1]@mul) #*X[0])
# <174>:1: TypeError: binop() missing 1 required positional argument: 'y'
# /home/pi/python/parle/func.py:18: TypeError: binop() missing 1 required positional argument: 'y'
#   __rmul__(
#     self=Func(<function compose.<locals>.compose at 0xb6503bb8>)
#     left=(2, (1, 2, 3))
#   )
# /home/pi/python/parle/func.py:12: TypeError: binop() missing 1 required positional argument: 'y'
#   __call__(self=Func(<function compose.<locals>.compose at 0xb6503bb8...
#     args=((2, (1, 2, 3)),)
#     kwargs={}
# /home/pi/python/parle/func.py:149: TypeError: binop() missing 1 required positional argument: 'y'
#   compose()
#     args=((2, (1, 2, 3)),)
#     kwargs={}
#     f=<function meth.<locals>.callmeth.<locals>.callmeth at 0xb67427c...
#     g=functools.partial(<function dmap at 0xb6473270>, Binop(<functio...
# /home/pi/python/parle/func.py:106: TypeError: binop() missing 1 required positional argument: 'y'
#   dmap(
#     f=<function Binop.__init__.<locals>.binop at 0xb6484420>
#     l=(1, 2, 3)
#   )
# >>> 
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
# Binop(<function Binop.__init__.<locals>.binop at 0xb6484270>)
# >>> add(2,2)
# 4
# >>> sub(2,3)
# -1
# >>> 2*sub
# LeftOp(functools.partial(<function Binop.__init__.<locals>.binop at 0xb64842b8>, 2))
# >>> _(3)
# -1
# >>> swap((0,1))
# (1, 0)
# >>> 
# >>> sub*2
# Func(functools.partial(<function compose.<locals>.compose at 0xb65033d8>, 2))
# >>> (sub*2)(3)
# 1
# >>> sub*2
# Func(functools.partial(<function compose.<locals>.compose at 0xb6503bb8>, 2))
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
# LeftOp(<bound method FuncRow.__call__ of FuncRow((Func(functools.partial(<function Binop.__init__.<locals>.binop at 0xb64842b8>, 1)), Func(functools.partial(<function Binop.__init__.<locals>.binop at 0xb64842b8>, 2)), Func(functools.partial(<function Binop.__init__.<locals>.binop at 0xb64842b8>, 3))))>)
# >>> _(1)&p
# (0, 1, 2)
# >>> _(2)&p
# (-1, 0, 1)
# >>> _@(1,2,3)
# ((0, 1, 2), (-1, 0, 1), (-2, -1, 0))
# >>> 
# >>> pairs('abcde')*L
# ['ab', 'bc', 'cd', 'de']
# >>> 
# >>> sum
# <built-in function sum>
# >>> sum=unstar(sum)
# >>> (1,2,3,4)**sum
# 10
# >>> f=sum(1,2,3,...)
# >>> f
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb67427c8>, <built-in function sum>, 1, 2, 3))
# >>> f(4)
# 10
# >>> f(5)
# 11
# >>> f(6,...)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb67427c8>, <built-in function sum>, 1, 2, 3, 6))
# >>> _(7)
# 19
# >>> from primes import isprime
# >>> 
# >>> rowtype(span(10))(filter(isprime,span(10)))
# [2, 3, 5, 7]
# >>> 
# >>> 
# >>> filter(isprime,span(10))
# [2, 3, 5, 7]
# >>> primesupto=span*filter(isprime,...)
# >>> primesupto(10)
# [2, 3, 5, 7]
# >>> primesupto(100)
# [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
# >>> 
# >>> (2,3,4,5,6)@(~isprime)
# (False, False, True, False, True)
# >>> 
# >>> 
# >>> 
# >>> dir(operator)
# ['__abs__', '__add__', '__all__', '__and__', '__builtins__', '__cached__', '__concat__', '__contains__', '__delitem__', '__doc__', '__eq__', '__file__', '__floordiv__', '__ge__', '__getitem__', '__gt__', '__iadd__', '__iand__', '__iconcat__', '__ifloordiv__', '__ilshift__', '__imatmul__', '__imod__', '__imul__', '__index__', '__inv__', '__invert__', '__ior__', '__ipow__', '__irshift__', '__isub__', '__itruediv__', '__ixor__', '__le__', '__loader__', '__lshift__', '__lt__', '__matmul__', '__mod__', '__mul__', '__name__', '__ne__', '__neg__', '__not__', '__or__', '__package__', '__pos__', '__pow__', '__rshift__', '__setitem__', '__spec__', '__sub__', '__truediv__', '__xor__', '_abs', 'abs', 'add', 'and_', 'attrgetter', 'concat', 'contains', 'countOf', 'delitem', 'eq', 'floordiv', 'ge', 'getitem', 'gt', 'iadd', 'iand', 'iconcat', 'ifloordiv', 'ilshift', 'imatmul', 'imod', 'imul', 'index', 'indexOf', 'inv', 'invert', 'ior', 'ipow', 'irshift', 'is_', 'is_not', 'isub', 'itemgetter', 'itruediv', 'ixor', 'le', 'length_hint', 'lshift', 'lt', 'matmul', 'methodcaller', 'mod', 'mul', 'ne', 'neg', 'not_', 'or_', 'pos', 'pow', 'rshift', 'setitem', 'sub', 'truediv', 'truth', 'xor']
# >>> 
# >>> op.not_
# Func(<built-in function not_>)
# >>> 
# >>> 
