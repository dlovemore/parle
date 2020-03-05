from itertools import tee

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
        x, xs = firstrest(xs)
        if x==t:
            yield x, xs
    return match

def alt(p,q):
    def alt(xs):
        pass

def f():
    yield 1
    yield 2


# >>> from parse import *
# >>> dir()
# ['__builtins__', '__doc__', '__name__', 'alt', 'f', 'first', 'firstrest', 'match', 'rest', 'tee']
# >>> it=iter([1,2,3])
# >>> next(it)
# 1
# >>> rest(it)
# <generator object rest at 0x7fb14ef3d780>
# >>> list(_)
# [2, 3]
# >>> 
# >>> 
# >>> match(1)
# <function match.<locals>.match at 0x7fb14e5cc7b8>
# >>> m=match(1)
# >>> first(m([1,2,3]))
# (1, <generator object rest at 0x7fb14e5c6678>)
# >>> list(match(2)(_[1]))
# [(2, <generator object rest at 0x7fb14e5c6780>)]
# >>> 
