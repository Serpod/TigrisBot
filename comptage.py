import numpy as np
import math


def one(s, val):
    yield s, val
    if val != 0:
        yield "-"+s, -val
    if val > -1:
        if val < 8 and val != 1 and val != 2:
            fac = math.factorial(val)
            yield s+"!", fac
        if val > 1:
            sqrt = np.int(math.sqrt(val))
            # For python 3.8 : sqrt = math.isqrt(val)
            if sqrt**2 == val:
                yield "√"+s, sqrt
                yield "-√"+s, -sqrt


def multi(s1, val1, s2, val2):
    if s2[0] != "-":
        yield f"({s1} + {s2})", val1+val2
        yield f"({s1} - {s2})", val1-val2
    if val1 > 0 or val2 > 0:
        yield f"({s1} * {s2})", val1*val2
        if val2 != 0:
            v = val1/val2
            vi = np.int(v)
            if vi == v:
                yield f"({s1} / {s2})", vi
    # if val1 == val2:
    #     yield f"{s1} = {s2}", val1


def full(s, val):
    for so, valo in one(s, val): yield so, valo
    for i in range(1, len(s)):
        s1 = s[:i]
        s2 = s[i:]
        val1 = int(s1)
        val2 = int(s2)

        ss1 = np.empty((5*32**len(s1)-1,), dtype="U25")
        vals1 = np.empty((5*32**len(s1)-1,), dtype="int_")
        n1 = 0

        for n1, (so, valo) in enumerate(full(s1, val1)):
            ss1[n1] = so
            vals1[n1] = valo

        ss2 = np.empty((5*32**len(s2)-1,), dtype="U25")
        vals2 = np.empty((5*32**len(s2)-1,), dtype="int_")
        n2 = 0

        for n2, (so, valo) in enumerate(full(s2, val2)):
            ss2[n2] = so
            vals2[n2] = valo

        for i1 in range(n1+1):
            for i2 in range(n2+1):
                for si, vali in multi(ss1[i1], vals1[i1], ss2[i2], vals2[i2]):
                    for so, valo in one(si, vali): yield so, valo


def generate(x):
    s = str(x)
    for i in range(1, len(s)):
        s1 = s[:i]
        s2 = s[i:]
        val1 = int(s1)
        val2 = int(s2)

        ss1 = np.empty((5*32**len(s1)-1,), dtype="U25")
        vals1 = np.empty((5*32**len(s1)-1,), dtype="int_")
        n1 = 0

        for n1, (so, valo) in enumerate(full(s1, val1)):
            ss1[n1] = so
            vals1[n1] = valo

        ss1.resize((n1,))
        vals1.resize((n1, ))
        sorted1 = vals1.argsort()
        ss1 = ss1[sorted1]
        vals1 = vals1[sorted1]

        ss2 = np.empty((5*32**len(s2)-1,), dtype="U25")
        vals2 = np.empty((5*32**len(s2)-1,), dtype="int_")
        n2 = 0

        for n2, (so, valo) in enumerate(full(s2, val2)):
            ss2[n2] = so
            vals2[n2] = valo

        ss2.resize((n2,))
        vals2.resize((n2, ))
        sorted2 = vals2.argsort()
        ss2 = ss2[sorted2]
        vals2 = vals2[sorted2]

        i1 = i2 = 0
        b1 = b2 = 0

        while i1 < n1 and i2 < n2:
            if vals1[i1] == vals2[i2] and vals1[i1] >= 0:
                b1 = i1
                b2 = i2
                while i1 < n1 and vals1[i1] == vals2[i2]:
                    i1 += 1
                while i2 < n2 and vals2[i2] == vals1[i1-1]:
                    i2 += 1
                for a1 in range(b1, i1):
                    for a2 in range(b2, i2):
                        yield vals1[a1],  f"{ss1[a1]} = {ss2[a2]}"
            elif vals1[i1] < vals2[i2]:
                i1 += 1
            else:
                i2 += 1
