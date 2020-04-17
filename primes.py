import collections
import itertools

def prod(*l):
    k=1
    for x in l:
        k*=x
    return k

_primes=[2,3]
def primes(n):
    if n>len(_primes):
        for pp in itertools.count(_primes[-1]+2,2):
            if isprime(pp):
                _primes.append(pp)
                if len(_primes)>=n:
                    break
    return _primes[:n]

def prime(n):
    if len(_primes) <=n:
        primes(n)
    return _primes[n-1]

def ispalindromic(i):
    s=str(i)
    return s==s[::-1]


_pps=[1]
def pp(n):
    if n>len(_pps):
        for pi in itertools.count(_pps[-1]+1):
            ppp=prime(pi)
            if ispalindromic(ppp):
                _pps.append(pi)
                if len(_pps)>=n:
                    break
    return prime(_pps[n-1])

def isprime(n):
    for k in range(1,n):
        pk=prime(k)
        if n<pk*pk:
            return True
        if n%pk==0:
            break
    return False

def isperfect(n):
    return som(n)==n

def issublime(n):
    return isperfect(sof(n)) and isperfect(nof(n))

def prod(xs):
    n=1
    for x in xs:
        n*=x
    return n

def factors(n):
    fs=[]
    k=n
    for p in (prime(j) for j in range(1,n)):
        if k<p*p:
            break
        while k%p==0:
            fs.append(p)
            k//=p
    if k!=1: fs+=[k]
    assert(prod(fs)==n)
    return fs

fs=factors

def pf(n):
    return collections.Counter(factors(n))

def npf(n):
    return [np(p) for p in factors(n)]

def npf(n):
    return {p:np(p) for p in factors(n)}

def allfactors(n):
    if n in (0,1): return ([],[1])[n]
    pps=pf(n)
    ps,ns=zip(*pps.items())
    fs = [prod([p**k for p,k in zip(ps,ks)]) for ks in itertools.product(*(range(0,n+1) for n in ns))]
    return sorted(fs)

