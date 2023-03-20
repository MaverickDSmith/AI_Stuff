from prettytable import PrettyTable, ALL
import copy
import random
import math
import sys
x = PrettyTable()
x.hrules = ALL
x.header = False


class CheckmoveReturn:
    def __init__(self, x1=None, y1=None, ret=0, x2=None, y2=None, des=None):
        self.x1 = x1
        self.y1 = y1
        self.ret = ret
        if x2 is not None:
            self.x2 = x2
            self.y2 = y2
            self.des = des


class ThinkturnReturn:
    def __init__(self, gain=0, loss=0, tar=None, x=-1, y=-1):
        self.gain = gain
        self.loss = loss
        self.tar = tar
        self.x = x
        self.y = y


class ThinkmoveReturn:
    def __init__(self, jmp=False, gain=0, loss=0, x=-1, y=-1, tar=None, jmparr=None):
        self.jmp = jmp
        self.gain = gain
        self.loss = loss
        self.x = x
        self.y = y
        self.tar = tar
        self.jmparr = jmparr


def is_yours(board, color, x, y):
    if color:
        c1 = 'w'
        c2 = 'W'
    else:
        c1 = 'b'
        c2 = 'B'
    if x > 7 or x < 0 or y > 3 or y < 0:
        print("this location does not exist")
        return 0
    if board.state[x][y] == 'x':
        print("there is no piece here")
        return 0
    elif board.state[x][y] == c1 or board.state[x][y] == c2:
        return 1
    else:
        print("there is an enemy piece here")
        return 2

def decide(board, list, count):
    gain_weight = 1
    loss_weight = 1
    gains = []
    losses = []
    diff = []
    bestdiff = []
    possible = []
    jumps = []
    for i in range(len(list)):
        gains.extend(list[i].gain)
        losses.extend(list[i].loss)
        jumps.extend(list[i].jmparr)
    for i in range(len(gains)):
        diff.append(((gains[i]) * gain_weight) * ((count-losses[i]) * loss_weight))
        curr = list[(math.floor(i/4))]
        currtar = i % 4
        if board.checkmove(curr.x, curr.y, currtar).ret != 0:
            possible.append(True)
        else:
            possible.append(False)
            diff[i] = -(sys.maxsize-1)
    maxdiff = max(diff)
    if True in jumps:
        for i in range(len(diff)):
            if jumps[i] == True:
                if diff[i] == maxdiff:
                    if possible[i]:
                        bestdiff.append(i)
    if True not in jumps or not bestdiff:
        for i in range(len(diff)):
            if diff[i] == maxdiff:
                if possible[i]:
                    bestdiff.append(i)
    choice = random.choice(bestdiff)
    tar = (choice%4)
    ret = list[math.floor(choice/4)]
    ret.tar = tar
    return ret



