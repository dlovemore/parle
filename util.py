from auto import *
from table import *
from func import *

dr=dir/~meth.startswith('_')*Row
Run=Attr(F(subprocess.run)(...,capture_output=True)*prop.stdout*method.decode)
runp=Attr(Run*p)
sh=Attr(F(subprocess.run)(...,shell=True,capture_output=True)*prop.stdout*method.decode*p)

@Func
@aslist
def bits(b):
    while b:
        n=b&-b
        yield n
        b-=n

pi=math.pi
exp=Func(math.exp)
ln=Func(math.log)
log=Func(math.log)
log2=Func(math.log2)
log10=Func(math.log10)
bp=log2*int
bps=bits@bp

def frac(x):
    a=1
    b=0





# >>> from parle import *
# >>> bps(10)
# [1, 3]
# >>> 
# >>> 
# >>> dr()
# 'args' 'f' 'g' 'kwargs'
# >>> dr(partial)
# 'f'
# >>> dr(Row)
# 'f'
# >>> dr(itertools)
# 'accumulate' 'chain' 'combinations' 'combinations_with_replacement' 'compress' 'count' 'cycle' 'dropwhile' 'filterfalse' 'groupby' 'islice' 'permutations' 'product' 'repeat' 'starmap' 'takewhile' 'tee' 'zip_longest'
# >>> Run.ls
# 'data.py\nfiles.py\nfunc.py\nhtmldraw.py\n__init__.py\n__init__.pyc\nlift.py\nmint.py\nparse.py\nprimes.py\n__pycache__\nsave.py\nsym.py\nt\ntable.py\nt.html\ntmpout\nu\nutil.py\n'
# >>> sh.ls
# data.py
# files.py
# func.py
# htmldraw.py
# __init__.py
# __init__.pyc
# lift.py
# mint.py
# parse.py
# primes.py
# __pycache__
# save.py
# sym.py
# t
# table.py
# t.html
# tmpout
# u
# util.py
# 
# >>> 
# >>> sh('ls -l')
# total 144
# -rw-r--r-- 1 pi pi 16109 Jan 20 22:06 data.py
# -rw-r--r-- 1 pi pi  4475 Apr 13 15:35 files.py
# -rw-r--r-- 1 pi pi 22006 May  6 06:44 func.py
# -rw-r--r-- 1 pi pi  5250 Apr 28 18:55 htmldraw.py
# -rw-r--r-- 1 pi pi   276 May  4 16:49 __init__.py
# -rw-r--r-- 1 pi pi   489 Apr 29 22:51 __init__.pyc
# -rw-r--r-- 1 pi pi  2738 Apr 28 09:43 lift.py
# -rw-r--r-- 1 pi pi  4243 Apr 28 09:43 mint.py
# -rw-r--r-- 1 pi pi  7339 Apr  1 16:48 parse.py
# -rw-r--r-- 1 pi pi  7513 May  4 16:57 primes.py
# drwxr-xr-x 2 pi pi  4096 May  6 08:10 __pycache__
# -rw-r--r-- 1 pi pi  4076 Feb 12 09:10 save.py
# -rw-r--r-- 1 pi pi  7418 Apr 28 09:32 sym.py
# -rw-r--r-- 1 pi pi    38 Apr 13 15:35 t
# -rw-r--r-- 1 pi pi 14847 Apr 29 18:38 table.py
# -rw-r--r-- 1 pi pi  1529 Apr 28 18:53 t.html
# -rw-r--r-- 1 pi pi    31 Apr 13 15:35 u
# -rw-r--r-- 1 pi pi  5001 May  6 08:10 util.py
# 
# >>> 
# >>> 
# >>> 
