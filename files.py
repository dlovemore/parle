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
    def __repr__(self):
        return f'{type(self).__name__}({str(self.path)!r})'

def HOME():
    return File(os.getenv('HOME'))
def cwd():
    return File(Path.cwd())

class Selector:
    def __init__(self, base):
        self.base=base
    def __truediv__(self, pat):
        return FileSel(self.base,pat)


class FileSel:
    def __init__(self, base, pat):
        self.base=base
        self.pat=pat
    def __truediv__(self, other):
        self.replace=other
        self.base.text=(re.sub(self.pat, other, self.base.text, flags=re.MULTILINE))
        return self.base
    def __repr__(self):
        return '\n'.join([mo[0] for mo in re.finditer(self.pat, self.base.text, flags=re.MULTILINE)])

# >>> from files import *
# >>> f=File('t')
# >>> f.text='Good day.\n'
# >>> f.text+='Another day\n'
# >>> f.text
# 'Good day.\nAnother day\n'
# >>> f.lines
# ['Good day.\n', 'Another day\n']
# >>> 
# >>> 
# >>> f.s
# <files.Selector object at 0xb65c36d0>
# >>> f.s
# <files.Selector object at 0xb64fb910>
# >>> f.s/'Good'/'Very good'
# File('t')
# >>> f.lines+=['The time','ends']
# >>> f.text
# 'Very good day.\nAnother day\nThe time\nends\n'
# >>> f.s/r'^.*other day\nThe.*$'
# Another day
# The time
# >>> 
# >>> 
# >>> HOME().path
# PosixPath('/home/pi')
# >>> (HOME()/'github.com').glob('*')
# <generator object Path.glob at 0xb652bdf0>
# >>> list(_)
# [PosixPath('/home/pi/github.com/dlovemore')]
# >>> 
# >>> Path.glob
# <function Path.glob at 0xb6592c00>
# >>> import auto
# >>> auto.os.listdir()
# ['__init__.py', '.git', 'fun.py', 'funtest.py', 'save.py', 'func.py', 'htmldraw.py', '.gitignore', 'table.py', 'mint.py', 'primes.py', 'data.py', '__pycache__', 'files.py', '.files.py.swp', 't', 'sym.py']
# >>> Path.cwd()
# PosixPath('/home/pi/python/parle')
# >>> cwd()
# File('/home/pi/python/parle')
# >>> prop.text(f)
# 'Very good day.\nAnother day\nThe time\nends\n'
# >>> text=Func(prop.text)|default('')
# >>> text(cwd())
# ''
# >>> text(f)
# 'Very good day.\nAnother day\nThe time\nends\n'
# >>> cwd().glob('*')
# Row([File('/home/pi/python/parle/__init__.py'), File('/home/pi/python/parle/.git'), File('/home/pi/python/parle/fun.py'), File('/home/pi/python/parle/funtest.py'), File('/home/pi/python/parle/save.py'), File('/home/pi/python/parle/func.py'), File('/home/pi/python/parle/htmldraw.py'), File('/home/pi/python/parle/.gitignore'), File('/home/pi/python/parle/table.py'), File('/home/pi/python/parle/mint.py'), File('/home/pi/python/parle/primes.py'), File('/home/pi/python/parle/data.py'), File('/home/pi/python/parle/__pycache__'), File('/home/pi/python/parle/files.py'), File('/home/pi/python/parle/.files.py.swp'), File('/home/pi/python/parle/t'), File('/home/pi/python/parle/sym.py')])
# >>> _@text@len
# Row([248, 0, 1145, 818, 4076, 7619, 1760, 18, 13910, 4346, 7689, 16109, 0, 3791, 0, 41, 7414])
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
