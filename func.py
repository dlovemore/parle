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
        if isinstance(right, FuncRow): return NotImplemented
        return Fun(right) and compose(self,partial(dmap,right)) or NotImplemented
    def __rmul__(self,left):
        return Fun(left) and compose(left,self) or self(left)
    def __mul__(self,right):
        if isinstance(right, FuncRow): return NotImplemented
        if isinstance(right, Binop): return NotImplemented
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
        return Fun(l) and orf(l,self) or NotImplemented
    def __or__(self,r):
        return Fun(r) and orf(self,r) or NotImplemented
    def __add__(self, right):
        if isinstance(right, Func):
            return FuncRow((self,right))
        return Fun(right) and FuncRow((self,right)) or NotImplemented
    def __pos__(self): return I+self
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
        self.row=Row
    def __call__(self, *args,**kwargs):
        return Row(f(*args,**kwargs) for f in self.fs)
    def __rmul__(self, left):
        if Fun(left): return compose(left, self)
        return Row(f(left) for f in self.fs)
    def __radd__(self, left):
        if isinstance(left, FuncRow):
            return FuncRow(left.fs+self.fs)
        if isinstance(left, Func):
            return FuncRow(((left.f,)+self.fs))
        return Fun(left) and FuncRow((left,)+self.fs) or NotImplemented
    def __add__(self, right):
        if isinstance(right, FuncRow):
            return FuncRow((self.fs+right.fs))
        if isinstance(right, Func):
            return FuncRow((self.fs+(right,)))
        return Fun(right) and FuncRow(self.fs+(Func(right),)) or NotImplemented
    def __pos__(self): return I+self
    def __getitem__(self,k): return FuncRow(self.fs[k])
    def __repr__(self):
        return f'{type(self).__name__}({self.fs!r})'

class AndFunc(Func):
    def __init__(self, fs):
        super().__init__(fs)
    def __call__(self):
        return ...

class AndState:
    def __init__(self,x):
        return f()

def andfn(f,g):
    def andg(x):
        if x:
            g(x)
    def fandg(*args):
        nonlocal f,g
        val = (f(*args))
        if val:
            return g(val)
        else: return val

    return Rewindable(g)

def values(g):
    if not iterable(g):
        g=(g,)
    return iter(g)

class Rewindable:
    def __init__(self, g):
        self.g=g
    def __iter__(self):
        return Record(iter(self.g))

class Record:
    def __init__(self, iterator):
        self.iterator = iterator
        self.xs = []
    def __next__(self):
        try:
            self.x=next(self.iterator)
        except:
            raise StopException
        self.xs.push(self.x)
        return self.x
    def __getitem__(self, i):
        limit=i if isinstance(i,int) else i.stop or -1
        try:
            while limit>=len(self.xs) or i<0:
                next(self)
        except StopIteration:
            pass
        return self.xs[i]

class Selection:
    def __init__(self,data,ix):
        self.d=data
        self.ix=ix
    def __getitem__(self, key):
        if isinstance(key,slice):
            if key.step!=1: raise IndexError(key)
            return self.d[key.start is not None and self.ix[key.start] or None:key.stop is not None and self.ix[key.stop] or None]
        return self.d[self.ix[key]]
    def __iter__(self):
        return (self.d[i] for i in self.ix)
    def __str__(self):
        return str(Row([self.d[i] for i in self.ix]))

