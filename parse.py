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
        s,xs = firstrest(xs)
        if s==t:
            yield [s],xs
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

def many(p):
    def many(xs):
        nonlocal p
        xs, xs1 = tee(xs)
        for s, ys in maybe(p)(xs):
            if s:
                ys, ys1 = tee(ys)
                for ss,zs in many(ys1):
                    yield s+ss,zs
        yield [],xs1
        return xs
    return many

# >>> from parse import *
# >>> dir()
# ['__builtins__', '__doc__', '__name__', 'alt', 'cat', 'chain', 'cut', 'first', 'firstrest', 'group', 'many', 'match', 'maybe', 'node', 'rest', 'rule', 'tee']
# >>> it=iter([1,2,3])
# >>> next(it)
# 1
# >>> rest(it)
# <generator object rest at 0x7efd15f903b8>
# >>> list(_)
# [2, 3]
# >>> 
# >>> 
# >>> match(1)
# <function match.<locals>.match at 0x7efd17e59e18>
# >>> m=match(1)
# >>> first(m([1,2,3]))
# ([1], <generator object rest at 0x7efd15660728>)
# >>> list(match(2)(_[1]))
# [([2], <generator object rest at 0x7efd156607d8>)]
# >>> match(1)([0])
# <generator object match.<locals>.match at 0x7efd15660830>
# >>> list(_)
# []
# >>> tee([1,2,3])
# (<itertools._tee object at 0x7efd1565e048>, <itertools._tee object at 0x7efd1565e088>)
# >>> list(_[0]),list(_[1])
# ([1, 2, 3], [1, 2, 3])
# >>> m0or1=alt(match(0), match(1))
# >>> list(m0or1([1,2,3]))
# [([1], <generator object rest at 0x7efd15660728>)]
# >>> list(m0or1([2,2,3]))
# []
# >>> list(m0or1([0,2,3]))
# [([0], <generator object rest at 0x7efd15660888>)]
# >>> m12=cat(match(1),match(2))
# >>> list(m12([1,2,3]))
# [([1, 2], <generator object rest at 0x7efd156609e8>)]
# >>> list(m12([1,1,3]))
# []
# >>> m123=cat(match(1),cat(match(2),match(3)))
# >>> list(m123([1,2,3]))
# [([1, 2, 3], <generator object rest at 0x7efd15660a98>)]
# >>> list(m123([1,2,4]))
# []
# >>> m1q2=cat(maybe(match(1)),match(2))
# >>> list(m1q2([1,2,3]))
# [([1, 2], <generator object rest at 0x7efd15660938>)]
# >>> list(m1q2([2,3,1]))
# [([2], <generator object rest at 0x7efd156607d8>)]
# >>> list(m1q2([3,2,1]))
# []
# >>> list(many(match(1))([1,2,3]))
# [([1], <itertools._tee object at 0x7efd1565e888>), ([], <itertools._tee object at 0x7efd1565e708>)]
# >>> list(many(match(1))([1,1,2,3]))
# [([1, 1], <itertools._tee object at 0x7efd1565ea48>), ([1], <itertools._tee object at 0x7efd1565e908>), ([], <itertools._tee object at 0x7efd1565e808>)]
# >>> 
# >>> list(cut(many(match(1)))([1,1,1,1,2,3]))
# [([1, 1, 1, 1], <itertools._tee object at 0x7efd1565ed08>)]
# >>> list(cut(many(alt(match(1),match(2))))([1,1,1,1,2,3]))
# [([1, 1, 1, 1, 2], <itertools._tee object at 0x7efd1565ef88>)]
# >>> list(cut(many(alt(match(1),match(2))))([5,1,1,1,1,2,3]))
# [([], <itertools._tee object at 0x7efd1565ebc8>)]
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
