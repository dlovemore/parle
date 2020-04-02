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
    def lines(self):
        with open(self.path) as f:
            return f.readlines()
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
# ['Good day.\n', 'Another day\n']
# >>> print(s('day','Day')(f))
# t
# >>> File('u').text = 'A very good time was had by all'
# >>> p=print
# >>> cwd().glob('?')
# Row([File('/home/pi/python/parle/u'), File('/home/pi/python/parle/t')])
# >>> p(_)
# u t
# >>> _@s(r'[gG]ood','GOOD')
# Row([File('/home/pi/python/parle/u'), File('/home/pi/python/parle/t')])
# >>> _@prop.text
# Row(['A very GOOD time was had by all', 'GOOD Day.\nAnother Day\n'])
# >>> glob('?')@prop.s
# Row([<files.Selector object at 0xb6473f30>, <files.Selector object at 0xb6473eb0>])
# >>> _/'GOOD'
# Row([u:GOOD, t:GOOD])
# >>> _/'good'
# Row([File('/home/pi/python/parle/u'), File('/home/pi/python/parle/t')])
# >>> _@s('^g','G')
# Row([File('/home/pi/python/parle/u'), File('/home/pi/python/parle/t')])
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
# <files.Selector object at 0xb6473fd0>
# >>> f.s
# <files.Selector object at 0xb6473f50>
# >>> f.s/'Good'/'Very good'
# File('t')
# >>> f.lines+=['The time','ends']
# >>> f.text
# 'Very good Day.\nAnother Day\nThe time\nends\n'
# >>> f.s/r'^.*other day\nThe.*$'
# t:
# >>> 
# >>> 
# >>> HOME().path
# PosixPath('/home/pi')
# >>> (HOME()/'github.com').glob('*')
# <generator object Path.glob at 0xb643fbf0>
# >>> list(_)
# [PosixPath('/home/pi/github.com/dlovemore')]
# >>> 
# >>> Path.glob
# <function Path.glob at 0xb6367f60>
# >>> import auto
# >>> auto.os.listdir()
# ['__init__.py', '.git', 'fun.py', 't.html', 'funtest.py', 'save.py', 'func.py', 'htmldraw.py', '.gitignore', 'table.py', 'mint.py', 'primes.py', 'data.py', '__pycache__', 'files.py', 'u', '.files.py.swp', 't', 'sym.py', 'parse.py']
# >>> Path.cwd()
# PosixPath('/home/pi/python/parle')
# >>> cwd()
# File('/home/pi/python/parle')
# >>> prop.text(f)
# 'Very good Day.\nAnother Day\nThe time\nends\n'
# >>> text=Func(prop.text)|K('')
# >>> text(cwd())
# ''
# >>> text(f)
# 'Very good Day.\nAnother Day\nThe time\nends\n'
# >>> cwd().glob('*')
# Row([File('/home/dl/github.com/dlovemore/parle/.gitignore'), File('/home/dl/github.com/dlovemore/parle/.git'), File('/home/dl/github.com/dlovemore/parle/htmldraw.py'), File('/home/dl/github.com/dlovemore/parle/u'), File('/home/dl/github.com/dlovemore/parle/__pycache__'), File('/home/dl/github.com/dlovemore/parle/primes.py'), File('/home/dl/github.com/dlovemore/parle/mint.py'), File('/home/dl/github.com/dlovemore/parle/__init__.py'), File('/home/dl/github.com/dlovemore/parle/func.py'), File('/home/dl/github.com/dlovemore/parle/.files.py.swp'), File('/home/dl/github.com/dlovemore/parle/files.py'), File('/home/dl/github.com/dlovemore/parle/fun.py'), File('/home/dl/github.com/dlovemore/parle/t'), File('/home/dl/github.com/dlovemore/parle/table.py'), File('/home/dl/github.com/dlovemore/parle/sym.py'), File('/home/dl/github.com/dlovemore/parle/save.py'), File('/home/dl/github.com/dlovemore/parle/funtest.py'), File('/home/dl/github.com/dlovemore/parle/sand'), File('/home/dl/github.com/dlovemore/parle/data.py'), File('/home/dl/github.com/dlovemore/parle/__init__.pyc')])
# >>> 
# >>> 
# >>> _@text@len
# Row([20, 0, 2049, 31, 0, 7689, 4346, 248, 18415, 0, 4689, 1145, 41, 14058, 7414, 4076, 818, 0, 16109, 0])
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
