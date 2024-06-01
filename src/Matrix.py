# -*- coding: utf-8 -*-
# not  ISO-8859-1

# derived by hjva from 
# mathguide Version 1.1b2 
# Copyright 2004-2008 Hartmut Ring

import sys, math  #os, random, re, inspect
isMICPYTH = sys.implementation.name == "micropython"
if not isMICPYTH:
    import operator
    from functools import reduce  # hjva
from random import randrange

#from typing import Tuple

#===============================================================
#  Elementary Functions
#---------------------------------------------------------------

def isInteger(n):
    """ <b>isInteger(n)</b><br/>
        returns <code>True</code> if and only if n is of type <code>int</code> or <code>long</code>.
    ----de----
        <b>isInteger(n)</b><br/>
        gibt <code>True</code> zurück genau dann, wenn n vom Typ <code>int</code> oder <code>long</code> ist.
    """
    if isinstance(n, float):
        return n.is_integer()
    return isinstance(n, int) # hjva or n.is_integer()
    #return type(n) in (int, long)

def isNatural(n):
    return isInteger(n) and n > 0

#............................................................

def sum(v):
    """ <b>sum(v)</b><br/>
        <i>The sum of the elements of list v</i><br/>
        The element type must define the operator + (e.g. numbers or strings).
    ----de----
        <b>sum(v)</b><br/>
        <i>Summe der Elemente der Liste v</i><br/>
        Die Elemente der Liste müssen mit dem Operator + verknüpfbar sein
        (z. B. Zahlen oder Strings).
    """
    if len(v) == 0:
        return 0
    if not isMICPYTH:
        return reduce(operator.add, v)
    return reduce(lambda a, b: a+b, v)

#............................................................

def product(v):
    """ <b>product(v)</b><br/>
        <i>The product of the elements of list v</i><br/>
        The element type must define the operator * (e.g. numbers or strings).
    ----de----
        <b>product(v)</b><br/>
        <i>Produkt der Elemente der Liste v</i><br/>
        Die Elemente der Liste müssen mit dem Operator * verknüpfbar sein
        (z. B. Zahlen oder Strings).
    """
    if len(v) == 0:
        return 1
    if not isMICPYTH:
        return reduce(operator.mul, v)
    return reduce(lambda a, b: a*b, v)

#............................................................

def join(l, filler=""):
    """ <b>join(l, filler="")</b><br/>
        <i>Joins the elements of <code>l</code> to a string</i><br/>
        Between each two adjacent elements <code>filler</code> is inserted.<br/>
        This is a replacement for the string method <code>join()</code>.<br/>
        In addition to the string method the list elements are converted to strings.<br/>
        <b>Example</b>: <code>join(fromTo(1,5), "-")</code>
        returns <code>"1-2-3-4-5"</code>.
    ----de----
        <b>join(l, filler="")</b><br/>
        <i>verbindet die Elemente von <code>l</code> zu einem String</i><br/>
        Zwischen je zwei Elemente wird <code>filler</code> eingefügt.<br/>
        Ersatz für die schwer lesbare String-Methode join()
        bzw. für die Funktion string.join().<br/>
        Im Gegensatz zu diesen Funktionen werden zusätzlich
        die Listenelemente zu Strings konvertiert.<br/>
        <b>Beispiel</b>: <code>join(fromTo(1,5), "-")</code>
        liefert <code>"1-2-3-4-5"</code>.
    """
    return filler.join([str(x) for x in l])


#===============================================================
#  Algorithms of Elementary Number Theory
#---------------------------------------------------------------

#---------------------------------------------------------------
#  Large random numbers

def rand(n):
    """ <b>rand(n)</b><br/>
        Integer random number from the range 0 ... <b>n</b>-1<br/>
        <b>n</b> must be a natural number (int or long).
    ----de----
        <b>rand(n)</b><br/>
        Zufallszahl im Bereich 0 ... <b>n</b>-1<br/>
        <b>n</b> kann eine beliebige natürliche Zahl sein (int oder long).
    """
    return randrange(n)

#---------------------------------------------------------------
#  Elementary number theoretic functions
#  Funktionen der elementaren Zahlentheorie

def gcd(a,b):
    """ <b>gcd(a,b)</b><br/>
        <i>greatest common divisor of a and b</i><br/>
        Calculated using the Euclidean algorithm<br/>
        <b>See also</b> <a href="#lcm"><code>lcm</code></a>
    ----de----
        <b>gcd(a,b)</b><br/>
        <i>Größter gemeinsamer Teiler von a und b</i><br/>
        Berechnung mit dem euklidischen Algorithmus<br/>
        <b>Siehe auch</b> <a href="#lcm"><code>lcm</code></a>
    """
    while b != 0:
        a, b = b, a % b
    return a

def lcm(a, b):
    """ <b>lcm(a,b)</b><br/>
        <i>Least common multiple of <b>a</b> and <b>b</b></i><br/>
        <b>See also</b> <a href="#gcd"><code>gcd</code></a>
    ----de----
        <b>lcm(a,b)</b><br/>
        <i>Kleinstes gemeinsames Vielfaches von <b>a</b> und <b>b</b></i><br/>
        <b>Siehe auch</b> <a href="#gcd"><code>gcd</code></a>
    """
    assert a > 0 and b > 0
    return (a * b) // gcd (a, b)

#===============================================================
#  Rational numbers and continued fractions
#  Rationale Zahlen, Kettenbrüche
#---------------------------------------------------------------

class  _MathGUIdeError(Exception):  #hjva
    pass


