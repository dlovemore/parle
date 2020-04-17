from auto import *
from bisect import bisect_right
from func import pairs, aslist, Func, GetItem, I, redparts, unstar, meth, prop, lmap
from functools import reduce, partial
import htmldraw
import operator

def tale(l):
    n=0
    tales=[]
    for x in l:
        n+=x
        tales.append(n)
    return tales

def table(words,vals):
    values=[str(v) for v in vals]
    words =[w.rjust(max(len(w),len(v)),' ') for w,v in zip(words,values)]
    values=[v.rjust(max(len(v),len(w)),' ') for v,w in zip(values,words)]
    return words,values

# In unicode Hebrew punctuation is represented by Mark modifiers that are
# printed with the previous letter. Such strings are therefore short by the
# number of modifiers. Adding in the number of modifiers to the text width
# serves to compensate for this in text justification.

def modifierlen(s):
    return sum([unicodedata.category(c) in {'Mn','Lm'} for c in s])

def fill(vv,fillvalue=''):
    vv=list(vv)
    M=max((len(v) for v in vv))
    return Table([v if len(v)==M else v+[fillvalue]*(M-len(v)) for v in vv])

def justify(vv,align='center'):
    zvv=list(itertools.zip_longest(*(map(str,v) for v in vv), fillvalue=''))
    maxes=[max((len(w)-modifierlen(w) for w in ws)) for ws in zvv]
    vvs=[[getattr(w,align)(M+modifierlen(w),' ') for w in ws] for M,ws in zip(maxes,zvv)]
    return list(zip(*vvs))

def table(*vv):
    vv=justify(vv)
    return vv

@GetItem
class Row(list):
    def __matmul__(self, f):
        return Row(map(f, self))
    def __mul__(self, f):
        return f(*self)
    def __getattr__(self, attr):
       return self@(getattr(prop, attr))
    def __rtruediv__(self, f):
        if callable(f):
            return reduce(f,self)
        return self@Func(partial(operator.truediv,f))
    def __truediv__(self, f):
        return Row(map(meth.__truediv__(f), self))
    def __rfloordiv__(self, f):
        return Row(redparts(f,self))
    def __str__(self):
        return ' '.join(map(str,self))
    def __repr__(self):
        return ' '.join(map(repr,self))
        return f'{type(self).__name__}({super().__repr__()})'

R=Row

# >>> from table import *
# >>> Row([1,2,3])
# 1 2 3
# >>> Row[1,2,3]
# 1 2 3
# >>> Row[1,]
# 1
# >>> 

class Index:
    def __init__(self, values):
        self.ix = tale(values)
        assert all((x>0 for x in self.values()))
    def value(self, k):
        if isinstance(k, int):
            return self.ix[k]-self.ix[k-1] if k else self.ix[0]
        elif isinstance(k, slice):
            return Index([self[i] for i in range(len(self.ix))[k]])
        else:
            raise TypeError
    def slice(self,i,j):
        a,b=self.lookup(i), self.lookup(j-1)
        iy=self.ix[a:b]
        iy=[] if i==j else [i]+iy+[j]
        return Index([b-a for a,b in pairs(iy)])
    def start(self,k): return self.ix[k-1] if k else 0
    def stop(self,k): return self.ix[k] if k is not None else self.ix[-1]
    def portion(self,k):
        return (self.start(k),self.stop(k))
    def portions(self):
        return [self.portion(k) for k in range(len(self.ix))]
    def lookup(self,k):
        return bisect_right(self.ix,k)
    def values(self):
        return [self.value(i) for i in range(len(self.ix))]
    def __len__(self): return len(self.ix)
    def __repr__(self):
        return f'{type(self).__name__}([{",".join(map(str,self.values()))}])'

def diff(l): return [y-x for x,y in pairs(l)]
def lookup(ix,iy): return Index(diff([0]+[iy.lookup(x) for x in ix.ix]))

