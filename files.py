from func import *
from table import *
from pathlib import Path
import os
import re

def ensurenl(s):
    return s if s[-1] in '\r\n' else s+'\n'

class File:
    def __init__(self, name):
        self.path=Path(name)
    def __getitem__(self, s):
        f=File(self.path/s)
    def glob(self, pat):
        return Row(map(File,self.path.glob(pat)))
    def __getitem__(self, other):
        return Path(self.path/other)
    def __truediv__(self, other):
        return Path(self.path/other)
    @property
    def s(self):
        return Selector(self)
    @property
    def text(self):
        return self.path.read_text()
    @text.setter
    def text(self, value):
        self.path.write_text(value)
    @property
    def rawlines(self):
        with open(self.path) as f:
            return f.readlines()
    @property
    def lines(self):
        with open(self.path) as f:
            return lmap(meth.rstrip('\n'),f.readlines())
    @lines.setter
    def lines(self, ls):
        ls=[ensurenl(l) for l in ls]
        self.text=''.join(ls)
    def __str__(self):
        return self.path.name
    def __repr__(self):
        return f'{type(self).__name__}({str(self.path)!r})'

def HOME():
    return File(os.getenv('HOME'))
def cwd():
    return File(Path.cwd())
def glob(pat): return cwd().glob(pat)

class Selector:
    def __init__(self, base):
        self.base=base
    def __truediv__(self, pat):
        return FileSel(self.base,pat)

def sub(pat, replace, phile, flags=re.MULTILINE):
    phile.text = re.sub(pat, replace, phile.text, flags)
    return phile

def s(pat, replace, flags=re.MULTILINE): return partial(sub, pat, replace)

class FileSel:
    def __init__(self, base, pat):
        self.base=base
        self.pat=pat
    def __truediv__(self, other):
        sub(self.pat, other, self.base)
        return self.base
    def __repr__(self):
        return str(self.base)+':'+'\n'.join([mo[0] for mo in re.finditer(self.pat, self.base.text, flags=re.MULTILINE)])

# >>> from files import *
# >>> f=File('t')
# >>> f.text='Good day.\n'
# >>> f.text+='Another day\n'
# >>> f.text
# 'Good day.\nAnother day\n'
# >>> f.lines
# ['Good day.', 'Another day']
# >>> print(s('day','Day')(f))
# t
# >>> File('u').text = 'A very good time was had by all'
# >>> p=print
# >>> cwd().glob('?')
# u t
# >>> p(_)
# u t
# >>> _@s(r'[gG]ood','GOOD')
# u t
# >>> _@prop.text
# A very GOOD time was had by all GOOD Day.
# Another Day
# 
# >>> glob('?')@prop.s
# <files.Selector object at 0xb64c7f90> <files.Selector object at 0xb64c7f10>
# >>> _/'GOOD'
# u:GOOD t:GOOD
# >>> _/'good'
# u t
# >>> _@s('^g','G')
# u t
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> f.text
# 'Good Day.\nAnother Day\n'
# >>> Path('path/file.ext').name
# 'file.ext'
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> f.s
# <files.Selector object at 0xb64c7fb0>
# >>> f.s
# <files.Selector object at 0xb63c5110>
# >>> f.s/'Good'/'Very good'
# File('t')
# >>> f.lines+=['The time','ends']
# >>> l=f.lines
# >>> l[2:3]=['1','2','3']
# >>> l
# ['Very good Day.', 'Another Day', '1', '2', '3', 'ends']
# >>> f.lines=l
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> f.lines
# ['Very good Day.', 'Another Day', '1', '2', '3', 'ends']
# >>> 
# >>> f.text
# 'Very good Day.\nAnother Day\n1\n2\n3\nends\n'
# >>> f.s/r'^.*other day\nThe.*$'
# t:
# >>> 
# >>> 
# >>> HOME().path
# PosixPath('/home/pi')
# >>> (HOME()/'github.com').glob('*')
# <generator object Path.glob at 0xb6493c70>
# >>> list(_)
# [PosixPath('/home/pi/github.com/dlovemore')]
# >>> 
# >>> Path.glob
# <function Path.glob at 0xb63be078>
# >>> import auto
# >>> auto.os.listdir()
# ['__init__.py', '.git', 'fun.py', 't.html', 'funtest.py', 'save.py', 'func.py', 'htmldraw.py', '.gitignore', 'table.py', 'mint.py', 'primes.py', 'data.py', '__pycache__', 'files.py', 'u', '.files.py.swp', 't', 'sym.py', 'parse.py']
# >>> Path.cwd()
# PosixPath('/home/pi/python/parle')
# >>> cwd()
# File('/home/pi/python/parle')
# >>> prop.text(f)
# 'Very good Day.\nAnother Day\n1\n2\n3\nends\n'
# >>> text=Func(prop.text)|K('')
# >>> text(cwd())
# ''
# >>> text(f)
# 'Very good Day.\nAnother Day\n1\n2\n3\nends\n'
# >>> cwd().glob('*')
# __init__.py .git fun.py t.html funtest.py save.py func.py htmldraw.py .gitignore table.py mint.py primes.py data.py __pycache__ files.py u .files.py.swp t sym.py parse.py
# >>> 
# >>> 
# >>> _@text@len
# 248 0 1145 1435 818 4076 9464 3326 27 14600 4346 7535 16109 0 4475 31 0 38 7414 7339
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
