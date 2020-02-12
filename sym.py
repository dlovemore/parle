class Base:
    def __init__(self, *args):
        self._args = args
    @property
    def args(self): return self._args
    @args.setter
    def args(self, value): self._args = value
    def __repr__(self):
        rargs = repr(list(self.args))[1:-1]
        return f'{type(self).__name__}({rargs})'

class E(Base):
    @property
    def op(self):
        return self.args[0]
    @property
    def exprs(self):
        return self.args[1:]
    @property
    def lhs(self):
        return self.args[1]
    @property
    def rhs(self):
        return self.args[2]
    @property
    def a1(self):
        return self.args[1]
    @property
    def a2(self):
        return self.args[2]
    def __add__(self, rhs):
        return E('+',self,rhs)
    def __contains__(self, lhs):
        return E(' in ',lhs,self)
    def __truediv__(self, rhs):
        return E('/',self,rhs)
    def __floordiv__(self, rhs):
        return E('//',self,rhs)
    def __and__(self, rhs):
        return E('&',self,rhs)
    def __xor__(self, rhs):
        return E('^',self,rhs)
    def __invert__(self):
        return E('~_',self)
    def __or__(self, rhs):
        return E('|',self,rhs)
    def __pow__(self, rhs):
        return E('**',self,rhs)
    def __getitem__(self, k):
        return E('[]',self, k)
    def __lshift__(self, rhs):
        return E('<<',self, rhs)
    def __mod__(self, rhs):
        return E('%',self, rhs)
    def __mul__(self, rhs):
        return E('*',self, rhs)
    def __matmul__(self, rhs):
        return E('@',self, rhs)
    def __neg__(self):
        return E('-_',self)
    def __pos__(self):
        return E('+_',self)
    def __rshift__(self, rhs):
        return E('>>',self, rhs)
    def __sub__(self, rhs):
        return E('-',self, rhs)
    def __lt__(self, rhs):
        return E('<',self, rhs)
    def __le__(self, rhs):
        return E('<=',self, rhs)
    def __eq__(self, rhs):
        return E('==',self, rhs)
    def __ne__(self, rhs):
        return E('!=',self, rhs)
    def __ge__(self, rhs):
        return E('>=',self, rhs)
    def __gt__(self, rhs):
        return E('>',self, rhs)
    def __call__(self, *args):
        return E('_()',self, *args)

def dolet(k,v): return E('=',k,v)

class LetClause(Base):
    def __getitem__(self, k):
        if isinstance(k,tuple):
            k=E(',',*k)
        return E('=',E('args',*self.args), k)

class Let:
    def __setitem__(self,k,v):
        stmts += dolet(k,v)
    def __call__(self,*args):
        return LetClause(*args)
let=Let()

class Stmt:
    def __init__(self,k):
        self.op = k
    def __getitem__(self, k):
        if isinstance(k,tuple):
            k=E(',',*k)
        return E(self.op, k)

# Use like:
#     let(x)[x+1]
# or [let(x)[4], let(Y)[X+1]]

class Env:
    def __init__(self, globals, op='var'):
        self.globals=globals
        self.vars=dict()
        self.op=op
    def __call__(self, name):
        if name not in self.vars:
            v=E(self.op, name)
            self.globals[name]=v
            self.vars[name]=v
        return self.vars[name]
    def __getattr__(self, name):
        return self(name)

var=Env(globals())
v=var
arg=var

class OnClause:
    def __init__(self, e):
        self.e=e
    def __getitem__(self, rhs):
        if isinstance(rhs, slice):
            assert(rhs.step is None)
            return E('?:', self.e, rhs.start, rhs.stop)
        else:
            return E('?', self.e, rhs)

class On:
    def __call__(self, e):
        return OnClause(e)
on=On()
IF=on

class LambdaClause:
    def __init__(self, *args):
        self.args=args
    def __getitem__(self, rhs):
        return E('λ',self.args,rhs)

class LambdaDefiner:
    def __call__(self, *args):
        return LambdaClause(args)
λ=LambdaDefiner()



class Ref:
    def __init__(self, r, uid):
        self.refmaker = r
        self.uid = uid
    def __matmul__(self, rhs):
        if self in self.refmaker.rees:
            raise RuntimeError
        self.refmaker.rees[self]=rhs
        return rhs
    def __repr__(self):
        return f'{self.uid}@R'