class Table:
    def __init__(self, values, levels=None, ixs=None):
        if isinstance(values, Table):
            self.vs=values.vs
            self.ixs=values.ixs
        elif ixs is not None:
            assert levels is None
            self.vs=values
            self.ixs=ixs
        else:
            if all((isinstance(v, Table) for v in values)):
                values=[v.values() for v in values]
            vs=values
            ixs=[]
            level=0
            while (levels is None or level < levels) and all((isinstance(v, list) for v in vs)):
                ixs.append(Index([len(v) for v in vs]))
                vs=sum(vs,[])
                level+=1
            self.vs=vs
            self.ixs=ixs
    def __matmul__(self, f):
        return Table(lmap(f, self.vs),ixs=self.ixs)
    def __add__(self, other):
        return Table(self.values()+Table(other).values())
    def __getitem__(self,k):
        if isinstance(k, int):
            i,j = self.ixs[-1].portion(k)
            ixs=[self.ixs[x].slice(i,j) for x in range(len(self.ixs)-1)]
            return Table(self.vs[i:j], ixs=ixs)
        elif isinstance(k, slice):
            i,j = self.ixs[-1].start(k.start), self.ixs[-1].stop(k.stop)
            ixs=[self.ixs[x].slice(i,j) for x in range(len(self.ixs))]
            return Table(self.vs[i:j], ixs=ixs)
    def __rtruediv__(self, f):
        if self.ixs:
            vs=[reduce(f,self.vs[i:j]) for i,j in self.ixs[0].portions()]
            ixs=[lookup(ix, self.ixs[0]) for ix in self.ixs[1:]]
            return Table(vs,ixs=ixs)
        else:
            reduce(f,self.vs)
    def __iter__(self):
        gs=self.groups()
        if gs is not None:
            yield from gs
    def __call__(self, f):
        def apply(f,*args):
            args = [a if isinstance(a,Table) else itertools.repeat(a) for a in args]
            vs=[f(*x) for x in zip(self.vs,*args)]
            return Table(vs,ixs=self.ixs)
        return functools.partial(apply,f)
    def __len__(self):
        if self.ixs:
            return len(self.ixs[-1])
        else:
            return len(self.vs)
    def size(self):
        return sum(self)
    def groups(self):
        if self.ixs:
            for i,j in self.ixs[-1].portions():
                ixs=[self.ixs[k].slice(i,j) for k in range(0,len(self.ixs)-1)]
                yield Table(self.vs[i:j],ixs=ixs)
        else:
            yield from self.vs
    def values(self):
        if self.ixs:
            return [g.values() for g in self.groups()]
        else:
            return self.vs
    def __str__(self):
        l=len(self.ixs)
        if l==1:
            just=justify(self.values(),'rjust')
            return '\n'.join((f"{' '.join(v)}" for v in just))+'\n'
        elif l>0:
            return '\n'.join((f'{g}' for g in self.groups()))+'\n'
        else:
            return ' '.join(map(str,self.vs))
    def __repr__(self):
        args = map(str,[self.vs,self.ixs])
        return f'{type(self).__name__}({",".join(args)})'