class Rational (object): # Rational numbers # Rationale Zahlen
    """ Class <code>Rational</code>: Rational numbers<br/>
        <b>Rational(p, q)</b> Example: <code>Rational(3,17)</code><br/>
        <b>Rational(n)</b> Example: <code>Rational(3)</code><br/>
        <b>Rational(s)</b> Example: <code>Rational("3/17")</code><br/>
        For <code>Rational</code> objects the arithmetical operators
        +, -, *, / are defined.
    ----de----
        Klasse <code>Rational</code>: Rationale Zahl<br/>
        <b>Rational(p, q)</b> Beispiel: <code>Rational(3,17)</code><br/>
        <b>Rational(n)</b> Beispiel: <code>Rational(3)</code><br/>
        <b>Rational(s)</b> Beispiel: <code>Rational("3/17")</code><br/>
        <code>Rational</code>-Objekte können mit den
        arithmetischen Operatoren +, -, *, / verknüpft werden.
    """
    def operators(self):
        """ <b>Rational.operators()</b><br/>
            <i>For documentation only</i><br/>
            The following operators are defined in the class <b>Rational</b>:<br/>
            <table>
             <tr><th>Op.</th><th>Function</th><th>Examples</th></tr>
             <tr><th>+</th><td>Addition</td><td><pre>a + b; a += b</pre></td></tr>
             <tr><th>-</th><td>Subtraction</td><td><pre>a - b; a -= b</pre></td></tr>
             <tr><th>*</th><td>Multiplication</td><td><pre>a * b; a *= b</pre></td></tr>
             <tr><th>/</th><td>Division</td><td><pre>a / b; a /= b</pre></td></tr>
             <tr><th>-</th><td>Unary minus</td><td><pre>-a</pre></td></tr>
             <tr><th>&lt; > &lt;= >=</th><td>Comparision operators</td><td></td></tr>
            </table>
            <font color="#000080" size="-2">This method is for documentation only. It has no effect.</font>
        ----de----
            <b>Rational.operators()</b><br/>
            <i>Nur zur Dokumentation</i><br/>
            Die Klasse <b>Rational</b> erlaubt folgende Operatoren:<br/>
            <table>
             <tr><th>Op.</th><th>Funktion</th><th>Beispiele</th></tr>
             <tr><th>+</th><td>Addition</td><td><pre>a + b; a += b</pre></td></tr>
             <tr><th>-</th><td>Subtraktion</td><td><pre>a - b; a -= b</pre></td></tr>
             <tr><th>*</th><td>Multiplikation</td><td><pre>a * b; a *= b</pre></td></tr>
             <tr><th>/</th><td>Division</td><td><pre>a / b; a /= b</pre></td></tr>
             <tr><th>-</th><td>unäres Minus</td><td><pre>-a</pre></td></tr>
             <tr><th>&lt; > &lt;= >=</th><td>Vergleichsoperatoren</td><td></td></tr>
            </table>
            <font color="#000080" size="-2">Diese Methode dient nur zur Dokumentation. Sie hat keine Wirkung.</font>
        """
        pass

    def __init__(self, p, q=1):
        """ Constructor
        """
        if type(p) == float:
            #r = ContFrac(p).toRational()
            r = p.as_integer_ratio()  # hjva 2023
            self.p, self.q = r[0], r[1]
            #self.p, self.q = r.p, r.q
            return
        if type(p) == Rational:
            self.p, self.q = p.p, p.q
            return
        if type(p) == str:   #  e.g. "3/17"
            l = p.split("/")
            p = int(l[0])
            if len(l) > 1:
                q = int(l[1])
        if q < 0:
            p,q = -p, -q  # denominator always positive
        d = gcd(abs(p), q)
        if d > 1:         # reduce fraction if possible
            p //= d
            q //= d
        self.p = p
        self.q = q

    def copy(self):
        """ <b>.copy()</b><br/>
            <i>independent copy ("clone")</i>
        ----de----
            <b>.copy()</b><br/>
            <i>unabhängige Kopie</i>
        """
        return Rational(self.p, self.q)

    def __abs__(self):
        """ Absolutbetrag
        """
        return Rational(abs(self.p), self.q)

    def abs(self):
        """ <b>r.abs()</b><br/>
            <i>absolute value</i><br/>
            Also as global function: <b>abs(r)</b><br/>
        ----de----
            <b>r.abs()</b><br/>
            <i>Absolutbetrag</i><br/>
            Auch globale Funktion: <b>abs(r)</b><br/>
        """
        return Rational(abs(self.p), self.q)

    def __float__(self):
        """ Conversion to floating point number
        """
        return float(self.p) / float(self.q)

    def toFloat(self):
        """ <b>r.toFloat()</b><br/>
            <i>Conversion to floating point number</i><br/>
            Also as global function: <b>float(r)</b><br/>
        ----de----
            <b>r.toFloat()</b><br/>
            <i>Konvertierung in Gleitkommazahl</i><br/>
            Auch globale Funktion: <b>float(r)</b><br/>
        """
        return float(self.p) / float(self.q)

    def __int__(self):
        """ Round to the nearest integer
        """
        assert self.q > 0
        return (self.p + self.q/2) // self.q

    def toInt(self):
        """ <b>r.toInt()</b><br/>
            <i>Round to the nearest integer</i><br/>
            Also as global function: <b>int(r)</b><br/>
        ----de----
            <b>r.toInt()</b><br/>
            <i>Rundung zur nächsten ganzen Zahl</i><br/>
            Auch globale Funktion: <b>int(r)</b><br/>
        """

    def __long__(self):
        """ Round to the nearest integer
        """
        assert self.q > 0
        return (self.p + self.q/2) // self.q

    def _unify(self, other):
        return (self, Rational(other))

    def __repr__(self):
        """ Object representation as string
        """
        if self.q == 1:
            return str(self.p)
        else:
            return "%d/%d" % (self.p, self.q)

    def toStr(self):
        """ <b>r.toStr()</b><br/>
            <i>Representation as string</i><br/>
            Also as global function: <b>str(r)</b><br/>
        ----de----
            <b>r.toStr()</b><br/>
            <i>Darstellung als String</i><br/>
            Auch globale Funktion: <b>str(r)</b><br/>
        """

    def __cmp__(a, b):
        """ <b>a.__cmp__(b)</b><br/>
            <i>value comparision</i><br/>
            Also operators: <b>== != &lt; > &lt;= >=</b><br/>
        """
        if type(b) == float:
            return cmp(float(a), b)
        if not isinstance(b, Rational):
            a,b = a._unify(b)
        return cmp(a.p*b.q, b.p*a.q)

    def __eq__(self, other): # hjva
        if isinstance(other, float):
            return other == self.__float__()
        if isinstance(other, int):
            return other == self.__int__()        
        return self.p*other.q == other.p*self.q
    def __lt__(self, other):  #hjva
        if isinstance(other, float):
            return self.__float__() < other
        if isinstance(other, int):
            return self.__int__() < other
        return self.p*other.q < other.p*self.q
    def __gt__(self, other):  #hjva
        if isinstance(other, float):
            return self.__float__() > other
        if isinstance(other, int):
            return self.__int__() > other
        return self.p*other.q > other.p*self.q

    def __neg__(self):
        """ Unary operator -
            -a --> a.__neg__()
        """
        return Rational(-self.p, self.q)

    def __add__(a, b):
        """ <b>a.__add__(b)</b><br/>
            <i>Addition</i><br/>
            Also operator notation: <b>a + b</b><br/>
            Instead of <code>a = a + b</code> you can write <code>a += b</code>.
        """
        if type(b) == float:
            return float(a) + b
        if not isinstance(b, Rational):
            a, b = a._unify(b)
        return Rational(a.p*b.q + b.p*a.q, a.q*b.q)

    #~ def add(a,b):
        #~ """ <b>a.add(b)</b><br/>
            #~ <i>Summe</i><br/>
            #~ Auch Operatorschreibweise: <b>a + b</b><br/>
            #~ Statt a = a + b kann auch a += b geschrieben werden.
        #~ ----de----
            #~ <b>a.add(b)</b><br/>
            #~ <i>Summe</i><br/>
            #~ Auch Operatorschreibweise: <b>a + b</b><br/>
            #~ Statt a = a + b kann auch a += b geschrieben werden.
        #~ """
        #~ return a + b

    def __radd__(a, b):
        """ Addition, see __add__
        """
        return a + b

    def __sub__(a, b):
        """ Subtraction:
            a - b  --> a.__sub__(b),  if a is of type Rational
                       b.__rsub__(a), otherwise
        """
        if type(b) == float:
            return float(a) - b
        if not isinstance(b, Rational):
            a,b = a._unify(b)
        return Rational(a.p*b.q - b.p*a.q, a.q*b.q)

    #~ def sub(a,b):
        #~ """ <b>a.sub(b)</b><br/>
            #~ <i>Difference</i><br/>
            #~ Auch Operatorschreibweise: <b>a - b</b><br/>
            #~ Statt a = a - b kann auch a -= b geschrieben werden.
        #~ """
        #~ return a - b

    def __rsub__(b, a):
        """ Subtraction, see __sub__
        """
        if type(a) == float:
            return a - float(b)
        if not isinstance(a, Rational):
            b,a = b._unify(a)
        return a - b

    def __mul__(a, b):
        """ Multiplication:
            a * b  --> a.__mul__(b),  if a is of type Rational
                       b.__rmul__(a), otherwise
        """
        if type(b) == float:
            return float(a) * b