def sof(n):
    "Sum of factors"
    if n==0: return 0
    r = prod([(p**(k+1)-1)//(p-1) for p,k in pf(n).items()])
    if r != sum(allfactors(n)): print( 'sof fail:', n,r, sum(allfactors(n)) )
    assert r == sum(allfactors(n))
    return r

def nof(n):
    "Number of factors"
    if n==0: return 0
    r = prod([k+1 for k in pf(n).values()])
    if r != len(allfactors(n)): print('nof fail',n,r,allfactors(n))
    assert r == len(allfactors(n))
    return r

def som(n):
    "Sum of multiples."
    return sof(n)-n

def lookupas(f,n):
    k=1
    while f(k)<=n:
        k*=2
    i, j=k//2, k
    while j-i>1:
        k=(i+j)//2
        v=f(k)
        if n<v: j=k
        elif n>v: i=k
        elif v==n: return k
    if f(i)==n: return i
    if f(j)==n: return j
    return (i,f(i),f(i)-n,n,f(j)-n,f(j),j)

φ=(1+5**.5)/2
ψ=1-φ
def Fn(n,f0=0,f1=1):
    return int(((f1-f0*ψ)*φ**n+(f0*φ-f1)*ψ**n)/(φ-ψ)+0.5)

Fibonacci=Fn

def base(b,x):
    def digits(x):
        while x:
            yield x%b
            x//=b
    return list(digits(x))[::-1]

def bases(x):
    for b in range(2,min(41,x)):
        print(b,base(b,x))

def rebase(b, x):
    if isinstance(x, int):
        x=[int(d) for d in str(x)]
    return sum([d*b**i for i,d in enumerate(x[::-1])])

def fbase(b,x):
    while True:
        yield int(x)
        x-=int(x)
        x*=b

def tri(n): return n*(n+1)//2

def np(p): return lookupas(pn,p)
def npp(p): return lookupas(pp,p)
def ntri(p): return lookupas(tri,p)
def nsq(p): return lookupas((lambda x: x*x),p)
def ncube(p): return lookupas((lambda x: x**3),p)
def nF(p): return lookupas(Fibonacci, p)
def nsof(p): return [i for i in range(p) if sof(i)==p]

def pn(n):
    return prime(n)

# >>> from primes import *
# >>> prime(1)
# 2
# >>> prime(1)
# 2
# >>> prime(2)
# 3
# >>> isprime(5)
# True
# >>> prime(5)
# 11
# >>> prime(5)
# 11
# >>> prime(4)
# 7
# >>> prime(3)
# 5
# >>> prime(12)
# 37
# >>> prime(21)
# 73
# >>> np(21)
# (8, 19, -2, 21, 2, 23, 9)
# >>> prime(1000)
# 7919
# >>> 
# >>> 
# >>> factors(66)
# [2, 3, 11]
# >>> factors(66)
# [2, 3, 11]
# >>> allfactors(66)
# [1, 2, 3, 6, 11, 22, 33, 66]
# >>> sum(allfactors(496))-496
# 496
# >>> sof(496)//2
# 496
# >>> bonacci(2)
# <console>:1: NameError: name 'bonacci' is not defined
# >>> bonacci(11)
# <console>:1: NameError: name 'bonacci' is not defined
# >>> 
# >>> sof(66)
# 144
# >>> sof(1189)
# 1260
# >>> sof(31102)
# 46656
# >>> pf(_)
# Counter({2: 6, 3: 6})
# >>> 
# >>> pn(13)
# 41
# >>> pn(12)
# 37
# >>> pn(21)
# 73
# >>> np(74)
# (21, 73, -1, 74, 5, 79, 22)
# >>> tri(27)
# 378
# >>> pf(378)
# Counter({3: 3, 2: 1, 7: 1})
# >>> 27*2*7
# 378
# >>> 
# >>> np(37)
# 12
# >>> np(38)
# (12, 37, -1, 38, 3, 41, 13)
# >>> np(73)
# 21
# >>> ncube(126)
# (5, 125, -1, 126, 90, 216, 6)
# >>> ncube(216)
# 6
# >>> pn(9)
# 23
# >>> pn(19)
# 67
# >>> pn(37)
# 157
# >>> 157*2
# 314
# >>> pn(73)
# 367
# >>> ispalindromic('99')
# True
# >>> for i in range(40,82):
# ...     print(i,pn(i),pp(i))
# ... 
# 40 173 17471
# 41 179 17971
# 42 181 18181
# 43 191 18481
# 44 193 19391
# 45 197 19891
# 46 199 19991
# 47 211 30103
# 48 223 30203
# 49 227 30403
# 50 229 30703
# 51 233 30803
# 52 239 31013
# 53 241 31513
# 54 251 32323
# 55 257 32423
# 56 263 33533
# 57 269 34543
# 58 271 34843
# 59 277 35053
# 60 281 35153
# 61 283 35353
# 62 293 35753
# 63 307 36263
# 64 311 36563
# 65 313 37273
# 66 317 37573
# 67 331 38083
# 68 337 38183
# 69 347 38783
# 70 349 39293
# 71 353 70207
# 72 359 70507
# 73 367 70607
# 74 373 71317
# 75 379 71917
# 76 383 72227
# 77 389 72727
# 78 397 73037
# 79 401 73237
# 80 409 73637
# 81 419 74047
# >>> np(589)
# (107, 587, -2, 589, 4, 593, 108)
# >>> factors(589)
# [19, 31]
# >>> 29*41
# 1189
# >>> 
# >>> 
# >>> 
# >>> pf(900)
# Counter({2: 2, 3: 2, 5: 2})
# >>> dict(_)
# {2: 2, 3: 2, 5: 2}
# >>> npf(900)
# {2: 1, 3: 2, 5: 3}
# >>> npf(1189)
# {29: 10, 41: 13}
# >>> npf(31102)
# {2: 1, 15551: 1814}
# >>> npf(1814)
# {2: 1, 907: 155}
# >>> npf(155)
# {5: 3, 31: 11}
# >>> base(12, 797)
# [5, 6, 5]
# >>> rebase(12, 797)
# 1123
# >>> rebase(12, 1123)
# 1899
# >>> [Fn(i) for i in range(32)]
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811, 514229, 832040, 1346269]
# >>> 789629/710647
# 1.1111409743515417
# >>> fs(789629)
# [311, 2539]
# >>> nF(710647)
# (29, 514229, -196418, 710647, 121393, 832040, 30)
# >>> Fn(28)/.9
# 353123.3333333333
# >>> 29-7
# 22
# >>> from bible import *
# >>> b.chapter(607)
# Psalms 129:1-8 (8 verses)
# >>> p(_)
# Psalms 129
# 1 Many a time have they afflicted me from my youth, may Israel now say:
# 2 Many a time have they afflicted me from my youth: yet they have not prevailed against me.
# 3 The plowers plowed upon my back: they made long their furrows.
# 4 The LORD is righteous: he hath cut asunder the cords of the wicked.
# 5 Let them all be confounded and turned back that hate Zion.
# 6 Let them be as the grass upon the housetops, which withereth afore it groweth up:
# 7 Wherewith the mower filleth not his hand; nor he that bindeth sheaves his bosom.
# 8 Neither do they which go by say, The blessing of the LORD be upon you: we bless you in the name of the LORD.
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 78982-64079
# 14903
# >>> 14903-9349
# 5554
# >>> 5554-3571
# 1983
# >>> 1983-1364
# 619
# >>> 619-521
# 98
# >>> 98-76
# 22
# >>> 22-18
# 4
# >>> Fn(10)
# 55
# >>> 
# >>> som(6)
# 6
# >>> som(28)
# 28
# >>> som(12)
# 16
# >>> sof(12)
# 28
# >>> nof(12)
# 6
# >>> issublime(12)
# True
# >>> any((issublime(i) for i in range(13,1000)))
# False
# >>> any((issublime(i) for i in range(1,12)))
# False
# >>> 
# >>> 
# >>> 
