

class Triplet:

    def __init__(self, exp, pos=0, neg=0):
        self.exp = exp
        self.pos = pos
        self.neg = neg

    # Verander deze funcs naar 1 func indien we een andere measure gebruiken :)
    def func1(self):
        if (self.pos + self.neg) == 0:
            return -200
        else:
            return self.pos / (self.pos+self.neg)
        # return self.pos

    def func2(self):
        return self.pos
        #return -self.neg

    def get_tuple(self):
        created_tuple = (-self.func1(), -self.func2(), len(self.exp), str(self.exp), self.exp)
        return created_tuple

    def comparator(a, b):
        ###############################################################
        # posalen = len(a.pos)
        # posblen = len(b.pos)
        # negalen = len(a.neg)
        # negblen = len(b.neg)
        # if posblen+negblen == 0:
        #     totalb = 0
        # else:
        #     totalb = (posblen/(posblen+negblen))
        # if posalen+negalen == 0:
        #     totala = 0
        # else:
        #     totala = (posalen/(posalen+negalen))
        # return totala < totalb
        ###############################################################

        # Look at positive coverage
        if a.func1() > b.func1():
            return 1
        elif a.func1() < b.func1():
            return -1

        # Look at negative coverage
        if a.func2() > b.func2():
            return 1
        elif a.func2() < b.func2():
            return -1

        # Equal
        return 0
