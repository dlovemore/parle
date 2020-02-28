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
# <files.Selector object at 0x7fbe1e5a04e0>
# >>> f.s
# <files.Selector object at 0x7fbe1e5a0f28>
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
# PosixPath('/home/dl')
# >>> (HOME()/'github.com').glob('*')
# <generator object Path.glob at 0x7fbe1e585f10>
# >>> list(_)
# [PosixPath('/home/dl/github.com/dlovemore'), PosixPath('/home/dl/github.com/ravenbrook'), PosixPath('/home/dl/github.com/clasp-developers')]
# >>> 
# >>> Path.glob
# <function Path.glob at 0x7fbe1e526378>
# >>> import auto
# >>> auto.os.listdir()
# ['.gitignore', '.git', '__pycache__', 'primes.py', 'mint.py', '__init__.py', 'func.py', '.files.py.swp', 'files.py', 'fun.py', 't', 'table.py', 'sym.py', 'save.py', 'funtest.py', 'data.py']
# >>> Path.cwd()
# PosixPath('/home/dl/github.com/dlovemore/parle')
# >>> cwd()
# File('/home/dl/github.com/dlovemore/parle')
# >>> cwd().glob('*')
# Row([File('/home/dl/github.com/dlovemore/parle/.gitignore'), File('/home/dl/github.com/dlovemore/parle/.git'), File('/home/dl/github.com/dlovemore/parle/__pycache__'), File('/home/dl/github.com/dlovemore/parle/primes.py'), File('/home/dl/github.com/dlovemore/parle/mint.py'), File('/home/dl/github.com/dlovemore/parle/__init__.py'), File('/home/dl/github.com/dlovemore/parle/func.py'), File('/home/dl/github.com/dlovemore/parle/.files.py.swp'), File('/home/dl/github.com/dlovemore/parle/files.py'), File('/home/dl/github.com/dlovemore/parle/fun.py'), File('/home/dl/github.com/dlovemore/parle/t'), File('/home/dl/github.com/dlovemore/parle/table.py'), File('/home/dl/github.com/dlovemore/parle/sym.py'), File('/home/dl/github.com/dlovemore/parle/save.py'), File('/home/dl/github.com/dlovemore/parle/funtest.py'), File('/home/dl/github.com/dlovemore/parle/data.py')])
# >>> 
# >>> 
