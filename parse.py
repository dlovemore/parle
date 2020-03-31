from itertools import tee, chain
from functools import reduce, partial
import operator

def rest(it):
    try:
        while True:
            yield next(it)
    except StopIteration:
        pass

def firstrest(xs):
    it=iter(xs)
    return next(it), rest(it)

def first(xs):
    return next(iter(xs))

def a(g):
    try:
        return first(g)
    except StopIteration:
        pass

def empty(xs):
    yield [],xs


def check(f):
    def check(xs):
        nonlocal f
        try:
            s,xs = firstrest(xs)
        except StopIteration:
            return
        if f(s):
            yield [s],xs
    return check

def const(k):
    def const(k,x):
        return k
    return const

def match(t): return check(partial(operator.eq, t))

def matches(ts): return cats(map(match,ts))

def star(f):
    def fn(*l):
        nonlocal f
        return f(l)
    return fn

def reduction(f): return star(partial(reduce,f))

@reduction
def alt(p,q):
    def alt(xs):
        nonlocal p,q
        xs, xs1 = tee(xs)
        yield from p(xs)
        yield from q(xs1)
    return alt

@reduction
def cat(p,q):
    def cat(xs):
        nonlocal p,q
        for s,xs in p(xs):
            for t,ys in q(xs):
                yield s+t, ys
    return cat

def cut(p):
    def cut(xs):
        nonlocal p
        yield first(p(xs))
    return cut

def group(p):
    def group(xs):
        nonlocal p
        for s,xs in p(xs):
            yield tuple(s),xs
    return group

def node(name,p):
    def node(xs):
        nonlocal name,p
        for s,xs in p(xs):
            yield tuple(chain([name],s)), xs
    return node

def rule(G,name):
    def rule(xs):
        nonlocal G, name
        return getattr(G, name)(xs)
    return rule

def maybe(p):
    def maybe(xs):
        nonlocal p
        xs, xs1 = tee(xs)
        g=p(xs)
        try:
            r,rs = firstrest(g)
            yield r
            yield from rs
        except StopIteration:
            yield [], xs1
            return
    return maybe

def anytimes(p):
    def anytimes(xs):
        nonlocal p
        xs, xs1 = tee(xs)
        for s, ys in maybe(p)(xs):
            if s:
                ys, ys1 = tee(ys)
                for ss,zs in anytimes(ys1):
                    yield s+ss,zs
        yield [],xs1
        return
    return anytimes

def mintimes(p):
    def mintimes(xs):
        nonlocal p
        xs, xs1 = tee(xs)
        yield [], xs1
        for s,xs in p(xs):
            for t,ys in mintimes(xs):
                yield s+t, ys
    return mintimes

def manysep(p,sep): return cat(p,anytimes(cat(sep,p)))

def anysep(p,sep): return alt(manysep(p,sep),empty)

def manysepfq(p,sep): return cat(cat(p,anytimes(sep,p)),maybe(sep))

def anysepfq(p,sep): return alt(manysepfq(p,sep),maybe(sep))

def many(p): return cat(p,anytimes(p))

matchany=check(const(True))

def either(ts): return alt(*map(match,ts))

def cats(ps): return cat(*ps)

def pone(g): return a(map(first,g))
def pall(g): return list(map(first,g))