#        if type(b) == Poly:
#            return b * a
        if not isinstance(b, Rational):
            a,b = a._unify(b)
        return Rational(a.p*b.p, a.q*b.q)

    #~ def mul(a,b):
        #~ """ <b>a.mul(b)</b><br/>
            #~ <i>Produkt</i><br/>
            #~ Auch Operatorschreibweise: <b>a * b</b><br/>
            #~ Statt a = a * b kann auch a *= b geschrieben werden.
        #~ """
        #~ return a * b

    def __rmul__(b, a):
        """ Multiplication, see __mul__
        """
        return b * a

    def __div__(a, b):
        """ exact Division
            a / b  --> a.__div__(b),  if a is of type Rational
                       b.__rdiv__(a), otherwise
        """
        if type(b) == float:
            return float(a) / b
        if not isinstance(b, Rational):
            a,b = a._unify(b)
        return Rational(a.p*b.q, a.q*b.p)

    #~ def div(a,b):
        #~ """ <b>a.div(b)</b><br/>
            #~ <i>exakte Division</i><br/>
            #~ Auch Operatorschreibweise: <b>a / b</b><br/>
            #~ Statt a = a / b kann auch a /= b geschrieben werden.
        #~ """
        #~ return a * b

    def __rdiv__(b, a):
        """ exact Division, see __div__
        """
        if type(a) == float:
            return a / float(b)
        if not isinstance(a, Rational):
            b,a = b._unify(a)
        return Rational(a.p*b.q, a.q*b.p)

    def __truediv__(a, b):   return a.__div__(b)
    def __rtruediv__(a, b):  return a.__rdiv__(b)
    def __floordiv__(a, b):  return a.__div__(b)
    def __rfloordiv__(a, b): return a.__rdiv__(b)

def toNumber(s):
    """ <b>toNumber(s)</b><br/>
        <i>converts the string s into a rational or floating point number</i><br/>
        <b>Examples</b>:<br/>
        <code>toNumber("3.1")</code><br/>
        <code>toNumber("7/3")</code>
        ----de----
        <b>toNumber(s)</b><br/>
        <i>verwandelt den String s in eine rationale oder Gleitkommazahl</i><br/>
        <b>Beispiele</b>:<br/>
        <code>toNumber("3.1")</code><br/>
        <code>toNumber("7/3")</code>
    """
    if "." in s or "e" in s or "E" in s:
        return float(s)
    else:
        return Rational(s)


#===============================================================
#  Lineare Algebra
#  Klassen Vector und Matrix
#---------------------------------------------------------------

class Vector (list): # Vectors # Vektoren
    """ Class <code>Vector</code> (with arithmetic operators)<br/>
        <b>Vector(v)</b> (v Liste or Tuple)<br/>
        The Indices of the elements of Vector are counted from 0 (as in Python lists etc.).
        <b>Example:</b> <code>Vector([1,2,3])</code>
        ----de----
        Klasse <code>Vector</code> (mit arithmetischen Operatoren)<br/>
        <b>Vector(v)</b> (v Liste oder Tupel)<br/>
        Die Indizes der Elemente von Vector werden (wie in Python-Listen etc.) ab 0 gezählt.
        <b>Beispiel:</b> <code>Vector([1,2,3])</code>
    """
    def operators(self):
        """ <b>Vector.operators()</b><br/>
            <i>For documentation only</i><br/>
            The following operators are defined in the class <b>Vector</b>:<br/>
            <table>
             <tr><th>Op.</th><th>Function</th><th>Examples</th></tr>
             <tr><th>+</th><td>elementwise Addition</td><td><pre>a + b; a += b</pre></td></tr>
             <tr><th>-</th><td>elementwise Subtraction</td><td><pre>a - b; a -= b</pre></td></tr>
             <tr><th>*</th><td>if both operators are Vectors: inner product,
               otherwise: scalar multiplication (elementwise)</td><td><pre>a * b; a *= b</pre></td></tr>
             <tr><th>-</th><td>Unary minus</td><td><pre>-a</pre></td></tr>
             <tr><th>[ ]</th><td>Index operator</td><td><code>A[i]</code> (Element)</td></tr>
            </table>
            <font color="#000080" size="-2">This method is for documentation only. It has no effect.</font>
        ----de----
            <b>Vector.operators()</b><br/>
            <i>Nur zur Dokumentation</i><br/>
            Die Klasse <b>Vector</b> erlaubt folgende Operatoren:<br/>
            <table>
             <tr><th>Op.</th><th>Funktion</th><th>Beispiele</th></tr>
             <tr><th>+</th><td>Elementweise Addition</td><td><pre>a + b; a += b</pre></td></tr>
             <tr><th>-</th><td>Elementweise Subtraktion</td><td><pre>a - b; a -= b</pre></td></tr>
             <tr><th>*</th><td>wenn beide Operanden Vektoren sind: Skalarprodukt,
                sonst Skalarmultiplikation (elementweise)</td><td><pre>a * b; a *= b</pre></td></tr>
             <tr><th>-</th><td>unäres Minus</td><td><pre>-a</pre></td></tr>
             <tr><th>[ ]</th><td>Indexoperator</td><td><code>A[i]</code> (Element)</td></tr>
            </table>
            <font color="#000080" size="-2">Diese Methode dient nur zur Dokumentation. Sie hat keine Wirkung.</font>
        """
        pass

    def __init__(v, n):
        """ Constructor
        """
        if isinstance(n, list):
            super().__init__(n)  # hjva
            #list.__init__(v, n)
        elif isinstance(n, tuple):
            super().__init__(list(n))  #hjva
            #list.__init__(v, list(n))
        else:
            super().__init__([x for x in n])  #hjva
            #assert 1  # hjva : what about strings?

#    @staticmethod
    def fromFunction(n, fn, offset=0):
        """ <b>Vector.fromFunction(n, fn, offset=0)</b><br/>
            <i>Vector, the elements of which are to be calculated using the function fn</i><br/>
            Returns: <code>Vector([fn(i+offset) for i in range(n)])<code><br/>
            <b>Example:</b><br/>
            <code>Vector.fromFunction(5, sqrt, 1)</code> returns Vector([1.0, 1.414, 1.732, 2.0, 2.236])
        ----de----
            <b>Vector.fromFunction(n, fn, offset=0)</b><br/>
            <i>Vector, dessen Elemente mit der Funktion fn berechnet werden</i><br/>
            Rückgabewert: <code>Vector([fn(i+offset) for i in range(n)])<code><br/>
            <b>Beispiel:</b><br/>
            <code>Vector.fromFunction(5, sqrt, 1)</code> ergibt Vector([1.0, 1.414, 1.732, 2.0, 2.236])
        """
        return Vector([fn(i+offset) for i in range(n)])
    fromFunction= staticmethod(fromFunction)

#    @staticmethod
    def fromString(s):
        """ <b>Vector.fromString(s)</b><br/>
            <i>Vector from String</i><br/>
            Elements (may also bbe Rationals) must be given as comma separated string.<br/>
            <b>Example:</b> <code>Vector.fromString("1, 2/3, 2")</code>
        ----de----
            <b>Vector.fromString(s)</b><br/>
            <i>Vector aus String</i><br/>
            Elemente (auch rationale Zahlen) müssen im String durch Kommas getrennt werden.<br/>
            <b>Beispiel:</b> <code>Vector.fromString("1, 2/3, 2")</code>
        """
        return Vector([toNumber(x) for x in s.split(",")])
    fromString = staticmethod(fromString) # hjva for S60 version of python

    #def __getitem__(V, i):  #hjva
    #    return V[i] # V.__getitem__(i)
    #__getitem__ = staticmethod(__getitem__)
    def __getitem__(self, index):  # hjva
        return super().__getitem__(index)

    def __repr__(A):
        """ Object representation as string
        """
        return A.__class__.__name__+"(%s)" % list.__repr__(A)   # hjva real name shown

    def __invert__(v):
        """ Operator ~ (transposition)
        """
        return v.transp()

    def transp(v):
        """ <b>v.transp()</b><br/>
            <i>berechnet die transponierte Matrix (Spaltenvektor)</i><br/>
            kürzer: ~v
        ----de----
            <b>v.transp()</b><br/>
            <i>calculates the transposed Matrix (column vektor)</i><br/>
            shorter: ~v
        """
        return Matrix([[a] for a in v])

    def concat(x, y):
        """ <b>.concat(v)</b><br/>
            <i>Verkettung mit dem Vektor v</i>
        ----de----
            <b>.concat(v)</b><br/>
            <i>Concatenation with Vector v</i>
        """
        return Vector(list(x)+list(y))

    def __neg__(v):
        """ unary oparator - (negative Vektor)
        """
        return Vector([-x for x in v])

    def __add__(x, y):
        """ operators + and += (Elementwise addition)
        """
        #   a + b  --> a.__add__ (b), if a is of type Vector
        #              b.__radd__(a), otherwise
        n = len(x)
        assert n == len(y)
        return Vector([x[i]+y[i] for i in range(n)])

    def __sub__(x, y):
        """ operators - and -= (elementwise subtraction)
        """
        return x + (-y)

    def __mul__(x, y):
        """ Operators * and *=
            Multiplikation
            if both operands are vektors sind: inner product,
            otherwise scalar multiplication (elementwise)
        """
        if isinstance(y, Vector): # Skalarprodukt
            n = len(x)
            assert n == len(y)
            return sum([x[i]*y[i] for i in range(n)])
        else:
            return Vector([y*x[i] for i in range(len(x))])

    def __rmul__(x, c):
        return x * c

    def __imul__(x, c):
        for i in range(len(x)):
            x[i] *= c
        return x

    def norm(x):
        """ <b>.norm()</b><br/>
            <i>Norm des Vektors</i>
        ----de----
            <b>.norm()</b><br/>
            <i>Norm of the Vector</i>        
            
        """
        return math.sqrt(x*x)