class Board:
    def __init__(self, state=None, w=12, b=12):
        if state is None:
           state = [
               ['w','w','w','w'],
               ['w','w','w','w'],
               ['w','w','w','w'],
               ['x','x','x','x'],
               ['x','x','x','x'],
               ['b','b','b','b'],
               ['b','b','b','b'],
               ['b','b','b','b']
           ]
        self.state = state
        self.w = w
        self.b = b


    #def copy(self, new):
    #    for i in range(len(self.state))


    def prettyboard(self):
        emptytable = [
            ['x','x','x','x','x','x','x','x'],
            ['x','x','x','x','x','x','x','x'],
            ['x','x','x','x','x','x','x','x'],
            ['x','x','x','x','x','x','x','x'],
            ['x','x','x','x','x','x','x','x'],
            ['x','x','x','x','x','x','x','x'],
            ['x','x','x','x','x','x','x','x'],
            ['x','x','x','x','x','x','x','x']
        ]
        for i in range(len(self.state)):
            for h in range(len(self.state[i])):
                if i % 2 == 0:
                    emptytable[i][((2 * h)+1)] = self.state[i][h]
                else:
                    emptytable[i][(2 * h)] = self.state[i][h]
        return emptytable


    def thinkmove(self, w, x, y, depth, maxdepth,jmp=False):
        ret = ThinkmoveReturn()
        gain = [0] * 4
        loss = [0] * 4
        jumps = [False] * 4
        for i in range(4):
            temp = copy.deepcopy(self)
            cur = self.checkmove(x, y, i).ret
            if cur == 2:
                move = temp.move(x,y,i)
                gain[i] = 1
                jump = temp.thinkmove(w, move[0], move[1], depth, maxdepth, True)
                gain[i] += jump.gain############
                loss[i] += jump.loss
                jumps[i] = True
            if cur == 1 and not jmp:
                temp = copy.deepcopy(self)
                move = temp.move(x,y,i)
            if cur == 1 or (cur != 2) and jmp:
                turnret = temp.thinkturn(not w, .5, depth-1, maxdepth)
                gain[i] += turnret.loss########
                loss[i] += turnret.gain##########
        if True in jumps:
            ret.jmp = True
        maxs = gain.index(max(gain))###########
        if depth == maxdepth and not jmp:
            ret.gain = gain
            ret.loss = loss
        else:
            ret.gain = max(gain)#############
            ret.loss = max(loss)############
        ret.jmparr = jumps
        return ret


    def thinkturn(self, w, dific, depth, maxdepth):
        ret = ThinkturnReturn()
        if depth == 0:
            return ret
        if w:
            color = 'w'
            ally = 'W'
            count = self.w
        else:
            color = 'b'
            ally = 'B'
            count = self.b
        moves = []
        gains = []
        losses = []
        for i in range(len(self.state)):
            for h in range(len(self.state[i])):
                if self.state[i][h] == color or self.state[i][h] == ally:
                    think = self.thinkmove(w, i, h, depth, maxdepth)
                    think.x = i
                    think.y = h
                    moves.append(think)
                    if depth == maxdepth:
                        b= 2
                        #print(i,h,think.jmp, think.gain, think.loss)
        for i in moves:
            gains.append(i.gain)
            losses.append(i.loss)
        ret.gain = max(gains)
        ret.loss = max(losses)
        jumps = []
        notjumps = []
        if depth == maxdepth:
            for i in moves:
                if i.jmp == True:
                    jumps.append(i)
                else:
                    notjumps.append(i)
            if jumps:
                deci = decide(self, jumps, count)
                return deci
            else:
                deci = decide(self, notjumps, count)
                return deci
        return ret



    def checkmove(self, x, y, tar, jmp=False, color=None):
        targ = CheckmoveReturn()
        if color == None:
            color = self.state[x][y]
        if color.isupper():
            ally = color.lower()
        else:
            ally = color.upper()
        if (x == 0 or color == 'w') and tar <= 1: # top edge case
            return targ
        if (x == 7 or color == 'b') and tar >= 2: # bottom edge case
            return targ
        if x % 2 == 0 and y == 3 and (tar == 1 or tar == 2): #right edge case
            return targ
        if x % 2 == 1 and y == 0 and (tar == 0 or tar == 3): #left edge case
            return targ
        if x % 2 == 0 and tar <= 1:
            targ.x1 = x-1
            targ.y1 = y+tar
        if x % 2 == 0 and tar >= 2:
            targ.x1 = x+1
            targ.y1 = y+3-tar
        if x % 2 == 1 and tar <= 1:
            targ.x1 = x-1
            targ.y1 = y-1+tar
        if x % 2 == 1 and tar >= 2:
            targ.x1 = x+1
            targ.y1 = y+2-tar
        if self.state[targ.x1][targ.y1] == color or self.state[targ.x1][targ.y1] == ally:
            return targ
        elif self.state[targ.x1][targ.y1] == 'x':
            targ.ret = 1
            return targ
        elif jmp == False:
            temp = self.checkmove(targ.x1, targ.y1, tar, True, color)
            if temp.ret == 1:
                targ.des = self.state[targ.x1][targ.y1]
                targ.x2 = temp.x1
                targ.y2 = temp.y1
                targ.ret = 2
                return targ
        else:
            return targ
        return targ


    def move(self, x, y, tar):
        ret = []
        check = self.checkmove(x, y, tar)
        if check.ret == 1:
            self.state[check.x1][check.y1] = self.state[x][y]
            if check.x1 == 7 or check.x1 == 0:
                self.state[check.x1][check.y1] = self.state[check.x1][check.y1].upper()
            self.state[x][y] = 'x'
            ret.append(check.x1)
            ret.append(check.y1)
        elif check.ret == 2:
            self.state[check.x2][check.y2] = self.state[x][y]
            self.state[x][y] = 'x'
            self.state[check.x1][check.y1] = 'x'
            if check.x2 == 7 or check.x2 == 0:
                self.state[check.x2][check.y2] = self.state[check.x2][check.y2].upper()
            if check.des == 'w' or check.des == 'W':
                self.w -= 1
            if check.des == 'b' or check.des == 'B':
                self.b -= 1
            ret.append(check.x2)
            ret.append(check.y2)
        else:
            return False
        return ret


