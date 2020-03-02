from functools import partial, reduce
from operator import itemgetter as li
import operator

class Attr:
    def __init__(self, f):
        self.f=f
    def __call__(self, attr):
        return self.f(attr)
    def __getattr__(self, attr):
        return self.f(attr)
    def __repr__(self):
        return f'{type(self).__name__}({self.f})'

class GetItem:
    def __init__(self,f):
        self.f=f
    def __call__(self, k):
        return self.f(k)
    def __getitem__(self, k):
        return self.f(k)

def I(x): return x

@Attr
class Unique:
    def __init__(self, name=None):
        if name: self.name=name
    def __repr__(self):
        return self.name if hasattr(self, 'name') else super().__repr__()

e=Unique.e

def redparts(f,xs):
    f=Binop(f)
    y=f.e
    for x in xs:
        y=Binop(f)(x,y)
        yield y

def callmethod(name,object,*args,**kwargs): return getattr(object,name)(*args,**kwargs)

@Attr
def method(name): return partial(callmethod,name)

def callmethod(name,object,*args,**kwargs): return getattr(object,name)(*args,**kwargs)

@Attr
def meth(name,*args,**kwargs):
    def callmeth(*args,**kwargs):
        def callmeth(object):
            nonlocal args, kwargs
            return callmethod(name,object,*args,**kwargs)
        return callmeth
    return callmeth

def getprop(name,object): return getattr(object,name)

@Attr
def prop(name): return partial(getprop,name)

def aslist(f):
    def tolist(f,*args):
        return list(f(*args))
    return partial(tolist,f)

def compose(f,g):
    def compose(f,g,*args,**kwargs):
        return g(f(*args,**kwargs))
    return partial(compose,f,g)

def star(f):
    def star(f,*l):
        return f(l)
    return partial(star,f)

def apply(f, l,**kwargs):
    return f(*l, **kwargs)

def unstar(f): return partial(apply,f)

l=star(list)

def orr(f,g,x):
    try:
        return f(x)
    except Exception:
        pass
    return g(x)

class Unique: pass

def default(x):
    def I(x,y): return x
    return partial(I,x)

class Func:
    def __init__(self,f,domain=None):
        self.f=f if callable(f) else default(f)
        self.domain=self.f if domain else domain
    def __contains__(self, k):
        return k in self.f
    def __call__(self,*args,**kwargs):
        return self.f(*args,**kwargs)
    def __or__(self,f):
        return Func(partial(orr,self.f,f))
    def __repr__(self):
        return f'{type(self).__name__}({self.f!r})'

class RightOp(Func):
    def __rmatmul__(self,x):
        return self.f(x)

class LeftOp(Func):
    def __matmul__(self,x):
        return self.f(x)


class Binop(Func):
    def __init__(self, f):
        def binop(x,y):
            nonlocal f
            if y is e:
                return x
            if x is e:
                return y
            return f(x,y)
        self.f=f.f if isinstance(f, Binop) else binop
        self.e=e
    def __rmatmul__(self,a):
        def aop(z):
            nonlocal a
            return self.f(a,z)
        return LeftOp(aop)
    def __matmul__(self,z):
        def opz(a):
            nonlocal z
            return self.f(a,z)
        return RightOp(opz)

class OrFunc(Func):
    pass

class F(Func):
    pass

add=Binop(operator.add)
sub=Binop(operator.sub)
pow=Binop(operator.pow)
divide=Binop(operator.truediv)
div=Binop(operator.floordiv)
mul=Binop(operator.mul)

class Dict(dict):
    def __call__(self,k):
        return super().get(k)
    def __or__(self,f):
        if isinstance(f, dict):
            d=type(self)(self)
            d.update(f)
            return d
        return Func(self)|f
    def __matmul__(self, f):
        ...
    def __getitem__(self,kvs):
        if isinstance(kvs, slice): kvs=(kvs,)
        return type(self)(zip((kv.start for kv in kvs), (kv.stop for kv in kvs)))|self
Dict=Dict()

def windows(n,xs):
    l=[]
    for i,x in enumerate(xs):
        l.append(x)
        if i>=n-1:
            yield tuple(l)
            l.pop(0)