class Matrix (Vector): # Matrices # Matrizen
    """ class <code>Matrix</code><br/>
        <i>see also: Menu: Insert -- Matrix</i><br/>
        <b>Matrix(v)</b>: v list of lists with uniform length.<br/>
        Example: <code>Matrix([[11,12,13],[21,22,23]])</code><br/>
        The class <code>Matrix</code> ist derived from <code>Vector</code>:<br/>
        A <code>Matrix</code> object ist a <code>Vector</code>
        of <code>Vector</code> objects with uniform length.<br/>
        The elements can be addressed using double indices (e.g.: <code>A[i,k]</code>).
        Indices are counted from 0 (as in Python lists etc.).<br/>
        see also. class methods with "Matrix."
        ----de----
        Klasse <code>Matrix</code><br/>
        <i>vgl. Menü: Einfügen -- Matrix</i><br/>
        <b>Matrix(v)</b>: v Liste von gleichlangen Listen,<br/>
        Beispiel: <code>Matrix([[11,12,13],[21,22,23]])</code><br/>
        Die Klasse <code>Matrix</code> ist abgeleitet von <code>Vector</code>:<br/>
        Ein <code>Matrix</code>-Objekt ist ein <code>Vector</code>
        von gleichlangen <code>Vector</code>-Objekten.<br/>
        Die Elemente können mit Doppelindizes (z.B.: <code>A[i,k]</code>) angesprochen werden.
        Indizes werden (wie in Python-Listen etc.) ab 0 gezählt.<br/>
        vgl. Klassenmethoden mit "Matrix."
    """

    def operators(self):
        """ <b>Matrix.operators()</b><br/>
            <i>For documentation only</i><br/>
            The following operators are defined in the class <b>Matrix</b>:<br/>
            <table>
             <tr><th>Op.</th><th>Function</th><th>Examples</th></tr>
             <tr><th>+</th><td>Addition</td><td><pre>a + b; a += b</pre></td></tr>
             <tr><th>-</th><td>Subtraction</td><td><pre>a - b; a -= b</pre></td></tr>
             <tr><th>*</th><td>Matrizenmultiplikation if both operands are Matrices, otherwise: Scalar multiplication</td><td><pre>a * b; a *= b</pre></td></tr>
             <tr><th>-</th><td>Unary minus</td><td><pre>-a</pre></td></tr>
             <tr><th>~</th><td>Transposed Matrix</td><td><pre>~A</pre></td></tr>
             <tr><th>|</th><td>Concatenation</td><td><pre>A | B; A |= B</pre></td></tr>
             <tr><th>[ ]</th><td>Index operator</td><td><code>A[i,k]</code><br/><code>A[i]</code> (Row Vector)</td></tr>
            </table>
            <font color="#000080" size="-2">This method is for documentation only. It has no effect.</font>
        ----de----
            <b>Matrix.operators()</b><br/>
            <i>Nur zur Dokumentation</i><br/>
            Die Klasse <b>Matrix</b> erlaubt folgende Operatoren:<br/>
            <table>
             <tr><th>Op.</th><th>Funktion</th><th>Beispiele</th></tr>
             <tr><th>+</th><td>Addition</td><td><pre>A + B; A += B</pre></td></tr>
             <tr><th>-</th><td>Subtraktion</td><td><pre>A - B; A -= B</pre></td></tr>
             <tr><th>*</th><td>Matrizenmultiplikation (wenn beide Operanden Matrizen sind) bzw. Skalarmultiplikation (sonst)</td><td><pre>a * b; a *= b</pre></td></tr>
             <tr><th>-</th><td>unäres Minus</td><td><pre>-A</pre></td></tr>
             <tr><th>~</th><td>Transponierte Matrix</td><td><pre>~A</pre></td></tr>
             <tr><th>|</th><td>Verkettung</td><td><pre>A | B; A |= B</pre></td></tr>
             <tr><th>[ ]</th><td>Indexoperator</td><td><code>A[i,k]</code><br/><code>A[i]</code> (Zeilenvektor)</td></tr>
            </table>
            <font color="#000080" size="-2">Diese Methode dient nur zur Dokumentation. Sie hat keine Wirkung.</font>
        """
        pass

    def __init__(A, v):
        """ Constructor
        """
        Vector.__init__(A, [Vector(v[i]) for i in range(len(v))])
        A._makeRational()

#    @staticmethod
    def null(m, n=0):
        """ <b>Matrix.null(m, n=0)</b><br/>
            <i>m*n-Null matrix</i><br/>
            Square Matrix, if n is omitted.<br/>
        ----de----
            <b>Matrix.null(m, n=0)</b><br/>
            <i>m*n-Nullmatrix</i><br/>
            Quadratische Matrix, falls n weggelassen wird.<br/>
        """
        if n == 0:
            n = m
        return Matrix([ [0 for k in range(n)]
                        for i in range(m)])
    null = staticmethod(null)

#    @staticmethod
    def id(n):
        """ <b>Matrix.id(n)</b><br/>
            <i>n*n Unity Matrix</i><br/>
        ----de----
            <b>Matrix.id(n)</b><br/>
            <i>n*n-Einheitsmatrix</i><br/>
        """
        return Matrix([ [int(i==k) for k in range(n)]
                        for i in range(n)])
    id = staticmethod(id)

#    @staticmethod
    def fromFunction(m, n, fn, offset=0):
        """ <b>Matrix.fromFunction(m,n, fn)</b><br/>
            <i>m*n-Matrix defined by function fn</i><br/>
            fn must be a binary function.<br/>
            Them the Matrix element <code>A[i,k]</code> is defined as <code>fn(i+offset,k+offset)</code>.<br/>
            <b>Example</b>:<br/>
            <code>Matrix.fromFunction(2,4, pow, 1)</code>
            returns the Matrix<br/><code>
            /&nbsp;1&nbsp;1&nbsp;1&nbsp;&nbsp;1&nbsp;\<br/>
            |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|<br/>
            \&nbsp;2&nbsp;4&nbsp;8&nbsp;16&nbsp;/</code>
        ----de----
            <b>Matrix.fromFunction(m,n, fn)</b><br/>
            <i>Durch Funktion fn berechnete m*n-Matrix</i><br/>
            fn muss eine zweistellige Funktion sein.<br/>
            Das allgemeine Element <code>A[i,k]</code> wird mit <code>fn(i+offset,k+offset)</code> berechnet.<br/>
            <b>Beispiel</b>:<br/>
            <code>Matrix.fromFunction(2,4, pow, 1)</code>
            liefert die Matrix<br/><code>
            /&nbsp;1&nbsp;1&nbsp;1&nbsp;&nbsp;1&nbsp;\<br/>
            |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|<br/>
            \&nbsp;2&nbsp;4&nbsp;8&nbsp;16&nbsp;/</code>
        """
        return Matrix([ [fn(i,k) for k in range(n)]
                        for i in range(m)])
    fromFunction = staticmethod(fromFunction)