def main():
    state = [
        ['w', 'w', 'w', 'w'],
        ['w', 'w', 'w', 'w'],
        ['w', 'w', 'w', 'w'],
        ['x', 'b', 'x', 'x'],
        ['x', 'x', 'x', 'x'],
        ['b', 'b', 'b', 'b'],
        ['b', 'x', 'b', 'b'],
        ['b', 'b', 'b', 'b']
    ]
    numbering = [
        ['x', "0,0", 'x', "0,1", 'x', "0,2", 'x', "0,3"],
        ["1,0", 'x', "1,1", 'x', "1,2", 'x', "1,3", 'x'],
        ['x', "2,0", 'x', "2,1", 'x', "2,2", 'x', "2,3"],
        ["3,0", 'x', "3,1", 'x', "3,2", 'x', "3,3", 'x'],
        ['x', "4,0", 'x', "4,1", 'x', "4,2", 'x', "4,3"],
        ["5,0", 'x', "5,1", 'x', "5,2", 'x', "5,3", 'x'],
        ['x', "6,0", 'x', "6,1", 'x', "6,2", 'x', "6,3"],
        ["7,0", 'x', "7,1", 'x', "7,2", 'x', "7,3", 'x']
    ]
    directions = [
        ['0','x','1'],
        ['x','w','x'],
        ['3','x','2']
    ]
    x.add_rows(numbering)
    print("this is the cordinate system used")
    print(x)
    x.clear()
    x.add_rows(directions)
    print("this is the direction system used")
    print(x)
    a = Board()
    loop = True
    turn = input("Enter 'y' if you want the bot to go first\nEnter anything else to go first yourself:")
    botturn = False
    jump = False
    skip = False
    if turn == 'y':
        botturn = True
    while loop:
        x.clear()
        x.add_rows(a.prettyboard())
        print(x)
        if botturn or skip:
            move = a.thinkturn(botturn, .5, 4, 4)
            if move.jmp:
                while a.thinkturn(botturn, .5, 4, 4).jmp:
                    move = a.thinkturn(botturn, .5, 4, 4)
                    a.move(move.x, move.y, move.tar)
                botturn = False
                if skip:
                    skip = False
                    botturn = True
            else:
                a.move(move.x, move.y, move.tar)
                x.clear()
                botturn = False
                if skip:
                    skip = False
                    botturn = True
        else:
            x1 = int(input("enter your piece's row number(0-7)(99 to quit)(55 to auto-move):"))
            if x1 == 99:
                loop = False
                continue
            if x1 == 55:
                skip = True
                continue
            y1 = int(input("enter your piece's column number(0-3):"))
            if is_yours(a, botturn, x1, y1) == 1:
                d1 = int(input("enter your target direction"))
                if d1 > 3 or d1 < 0:
                    print("direction invalid")
                    continue
                check = a.checkmove(x1, y1, d1).ret
                if check == 0:
                    print("this movement is invalid")
                    continue
                elif check == 1 and not jump:
                    a.move(x1, y1, d1)
                    botturn = True
                    continue
                elif check == 2:
                    jump = True
                    a.move(x1, y1, d1)
                    continue
                else:
                    again = input("normal moves are not allowed after jumps\nEnter 'y' to attempt another jump\nEnter anything else give up your current turn at this point:")
                    if again == 'y':
                        continue
                    else:
                        botturn = True
                        continue


if __name__ == '__main__':
    main()
