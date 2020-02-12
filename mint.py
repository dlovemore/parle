class mint(int):
    def __astype__(self,x):
        return type(self)(x) if isinstance(x,int) else x
    def __abs__(self):
        return type(self)(super().__abs__())
    def __add__(self,other):
        return self.__astype__(super().__add__(other))
    def __and__(self,other):
        return type(self)(super().__and__(other))
    def __ceil__(self):
        return type(self)(super().__ceil__())
    def __divmod__(self,other):
        x = super().__divmod__(other)
        return tuple(map(self.__astype__,x))
    def __div__(self,other):
        return self.__astype__(int(self)/other)
    def __floor__(self):
        return type(self)(super().__floor__())
    def __floordiv__(self,other):
        return type(self)(super().__floordiv__(other))
    def __invert__(self):
        return type(self)(super().__invert__())
    def __lshift__(self,other):
        return type(self)(super().__lshift__(other))
    def __mod__(self,other):
        return self.__astype__(super().__mod__(other))
    def __mul__(self,other):
        return self.__astype__(super().__mul__(other))
    def __neg__(self):
        return type(self)(super().__neg__())
    def __or__(self,other):
        return type(self)(super().__or__(other))
    def __pos__(self,other):
        return type(self)(super().__pos__(other))
    def __pow__(self,other):
        return self.__astype__(super().__pow__(other))
    def __radd__(self,other):
        return self.__astype__(super().__radd__(other))
    def __rand__(self,other):
        return type(self)(super().__rand__(other))
    def __rdivmod__(self,other):
        x = super().__rdivmod__(other)
        return tuple(map(self.__astype__,x))
    def __rdiv__(self,other):
        return self.__astype__(other/int(self))
    def __rfloordiv__(self,other):
        return type(self)(super().__rfloordiv__(other))
    def __rlshift__(self,other):
        return type(self)(super().__rlshift__(other))
    def __rmod__(self,other):
        return type(self)(super().__rmod__(other))
    def __rmul__(self,other):
        return self.__astype__(super().__rmul__(other))
    def __ror__(self,other):
        return type(self)(super().__ror__(other))
    def __round__(self,other):
        return type(self)(super().__round__(other))
    def __rpow__(self,other):
        return self.__astype__(super().__rpow__(other))
    def __rrshift__(self,other):
        return type(self)(super().__rrshift__(other))
    def __rshift__(self,other):
        return type(self)(super().__rshift__(other))
    def __rsub__(self,other):
        return type(self)(super().__rsub__(other))
    def __rtruediv__(self,other):
        return self.__astype__(super().__rtruediv__(other))
    def __rxor__(self,other):
        return type(self)(super().__rxor__(other))
    def __sub__(self,other):
        return type(self)(super().__sub__(other))
    def __truediv__(self,other):
        return self.__astype__(super().__truediv__(other))
    def __trunc__(self):
        return type(self)(super().__trunc__())
    def __xor__(self,other):
        return type(self)(super().__xor__(other))
    def conjugate(self):
        return self
    def denominator(self):
        return type(self)(super().denominator())
    def imag(self):
        return type(self)(super().imag())
    def numerator(self,other):
        return type(self)(super().numerator(other))
    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'

class sint(int):
    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'

# >>> from mint import *
# >>> sint(3)
# sint(3)
# >>> sint(3)+1
# 4
# >>> mint(3)
# mint(3)
# >>> min(3)+4
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# TypeError: 'int' object is not iterable
# >>> print(type(_))
# <class 'mint.mint'>
# >>> _/3,_//3
# (1.0, mint(1))
# >>> 
# >>> mint(5)/mint(2)
# 2.5
# >>> 
# >>> mint(5).__astype__(4.4)
# 4.4
# >>> 
# >>> mint(5).__astype__(4)
# mint(4)
# >>> 5/2
# 2.5
# >>> mint(5)/2
# 2.5
# >>> 
# >>> mint(5).__div__(2)
# 2.5
# >>> mint(5)/mint(2)
# 2.5
# >>> int(mint(5))/2
# 2.5
# >>> 5//2
# 2
# >>> x=5
# >>> x.__truediv__(2)
# 2.5
# >>> mint(5).__truediv__(2)
# 2.5
# >>> mint(5).__div__(2)
# 2.5
# >>> int(5).__truediv__(2)
# 2.5
# >>> 
# >>> 
# >>> mint(100)//7
# mint(14)
# >>> 100//mint(7)
# mint(14)
# >>> 