#    @staticmethod
    def fromString(s):
        """ <b>Matrix.fromString(s)</b><br/>
            <i>Matrix given by a string</i><br/>
            The string s must contains the elementa row by row.<br/>
            The rows are divided by semicolon, the elemente within a row by comma.<br/>
            Elemente may also be rational (notated with slash).<br/>
            <b>Example</b>:
            <code>Matrix.fromString("1, 2, 3.14; 4/5, 5, 6")</code>
            returns the matrix<br/><code>
            /&nbsp;1&nbsp;&nbsp;&nbsp;2&nbsp;&nbsp;3.14&nbsp;\<br/>
            |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|<br/>
            \&nbsp;4/5&nbsp;&nbsp;5&nbsp;&nbsp;&nbsp;6&nbsp;&nbsp;/</code>
        ----de----
            <b>Matrix.fromString(s)</b><br/>
            <i>Matrix aus String</i><br/>
            Im String s werden die Elemente der Matrix zeilenweise angegeben.<br/>
            Die Zeilen werden durch Semikolon getrennt, die Elemente innerhalb der Zeilen durch Komma.<br/>
            Elemente können auch rational sein (mit Schrägstrich).<br/>
            <b>Beispiel</b>:
            <code>Matrix.fromString("1, 2, 3.14; 4/5, 5, 6")</code>
            liefert die Matrix<br/><code>
            /&nbsp;1&nbsp;&nbsp;&nbsp;2&nbsp;&nbsp;3.14&nbsp;\<br/>
            |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|<br/>
            \&nbsp;4/5&nbsp;&nbsp;5&nbsp;&nbsp;&nbsp;6&nbsp;&nbsp;/</code>
        """
        return Matrix([ [toNumber(a) for a in row.split(",")]
                        for row in s.split(";")])
    fromString = staticmethod(fromString) # hjva for S60 version of python

    def _makeRational(A):
        for i in A.rowRange():
            for k in A.colRange():
                if isInteger(A[i,k]):
                    A[i,k] = Rational(A[i,k])

    def copy(A):
        """ <b>.copy()</b><br/>
            <i>independent copy of the matrix ("clone")</i>
        ----de----
            <b>.copy()</b><br/>
            <i>unabhängige Kopie der Matrix</i>
        """
        return Matrix([ [copy(A[i,k]) for k in A.colRange()]
                        for i in A.rowRange()])

    def isSquare(A):
        """ <b>.isSquare()</b><br/>
            <i>Truth value (A is square matrix)</i>
        ----de----
            <b>.isSquare()</b><br/>
            <i>Wahrheitswert (A quadratisch)</i>
        """
        return A.height() == A.width()

    def str(A, i,k):
        """ <b>.str(i,k)</b><br/>
            <i>string representation of the element [i,k]</i>
        ----de----
            <b>.str(i,k)</b><br/>
            <i>String-Darstellung des Elements [i,k]</i>
        """
        if type(A[i,k]) == float:
            return "%g" % A[i,k]
        else:
            return str(A[i,k])

    def _getColWidth(A, k):
        return max([len(A.str(i,k)) for i in A.rowRange()])

    def _pp(A, name=""):
        w = [A._getColWidth(k) for k in A.colRange()]
        strW = sum(w) + 3 * (A.width()-1)
        if A.height() == 1:
            left, right = "[", "]"
        else:
            mid = (2*A.height()-3) * "|"
            left, right = "/"+mid+"\\",  "\\"+mid+"/"
        s = ""
        fill = len(name) * " "

        n = 2*A.height()-1
        for j in range(n):
            if j == A.height()-1:
                s += name
            else:
                s += fill
            i = j // 2
            if j % 2 == 0:
                s += left[j] + " "
                for k in A.colRange():
                    s += A.str(i,k).center(w[k])
                    if k < A.width()-1:
                        s += "   "
                s += " " + right[j] +  "\n"
            else:
                s += "|" + (strW+2) * " " +  "|\n"
        return s

    def __repr__(A):
        """ Object representation as string
        """
        return A._pp()

    def __getitem__(A, i):
        """ Definition of the Index operator []
            Counts from 0
            A[i]   --> i-th row vector
            A[i,k] --> element in i-th row, k-th column
        """
        if isinstance(i, tuple):
            return A[i[0]][i[1]]
        else:
            #return Vector(A[i])  # hjva
            return Vector.__getitem__(A, i) 

    def __setitem__(A, i, x):
        """ Definition of the Index operator [] for assignments
            Counts from 0
            A[i]   --> i-th row vector
            A[i,k] --> element in i-th row, k-th column
        """
        if isinstance(i, tuple):
            A[i[0]][i[1]] = x
        else:
            Vector.__setitem__(A, i, x)

    #~ def __delitem__(A, i):
        #~ """
        #~ """
        #~ if isinstance(i, tuple):
            #~ del A[i[0]][i[1]]
        #~ else:
            #~ Vector.__delitem__(A, i)

    def height(A):
        """ <b>.height()</b><br/>
            <i>Number of rows of the Matrix</i>
        ----de----
            <b>.height()</b><br/>
            <i>Anzahl der Zeilen der Matrix</i>
        """
        return len(A)

    def width(A):
        """ <b>.height()</b><br/>
            <i>Number of columns of the Matrix</i>
        ----de----
            <b>.width()</b><br/>
            <i>Anzahl der Spalten der Matrix</i>
        """
        return len(A[0])

    def rowRange(A):
        """ <b>.rowRange()</b><br/>
            <i>List of all row indices</i>
        ----de----
            <b>.rowRange()</b><br/>
            <i>Liste aller Zeilenindizes</i>
        """
        return range(A.height())

    def colRange(A):
        """ <b>.rowRange()</b><br/>
            <i>List of all column indices</i>
        ----de----
            <b>.rowRange()</b><br/>
            <i>Liste aller Spaltenindizes</i>
        """
        return range(A.width())

    def __neg__(A):
        """ unary minus operator
        """
        return Matrix([ [-A[i,k] for k in A.colRange()]
                        for i in A.rowRange()])

    def __cmp__(A, B):
        if A.heigth() != B.heigth():
            return A.heigth() - B.heigth()
        for i in A.rowRange():
            if A[i] != A[i]:
                return cmp(A[i], B[i])
        return 0

    def concat(A, B):
        """ <b>.concat(B)</b><br/>
            <i>Horizontal concatenation with B</i><br/>
            <b>Requires</b>: Both Matrices must have the same row count.
        ----de----
            <b>.concat(B)</b><br/>
            <i>Horizontale Verkettung mit B</i><br/>
            <b>Voraussetzung</b>: Die beiden Matrizen müssen gleich viele Zeilen haben.
        """
        assert A.height() == B.height()
        return Matrix([ list(A[i])+list(B[i]) for i in A.rowRange()])

    def __or__(A, B):
        """ <b>A.__or__(B)</b><br/>
            <i>Horizontal concatenation with B</i><br/>
            A | B is the same as A.concat(B)<br/>
            Instead of A = A | B you may write A |= B.
            <b>Requires</b>: Both matrices must have the same row count.
        """
        assert A.height() == B.height()
        return Matrix([ list(A[i])+list(B[i]) for i in A.rowRange()])

    def __add__(A, B):
        """ <b>A.__add__(B)</b><br/>
            <i>Matrix addition operator</i><br/>
            Instead of A = A + B you may write A += B.
        """
        #   a + b  --> a.__add__ (b), wenn a vom Typ Matrix ist
        #              b.__radd__(a), sonst
        assert A.height() == B.height() and A.width() == B.width()
        return Matrix([ [A[i,k]+B[i,k] for k in A.colRange()]
                        for i in A.rowRange()
                      ])

    def __sub__(A, B):
        """ <b>A.__sub__(B)</b><br/>
            <i>Matrix subtraction operator</i><br/>
            Instead of A = A - B you may write A -= B.
        """
        return A + (-B)

    def __mul__(A, B):
        """ <b>A.__sub__(B)</b><br/>
            <i>Scalar or matrix multiplication</i><br/>
            Instead of A = A * B you may write A *= B.
        """
        # If both operands are matrices, matrix multiplication is applied,
        # otherwise scalar multiplikation
        if isinstance(B, Matrix): # matrix multiplication
            assert A.width() == B.height()
            return Matrix(
                [ [ sum([A[i,j] * B[j,k] for j in A.colRange()])
                    for k in B.colRange()]
                  for i in A.rowRange()])
        elif isinstance(B, Vector):   # hjva 080406
            return Vector(
                [  sum([A[i,j] * B[j] for j in A.colRange()])
                  for i in A.rowRange()])
        else: # scalar multiplikation
            return Matrix([ [B*A[i,k] for k in A.colRange()]
                            for i in A.rowRange()])

    def __rmul__(A, B):
        assert not isinstance(B, Matrix)
        return A * B

    def __imul__(A, B):  # hjva otherwise the Vector method is called
        A = A.__mul__(B)
        return A


    def transp(A):
        """ <b>.transp()</b><br/>
            <i>returns the transposed Matrix</i><br/>
            short form: ~A
        ----de----
            <b>.transp()</b><br/>
            <i>berechnet die transponierte Matrix</i><br/>
            kürzer: ~A
        """
        return Matrix([ [A[i,k] for i in A.rowRange()]
                        for k in A.colRange()])

    def __invert__(A):
        """ Operator ~ (transposition)
        """
        return A.transp()

    def submatrix(A, i, k, m, n):
        """ <b>.submatrix(i, k, m, n)</b><br/>
            <i>m*n Submatrix (rows  i..i+m-1, columns k..k+n-1)</i><br/>
        ----de----
            <b>.submatrix(i, k, m, n)</b><br/>
            <i>m*n-Untermatrix (Zeilen i..i+m-1, Spalten k..k+n-1)</i><br/>
        """
        assert i+m-1 < A.height() and k+n-1 < A.width()
        return Matrix([ [A[i1,k1] for k1 in range(k,k+n)]
                        for i1 in range(i,i+m)])

    def complement(A, i, k):
        """ <b>.complement(i, k)</b><br/>
            <i>Matrix without row i and column k</i><br/>
            (Algebraic complement)
        ----de----
            <b>.complement(i, k)</b><br/>
            <i>Matrix ohne die Zeile i und die Spalte k</i><br/>
            (Algebraisches Komplement)
        """
        return Matrix([ [A[i1,k1] for k1 in A.colRange() if k1 != k]
                        for i1 in A.rowRange() if i1 != i])

    def minor(A, i, k):
        """ <b>.minor(i, k)</b><br/>
            <i>Minor for row i, column k</i><br/>
            (Determinant of the algebraic complement)
        ----de----
            <b>.minor(i, k)</b><br/>
            <i>Minor zur Zeile i und der Spalte k</i><br/>
            (Determinante des Algebraischen Komplements)
        """
        return A.complement(i,k).det()

    def cofactor(A, i, k):
        """ <b>.cofactor(i, k)</b><br/>
            <i>Cofactor for row i, columns k</i><br/>
            (signed minor)
        ----de----
            <b>.cofactor(i, k)</b><br/>
            <i>Kofaktor zur Zeile i und der Spalte k</i><br/>
            (Minor mit Vorzeichen)
        """
        return (-1)**(i+k) * A.minor(i,k)

    def adjoint(A):
        """ <b>.adjoint()</b><br/>
            <i>Adjoint matrix</i><br/>
        ----de----
            <b>.adjoint()</b><br/>
            <i>Adjungierte Matrix</i><br/>
        """
        assert A.isSquare()
        return Matrix([ [A.cofactor(k,i) for k in A.rowRange()]
                        for i in A.colRange()])
    def det(A):
        """ <b>.det()</b><br/>
            <i>Determinant of the matrix</i><br/>
        ----de----
            <b>.det()</b><br/>
            <i>Determinante der Matrix</i><br/>
        """
        if not A.isSquare():
            raise _MathGUIdeError("A is not a square matrix")
        n = A.height()
        if n == 1:
            return A[0,0]
        else:
            return sum([A[0,k] * A.cofactor(0,k)
                        for k in A.colRange()])

    def _gaussElim0(A, jordan=True):
        """ unsichere Vorstufe zu gaussElim
        """
        m, n = A.height(), A.width()
        k = 0
        for i0 in A.rowRange():
            k = i0
            # oberste Zeile für führende Eins passend durchmultiplizieren
            A[i0] *= 1/A[i0,k]

            # Passende Vielfache zu anderen Zeilen addieren, so dass
            # unterhalb der führenden Eins Nullen entstehen
            for i in range(i0+1, m):
                A[i] -= A[i0] * A[i,k]
            if jordan:
                # Gau�-Jordan: dto. auch oberhalb der führenden Eins
                for i in range(i0):
                    A[i] -= A[i0] * A[i,k]

    def gaussElim(A, jordan=True):
        """ <b>.gaussElim(jordan=True)</b><br/>
            <i>Transforms A to (reduced, if jordan==True) row echelon form.</i><br/>
            No return value!
        ----de----
            <b>.gaussElim(jordan=True)</b><br/>
            <i>reduziert A auf Zeilenstufenform.</i><br/>
            Kein Rückgabewert!
        """
        m, n = A.height(), A.width()
        k = -1
        for i0 in A.rowRange():
            # Bestimme die am weitesten links stehende Spalte k, die
            # (ab Zeile i0) von Null verschiedene Elemente enthält:
            k += 1
            aMax, iMax = 0, i0
            while aMax == 0 and k < n:
                for i in range(i0,m):
                    if abs(A[i,k]) > aMax:
                        aMax, iMax = abs(A[i,k]), i
                if aMax == 0:
                    k += 1
            if k < n:
                # Oberste Zeile mit der vertauschen, die das (dem Betrag nach)
                # größte Element in Spalte i0 enthält
                A[iMax], A[i0] = A[i0], A[iMax]

                # oberste Zeile für führende Eins passend durchmultiplizieren
                A[i0] *= 1/A[i0,k]

                # Passende Vielfache zu anderen Zeilen addieren, so dass
                # unterhalb der führenden Eins Nullen entstehen
                for i in range(i0+1, m):
                    A[i] -= A[i0] * A[i,k]
                if jordan:
                    # Gauß-Jordan: dto. auch oberhalb der führenden Eins
                    for i in range(i0):
                        A[i] -= A[i0] * A[i,k]

    def rank(A):
        """ <b>.rank()</b><br/>
            <i>Rank of the matrix</i><br/>
        ----de----
            <b>.rank()</b><br/>
            <i>Rang der Matrix</i><br/>
        """
        B = Matrix(A)
        B.gaussElim()
        r = 0
        while r < B.height() and B[r].norm() != 0:
            r += 1
        return r

    def inverse(A):
        """ <b>.inverse()</b><br/>
            <i>Inverse og the matrix</i><br/>
        ----de----
            <b>.inverse()</b><br/>
            <i>Inverse Matrix</i><br/>
        """
        if not A.isSquare():
            raise _MathGUIdeError("A is not a square matrix")
        n = A.height()
        I = Matrix.id(n)
        B = A.concat(I)
        B.gaussElim()
        if B.submatrix(0,0,n,n) != I:
            raise _MathGUIdeError("Matrix is not invertible")
        return B.submatrix(0,n,n,n)