def failas(f,failresult=None,exc=None):
    def failsafe2(f,failresult,*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except:
            return failresult
    def failsafe3(f,failresult,exc,*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except exc:
            return failresult
    return partial(failsafe3,f,failresult,exc) if exc else partial(failsafe2,f,failresult)

@aslist
def inks(k,l):
    for i in range(0,len(l),k):
        yield tuple(l[i:i+k])

pairs=partial(windows,2)
twos=partial(inks,2)
threes=partial(inks,3)

class Unique:
    pass

@aslist
def withoutrepeats(xs):
    y=Unique()
    for x in xs:
        if x!=y:
            yield x
        y=x

def splitat(poss, xs):
    return [xs[x:y] for x,y in pairs(poss+[len(xs)])]

def positions(bs):
    return [i for i,b in enumerate(bs) if b]

def perm(*ks):
    assert sorted(ks)==list(range(len(ks)))
    def perm(l):
        nonlocal ks
        return type(l)([l[k] for k in ks])+l[len(ks):]
    return perm

def permargs(*ks):
    def permargs(f):
        nonlocal ks
        return compose(star(perm(*ks)),unstar(f))
    return permargs

def fggf(fg):
    def gf(*args1,**kwargs1):
        def f(args,**kwargs):
            nonlocal args1,kwargs1,fg
            return fg(args,kwargs)(*args1,kwargs1)
        return f
    return gf

swap=star(perm(1,0))
swapargs=permargs(1,0)

## >>> class List(list):
## >>> 
## ...     def total(self): return sum(self)
## ...     l=functools.partialmethod(total)
## ... 
## >>> List([1,2,3]).l()
## >>> list.x
## >>> 
## Traceback (most recent call last):
##   File "<console>", line 1, in <module>
## AttributeError: type object 'list' has no attribute 'x'
## >>> l=functools.partialmethod(list.__len__)
## >>> list.l=l
## Traceback (most recent call last):
##   File "<console>", line 1, in <module>
## TypeError: can't set attributes of built-in/extension type 'list'
## >>> l([1,2,3])
## Traceback (most recent call last):
##   File "<console>", line 1, in <module>
## TypeError: 'partialmethod' object is not callable
## >>> 
## 6


# >>> from auto import *
# >>> from func import *
# >>> 
# >>> 
# >>> 
# >>> method.join
# functools.partial(<function callmethod at 0xb64bdd68>, 'join')
# >>> method.join(',','abc')
# 'a,b,c'
# >>> 
# >>> ap=Attr(print)
# >>> ap
# Attr(<built-in function print>)
# >>> ap.abc
# abc
# >>> pairs('abcdefg')
# <generator object windows at 0xb64bff30>
# >>> list(_)
# [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'f'), ('f', 'g')]
# >>> 
# >>> l(1,2,3)
# [1, 2, 3]
# >>> 
# >>> F(list)
# F(<class 'list'>)
# >>> _([1,2,3])
# [1, 2, 3]
# >>> 
# >>> star(li(2,1,3))(4,5,6,7)
# (6, 5, 7)
# >>> 
# >>> swap(1,2,3)
# (2, 1, 3)
# >>> 
# >>> swap(2,3)
# (3, 2)
# >>> isinstance(*swap(int, 3))
# True
# >>> 
# >>> unstar(isinstance)(swap(int, 3))
# True
# >>> partial(compose(swap,unstar(isinstance)),int)
# functools.partial(<function compose.<locals>.compose at 0xb64bd8a0>, functools.partial(<function star.<locals>.star at 0xb64739c0>, <function perm.<locals>.perm at 0xb6473978>), functools.partial(<function apply at 0xb64bdf18>, <built-in function isinstance>), <class 'int'>)
# >>> _(9),_(True),_('aa'),_((1,2))
# (True, True, False, False)
# >>> 
# >>> 
# >>> 
# >>> partial(compose(swap,partial(apply,isinstance)),int)
# functools.partial(<function compose.<locals>.compose at 0xb64bd8a0>, functools.partial(<function star.<locals>.star at 0xb64739c0>, <function perm.<locals>.perm at 0xb6473978>), functools.partial(<function apply at 0xb64bdf18>, <built-in function isinstance>), <class 'int'>)
# >>> _('a'),_(3)
# (False, True)
# >>> 
# >>> 
# >>> 
# >>> swap(1,2,3,4)
# (2, 1, 3, 4)
# >>> perm(1,0)([1,2,3,4])
# [2, 1, 3, 4]
# >>> perm(1,0)([1,2,3,4])
# [2, 1, 3, 4]
# >>> compose(star(perm(1,0)),unstar(l))(1,2,3,4)
# [2, 1, 3, 4]
# >>> 
# >>> 
# >>> 
# >>> permargs(1,0)(l)(1,2,3,4)
# [2, 1, 3, 4]
# >>> 
# >>> 
# >>> 
# >>> f=Dict|{1:2, 3:4}|default(7)
# >>> [f(x) for x in range(1,6)]
# [2, None, 4, None, None]
# >>> 
# >>> swapargs(l)(1,2,3)
# [2, 1, 3]
# >>> Dict[3:4](3)
# 4
# >>> 
# >>> meth.join(map(str,range(10)))(', ')
# '0, 1, 2, 3, 4, 5, 6, 7, 8, 9'
# >>> 
# >>> fggf(meth.join)(',')(map(str,[1,2,3]))
# <console>:1: callmeth() takes 1 positional argument but 2 were given
#     auto=<module 'auto.auto' from '/home/pi/python/auto/auto.py'>
#     imported_modules={}
#     Importer=<class 'auto.auto.Importer'>
#     module_names=<function module_names at 0xb64bd660>
#     autos=<function autos at 0xb64bd810>
#     re=Importer('re')
#     difflib=Importer('difflib')
#     textwrap=Importer('textwrap')
#     unicodedata=Importer('unicodedata')
#     stringprep=Importer('stringprep')
#     readline=Importer('readline')
#     rlcompleter=Importer('rlcompleter')
#     struct=Importer('struct')
#     codecs=Importer('codecs')
#     datetime=Importer('datetime')
#     calendar=Importer('calendar')
#     collections=Importer('collections''abc')
#     heapq=Importer('heapq')
#     bisect=Importer('bisect')
#     array=Importer('array')
#     weakref=Importer('weakref')
#     types=Importer('types')
#     copy=Importer('copy')
#     pprint=Importer('pprint')
#     reprlib=Importer('reprlib')
#     enum=Importer('enum')
#     numbers=Importer('numbers')
#     math=Importer('math')
#     cmath=Importer('cmath')
#     decimal=Importer('decimal')
#     fractions=Importer('fractions')
#     random=Importer('random')
#     statistics=Importer('statistics')
#     itertools=Importer('itertools')
#     functools=Importer('functools')
#     operator=<module 'operator' from '/usr/lib/python3.7/operator.py'>
#     pathlib=Importer('pathlib')
#     fileinput=Importer('fileinput')
#     stat=Importer('stat')
#     filecmp=Importer('filecmp')
#     tempfile=Importer('tempfile')
#     glob=Importer('glob')
#     fnmatch=Importer('fnmatch')
#     linecache=Importer('linecache')
#     shutil=Importer('shutil')
#     macpath=Importer('macpath')
#     pickle=Importer('pickle')
#     copyreg=Importer('copyreg')
#     shelve=Importer('shelve')
#     marshal=Importer('marshal')
#     dbm=Importer('dbm')
#     sqlite3=Importer('sqlite3')
#     zlib=Importer('zlib')
#     gzip=Importer('gzip')
#     bz2=Importer('bz2')
#     lzma=Importer('lzma')
#     zipfile=Importer('zipfile')
#     tarfile=Importer('tarfile')
#     csv=Importer('csv')
#     configparser=Importer('configparser')
#     netrc=Importer('netrc')
#     xdrlib=Importer('xdrlib')
#     plistlib=Importer('plistlib')
#     hashlib=Importer('hashlib')
#     hmac=Importer('hmac')
#     os=Importer('os''path')
#     io=Importer('io')
#     time=Importer('time')
#     argparse=Importer('argparse')
#     getopt=Importer('getopt')
#     logging=Importer('logging''config''handlers')
#     getpass=Importer('getpass')
#     curses=Importer('curses''textpad''ascii''panel')
#     platform=Importer('platform')
#     errno=Importer('errno')
#     ctypes=Importer('ctypes')
#     threading=Importer('threading')
#     multiprocessing=Importer('multiprocessing')
#     concurrent=Importer('concurrent''futures')
#     subprocess=Importer('subprocess')
#     sched=Importer('sched')
#     queue=Importer('queue')
#     dummy_threading=Importer('dummy_threading')
#     socket=Importer('socket')
#     ssl=Importer('ssl')
#     select=Importer('select')
#     selectors=Importer('selectors')
#     asyncio=Importer('asyncio')
#     asyncore=Importer('asyncore')
#     asynchat=Importer('asynchat')
#     signal=Importer('signal')
#     mmap=Importer('mmap')
#     email=Importer('email''charset''contentmanager''encoders''errors'...
#     json=Importer('json')
#     mailcap=Importer('mailcap')
#     mailbox=Importer('mailbox')
#     mimetypes=Importer('mimetypes')
#     base64=Importer('base64')
#     binhex=Importer('binhex')
#     binascii=Importer('binascii')
#     quopri=Importer('quopri')
#     uu=Importer('uu')
#     html=Importer('html''parser''entities')
#     xml=Importer('xml'('etree', 'ElementTree')('dom', 'minidom', 'pul...
#     webbrowser=Importer('webbrowser')
#     cgi=Importer('cgi')
#     cgitb=Importer('cgitb')
#     wsgiref=Importer('wsgiref')
#     urllib=Importer('urllib''request''response''parse''error''robotpa...
#     http=Importer('http''server''cookies''cookiejar')
#     ftplib=Importer('ftplib')
#     poplib=Importer('poplib')
#     imaplib=Importer('imaplib')
#     nntplib=Importer('nntplib')
#     smtplib=Importer('smtplib')
#     smtpd=Importer('smtpd')
#     telnetlib=Importer('telnetlib')
#     uuid=Importer('uuid')
#     socketserver=Importer('socketserver')
#     xmlrpc=Importer('xmlrpc''client''server')
#     ipaddress=Importer('ipaddress')
#     audioop=Importer('audioop')
#     aifc=Importer('aifc')
#     sunau=Importer('sunau')
#     wave=Importer('wave')
#     chunk=Importer('chunk')
#     colorsys=Importer('colorsys')
#     imghdr=Importer('imghdr')
#     sndhdr=Importer('sndhdr')
#     ossaudiodev=Importer('ossaudiodev')
#     gettext=Importer('gettext')
#     locale=Importer('locale')
#     turtle=Importer('turtle')
#     cmd=Importer('cmd')
#     shlex=Importer('shlex')
#     tkinter=Importer('tkinter''ttk''tix''scrolledtext')
#     IDLE=Importer('IDLE')
#     Other=Importer('Other')
#     typing=Importer('typing')
#     pydoc=Importer('pydoc')
#     doctest=Importer('doctest')
#     unittest=Importer('unittest''mock')
#     test=Importer('test''support')
#     bdb=Importer('bdb')
#     faulthandler=Importer('faulthandler')
#     pdb=Importer('pdb')
#     The=Importer('The')
#     timeit=Importer('timeit')
#     trace=Importer('trace')
#     tracemalloc=Importer('tracemalloc')
#     distutils=Importer('distutils')
#     ensurepip=Importer('ensurepip')
#     venv=Importer('venv')
#     zipapp=Importer('zipapp')
#     sys=Importer('sys')
#     sysconfig=Importer('sysconfig')
#     builtins=Importer('builtins')
#     warnings=Importer('warnings')
#     contextlib=Importer('contextlib')
#     abc=Importer('abc')
#     atexit=Importer('atexit')
#     traceback=Importer('traceback')
#     gc=Importer('gc')
#     inspect=Importer('inspect')
#     site=Importer('site')
#     fpectl=Importer('fpectl')
#     code=Importer('code')
#     codeop=Importer('codeop')
#     zipimport=Importer('zipimport')
#     pkgutil=Importer('pkgutil')
#     modulefinder=Importer('modulefinder')
#     runpy=Importer('runpy')
#     importlib=Importer('importlib''resources')
#     parser=Importer('parser')
#     ast=Importer('ast')
#     symtable=Importer('symtable')
#     symbol=Importer('symbol')
#     token=Importer('token')
#     keyword=Importer('keyword')
#     tokenize=Importer('tokenize')
#     tabnanny=Importer('tabnanny')
#     pyclbr=Importer('pyclbr')
#     py_compile=Importer('py_compile')
#     compileall=Importer('compileall')
#     dis=Importer('dis')
#     pickletools=Importer('pickletools')
#     formatter=Importer('formatter')
#     msilib=Importer('msilib')
#     msvcrt=Importer('msvcrt')
#     winreg=Importer('winreg')
#     winsound=Importer('winsound')
#     posix=Importer('posix')
#     pwd=Importer('pwd')
#     spwd=Importer('spwd')
#     grp=Importer('grp')
#     crypt=Importer('crypt')
#     termios=Importer('termios')
#     tty=Importer('tty')
#     pty=Importer('pty')
#     fcntl=Importer('fcntl')
#     pipes=Importer('pipes')
#     resource=Importer('resource')
#     nis=Importer('nis')
#     syslog=Importer('syslog')
#     optparse=Importer('optparse')
#     imp=Importer('imp')
#     ntpath=Importer('ntpath')
#     posixpath=Importer('posixpath')
#     secrets=Importer('secrets')
#     contextvars=Importer('contextvars')
#     dataclasses=Importer('dataclasses')
#     partial=<class 'functools.partial'>
#     reduce=<built-in function reduce>
#     li=<class 'operator.itemgetter'>
#     Attr=<class 'func.Attr'>
#     GetItem=<class 'func.GetItem'>
#     I=<function I at 0xb64bd8e8>
#     Unique=<class 'func.Unique'>
#     e=e
#     redparts=<function redparts at 0xb64bdc00>
#     callmethod=<function callmethod at 0xb64bdd68>
#     method=Attr(<function method at 0xb64bdd20>)
#     meth=Attr(<function meth at 0xb64bdcd8>)
#     getprop=<function getprop at 0xb64bddb0>
#     prop=Attr(<function prop at 0xb64bddf8>)
#     aslist=<function aslist at 0xb64bde40>
#     compose=<function compose at 0xb64bde88>
#     star=<function star at 0xb64bded0>
#     apply=<function apply at 0xb64bdf18>
#     unstar=<function unstar at 0xb64bdf60>
#     l=functools.partial(<function star.<locals>.star at 0xb64bdfa8>, ...
#     orr=<function orr at 0xb6473030>
#     default=<function default at 0xb6473078>
#     Func=<class 'func.Func'>
#     RightOp=<class 'func.RightOp'>
#     LeftOp=<class 'func.LeftOp'>
#     Binop=<class 'func.Binop'>
#     OrFunc=<class 'func.OrFunc'>
#     F=<class 'func.F'>
#     add=Binop(<function Binop.__init__.<locals>.binop at 0xb64730c0>)
#     sub=Binop(<function Binop.__init__.<locals>.binop at 0xb64733d8>)
#     pow=Binop(<function Binop.__init__.<locals>.binop at 0xb6473420>)
#     divide=Binop(<function Binop.__init__.<locals>.binop at 0xb647346...
#     div=Binop(<function Binop.__init__.<locals>.binop at 0xb64734b0>)
#     mul=Binop(<function Binop.__init__.<locals>.binop at 0xb64734f8>)
#     Dict={}
#     windows=<function windows at 0xb6473540>
#     failas=<function failas at 0xb64736a8>
#     inks=functools.partial(<function aslist.<locals>.tolist at 0xb647...
#     pairs=functools.partial(<function windows at 0xb6473540>, 2)
#     twos=functools.partial(<function aslist.<locals>.tolist at 0xb647...
#     threes=functools.partial(<function aslist.<locals>.tolist at 0xb6...
#     withoutrepeats=functools.partial(<function aslist.<locals>.tolist...
#     splitat=<function splitat at 0xb6473810>
#     positions=<function positions at 0xb6473858>
#     perm=<function perm at 0xb64738a0>
#     permargs=<function permargs at 0xb64738e8>
#     fggf=<function fggf at 0xb6473930>
#     swap=functools.partial(<function star.<locals>.star at 0xb64739c0...
#     swapargs=<function permargs.<locals>.permargs at 0xb6473a08>
#     ap=Attr(<built-in function print>)
#     f=Func(functools.partial(<function orr at 0xb6473030>, {1: 2, 3: ...
# /home/pi/python/parle/func.py:234: callmeth() takes 1 positional argument but 2 were given
#     args=<map object at 0xb64717f0>
#     kwargs={}
#     args1=(',',)
#     fg=<function meth.<locals>.callmeth at 0xb6473ae0>
#     kwargs1={}
# >>> 
# >>> 
# >>> 
# >>> 