# >>> from table import *
# >>> p=print
# >>> Index([10,20,30])
# Index([10,20,30])
# >>> p(_.values())
# [10, 20, 30]
# >>> p(_.values()[1:])
# [20, 30]
# >>> 
# >>> 
# >>> 
# >>> p([_.lookup(i) for i in range(5,40,5)])
# [0, 1, 1, 1, 1, 2, 2]
# >>> Index([10,10,10,10])
# Index([10,10,10,10])
# >>> p(_.ix)
# [10, 20, 30, 40]
# >>> p(_.slice(11,29))
# Index([9,9])
# >>> p(_.slice(11,30))
# Index([9,10])
# >>> p(_.slice(9,30))
# Index([1,10,10])
# >>> p(_.slice(10,31))
# Index([10,10,1])
# >>> p(_.slice(10,30))
# Index([10,10])
# >>> p(_.slice(0,5))
# Index([5])
# >>> p(_.slice(0,10))
# Index([10])
# >>> p(_.slice(10,20))
# Index([10])
# >>> p(_.slice(10,24))
# Index([10,4])
# >>> p(_.slice(10,10))
# Index([])
# >>> p(_.slice(5,35))
# Index([5,10,10,5])
# >>> 
# >>> 
# >>> 
# >>> Table([1,2,3])
# Table([1, 2, 3],[])
# >>> p(_)
# 1 2 3
# >>> p(list(_.groups()))
# [1, 2, 3]
# >>> 
# >>> Table([list(range(i,i+10)) for i in range(0,100,10)])
# Table([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99],[Index([10,10,10,10,10,10,10,10,10,10])])
# >>> Table(list(range(100)),ixs=[Index([10]*10)])
# Table([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99],[Index([10,10,10,10,10,10,10,10,10,10])])
# >>> 
# >>> p(_)
#  0  1  2  3  4  5  6  7  8  9
# 10 11 12 13 14 15 16 17 18 19
# 20 21 22 23 24 25 26 27 28 29
# 30 31 32 33 34 35 36 37 38 39
# 40 41 42 43 44 45 46 47 48 49
# 50 51 52 53 54 55 56 57 58 59
# 60 61 62 63 64 65 66 67 68 69
# 70 71 72 73 74 75 76 77 78 79
# 80 81 82 83 84 85 86 87 88 89
# 90 91 92 93 94 95 96 97 98 99
# 
# >>> p(_[0])
# 0 1 2 3 4 5 6 7 8 9
# >>> p(_[1])
# 10 11 12 13 14 15 16 17 18 19
# >>> p(_[-1])
# 90 91 92 93 94 95 96 97 98 99
# >>> p(_[1:3])
# 10 11 12 13 14 15 16 17 18 19
# 20 21 22 23 24 25 26 27 28 29
# 30 31 32 33 34 35 36 37 38 39
# 
# >>> p(_[:2])
#  0  1  2  3  4  5  6  7  8  9
# 10 11 12 13 14 15 16 17 18 19
# 20 21 22 23 24 25 26 27 28 29
# 
# >>> p(_[4:])
# 40 41 42 43 44 45 46 47 48 49
# 50 51 52 53 54 55 56 57 58 59
# 60 61 62 63 64 65 66 67 68 69
# 70 71 72 73 74 75 76 77 78 79
# 80 81 82 83 84 85 86 87 88 89
# 90 91 92 93 94 95 96 97 98 99
# 
# >>> p(_[:])
#  0  1  2  3  4  5  6  7  8  9
# 10 11 12 13 14 15 16 17 18 19
# 20 21 22 23 24 25 26 27 28 29
# 30 31 32 33 34 35 36 37 38 39
# 40 41 42 43 44 45 46 47 48 49
# 50 51 52 53 54 55 56 57 58 59
# 60 61 62 63 64 65 66 67 68 69
# 70 71 72 73 74 75 76 77 78 79
# 80 81 82 83 84 85 86 87 88 89
# 90 91 92 93 94 95 96 97 98 99
# 
# >>> 
# >>> p(list(_.groups()))
# [Table([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],[]), Table([10, 11, 12, 13, 14, 15, 16, 17, 18, 19],[]), Table([20, 21, 22, 23, 24, 25, 26, 27, 28, 29],[]), Table([30, 31, 32, 33, 34, 35, 36, 37, 38, 39],[]), Table([40, 41, 42, 43, 44, 45, 46, 47, 48, 49],[]), Table([50, 51, 52, 53, 54, 55, 56, 57, 58, 59],[]), Table([60, 61, 62, 63, 64, 65, 66, 67, 68, 69],[]), Table([70, 71, 72, 73, 74, 75, 76, 77, 78, 79],[]), Table([80, 81, 82, 83, 84, 85, 86, 87, 88, 89],[]), Table([90, 91, 92, 93, 94, 95, 96, 97, 98, 99],[])]
# >>> p(list(map(str,_.groups())))
# ['0 1 2 3 4 5 6 7 8 9', '10 11 12 13 14 15 16 17 18 19', '20 21 22 23 24 25 26 27 28 29', '30 31 32 33 34 35 36 37 38 39', '40 41 42 43 44 45 46 47 48 49', '50 51 52 53 54 55 56 57 58 59', '60 61 62 63 64 65 66 67 68 69', '70 71 72 73 74 75 76 77 78 79', '80 81 82 83 84 85 86 87 88 89', '90 91 92 93 94 95 96 97 98 99']
# >>> 
# >>> p(Table(range(100),ixs=[Index([9]*11+[1])]))
#  0  1  2  3  4  5  6  7  8
#  9 10 11 12 13 14 15 16 17
# 18 19 20 21 22 23 24 25 26
# 27 28 29 30 31 32 33 34 35
# 36 37 38 39 40 41 42 43 44
# 45 46 47 48 49 50 51 52 53
# 54 55 56 57 58 59 60 61 62
# 63 64 65 66 67 68 69 70 71
# 72 73 74 75 76 77 78 79 80
# 81 82 83 84 85 86 87 88 89
# 90 91 92 93 94 95 96 97 98
# 99                        
# 
# >>> t=Table(range(50), ixs=[Index([3,3,3,1]*5),Index([10,20,10,10])])
# >>> t
# Table(range(0, 50),[Index([3,3,3,1,3,3,3,1,3,3,3,1,3,3,3,1,3,3,3,1]), Index([10,20,10,10])])
# >>> p(_.ixs[0])
# Index([3,3,3,1,3,3,3,1,3,3,3,1,3,3,3,1,3,3,3,1])
# >>> p(_.ixs[0].slice(0,10))
# Index([3,3,3,1])
# >>> help(justify)
# Help on function justify in module table:
# 
# justify(vv, align='center')
# 
# >>> Table([Table([1,2,3]),Table([4,5,6])])
# Table([1, 2, 3, 4, 5, 6],[Index([3,3])])
# >>> 
# >>> 
# >>> p(list(_.groups()))
# [Table([1, 2, 3],[]), Table([4, 5, 6],[])]
# >>> 
# >>> p(list(map(str,_.groups())))
# ['1 2 3', '4 5 6']
# >>> p(_)
# 1 2 3
# 4 5 6
# 
# >>> p(_.values())
# [[1, 2, 3], [4, 5, 6]]
# >>> 
# >>> p(t(add)(200))
# <console>:1: NameError: name 'add' is not defined
# >>> t
# Table(range(0, 50),[Index([3,3,3,1,3,3,3,1,3,3,3,1,3,3,3,1,3,3,3,1]), Index([10,20,10,10])])
# >>> add/t
# <console>:1: NameError: name 'add' is not defined
# >>> p(_)
# 0 1 2
# 3 4 5
# 6 7 8
# 9    
# 
# 10 11 12
# 13 14 15
# 16 17 18
# 19      
# 20 21 22
# 23 24 25
# 26 27 28
# 29      
# 
# 30 31 32
# 33 34 35
# 36 37 38
# 39      
# 
# 40 41 42
# 43 44 45
# 46 47 48
# 49      
# 
# 
# >>> from htmldraw import *
# >>> th(table(_.values()))
# '<table><tr><td>range(0, 3)</td><td>range(3, 6)</td><td>range(6, 9)</td><td>range(9, 10)</td></tr><tr><td>range(10, 13)</td><td>range(13, 16)</td><td>range(16, 19)</td><td>range(19, 20)</td><td>range(20, 23)</td><td>range(23, 26)</td><td>range(26, 29)</td><td>range(29, 30)</td></tr><tr><td>range(30, 33)</td><td>range(33, 36)</td><td>range(36, 39)</td><td>range(39, 40)</td></tr><tr><td>range(40, 43)</td><td>range(43, 46)</td><td>range(46, 49)</td><td>range(49, 50)</td></tr></table>'
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> r=Row([1,2,3])
# >>> r
# 1 2 3
# >>> r@functools.partial(operator.add,1)
# 2 3 4
# >>> from parle.sym import E
# >>> dir(E)
# ['__add__', '__and__', '__call__', '__class__', '__contains__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__floordiv__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__invert__', '__le__', '__lshift__', '__lt__', '__matmul__', '__mod__', '__module__', '__mul__', '__ne__', '__neg__', '__new__', '__or__', '__pos__', '__pow__', '__reduce__', '__reduce_ex__', '__repr__', '__rshift__', '__setattr__', '__sizeof__', '__str__', '__sub__', '__subclasshook__', '__truediv__', '__weakref__', '__xor__', 'a1', 'a2', 'args', 'exprs', 'lhs', 'op', 'rhs']
# >>> E(2)
# E(2)
# >>> E(1)+E(r)
# E('+', E(1), E(1 2 3))
# >>> def x(n): return functools.partial(operator.mul,n)
# ... 
# >>> r@x(3)
# 3 6 9
# >>> 
# >>> from parle.func import *
# >>> f=Dict[1:2, 3:4]|K(-1)
# >>> Row([1,2,3,4])@f
# 2 None 4 None
# >>> 
# >>> operator.add/Row([1,2,3,4,5])
# 15
# >>> 1/Row([1,2,3,4,5])
# 1.0 0.5 0.3333333333333333 0.25 0.2
# >>> 
# >>> Func
# <class 'parle.func.Func'>
# >>> callable(Func(operator.add))
# True
# >>> Func(partial(operator.add,1))(2)
# 3
# >>> operator.add/Row(span(10))
# <console>:1: NameError: name 'span' is not defined
# >>> 
# >>> Row[12,]
# 12
# >>> Row[1,2,3,4,5]
# 1 2 3 4 5
# >>> Row([[1,2]])
# [1, 2]
# >>> 
# >>> gi=GetItem(I)
# >>> gi[1:10]
# slice(1, 10, None)
# >>> 
# >>> operator.add//Row[1000,1,2,3,4]
# 1000 1001 1003 1006 1010
# >>> 
# >>> Row[range(10)]@(Dict[2:3,5:7,4:13]|I)
# None None 3 None 13 7 None None None None
# >>> sub=Binop(operator.sub)
# >>> 
# >>> Row([100,200,300])
# 100 200 300
# >>> 
# >>> 10@sub@2
# 8
# >>> 
# >>> unstar(range)
# functools.partial(<function apply at 0xb63661e0>, <class 'range'>)
# >>> _((1,2))
# range(1, 2)
# >>> 
# >>> Row[1,23]
# 1 23
# >>> 
# >>> 
# >>> 
