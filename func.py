from functools import partial, reduce
from operator import itemgetter as li
import operator

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

def I(x): return x

@Attr
class Unique:
    def __init__(self, name=None):
        if name: self.name=name
    def __repr__(self):
        return self.name if hasattr(self, 'name') else super().__repr__()

e=Unique.e

def redparts(f,xs):
    f=Binop(f)
    y=f.e
    for x in xs:
        y=Binop(f)(x,y)
        yield y

def callmethod(name,object,*args,**kwargs): return getattr(object,name)(*args,**kwargs)

@Attr
def method(name): return partial(callmethod,name)

def callmethod(name,object,*args,**kwargs): return getattr(object,name)(*args,**kwargs)

@Attr
def meth(name,*args,**kwargs):
    def callmeth(*args,**kwargs):
        def callmeth(object):
            nonlocal args, kwargs
            return callmethod(name,object,*args,**kwargs)
        return callmeth
    return callmeth

def getprop(name,object): return getattr(object,name)

@Attr
def prop(name): return partial(getprop,name)

def aslist(f):
    def tolist(f,*args):
        return list(f(*args))
    return partial(tolist,f)

def compose(f,g):
    def compose(f,g,*args,**kwargs):
        return g(f(*args,**kwargs))
    return partial(compose,f,g)

def star(f):
    def star(f,*l):
        return f(l)
    return partial(star,f)

def apply(f, l,**kwargs):
    return f(*l, **kwargs)

def unstar(f): return partial(apply,f)

l=star(list)
lmap=aslist(map)

def orr(f,g,x):
    try:
        return f(x)
    except Exception:
        pass
    return g(x)

class Unique: pass

def default(x):
    def I(x,y): return x
    return partial(I,x)

class Func:
    def __init__(self,f,domain=None):
        self.f=f if callable(f) else default(f)
        self.domain=self.f if domain else domain
    def __contains__(self, k):
        return k in self.f
    def __call__(self,*args,**kwargs):
        return self.f(*args,**kwargs)
    def __matmul__(self,other):
        if isinstance(f, Func):
            return Func(compose(self.f,other.F))
        raise NotImplemented
    def __or__(self,f):
        return Func(partial(orr,self.f,f))
    def __repr__(self):
        return f'{type(self).__name__}({self.f!r})'

class RightOp(Func):
    def __rmatmul__(self,x):
        return self.f(x)

class LeftOp(Func):
    def __matmul__(self,x):
        return self.f(x)


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

class OrFunc(Func):
    pass

class F(Func):
    pass

add=Binop(operator.add)
sub=Binop(operator.sub)
pow=Binop(operator.pow)
divide=Binop(operator.truediv)
div=Binop(operator.floordiv)
mul=Binop(operator.mul)

class Dict(dict):
    def __call__(self,k):
        return super().get(k)
    def __or__(self,f):
        if isinstance(f, dict):
            d=type(self)(self)
            d.update(f)
            return d
        return Func(self)|f
    def __matmul__(self, f):
        ...
    def __getitem__(self,kvs):
        if isinstance(kvs, slice): kvs=(kvs,)
        return type(self)(zip((kv.start for kv in kvs), (kv.stop for kv in kvs)))|self
Dict=Dict()

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

class Unique:
    pass

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
    def perm(l):
        nonlocal ks
        return type(l)([l[k] for k in ks])+l[len(ks):]
    return perm

def permargs(*ks):
    def permargs(f):
        nonlocal ks
        return compose(star(perm(*ks)),unstar(f))
    return permargs

def fggf(fg):
    def gf(*args1,**kwargs1):
        def f(*args,**kwargs):
            nonlocal args1,kwargs1,fg
            return fg(*args,**kwargs)(*args1,**kwargs1)
        return f
    return gf

swap=star(perm(1,0))
swapargs=permargs(1,0)

