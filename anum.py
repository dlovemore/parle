# accurate numbers
from func import *
from fractions import Fraction as fr, gcd

def cfr(n):
    while n:
        k=int(n)
        r=n-k
        yield 1,k
        if r==0: return
        n=1/r

def cfe(g):
    p,q,r,s=0,1,1,0
    for α,b in g:
        p,q,r,s=r,s,r*b+p*α,s*b+q*α
        yield fr(r,s)

def cfa(x): return cfe(cfr(x))

def cfae():
    p,q,r,s,b,d=3,1,19,7,10,1
    while True:
        p,q,r,s,b,d=r,s,r*b+p,s*b+q,b+4,d*10
        yield (d*r//s%10)

def cfre():
    yield 1,2
    yield 1,1
    yield 2,5
    b=10
    while True:
        yield 1,b
        b+=4

def cfre1():
    yield 1,3
    yield -2,7
    b=10
    while True:
        yield 1,b
        b+=4

# >>> from math import *
# >>> from anum import *
# >>> from fractions import *
# >>> from parle import *
# >>> 
# >>> 
# >>> firstn(7,cfr(pi))
# [(1, 3), (1, 7), (1, 15), (1, 1), (1, 292), (1, 1), (1, 1)]
# >>> cfe(_)*L
# [Fraction(3, 1), Fraction(22, 7), Fraction(333, 106), Fraction(355, 113), Fraction(103993, 33102), Fraction(104348, 33215), Fraction(208341, 66317)]
# >>> cfr(fr(2,7))
# <generator object cfr at 0xb65b6d70>
# >>> list(_)
# [(1, 0), (1, 3), (1, 2)]
# >>> firstn(7,cfre())
# [(1, 2), (1, 1), (2, 5), (1, 10), (1, 14), (1, 18), (1, 22)]
# >>> list(cfe(_))
# [Fraction(2, 1), Fraction(3, 1), Fraction(19, 7), Fraction(193, 71), Fraction(2721, 1001), Fraction(49171, 18089), Fraction(1084483, 398959)]
# >>> firstn(7,cfe(cfre1()))
# [Fraction(3, 1), Fraction(19, 7), Fraction(193, 71), Fraction(2721, 1001), Fraction(49171, 18089), Fraction(1084483, 398959), Fraction(28245729, 10391023)]
# >>> 1084483/398959
# 2.7182818284585633
# >>> exp(1)
# 2.718281828459045
# >>> 28245729/10391023
# 2.718281828459046
# >>> 
# >>> 
# >>> 
# >>> 
# >>> firstn(4,cfa(pi))
# [Fraction(3, 1), Fraction(22, 7), Fraction(333, 106), Fraction(355, 113)]
# >>> firstn(4,cfa(1/pi))
# [Fraction(0, 1), Fraction(1, 3), Fraction(7, 22), Fraction(106, 333)]
# >>> firstn(10,cfa(fr(355,113)))
# [Fraction(3, 1), Fraction(22, 7), Fraction(355, 113)]
# >>> a=fr(3)
# >>> a
# Fraction(3, 1)
# >>> 
# >>> firstn(15,cfe(cfre()))
# [Fraction(2, 1), Fraction(3, 1), Fraction(19, 7), Fraction(193, 71), Fraction(2721, 1001), Fraction(49171, 18089), Fraction(1084483, 398959), Fraction(28245729, 10391023), Fraction(848456353, 312129649), Fraction(28875761731, 10622799089), Fraction(1098127402131, 403978495031), Fraction(46150226651233, 16977719590391), Fraction(2124008553358849, 781379079653017), Fraction(106246577894593683, 39085931702241241), Fraction(5739439214861417731, 2111421691000680031)]
# >>> 5739439214861417731/2111421691000680031
# 2.718281828459045
# >>> 19/7
# 2.7142857142857144
# >>> 
# >>> exp(1)
# 2.718281828459045
# >>> 
# >>> 2721/1001
# 2.7182817182817183
# >>> 49171/18089
# 2.718281828735696
# >>> 193/71
# 2.7183098591549295
# >>> (193*1000)//71%10
# 8
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> 
# >>> fn=lambda n,p=3,q=1,r=19,s=7,b=10,x=1,y=0:x-y and fn(n,r,s,r*b+p,s*b+q,b+4,p*100**n//q,x) or str(x)[:n]
# >>> fn(950)
# '27182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274274663919320030599218174135966290435729003342952605956307381323286279434907632338298807531952510190115738341879307021540891499348841675092447614606680822648001684774118537423454424371075390777449920695517027618386062613313845830007520449338265602976067371132007093287091274437470472306969772093101416928368190255151086574637721112523897844250569536967707854499699679468644549059879316368892300987931277361782154249992295763514822082698951936680331825288693984964651058209392398294887933203625094431173012381970684161403970198376793206832823764648042953118023287825098194558153017567173613320698112509961818815930416903515988885193458072738667385894228792284998920868058257492796104841984443634632449684875602336248270419786232090021609902353043699418491463140934317381436405462531520961836908887070167683964243781405927145635490613031072085103837505'
# >>> 
# >>> 
# >>> f=lambda n,p=3,q=1,r=19,s=7,b=10,d=1,x=1,y=0:x-y and f(n,r,s,r*b+p,s*b+q,b+4,100**n,p*d//q,x) or str(x)[n]
# >>> ''.join(span(100)@F(f)@F(str))
# '71828182845904523536028747135266249775724709369995957496696762772407663035354759457138217852516642742746639193200305992181741359662904357290033429526059563073813232862794349076323382988075319525101901157383418793070215408914993488416750924476146066808226480016847741185374234544243710753907774499206955170276183860626133138458300075204493382656029760673711320070932870912744374704723069697720931014169283681902551510865746377211125238978442505695369677078544996996794686445490598793163688923009879312773617821542499922957635148220826989519366803318252886939849646510582093923982948879332036250944311730123819706841614039701983767932068328237646480429531180232878250981945581530175671736133206981125099618188159304169035159888851934580727386673858942287922849989208680582574927961048419844436346324496848756023362482704197862320900216099023530436994184914631409343173814364054625315209618369088870701676839642437814059271456354906130310720851038375051'