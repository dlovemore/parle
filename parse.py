from itertools import tee, chain
from functools import reduce

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

def match(t):
    def eq(xs):
        nonlocal t
        s,xs = firstrest(xs)
        if s==t:
            yield [s],xs
    return eq

def matches(ts):
    return cats(map(match,ts))

def alt(p,q):
    def alt(xs):
        nonlocal p,q
        xs, xs1 = tee(xs)
        yield from p(xs)
        yield from q(xs1)
    return alt

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
            yield first(g)
        except StopIteration:
            yield [], xs1
            return
        yield from rest(g)
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
        return xs
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

def many(p): return cat(p,anytimes(p))

def either(ts): return reduce(alt, map(match,ts))

def cats(ps): return reduce(cat,ps)

def pone(g): return a(map(first,g))
def pall(g): return list(map(first,g))

# >>> from parse import *
# >>> dir()
# ['__builtins__', '__doc__', '__name__', 'alt', 'anytimes', 'cat', 'cats', 'chain', 'cut', 'either', 'first', 'firstrest', 'group', 'many', 'match', 'matches', 'maybe', 'mintimes', 'node', 'reduce', 'rest', 'rule', 'tee']
# >>> it=iter([1,2,3])
# >>> next(it)
# 1
# >>> rest(it)
# <generator object rest at 0x7fac2b2e0728>
# >>> list(_)
# [2, 3]
# >>> 
# >>> 
# >>> match(1)
# <function match.<locals>.eq at 0x7fac2dad9e18>
# >>> m=match(1)
# >>> first(m([1,2,3]))
# ([1], <generator object rest at 0x7fac2b2e07d8>)
# >>> list(match(2)(_[1]))
# [([2], <generator object rest at 0x7fac2b2e0888>)]
# >>> match(1)([0])
# <generator object match.<locals>.eq at 0x7fac2b2e08e0>
# >>> list(_)
# []
# >>> tee([1,2,3])
# (<itertools._tee object at 0x7fac2b2e3888>, <itertools._tee object at 0x7fac2b2e37c8>)
# >>> list(_[0]),list(_[1])
# ([1, 2, 3], [1, 2, 3])
# >>> m0or1=alt(match(0), match(1))
# >>> list(m0or1([1,2,3]))
# [([1], <generator object rest at 0x7fac2b2e07d8>)]
# >>> list(m0or1([2,2,3]))
# []
# >>> list(m0or1([0,2,3]))
# [([0], <generator object rest at 0x7fac2b2e0938>)]
# >>> m12=cat(match(1),match(2))
# >>> list(m12([1,2,3]))
# [([1, 2], <generator object rest at 0x7fac2b2e0a98>)]
# >>> list(m12([1,1,3]))
# []
# >>> m123=cat(match(1),cat(match(2),match(3)))
# >>> list(m123([1,2,3]))
# [([1, 2, 3], <generator object rest at 0x7fac2b2e0b48>)]
# >>> list(m123([1,2,4]))
# []
# >>> m1q2=cat(maybe(match(1)),match(2))
# >>> list(m1q2([1,2,3]))
# [([1, 2], <generator object rest at 0x7fac2b2e09e8>)]
# >>> list(m1q2([2,3,1]))
# [([2], <generator object rest at 0x7fac2b2e0888>)]
# >>> list(m1q2([3,2,1]))
# []
# >>> list(anytimes(match(1))([1,2,3]))
# [([1], <itertools._tee object at 0x7fac2b2e3f08>), ([], <itertools._tee object at 0x7fac2b2e3e88>)]
# >>> list(anytimes(match(1))([1,1,2,3]))
# [([1, 1], <itertools._tee object at 0x7fac2b2ed148>), ([1], <itertools._tee object at 0x7fac2b2ed048>), ([], <itertools._tee object at 0x7fac2b2e3d88>)]
# >>> 
# >>> list(cut(anytimes(match(1)))([1,1,1,1,2,3]))
# [([1, 1, 1, 1], <itertools._tee object at 0x7fac2b2ed408>)]
# >>> list(cut(anytimes(alt(match(1),match(2))))([1,1,1,1,2,3]))
# [([1, 1, 1, 1, 2], <itertools._tee object at 0x7fac2b2ed648>)]
# >>> list(cut(anytimes(alt(match(1),match(2))))([5,1,1,1,1,2,3]))
# [([], <itertools._tee object at 0x7fac2b2e3fc8>)]
# >>> 
# >>> list(either('abc')('a'))
# [(['a'], <generator object rest at 0x7fac2b2e0e60>)]
# >>> list(either('abc')('c'))
# [(['c'], <generator object rest at 0x7fac2b2e0938>)]
# >>> list(either('abc')('d'))
# []
# >>> list(anytimes(either('abc'))('ababcdab'))
# [(['a', 'b', 'a', 'b', 'c'], <itertools._tee object at 0x7fac2b2ed6c8>), (['a', 'b', 'a', 'b'], <itertools._tee object at 0x7fac2b2ed588>), (['a', 'b', 'a'], <itertools._tee object at 0x7fac2b2ed408>), (['a', 'b'], <itertools._tee object at 0x7fac2b2ed288>), (['a'], <itertools._tee object at 0x7fac2b2ed108>), ([], <itertools._tee object at 0x7fac2b2e39c8>)]
# >>> first(anytimes(either('abc'))('ababcdab'))
# (['a', 'b', 'a', 'b', 'c'], <itertools._tee object at 0x7fac2b2ed988>)
# >>> first(many(either('abc'))('ababcdab'))
# (['a', 'b', 'a', 'b', 'c'], <itertools._tee object at 0x7fac2b2ed548>)
# >>> 
# >>> list(many(either('abc'))('dababcdab'))
# []
# >>> first(anytimes(either('abc'))('dababcdab'))
# ([], <itertools._tee object at 0x7fac2b2e3f88>)
# >>> 
# >>> list(cats([m0or1,match(1),m0or1])([1,0,1]))
# []
# >>> list(cats([m0or1,match(1),m0or1])([0,1,1]))
# [([0, 1, 1], <generator object rest at 0x7fac2b2ee1a8>)]
# >>> list(mintimes(m0or1)([0,1,1,0,2]))
# [([], <itertools._tee object at 0x7fac2b2e3d88>), ([0], <itertools._tee object at 0x7fac2b2ed0c8>), ([0, 1], <itertools._tee object at 0x7fac2b2ed188>), ([0, 1, 1], <itertools._tee object at 0x7fac2b2ed248>), ([0, 1, 1, 0], <itertools._tee object at 0x7fac2b2ed308>)]
# >>> first(cat(mintimes(m0or1),match(2))([0,1,2,1]))
# ([0, 1, 2], <generator object rest at 0x7fac2b2ee360>)
# >>> first(cat(mintimes(m0or1),match(1))([0,1,2,1]))
# ([0, 1], <generator object rest at 0x7fac2b2ee0a0>)
# >>> 
# >>> 
