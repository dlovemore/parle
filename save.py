from parle.sym import *

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

# >>> from save import *
# >>> # save/load
# >>> 
# >>> R=RefMaker()
# >>> 1@R
# 1@R
# >>> 1@R
# 1@R
# >>> 1@R@37
# 37
# >>> 1@R
# 1@R
# >>> 2@R==2@R
# True
# >>> 2@R==1@R
# False
# >>> [1]==[1]
# True
# >>> [1,2]==[1,2]
# True
# >>> [1,2] is [1,2]
# False
# >>> 1@R is 1@R
# True
# >>> {[1],[1]}
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# TypeError: unhashable type: 'list'
# >>> {1@R,2@R}
# {1@R, 2@R}
# >>> 
# >>> [].__hash__
# >>> [].__hash__ is None
# True
# >>> if ('').__hash__: print('hashable')
# ... 
# hashable
# >>> ([],).__hash__
# <method-wrapper '__hash__' of tuple object at 0xb654b530>
# >>> hash(([],))
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# TypeError: unhashable type: 'list'
# >>> id([])
# 3059102264
# >>> id(4)
# 4407748
# >>> id(4)
# 4407748
# >>> id(5)
# 4407764
# >>> id(5)==id(5)
# True
# >>> x=5
# >>> y=5
# >>> x=y=100000000000000
# >>> x=100000000000000
# >>> id(x)==id(y)
# False
# >>> save(0)
# '0'
# >>> save([])
# '[]'
# >>> save({1,2,3})
# '{1, 2, 3}'
# >>> save(v.x+1)
# "E('+',E('var','x'),1)"
# >>> a=v.X<7
# >>> a
# E('<', E('var', 'X'), 7)
# >>> save(a)
# "E('<',E('var','X'),7)"
# >>> load(save(a))
# E('<', E('var', 'X'), 7)
# >>> a
# E('<', E('var', 'X'), 7)
# >>> a.args
# ('<', E('var', 'X'), 7)
# >>> a
# E('<', E('var', 'X'), 7)
# >>> save(a)
# "E('<',E('var','X'),7)"
# >>> eval(save(a))
# E('<', E('var', 'X'), 7)
# >>> E=fun.E
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# NameError: name 'fun' is not defined
# >>> 
# >>> a.args
# ('<', E('var', 'X'), 7)
# >>> a.args+=(a,)
# >>> 
# >>> save(a)
# "1@R@E('<',E('var','X'),7,1@R)"
# >>> saveda=save(a)
# >>> saveda
# "1@R@E('<',E('var','X'),7,1@R)"
# >>> R=RefMaker()
# >>> eval(saveda)
# E('<', E('var', 'X'), 7, 1@R)
# >>> save(load(saveda))
# "1@R@E('<',E('var','X'),7,1@R)"
# >>> save(load(saveda))==saveda
# True
# >>> x=var.x
# >>> y=var.y
# >>> x
# E('var', 'x')
# >>> 
# >>> x+y
# E('+', E('var', 'x'), E('var', 'y'))
# >>> x.args+=(y,)
# >>> y.args+=(x,)
# >>> save(x+y)
# "E('+',1@R@E(2@R@'var','x',3@R@E(2@R,'y',1@R)),3@R)"
# >>> save(load(save(x+y)))
# "E('+',1@R@E(2@R@'var','x',3@R@E(2@R,'y',1@R)),3@R)"
# >>> 
