Parle prototype project

Can we write clean code that allows higher-order optimisation?

The code in this project is not itself clean, but Python hacks to
experiment with clean higher order program expression.

We work over data structures rather than element at a time.

    >>> from parle import *
    >>> span(10)
    range(1, 11)
    >>> Row(span(10))
    1 2 3 4 5 6 7 8 9 10
    >>> _@mul*2
    2 4 6 8 10 12 14 16 18 20
    >>> span(10)@pow*2
    1 4 9 16 25 36 49 64 81 100
    >>> 

Function composition is expressed with *

    >>> f=(pow*2)*(mul*2)
    >>> 1*f
    2
    >>> 2*f
    8
    >>> 3*f, 3**2*2
    (18, 18)
    >>> span(10)@f
    2 8 18 32 50 72 98 128 162 200
    >>> 1*f*f*f
    128
    >>> 1*(f**3)
    128

/f Does a search for elements that match truth(f(x)).

    >>> ['spring','frogs','lemons','grass','tree']@meth.endswith('s')
    [False, True, True, True, False]
    >>> ['spring','frogs','lemons','grass','tree']/meth.endswith('s')
    ['frogs', 'lemons', 'grass']
    >>> 
    >>> eq=Binop(op.eq)
    >>> span(10)/(eq*3)
    3
    >>> span(10)/(mod*2*eq*1)
    1 3 5 7 9
    >>> span(10)/(mod*2*eq*0)
    2 4 6 8 10
    >>> 

We can also sum over elements

    >>> Span=span*Row
    >>> Span(3)
    1 2 3
    >>> add/Span(3)
    6
    >>> add/Span(10)
    55
    >>> 

Why?

- When we work on collections rather than individual elements we are
optimising over loops.

- Code can be vectorised

- Code can be parallelised

- Code can be specialised for the data and code being optimised.

- Data reperesentation can be specialised for the data and code being
optimised.

- Complexity when working over a data structure can be better than working
element at a time.

To gain these benefits we need a sufficently clean expression of what
we are doing to allow higher order optimisation. The purpose of this
project is to experiment with program expression.

This is an unsupported prototype project and is subject to error and
discontinuation.

Algorithm optimisation

Suppose we write a program to count the number of lines in a file.

The code to do this is something like:

    >>> len(File('README.md').lines)
    111

Because of the way Python is executed, those lines are actually going to
be read and contructed as strings even though we only desire to know the
total length of the constructed array.

As A function this can be written:

    >>> wc=File*prop.lines*len
    >>> 'README.md'*wc
    111

A "more efficient" program is:

    >>> Path('README.md').read_bytes()/(eq*10)*F(len)
    111

Which can be written as a function:

    >>> wc1=Path*method.read_bytes/(eq*10)*len
    >>> wc1('README.md')
    111

If we can transform one into the other then we get a performance gain
without writing a "more efficient" program. This is because we are
instructing the computer what to calculate not how to calculate it.

The easiness with which this is done depends on the cleanliness of the
semantics of the program. And the cleaner the semantics and the less
dependent on architecture specifics the more the compiler is able to
recognise what is going on and do it efficiently.

Consider a C program to do the task:

    { int n; for(n=0;(c=fgetc(fp))!=EOF; n+=c=='\n');

This does the task, but not in the *most* efficient way.

For example it reads characters one at a time, yet an optimized array
search can be both vectorised and parallelised.

Systems like APL, kdb, perform these array operations in highly
optimised ways. But APLs high level data structures are geared toward
matrices.

One point of interest is can we also express programs on more general
graphs in terms of bulk operations that can be specialised, vectorised,
parallelised.
