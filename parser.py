from itertools import tee

def rest(it):
    try:
        while True:
            yield next(it)
    except StopIteration:
        pass

def firstrest(xs):
    it=iter(xs)
    x=next(it)
    y = rest(it)
    return x, y

def first(xs): return firstrest(xs)[0]
def rest(xs): return firstrest(xs)[1]

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




# >>> from parser import *
# >>> dir()
# ['__builtins__', '__doc__', '__name__', 'alt', 'first', 'firstrest', 'match', 'rest', 'tee']
# >>> it=iter([1,2,3])
# >>> next(it)
# 1
# >>> rest(it)
# <console>:1: 
#     tee=<built-in function tee>
#     rest=<function rest at 0x7f80f48466a8>
#     firstrest=<function firstrest at 0x7f80f4846598>
#     first=<function first at 0x7f80f4846620>
#     match=<function match at 0x7f80f4846510>
#     alt=<function alt at 0x7f80f4846730>
#     it=<list_iterator object at 0x7f80f48409e8>
# /home/dl/github.com/dlovemore/parle/parser.py:17: 
#     xs=<list_iterator object at 0x7f80f48409e8>
# /home/dl/github.com/dlovemore/parle/parser.py:13: 
#     x=2
#     it=<list_iterator object at 0x7f80f48409e8>
#     xs=<list_iterator object at 0x7f80f48409e8>
# /home/dl/github.com/dlovemore/parle/parser.py:17: 
#     xs=<list_iterator object at 0x7f80f48409e8>
# /home/dl/github.com/dlovemore/parle/parser.py:13: 
#     x=3
#     it=<list_iterator object at 0x7f80f48409e8>
#     xs=<list_iterator object at 0x7f80f48409e8>
# /home/dl/github.com/dlovemore/parle/parser.py:17: 
#     xs=<list_iterator object at 0x7f80f48409e8>
# /home/dl/github.com/dlovemore/parle/parser.py:12: 
#     it=<list_iterator object at 0x7f80f48409e8>
#     xs=<list_iterator object at 0x7f80f48409e8>
# >>> next(it)
# <console>:1: 
#     tee=<built-in function tee>
#     rest=<function rest at 0x7f80f48466a8>
#     firstrest=<function firstrest at 0x7f80f4846598>
#     first=<function first at 0x7f80f4846620>
#     match=<function match at 0x7f80f4846510>
#     alt=<function alt at 0x7f80f4846730>
#     it=<list_iterator object at 0x7f80f48409e8>
# >>> 
# >>> 
# >>> 
# >>> 
# >>> match(1)
# <function match.<locals>.match at 0x7f51e9774e18>
# >>> m=match(1)
# >>> m([1,2,3])
# <generator object match.<locals>.match at 0x7f51e7893620>
# >>> list(_)
# []
# >>> 