##    def flatten(A):
##        assert isinstance(A[1,1], Matrix)
##        v = []
##        for i in A.rowRange():
##            v.append(list(reduce(Matrix.concat, A[i])))
##        return Matrix(v)

    def gramSchmidt(A):
        """ <b>A.gramSchmidt()</b><br/>
            <i>Orthogonalizing using the Gram–Schmidt process</i><br/>
            <code>A</code> must be the matrix of the vectors to be orthogonalized (als rows).<br/>
            <b>Example</b>:<br/><code>
            A = Matrix([[1,1],[2,0]])<br/>
            A.gramSchmidt()<br/>
            print A</code><br/>
            returns the matrix<br/><code>
            /&nbsp;1&nbsp;&nbsp;&nbsp;1&nbsp;\<br/>
            |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|<br/>
            \&nbsp;1&nbsp;&nbsp;-1&nbsp;/</code>
        ----de----
            <b>A.gramSchmidt()</b><br/>
            <i>Gram-Schmidt'sches Orthogonalisierungsverfahren.</i><br/>
            <code>A</code> muss Matrix aus den zu orthogonalisierenden Vektoren (als Zeilen) sein.<br/>
            <b>Beispiel</b>:<br/><code>
            A = Matrix([[1,1],[2,0]])<br/>
            A.gramSchmidt()<br/>
            print A</code><br/>
            liefert die Matrix<br/><code>
            /&nbsp;1&nbsp;&nbsp;&nbsp;1&nbsp;\<br/>
            |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|<br/>
            \&nbsp;1&nbsp;&nbsp;-1&nbsp;/</code>
        """
        n = A.height()
        for i in range(1,n):
            for k in range(i):
                A[i] -= A[k] * ((A[i]*A[k])/(A[k]*A[k]))

    def _luRecursive(A):
        """ Vorstufe: funktioniert nicht für jede reguläre Matrix!
        """
        assert A.isSquare()
        n = A.height()
        # Rekursionsabbruch bei 1*1-Matrix
        if n==1:
            return Matrix.id(1), A.copy()

        #     /a11 :  w  \   / 1      :  0 \   /a11:     w       \
        #     |..........|   |.............|   |................ |
        # A = |    :     | = |  1     :    | * |   :      1      |
        #     | ~v :  A1 |   | --- ~v :  I |   | 0 : A1- --- ~v*w|
        #     \    :     /   \ a11    :    /   \   :     a11     /
        v = Matrix([[A[i,0] for i in range(1,n)]])
        w = Matrix([[A[0,k] for k in range(1,n)]])

        A1 = Matrix([ [A[i,k] for k in range(1,n)]
                      for i in range(1,n)]) - (1/A[0,0]) * ~v * w

        L1, R1 = A1._luRecursive()

        #       /  1     :   0     \     /  a11 :     w       \
        #       | ................ |     | .................. |
        #  A =  |  1     :         |  *  |      :             |
        #       | --- ~v :   I     |     |   0  :   L1 * R1   |
        #       \ a11    :         /     \      :             /
        #
        #
        #       /  1     :   0     \     /  a11 :     w       \
        #       | ................ |     | .................. |
        #    =  |  1     :         |  *  |      :             |
        #       | --- ~v :   L1    |     |   0  :     R1      |
        #       \ a11    :         /     \      :             /
        #
        #    =           L            *          R

        def elementL(i,k):
            if   i==0:
                return int(k == 0)
            elif k==0:
                return v[0,i-1]/A[0,0]
            else:
                return L1[i-1,k-1]

        L = Matrix.fromFunction(n,n, elementL)

        def elementR(i,k):
            if i==0:
                if k==0:
                    return A[0,0]
                else:
                    return w[0,k-1]
            else:
                if k==0:
                    return 0
                else:
                    return R1[i-1,k-1]

        R = Matrix.fromFunction (n,n, elementR)
        return L,R

    def _luIter(self):
        A = self.copy()
        assert A.isSquare()
        n = A.height()
        for k in range(n-1):
            assert A[k,k] != 0 # sonst scheitert der Algorithmus!
            for i in range(k+1,n):
                A[i,k] /= A[k,k]
                for j in range(k+1,n):
                    A[i,j] -= A[i,k] * A[k,j]
        # A in linke und rechte Dreiecksmatrix zerlegen
        L = Matrix.id(n)
        U = Matrix.id(n)
        for i in range(n):
            for k in range(n):
                if k < i:  L[i,k] = A[i,k]
                else:      U[i,k] = A[i,k]
        return L, U

    def lup(self):
        """ <b>.lup()</b><br/>
            <i>LUP decomposition of the matrix</i><br/>
            Returns a triplet (L, U, P) with P*A = L*R, where:<br/>
            P is a Permutation matrix,<br/>
            L is a Lower triangular matrix where all diagonal elements are one.<br/>
            R is an upper triangular matrix.<br/>
            <bRequires</b>: Matrix ist invertible.
        ----de----
        <b>.lup()</b><br/>
            <i>LRP-Zerlegung (LUP decomposition) der Matrix</i><br/>
            Rückgabewert: Tripel (L, U, P)<br/>
            P: Permutationsmatrix<br/>
            L: linke Dreiecksmatrix mit Einsen auf Diagonale<br/>
            R: rechte Dreiecksmatrix<br/>
            Es gilt dann: P*A = L*R<br/>
            <b>Voraussetzung</b>: Matrix ist invertierbar.
        """
        A = self.copy()
        assert A.isSquare()
        n = A.height()
        def id(x):
            return x
        P = Matrix.id(n)
        for k in range(n-1):
            # Suche das dem Betrag nach größte Element
            # der k-ten Spalte ab der k-ten Zeile und seinen Zeilenindex
            absMax, kMax = max([(abs(A[i,k]), -i) for i in range(k,n)])
            kMax = -kMax # -i im Paar --> bei mehreren gleichen erstes
            assert absMax > 0

            # Vertausche die Zeile des größten Elements
            # mit der k-ten Zeile (Permutation und Matrix)
            P[k], P[kMax] = P[kMax], P[k]
            A[k], A[kMax] = A[kMax], A[k]

            for i in range(k+1,n):
                A[i,k] /= A[k,k]
                for j in range(k+1,n):
                    A[i,j] -= A[i,k] * A[k,j]

        # A in linke und rechte Dreiecksmatrix zerlegen
        L = Matrix.id(n)
        U = Matrix.id(n)
        for i in range(n):
            for k in range(n):
                if k < i:  L[i,k] = A[i,k]
                else:      U[i,k] = A[i,k]
        return L, U, P

    def solve(A, b):
        """ <b>A.solve(b)</b><br/>
            <i>Solution of the linear equation system Ax = b</i><br/>
            b may be Vektor or column Matrix.
        ----de----
            <b>A.solve(b)</b><br/>
            <i>Lösung x des linearen Gleichungssystems Ax = b</i><br/>
            b kann Vektor oder Spaltenmatrix sein.
        """
        if not isinstance(b, Matrix):
            assert isinstance(b, Vector)
            b = ~b
        return A.inverse() * b

    def leastSquares(A, b):
        """ <b>A.leastSquares(b)</b><br/>
            <i>Solution of the normal system</i><br/>
            Returns: <code>(~A*A).solve(~A*b)</code>
        ----de----
            <b>A.leastSquares(b)</b><br/>
            <i>Lösung der Normalgleichung</i><br/>
            Rückgabewert: <code>(~A*A).solve(~A*b)</code>
        """
        return (~A*A).solve(~A*b)

