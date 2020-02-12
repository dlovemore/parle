>>> from fun import *
>>> X
E('X')
>>> print(v.Y)
E('Y')
>>> f=Table()
>>> f[3]=4
>>> f[3]
4
>>> f[7]
Traceback (most recent call last):
  File "<console>", line 1, in <module>
  File "/home/pi/python/parle/fun.py", line 156, in __getitem__
    i = self.keys.index(key)
ValueError: 7 is not in list
>>> f[7]=6
>>> f[7]
6
>>> f[3]
4
>>> f.keys
[7, 3]
>>> f.values
[6, 4]
>>> f[3]=8
>>> f[3]
8
>>> f.keys
[3, 7]
>>> f.values
[8, 6]
>>> f[1]=2
>>> f
<fun.Table object at 0xb66060b0>
>>> a=[1,2]
>>> a[0]=3
>>> a[0]+=3
>>> E('a','var')[3]
E(E('a'),'[]',3)
>>> a=v.a
>>> a[0]
E(E('a'),'[]',0)
>>> v.X<v.Y
E(E('X'),'<',E('Y'))
>>> v.X[v.X+1,]
E(E('X'),'[]',(E(E('X'),'+',1),))
>>> 
>>> globals()['ai']=12
>>> ai
12
>>> 
>>> on(X)[3:4]
E(E('X'),'?:',3,4)
>>> on(X)[3]
E(E('X'),'?',3)
>>> E(E('X'),'?',3)
E(E('X'),'?',3)
>>> 