# >>> from parse import *
# >>> dir()
# ['__builtins__', '__doc__', '__name__', 'a', 'alt', 'anytimes', 'cat', 'cats', 'chain', 'check', 'const', 'cut', 'either', 'first', 'firstrest', 'group', 'many', 'match', 'matchany', 'matches', 'maybe', 'mintimes', 'node', 'operator', 'pall', 'partial', 'pone', 'reduce', 'reduction', 'rest', 'rule', 'star', 'tee']
# >>> it=iter([1,2,3])
# >>> next(it)
# 1
# >>> rest(it)
# <generator object rest at 0xb65919b0>
# >>> list(_)
# [2, 3]
# >>> 
# >>> 
# >>> match(1)
# <function check.<locals>.check at 0xb6599228>
# >>> m=match(1)
# >>> first(m([1,2,3]))
# ([1], <generator object rest at 0xb6591930>)
# >>> list(match(2)(_[1]))
# [([2], <generator object rest at 0xb65918b0>)]
# >>> match(1)([0])
# <generator object check.<locals>.check at 0xb65918f0>
# >>> list(_)
# []
# >>> tee([1,2,3])
# (<itertools._tee object at 0xb65b7328>, <itertools._tee object at 0xb65bbe40>)
# >>> list(_[0]),list(_[1])
# ([1, 2, 3], [1, 2, 3])
# >>> m0or1=alt(match(0), match(1))
# >>> list(m0or1([1,2,3]))
# [([1], <generator object rest at 0xb6591930>)]
# >>> list(m0or1([2,2,3]))
# []
# >>> list(m0or1([0,2,3]))
# [([0], <generator object rest at 0xb65918b0>)]
# >>> m12=cat(match(1),match(2))
# >>> list(m12([1,2,3]))
# [([1, 2], <generator object rest at 0xb6577370>)]
# >>> list(m12([1,1,3]))
# []
# >>> m123=cat(match(1),cat(match(2),match(3)))
# >>> list(m123([1,2,3]))
# [([1, 2, 3], <generator object rest at 0xb65776b0>)]
# >>> list(m123([1,2,4]))
# []
# >>> m1q2=cat(maybe(match(1)),match(2))
# >>> list(m1q2([1,2,3]))
# [([1, 2], <generator object rest at 0xb6577670>)]
# >>> list(m1q2([2,3,1]))
# [([2], <generator object rest at 0xb6577770>)]
# >>> list(m1q2([3,2,1]))
# []
# >>> list(anytimes(match(1))([1,2,3]))
# [([1], <itertools._tee object at 0xb65a1c88>), ([], <itertools._tee object at 0xb65a1bc0>)]
# >>> list(anytimes(match(1))([1,1,2,3]))
# [([1, 1], <itertools._tee object at 0xb65a1da0>), ([1], <itertools._tee object at 0xb65a1d00>), ([], <itertools._tee object at 0xb65a1c60>)]
# >>> 
# >>> list(cut(anytimes(match(1)))([1,1,1,1,2,3]))
# [([1, 1, 1, 1], <itertools._tee object at 0xb65a1f58>)]
# >>> list(cut(anytimes(alt(match(1),match(2))))([1,1,1,1,2,3]))
# [([1, 1, 1, 1, 2], <itertools._tee object at 0xb652a0f8>)]
# >>> list(cut(anytimes(alt(match(1),match(2))))([5,1,1,1,1,2,3]))
# [([], <itertools._tee object at 0xb65a1be8>)]
# >>> 
# >>> list(either('abc')('a'))
# [(['a'], <generator object rest at 0xb65775b0>)]
# >>> list(either('abc')('c'))
# [(['c'], <generator object rest at 0xb65772b0>)]
# >>> list(either('abc')('d'))
# []
# >>> list(anytimes(either('abc'))('ababcdab'))
# [(['a', 'b', 'a', 'b', 'c'], <itertools._tee object at 0xb652b0a8>), (['a', 'b', 'a', 'b'], <itertools._tee object at 0xb65a1f08>), (['a', 'b', 'a'], <itertools._tee object at 0xb65a1fa8>), (['a', 'b'], <itertools._tee object at 0xb65a1c88>), (['a'], <itertools._tee object at 0xb65a1d00>), ([], <itertools._tee object at 0xb65a1be8>)]
# >>> first(anytimes(either('abc'))('ababcdab'))
# (['a', 'b', 'a', 'b', 'c'], <itertools._tee object at 0xb652b260>)
# >>> first(many(either('abc'))('ababcdab'))
# (['a', 'b', 'a', 'b', 'c'], <itertools._tee object at 0xb652b2d8>)
# >>> 
# >>> list(many(either('abc'))('dababcdab'))
# []
# >>> first(anytimes(either('abc'))('dababcdab'))
# ([], <itertools._tee object at 0xb65a1c38>)
# >>> 
# >>> reduction(operator.add)
# <function star.<locals>.fn at 0xb65a6e88>
# >>> _(1,2,3)
# 6
# >>> 
# >>> list(cat(m0or1,match(1),m0or1)([1,0,1]))
# []
# >>> list(cat(m0or1,match(1),m0or1)([0,1,1]))
# [([0, 1, 1], <generator object rest at 0xb6577ab0>)]
# >>> list(mintimes(m0or1)([0,1,1,0,2]))
# [([], <itertools._tee object at 0xb656be18>), ([0], <itertools._tee object at 0xb656bda0>), ([0, 1], <itertools._tee object at 0xb656bdf0>), ([0, 1, 1], <itertools._tee object at 0xb656bc60>), ([0, 1, 1, 0], <itertools._tee object at 0xb656bf08>)]
# >>> first(cat(mintimes(m0or1),match(2))([0,1,2,1]))
# ([0, 1, 2], <generator object rest at 0xb65410b0>)
# >>> first(cat(mintimes(m0or1),match(1))([0,1,2,1]))
# ([0, 1], <generator object rest at 0xb6541bf0>)
# >>> 
# >>> pall(maybe(match('x'))(''))
# [[]]
# >>> pall(anytimes(match('x'))('xxx'))
# [['x', 'x', 'x'], ['x', 'x'], ['x'], []]
# >>> pall(many(match('x'))('xxx'))
# [['x', 'x', 'x'], ['x', 'x'], ['x']]
# >>> 