class Choice(Selection):
    def __init__(self, values, i=0):
        super().__init__(values, [i])
        self.val=values[i]
    def __prev__(self):
        try:
            return Choice(self.d,[self.ix[0]-1])
        except IndexError:
            raise StopException
    def __next__(self):
        try:
            return Choice(self.d,[self.ix[0]+1])
        except IndexError:
            raise StopException
    def __getattr__(self, a): return getattr(self.val,a)
    def __add__(self, rhs): return self.val.__add__(rhs)
    def __contains__(self, lhs): self.val.__contains__(lhs)
    def __truediv__(self, rhs): return self.val.__truediv__(rhs)
    def __floordiv__(self, rhs): return self.val.__floordiv__(rhs)
    def __and__(self, rhs): return self.val.__and__(rhs)
    def __xor__(self, rhs): return self.val.__xor__(rhs)
    def __invert__(self): return self.val.__invert__()
    def __or__(self, rhs): return self.val.__or__(rhs)
    def __pow__(self, rhs): return self.val.__pow__(rhs)
    def __getitem__(self, k): return self.val.__getitem__(k)
    def __lshift__(self, rhs): return self.val.__lshift__(rhs)
    def __mod__(self, rhs): return self.val.__mod__(rhs)
    def __mul__(self, rhs): return self.val.__mul__(rhs)
    def __matmul__(self, rhs): return self.val.__matmul__(rhs)
    def __neg__(self): return self.val.__neg__()
    def __pos__(self): return self.val.__pos__()
    def __rshift__(self, rhs): return self.val.__rshift__(rhs)
    def __sub__(self, rhs): return self.val.__sub__(rhs)
    def __lt__(self, rhs): return self.val.__lt__(rhs)
    def __le__(self, rhs): return self.val.__le__(rhs)
    def __eq__(self, rhs): return self.val.__eq__(rhs)
    def __ne__(self, rhs): return self.val.__ne__(rhs)
    def __ge__(self, rhs): return self.val.__ge__(rhs)
    def __gt__(self, rhs): return self.val.__gt__(rhs)
    def __radd__(self, lhs): return self.val.__radd__(lhs)
    def __rcontains__(self, lhs): self.val.__rcontains__(lhs)
    def __rtruediv__(self, lhs): return self.val.__rtruediv__(lhs)
    def __rfloordiv__(self, lhs): return self.val.__rfloordiv__(lhs)
    def __rand__(self, lhs): return self.val.__rand__(lhs)
    def __rxor__(self, lhs): return self.val.__rxor__(lhs)
    def __ror__(self, lhs): return self.val.__ror__(lhs)
    def __rpow__(self, lhs): return self.val.__rpow__(lhs)
    def __rlshift__(self, lhs): return self.val.__rlshift__(lhs)
    def __rmod__(self, lhs): return self.val.__rmod__(lhs)
    def __rmul__(self, lhs): return self.val.__rmul__(lhs)
    def __rmatmul__(self, lhs): return self.val.__rmatmul__(lhs)
    def __rrshift__(self, lhs): return self.val.__rrshift__(lhs)
    def __rsub__(self, lhs): return self.val.__rsub__(lhs)
    def __rlt__(self, lhs): return self.val.__rlt__(lhs)
    def __rle__(self, lhs): return self.val.__rle__(lhs)
    def __req__(self, lhs): return self.val.__req__(lhs)
    def __rne__(self, lhs): return self.val.__rne__(lhs)
    def __rge__(self, lhs): return self.val.__rge__(lhs)
    def __rgt__(self, lhs): return self.val.__rgt__(lhs)
    def __call__(self, *args,**kwargs): return self.val.__call__(*args,**kwargs)
    def __str__(self): return self.val.__str__(self)
    def __repr__(self): return self.val.__repr__(self)

class Row(list):
    def __matmul__(self, f):
        if isinstance(f, Func): return NotImplemented # drop into rmatmul
        return self@Fun(f)
    def __mul__(self, rh):
        if isinstance(rh, Func): return NotImplemented
        return self*Func(rh)
    def __rpow__(self, lh):
        return Func(lh)(*self)
    def __pow__(self, f):
        return Fun(f) and f(*self) or NotImplemented
    def __getitem__(self, key):
        if isinstance(key, slice):
            return Row(super().__getitem__(key))
        return super().__getitem__(key)
    def __getattr__(self, attr):
       return self@(getattr(prop, attr))
    def __rtruediv__(self, f):
        if callable(f):
            return qqqreduce(f,self)
        return self@Func(partial(operator.truediv,f))
    def __truediv__(self, f):
        if callable(f):
            return Row([x for x in self if f(x)])
        return Row(map(meth.__truediv__(f), self))
    def __rfloordiv__(self, f):
        return Row(redparts(f,self))
    def __str__(self):
        return ' '.join(map(str,self))
    def __repr__(self):
        return ' '.join(map(repr,self))
        return f'{type(self).__name__}({super().__repr__()})'