class RefMaker:
    def __init__(self):
        self.refs = dict() # uid->ref
        self.rees = dict() # ref->referee
    def __rmatmul__(self, uid):
        "Handles uid@self"
        if uid not in self.refs:
            self.refs[uid] = Ref(self,uid)
        return self.refs[uid]


def save(x):
    seen=set()
    many=set()
    def mr(x):
        if id(x) in seen:
            many.add(id(x))
        else:
            seen.add(id(x))
            if isinstance(x, Base):
                for a in x.args:
                    mr(a)
    mr(x)
    uids=dict() # ref id->ids
    uid=1
    def pr(x):
        nonlocal uid
        s=''
        if id(x) in many:
            if id(x) in uids:
                return f'{uids[id(x)]}@R'
            else:
                uids[id(x)]=uid
                s+=f'{uid}@R@'
                uid+=1
        if isinstance(x, Base):
            first=True
            s+=f'{type(x).__name__}('
            for arg in x.args:
                if first: first=False
                else: s+=','
                s+=pr(arg)
            s+=')'
        else:
            s+=repr(x)
        return s
    return pr(x)

def load(s):
    global R
    R=RefMaker()
    b=eval(s)
    seen=set()
    def resolve(x):
        if id(x) not in seen:
            seen.add(id(x))
            if isinstance(x, Base):
                x.args=[resolve(a) for a in x.args]
        if isinstance(x, Ref):
            return R.rees[x]
        else:
            return x
    resolve(b)
    return b

# >>> from sym import *
# >>> X=var.X
# >>> print(v.Y)
# E('var', 'Y')
# >>> a=[1,2]
# >>> a[0]=3
# >>> a[0]+=3
# >>> E('a','var')[3]
# E('[]', E('a', 'var'), 3)
# >>> a=v.a
# >>> a[0]
# E('[]', E('var', 'a'), 0)
# >>> v.X<v.Y
# E('<', E('var', 'X'), E('var', 'Y'))
# >>> v.X[v.X+1,]
# E('[]', E('var', 'X'), (E('+', E('var', 'X'), 1),))
# >>> 
# >>> globals()['ai']=12
# >>> ai
# 12
# >>> 
# >>> on(X)[3:4]
# E('?:', E('var', 'X'), 3, 4)
# >>> on(X)[3]
# E('?', E('var', 'X'), 3)
# >>> E(E('X','var'),'?',3)
# E(E('X', 'var'), '?', 3)
# >>> var.A
# E('var', 'A')
# >>> A
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# NameError: name 'A' is not defined
# >>> var=Env(globals())
# >>> var.A
# E('var', 'A')
# >>> A
# E('var', 'A')
# >>> E
# <class 'sym.E'>
# >>> 
# >>> [getattr(var,x) for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
# [E('var', 'A'), E('var', 'B'), E('var', 'C'), E('var', 'D'), E('var', 'E'), E('var', 'F'), E('var', 'G'), E('var', 'H'), E('var', 'I'), E('var', 'J'), E('var', 'K'), E('var', 'L'), E('var', 'M'), E('var', 'N'), E('var', 'O'), E('var', 'P'), E('var', 'Q'), E('var', 'R'), E('var', 'S'), E('var', 'T'), E('var', 'U'), E('var', 'V'), E('var', 'W'), E('var', 'X'), E('var', 'Y'), E('var', 'Z')]
# >>> A
# E('var', 'A')
# >>> E
# E('var', 'E')
# >>> import fun
# >>> fun.E
# <class 'parle.sym.E'>
# >>> var.E
# E('var', 'E')
# >>> fun.E
# <class 'parle.sym.E'>
# >>> λ(X)[X+1]
# E('λ', ((E('var', 'X'),),), E('+', E('var', 'X'), 1))
# >>> 
# >>> 
# >>> let(X)
# LetClause(E('var', 'X'))
# >>> let(X)[X+1]
# E('=', E('args', E('var', 'X')), E('+', E('var', 'X'), 1))
# >>> LET=Stmt('let')
# >>> 
# >>> LET(X)
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# TypeError: 'Stmt' object is not callable
# >>> LET[X]
# E('let', E('var', 'X'))
# >>> 