#    @staticmethod
    def random(m,n=0, r=10):
        """ <b>Matrix.random(m,n=0, r=10)</b><br/>
            <i>m*n matrix with random elements in 0..r-1</i>
        ----de----
            <b>Matrix.random(m,n=0, r=10)</b><br/>
            <i>m*n-Matrix mit Zufallswerten 0..r-1</i>
        """
        if n == 0:
            n = m
        return Matrix([ [rand(r) for k in range(n)]
                        for i in range(m)])
    random = staticmethod(random)

from math import log,exp   # hjva 
def fit(data, functions):
    """ <b>fit(data, functions)</b><br/>
        <i>Interpolation using the Gaussian method of least squares</i><br/>
        <code>fit (data, functions)</code>
        calculates (using the method of least squares)
        a linear combination of the functions in <code>functions</code>
        with the variable <code>x</code>.<br/>
        (corresponds to the Mathematica function <code>Fit</code>).<br/>
        <b>Example</b>:
        <code>fit ([[-1,2], [1,1], [2,1], [3,0], [5,3]], ["1", "x", "x**2"])</code><br/>
        calculates <code>[c1, c2, c3]</code> such that the function<br/>
        <code>f(x) = c1*1  + c2*x + c3 * x**2</code><br/>
        approximates the conditions f(-1)=2, f(1)=1, f(2)=1, f(3)=0, f(5)=3 .<br/>
        Result: "(6/5 * 1) + (-53/70 * x) + (3/14 * x**2)"
        ----de----
        <b>fit(data, functions)</b><br/>
        <i>Interpolation mit der Gaußschen Methode der kleinsten Quadrate</i><br/>
        <code>fit (data, functions)</code>
        berechnet nach der Methode der kleinsten Quadrate
        eine Linearkombination der Funktionen in <code>functions</code>
        mit der Variablen <code>x</code>.<br/>
        (entspricht der Mathematica-Funktion <code>Fit</code>).<br/>
        <b>Beispiel</b>:
        <code>fit ([[-1,2], [1,1], [2,1], [3,0], [5,3]], ["1", "x", "x**2"])</code><br/>
        berechnet <code>[c1, c2, c3]</code> so dass die Funktion<br/>
        <code>f(x) = c1*1  + c2*x + c3 * x**2</code><br/>
        die Bedingungen f(-1)=2, f(1)=1, f(2)=1, f(3)=0, f(5)=3 approximiert.<br/>
        Ergebnis: "(6/5 * 1) + (-53/70 * x) + (3/14 * x**2)"
    """
                              # from the example:
    m = len(data)             # m = 5
    n = len (functions)       # n = 3   / 1  -1   1 \         /  2  \
    A = Matrix.null(m, n)     #        |  1   1   1  |        |  1  |
    for i in A.rowRange():    # A =    |  1   2   4  |    b = |  1  |
        for k in A.colRange():#        |  1   3   9  |        |  0  |
            x = data[i][0]    #         \ 1   5  25 /         \  3  /
            A[i,k] = eval(functions[k])
    def f(i,k):
        return data[i][1]
    b = Matrix.fromFunction(m,1, f)
    y = A.leastSquares(b)     # Solution of the normal system (column matrix):
    s = ""                    # y = [[6/5], [-53/70], [3/14]]
    for i in y.rowRange():    # Create linear combination:
        s += "(%s * %s)" % (str(y[i,0]), str(functions[i]))
        if i < y.height()-1:
            s += " + "
    return s                  # "(6/5 * 1) + (-53/70 * x) + (3/14 * x**2)"