class GetItem:
    def __init__(self,f):
        self.f=f
    def __call__(self, k):
        return self.f(k)
    def __getitem__(self, k):
        return self.f(k)

class Attr:
    def __init__(self, f):
        self.f=f
    def __call__(self, attr):
        return self.f(attr)
    def __getattr__(self, attr):
        return self.f(attr)
    def __repr__(self):
        return f'{type(self).__name__}({self.f})'

R=GetItem(Row)

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

@Fun
def I(x):return x
@Func
class Ith(Func):
    def __init__(self,f=I):
        super().__init__(f)
    def __getitem__(self,k):
        return Func(op.itemgetter(k))
    def __getattr__(self,a):
        return getattr(method,a)
I=Ith()

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
sort=Func(sorted)

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
def orf(f,g):
    f,g=fun(f),fun(g)
    @Func
    def orf(*args,**kwargs):
        nonlocal f,g
        try:
            return f(*args,**kwargs)
        except Exception:
            pass
        return g(*args,**kwargs)
    return orf

e=Unique.e

@Func
def span(a,b=None,step=1):
    if isinstance(a,slice): a,b,step=a
    if isinstance(a,str): return ''.join(map(chr,span(ord(a),ord(b),step)))
    if b is None: a,b=1,a
    return range(1,a+1,step) if b is None else range(a,b+1,step)

def redparts(f,xs):
    f=Binop(f)
    y=f.e
    for x in xs:
        y=Binop(f)(x,y)
        yield y

class LeftOp(Func):
    def __mul__(self,x):
        return self(x)
    def __matmul__(self,x):
        return dmap(self,x)

class RightOp(Func):
    def __rmatmul__(self,x):
        return self(x)

class Binop(Func):
    def __init__(self, op):
        def binop(x,y):
            nonlocal op
            if y is e:
                return x
            if x is e:
                return y
            return op(x,y)
        self.op=op
        self.f=op.f if isinstance(op, Binop) else binop
        self.e=e
    def __rmul__(self,a):
        def binop(x,y):
            nonlocal a
            return self.f(a(x),y)
        return Fun(a) and Binop(binop) or LeftOp(partial(self,a))
    def __mul__(self,z):
       return Fun(z) and NotImplemented or partial(unstar(swap)**self,z)
    def __rmatmul__(self,a):
        return Fun(a) and Binop(Fun(a)) or LeftOp(pmap(self,a))
    def __matmul__(self,z):
        return Fun(z) and NotImplemented or FuncRow(lmap(self,partial(swap*self,z)))

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

trystr=F(Row)*(''.join|I)