## >>> class List(list):
## >>> 
## ...     def total(self): return sum(self)
## ...     l=functools.partialmethod(total)
## ... 
## >>> List([1,2,3]).l()
## >>> list.x
## >>> 
## Traceback (most recent call last):
##   File "<console>", line 1, in <module>
## AttributeError: type object 'list' has no attribute 'x'
## >>> l=functools.partialmethod(list.__len__)
## >>> list.l=l
## Traceback (most recent call last):
##   File "<console>", line 1, in <module>
## TypeError: can't set attributes of built-in/extension type 'list'
## >>> l([1,2,3])
## Traceback (most recent call last):
##   File "<console>", line 1, in <module>
## TypeError: 'partialmethod' object is not callable
## >>> 
## 6


# >>> from auto import *
# >>> from func import *
# >>> 
# >>> 
# >>> 
# >>> method.join
# functools.partial(<function callmethod at 0xb6531d20>, 'join')
# >>> method.join(',','abc')
# 'a,b,c'
# >>> 
# >>> ap=Attr(print)
# >>> ap
# Attr(<built-in function print>)
# >>> ap.abc
# abc
# >>> pairs('abcdefg')
# <generator object windows at 0xb6529f30>
# >>> list(_)
# [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'f'), ('f', 'g')]
# >>> 
# >>> l(1,2,3)
# [1, 2, 3]
# >>> 
# >>> F(list)
# F(<class 'list'>)
# >>> _([1,2,3])
# [1, 2, 3]
# >>> 
# >>> star(li(2,1,3))(4,5,6,7)
# (6, 5, 7)
# >>> 
# >>> swap(1,2,3)
# (2, 1, 3)
# >>> 
# >>> swap(2,3)
# (3, 2)
# >>> isinstance(*swap(int, 3))
# True
# >>> 
# >>> unstar(isinstance)(swap(int, 3))
# True
# >>> partial(compose(swap,unstar(isinstance)),int)
# functools.partial(<function compose.<locals>.compose at 0xb6531858>, functools.partial(<function star.<locals>.star at 0xb64e69c0>, <function perm.<locals>.perm at 0xb64e6978>), functools.partial(<function apply at 0xb6531ed0>, <built-in function isinstance>), <class 'int'>)
# >>> _(9),_(True),_('aa'),_((1,2))
# (True, True, False, False)
# >>> 
# >>> 
# >>> 
# >>> partial(compose(swap,partial(apply,isinstance)),int)
# functools.partial(<function compose.<locals>.compose at 0xb6531858>, functools.partial(<function star.<locals>.star at 0xb64e69c0>, <function perm.<locals>.perm at 0xb64e6978>), functools.partial(<function apply at 0xb6531ed0>, <built-in function isinstance>), <class 'int'>)
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
# >>> compose(star(perm(1,0)),unstar(l))(1,2,3,4)
# [2, 1, 3, 4]
# >>> 
# >>> 
# >>> 
# >>> permargs(1,0)(l)(1,2,3,4)
# [2, 1, 3, 4]
# >>> 
# >>> 
# >>> 
# >>> f=Dict|{1:2, 3:4}|default(7)
# >>> [f(x) for x in range(1,6)]
# [2, None, 4, None, None]
# >>> 
# >>> swapargs(l)(1,2,3)
# [2, 1, 3]
# >>> Dict[3:4](3)
# 4
# >>> 
# >>> meth.join(map(str,range(10)))(', ')
# '0, 1, 2, 3, 4, 5, 6, 7, 8, 9'
# >>> 
# >>> fggf(meth.join)(',')(map(str,[1,2,3]))
# '1,2,3'
# >>> 
# >>> 
# >>> 
# >>> aslist(map)(operator.neg,[1,2,3])
# [-1, -2, -3]
# >>> 
# >>> callable(F)
# True
# >>> F(list)@F(map)
# <console>:1: TypeError: unsupported operand type(s) for @: 'F' and 'F'
# >>> 