#===============================================================
#  Testing
#  to assert fuctionality
#---------------------------------------------------------------

def fromTo(a, b, step=1):
    """ <b>fromTo(a, b, step=1)</b><br/>
        <i>list of equidistant integers from <b>a</b> to <b>b</b></i><br/>
        If no <b>step</b> is given, <b>step</b> is automatically set
        to 1 (for a >= b) or -1 (for a &lt; b).<hr/>
        <b>Examples</b>:<br/>
        <code>fromTo(3, 6)</code> returns <code>[3,4,5,6]</code><br/>
        <code>fromTo(3, 6, 2)</code> returns <code>[3,5]</code><br/>
        <code>fromTo(6, 3)</code> returns <code>[6,5,4,3]</code><br/>
        <code>fromTo(6, 3, 1)</code> returns empty list<br/>
        <code>fromTo(6, 3, -2)</code> returns <code>[6,4]</code>.
    ----de----
        <b>fromTo(a, b, step=1)</b><br/>
        <i>Ganzzahlliste von a bis einschl. b</i><br/>
        Wenn <b>step</b> nicht übergeben wird, wird b>step</b> automatisch
        auf 1 (für a >= b) oder -1 (für a &lt; b) gesetzt.<hr/>
        <b>Beispiele</b>:<br/>
        <code>fromTo(3, 6)</code> ergibt <code>[3,4,5,6]</code><br/>
        <code>fromTo(3, 6, 2)</code> ergibt <code>[3,5]</code><br/>
        <code>fromTo(6, 3)</code> ergibt <code>[6,5,4,3]</code><br/>
        <code>fromTo(6, 3, 2)</code> ergibt die leere Liste<br/>
        <code>fromTo(6, 3, -2)</code> ergibt code>[6,4]</code>
    """
    if step > 0:
        return range(a, b+1, step)
    else:
        return range(a, b-1, step)

if __name__ == '__main__':
    from math import log, exp
    v =  Vector([Rational(i,7) for i in fromTo(1 , 8)])
    print( v)
    r = Rational(5,11)
    # Alternative Definitionen für die gleiche Matrix:
    A1 = Matrix([[Rational(2,3), 1, 1, 0],
                 [     3,        5, 0, 1]])

#    A2 = Matrix("""2/3, 1, 1, 0;
#                    3,  5, 0, 1""")

    A = Matrix.fromString('2/3, 1, 1, 0;  3, 5, 0, 1')  # hjva !!! not the same
    print("A eq A1:{}".format(A == A1))
    print('A.height=%d A.width=%d' % (A.height(),A.width()))
    print (A._pp('A =    '))
    print()

    B = A.submatrix(0,1,2,2)
    #B = A1.submatrix(0,0,2,2)   # hjva 080323
    print (B._pp('B =    '))
    print (B.inverse()._pp('B^-1 = '))
    print (Matrix.id(1)._pp('I1 = '))
    print (Matrix.id(2)._pp('I2 = '))

    # 2*4-Zufallsmatrix mit Werten im Bereich 0 bis 99
    R = Matrix.random(2, 4, 100)
    print (R._pp('Rand = '))
    # Transponierte Matrix
    # (lässt sich auch als R.transpose() schreiben)
    T = ~R
    print (T._pp('Tranpose = '))
    # Produktmatrix
    P = R * T
    print (P._pp('Product = '))

    
    # Determinante von P
    P.det()
    
    #b = Matrix([[Rational(5)],[Rational(1)]])
    b = Matrix('5;1')
    print()
    print ('b.height=%d b.width=%d' % (b.height(),b.width()))

    # Gaußsche Methode der kleinsten Quadrate:
    # Optimale Parabel durch die Punkte
    # [-1, 2], [1, 1], [2, 1], [3, 0], [5, 3]
    As = Matrix(
        [[1,-1, 1],
         [1, 1, 1],
         [1, 2, 4],
         [1, 3, 9],
         [1, 5,25]])

    #bs = ~Matrix([[2,1,1,0,3]])
    bs = Matrix.fromString('2; 1; 1; 0; 3')
    print (As.leastSquares(bs))

    #------------- Lineare Funktion:
    data1 = [[3,3], [6,3], [9,6]]
    fn1 = ['1', 'x']
    print ('fit(%s, %s):' % (str(data1), str(fn1)))
    print (fit(data1, fn1))
    #plot (x=3, 9, eval(f))

    #------------- Parabel:
    data2 = [[-1,2], [0,2], [1,1], [2,0]]
    fn2 = ['1', 'x', 'x**2']
    print ('fit(%s, %s):' % (str(data2), str(fn2)))
    print (fit(data2, fn2))   # (37/20 * 1) + (-9/20 * x) + (-1/4 * x**2)
    #plot (x=-1, 2, eval(f))

    #------------- Transzendente Funktion:
    #from math import log, exp
    data3 = [[1,1],[2,1],[3,3],[4,8]]
    fn3 = ['1', 'x*log(x)', 'exp(x)']
    print ('fit(%s, %s):' % (str(data3), str(fn3)))
    print (fit (data3, fn3))  # (0.4117 * 1) + (-0.2956 * x*log(x)) + (0.1695 * exp(x))
    #plot (x=1, 4, eval(f))