def rowtype(o):
    return ((isinstance(o, list) or
                isinstance(o, tuple) or
                isinstance(o, FuncRow)) and type(o) or
            isinstance(o, str) and trystr or Row)

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
orr=Binop(operator.or_)
amp=Binop(operator.and_)
truediv=over=Binop(operator.truediv)
floordiv=Binop(operator.floordiv)
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
# Func(functools.partial(<function callmethod at 0xb6419468>, 'join'))
# >>> method.join(',','abc')
# 'a,b,c'
# >>> meth.startswith('a')
# Func(<function meth.<locals>.callmeth.<locals>.callmeth at 0xb64ecbb8>)
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
# <generator object windows at 0xb65edf70>
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
# >>> 
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
# Func(functools.partial(<function compose.<locals>.compose at 0xb64ecbb8>, <class 'int'>))
# >>> _(9),_('ab')
# (True, False)
# >>> 
# >>> push(3)
# >>> (1,2)*push(3)
# <45>:1: TypeError: can't multiply sequence by non-int of type 'NoneType'
# >>> 
# >>> _*push(4)
# <47>:1: TypeError: can't multiply sequence by non-int of type 'NoneType'
# >>> 
# >>> _(9),_(True),_('aa'),_((1,2))
# <49>:1: TypeError: 'tuple' object is not callable
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
# <76>:1: TypeError: unsupported operand type(s) for |: 'dict' and 'dict'
# >>> 
# >>> rowtype([])
# <class 'list'>
# >>> rowtype(())
# <class 'tuple'>
# >>> rowtype(2)
# <class 'func.Row'>
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
# Func(<function compose.<locals>.compose at 0xb64198a0>)
# >>> rowtype('abc')('def')
# 'def'
# >>> 
# >>> f=Dict|{1:2, 3:4}|K(7)
# >>> [f(x) for x in range(1,6)]
# [2, 7, 4, 7, 7]
# >>> span(5)@f
# 2 7 4 7 7
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
# Func(<function compose.<locals>.compose at 0xb64263d8>)
# >>> F(list)
# Func(<class 'list'>)
# >>> type(_)
# <class 'func.Func'>
# >>> (I|l)(1,2,3)
# [1, 2, 3]
# >>> Dict['a':'b']|I
# Func(<function orf.<locals>.orf at 0xb64263d8>)
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
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb64197c8>, <class 'list'>, 0))
# >>> partial(partial(partial(l,0),1),2)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb64197c8>, <class 'list'>, 0, 1, 2))
# >>> partial(partial(partial(partial(l,0),1),2),3)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb64197c8>, <class 'list'>, 0, 1, 2, 3))
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
# False False False False
# >>> 
# >>> 
# >>> type(partial(I))
# <class 'func.Func'>
# >>> type(functools.partial(I))
# <class 'functools.partial'>
# >>> I
# Ith(<function I at 0xb641eed0>)
# >>> _(3)
# 3
# >>> K
# Func(<function const at 0xb641ef18>)
# >>> 
# >>> K(9)
# Func(<function const.<locals>.const at 0xb6426300>)
# >>> _(9)
# 9
# >>> 
# >>> 
# >>> I+K(9)
# FuncRow((Ith(<function I at 0xb641eed0>), Func(<function const.<locals>.const at 0xb6426300>)))
# >>> 3*_,_(4)
# (3 9, 4 9)
# >>> 3*+K(9)
# 3 9
# >>> 'abcdef'*+Func(len)
# 'abcdef' 6
# >>> 
# >>> 
# >>> meth.add
# Func(<function meth.<locals>.callmeth at 0xb6426540>)
# >>> m=Attr(((K(callmethod)+I)**partial*(I+K(I)))**partial)
# >>> 
# >>> 'join'
# 'join'
# >>> _*(K(callmethod)+I)
# <function callmethod at 0xb6419468> 'join'
# >>> _**partial
# Func(functools.partial(<function callmethod at 0xb6419468>, 'join'))
# >>> _*(I*K+K(I))
# Func(<function compose.<locals>.compose at 0xb6426738>)
# >>> _*FuncRow
# Func(<function compose.<locals>.compose at 0xb64267c8>)
# >>> (',')*_
# <169>:1: TypeError: join() takes exactly one argument (0 given)
# /home/pi/python/parle/func.py:19: TypeError: join() takes exactly one argument (0 given)
#   __rmul__(
#     self=Func(<function compose.<locals>.compose at 0xb64267c8>)
#     left=,
#   )
# /home/pi/python/parle/func.py:12: TypeError: join() takes exactly one argument (0 given)
#   __call__(self=Func(<function compose.<locals>.compose at 0xb64267c8...
#     args=(',',)
#     kwargs={}
# /home/pi/python/parle/func.py:323: TypeError: join() takes exactly one argument (0 given)
#   compose()
#     args=(',',)
#     kwargs={}
#     f=<function compose.<locals>.compose at 0xb6426738>
#     g=<class 'func.FuncRow'>
# /home/pi/python/parle/func.py:323: TypeError: join() takes exactly one argument (0 given)
#   compose()
#     args=(',',)
#     kwargs={}
#     f=functools.partial(<function callmethod at 0xb6419468>, 'join')
#     g=<bound method FuncRow.__call__ of FuncRow((Func(<function compo...
# /home/pi/python/parle/func.py:431: TypeError: join() takes exactly one argument (0 given)
#   callmethod(name=join, object=,)
#     args=()
#     kwargs={}
# >>> 
# >>> _**apply
# Func(<function compose.<locals>.compose at 0xb64268e8>)
# >>> 
# >>> 
# >>> 
# >>> 
# >>> meth.join(['1','2','3'])(',')
# '1,2,3'
# >>> 
# >>> (2,(1,2,3))*(X[1]@mul) #*X[0])
# LeftOp(functools.partial(<function Binop.__init__.<locals>.binop at 0xb64267c8>, (2, (1, 2, 3))))
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
# Binop(<function Binop.__init__.<locals>.binop at 0xb64199c0>)
# >>> add(2,2)
# 4
# >>> sub(2,3)
# -1
# >>> 2*sub
# LeftOp(functools.partial(<function Binop.__init__.<locals>.binop at 0xb6419a08>, 2))
# >>> _(3)
# -1
# >>> swap((0,1))
# (1, 0)
# >>> 
# >>> sub*2
# Func(functools.partial(<function compose.<locals>.compose at 0xb64ecbb8>, 2))
# >>> (sub*2)(3)
# 1
# >>> sub*2
# Func(functools.partial(<function compose.<locals>.compose at 0xb64ec3d8>, 2))
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
# LeftOp(<bound method FuncRow.__call__ of FuncRow((Func(functools.partial(<function Binop.__init__.<locals>.binop at 0xb6419a08>, 1)), Func(functools.partial(<function Binop.__init__.<locals>.binop at 0xb6419a08>, 2)), Func(functools.partial(<function Binop.__init__.<locals>.binop at 0xb6419a08>, 3))))>)
# >>> _(1)&p
# 0 1 2
# >>> _(2)&p
# -1 0 1
# >>> _@(1,2,3)
# (0 1 2, -1 0 1, -2 -1 0)
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
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb672c7c8>, <built-in function sum>, 1, 2, 3))
# >>> f(4)
# 10
# >>> f(5)
# 11
# >>> f(6,...)
# Func(functools.partial(<function unstar.<locals>.unstar at 0xb672c7c8>, <built-in function sum>, 1, 2, 3, 6))
# >>> _(7)
# 19
# >>> from primes import isprime
# >>> 
# >>> rowtype(span(10))(filter(isprime,span(10)))
# 2 3 5 7
# >>> 
# >>> 
# >>> filter(isprime,span(10))
# 2 3 5 7
# >>> primesupto=span*filter(isprime,...)
# >>> primesupto(10)
# 2 3 5 7
# >>> primesupto(100)
# 2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97
# >>> 
# >>> (2,3,4,5,6)@(~isprime)
# (False, False, True, False, True)
# >>> 
# >>> 
# >>> 
# >>> op.not_
# Func(<built-in function not_>)
# >>> 
# >>> span('a','z')
# 'abcdefghijklmnopqrstuvwxyz'
# >>> 
# >>> 
# >>> 
# >>> op.eq(2,...)
# Func(functools.partial(<built-in function eq>, 2))
# >>> (2,3)@_
# (True, False)
# >>> 'abc'*F(len)*sub*1
# 2
# >>> 'abc'*(len*sub)*1
# 2
# >>> 'abc'*((len*sub)*1)
# 2
# >>> 
# >>> ord=F(ord)
# >>> 'a'*ord*mod*9
# 7
# >>> 'a'*(ord*mod*9)
# 7
# >>> 
# >>> li(2,4)((1,2,3,4,5))
# (3, 5)
# >>> 
