from itertools import tee, chain

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

def match(t):
    def match(xs):
        nonlocal t
        x,xs = firstrest(xs)
        if x==t:
            yield [x],xs
    return match

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
        for x,xs in p(xs):
            for y,ys in q(xs):
                yield x+y, ys
    return cat

def cut(p):
    def cut(xs):
        nonlocal p
        yield first(p(xs))
    return cut

def group(p):
    def group(xs):
        nonlocal p
        for x,xs in p(xs):
            yield tuple(x),xs
    return group

def node(name,p):
    def node(xs):
        nonlocal name,p
        for x,xs in p(xs):
            yield tuple(chain([name],xs)), xs
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
            yield [None], xs1
            return
        yield from rest(g)
    return maybe

def many(xs):
    pass


# >>> from parse import *
# >>> dir()
# ['__builtins__', '__doc__', '__name__', 'alt', 'cat', 'chain', 'cut', 'first', 'firstrest', 'group', 'many', 'match', 'maybe', 'node', 'rest', 'rule', 'tee']
# >>> it=iter([1,2,3])
# >>> next(it)
# 1
# >>> rest(it)
# <generator object rest at 0xb65d8eb0>
# >>> list(_)
# [2, 3]
# >>> 
# >>> 
# >>> match(1)
# <function match.<locals>.match at 0xb672a7c8>
# >>> m=match(1)
# >>> first(m([1,2,3]))
# ([1], <generator object rest at 0xb64e4530>)
# >>> list(match(2)(_[1]))
# [([2], <generator object rest at 0xb64e44b0>)]
# >>> match(1)([0])
# <generator object match.<locals>.match at 0xb64e44f0>
# >>> list(_)
# []
# >>> tee([1,2,3])
# (<itertools._tee object at 0xb650ba80>, <itertools._tee object at 0xb650ba58>)
# >>> list(_[0]),list(_[1])
# ([1, 2, 3], [1, 2, 3])
# >>> m0or1=alt(match(0), match(1))
# >>> list(m0or1([1,2,3]))
# [([1], <generator object rest at 0xb64e4530>)]
# >>> list(m0or1([2,2,3]))
# []
# >>> list(m0or1([0,2,3]))
# [([0], <generator object rest at 0xb64e44b0>)]
# >>> m12=cat(match(1),match(2))
# >>> list(m12([1,2,3]))
# [([1, 2], <generator object rest at 0xb64e43f0>)]
# >>> list(m12([1,1,3]))
# []
# >>> m123=cat(match(1),cat(match(2),match(3)))
# >>> list(m123([1,2,3]))
# [([1, 2, 3], <generator object rest at 0xb64e42f0>)]
# >>> list(m123([1,2,4]))
# []
# >>> m1q2=cat(maybe(match(1)),match(2))
# >>> list(m1q2([1,2,3]))
# [([1, 2], <generator object rest at 0xb64e4430>)]
# >>> list(m1q2([2,3,1]))
# [([None, 2], <generator object rest at 0xb64e42b0>)]
# >>> list(m1q2([3,2,1]))
# []
# >>> 
# >>> 
# >>> 
