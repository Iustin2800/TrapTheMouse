import pyxel
import os
import time

class App:
    def __init__(self):
        pyxel.init(230, 180)
        pyxel.mouse(True)
        self.dim = (11, 11)
        self.dim_s = (10, 10)
        self.grid = []
        self.mouse = (5, 5)
        self.hover = (-1, -1)
        self.turn = 1
        self.difficulty = 1
        for i in range(0, self.dim[0]):
            self.grid.append([])
            for j in range(0, self.dim[1]):
                if pyxel.rndi(1, self.dim[0] * self.dim[1]) <= 5 and self.mouse[0] != i and self.mouse[1] != j:
                    self.grid[i].append(-1)
                else:
                    self.grid[i].append(0)
        pyxel.load("resources.pyxres")
        pyxel.run(self.update, self.draw)

    def possible_moves(self, y):
        if y % 2 == 0:
            return [(-1,0),(1,0),(0,-1),(1,-1),(0,1),(1,1)]
        else:
            return [(-1,0),(1,0),(0,-1),(-1,-1),(0,1),(-1,1)]

    def analyze(self, x, y, k):
        possible_moves = self.possible_moves(y)
        for move in possible_moves:
            if 0 <= x + move[0] < self.dim[0] and 0 <= y + move[1] < self.dim[1]:
                if self.grid[x + move[0]][y + move[1]] != -1:
                    saved = self.grid[x + move[0]][y + move[1]]
                    self.grid[x + move[0]][y + move[1]] = -1
                    siz = self.analyze(x + move[0], y + move[1], k + 1)
                    self.grid[x + move[0]][y + move[1]] = saved
                    if siz is not None and siz < self.grid[x + move[0]][y + move[1]]:
                        self.grid[x + move[0]][y + move[1]] = siz
                        return siz
            else:
                return k
                    

    def best_path(self, x, y):
        SPT = []
        sptSet = []
        for i in range(0, self.dim[0]):
            sptSet.append([])
            for j in range(0, self.dim[1]):
                sptSet[i].append(1000)
        sptSet[x][y] = 0
        SPT.append((x, y))
        moves = self.possible_moves(y)
        for move in moves:
            if 0 <= x + move[0] < self.dim[0] and 0 <= y + move[1] < self.dim[1] and self.grid[x + move[0]][y + move[1]] != -1:
                sptSet[x + move[0]][y + move[1]] = 1
        while True:
            min_vertex = None
            min = 1000
            for i in range(0, self.dim[0]):
                for j in range(0, self.dim[1]):
                    ok = True
                    for k in SPT:
                        if k[0] == i and k[1] == j:
                            ok = False
                    if ok and sptSet[i][j] < min:
                        min = sptSet[i][j]
                        min_vertex = (i, j)
            if min_vertex is not None:
                ok = False
                SPT.append(min_vertex)
                moves = self.possible_moves(min_vertex[1])
                for move in moves:
                    ok2 = True
                    for k in SPT:
                        if k[0] == min_vertex[0] + move[0] and k[1] == min_vertex[1] + move[1] and sptSet[k[0]][k[1]] < min + 1 or 0 <= min_vertex[0] + move[0] < self.dim[0] and 0 <= min_vertex[1] + move[1] < self.dim[1] and sptSet[min_vertex[0] + move[0]][min_vertex[1] + move[1]] < min + 1:
                            ok2 = False
                    if not 0 <= min_vertex[0] + move[0] < self.dim[0] or not 0 <= min_vertex[1] + move[1] < self.dim[1]:
                        ok = True
                        break
                    if ok2 and self.grid[min_vertex[0] + move[0]][min_vertex[1] + move[1]] != -1:
                        sptSet[min_vertex[0] + move[0]][min_vertex[1] + move[1]] = min + 1
                if ok:
                    break
            else:
                break
        return sptSet


    def best_move(self, possible_moves):
        if self.difficulty == 1:
            return pyxel.rndi(0, len(possible_moves) - 1)
            

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
             pyxel.quit()
        if (self.dim_s[1] + pyxel.mouse_y - 8) // 14 % 2 == 1:
            self.hover = ((self.dim_s[0] + pyxel.mouse_x - 8) // 18 - 1, (self.dim_s[1] + pyxel.mouse_y - 8) // 14 - 1)
        else:
            self.hover = ((self.dim_s[0] + pyxel.mouse_x - 0) // 18 - 1, (self.dim_s[1] + pyxel.mouse_y - 8) // 14 - 1)
        if self.hover[0] >= 0 and self.hover[0] < self.dim[0] and self.hover[1] >= 0 and self.hover[1] < self.dim[1]:
            if self.grid[self.hover[0]][self.hover[1]] == -1 or self.hover[0] == self.mouse[0] and self.hover[1] == self.mouse[1]:
                self.hover = (-1, -1)
            elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.turn == 1:
                self.grid[self.hover[0]][self.hover[1]] = -1
                self.turn = 2
        if self.turn == 2:
            possible_moves = self.possible_moves(self.mouse[1])
            for move in possible_moves:
                if not 0 <= self.mouse[0] + move[0] < self.dim[0] or not 0 <= self.mouse[1] + move[1] < self.dim[1]:
                    print("YOU LOSE")
                    pyxel.quit()
            spt = self.best_path(self.mouse[0], self.mouse[1])
            target = None
            target_left = 1000
            for i in range(0, self.dim[0]):
                for j in range(0, self.dim[1]):
                    if (i == 0 or i == self.dim[0] - 1 or j == 0 or j == self.dim[1] - 1) and spt[i][j] != 1000 :
                        target = (i, j)
                        target_left = spt[i][j]
            original_target = target
            while target_left > 1 and target_left != 1000 and target is not None:
                moves = self.possible_moves(target[1])
                new_target = None
                has_zero = False
                for move in moves:
                    if 0 <= target[0] + move[0] < self.dim[0] and 0 <= target[1] + move[1] < self.dim[1] and spt[target[0] + move[0]][target[1] + move[1]] == 0:
                        has_zero = True
                    if 0 <= target[0] + move[0] < self.dim[0] and 0 <= target[1] + move[1] < self.dim[1] and spt[target[0] + move[0]][target[1] + move[1]] != 0:
                        if spt[target[0] + move[0]][target[1] + move[1]] < target_left or ((spt[target[0] + move[0]][target[1] + move[1]] == target_left) and (abs(target[0] + move[0] - original_target[0]) < abs(target[0] - original_target[0]) or abs(target[1] + move[1] - original_target[1]) < abs(target[1] - original_target[1]))):
                            target_left = spt[target[0] + move[0]][target[1] + move[1]]
                            new_target = (target[0] + move[0], target[1] + move[1])
                target = new_target
                if has_zero:
                    break
            if target is not None:
                self.turn = 1
                self.mouse = target
            else:
                print("YOU WIN!")
                pyxel.quit()
            
    def draw(self):
        pyxel.cls(0)
        for i in range(0, 240):
            if i % 2 == 0:
                pyxel.line(i, 0, i, 180, 1)
        for j in range(0, self.dim[0]):
            for i in range(0, self.dim[1]):
                if j % 2 == 1:
                    if self.hover[0] == i and self.hover[1] == j:
                        pyxel.blt(self.dim_s[0] + i * 18, self.dim_s[1] + j * 14, 0, 16, 0, 16, 16, 0)
                    elif self.grid[i][j] == -1:
                        pyxel.blt(self.dim_s[0] + i * 18, self.dim_s[1] + j * 14, 0, 32, 0, 16, 16, 0)
                    else:
                        pyxel.blt(self.dim_s[0] + i * 18, self.dim_s[1] + j * 14, 0, 0, 0, 16, 16, 0)
                else:
                    if self.hover[0] == i and self.hover[1] == j:
                        pyxel.blt(self.dim_s[0] + i * 18 + 8, self.dim_s[1] + j * 14, 0, 16, 0, 16, 16, 0)
                    elif self.grid[i][j] == -1:
                        pyxel.blt(self.dim_s[0] + i * 18 + 8, self.dim_s[1] + j * 14, 0, 32, 0, 16, 16, 0)
                    else:
                        pyxel.blt(self.dim_s[0] + i * 18 + 8, self.dim_s[1] + j * 14, 0, 0, 0, 16, 16, 0)
        if self.mouse[1] % 2 == 1:
            pyxel.blt(self.dim_s[0] + self.mouse[0] * 18, self.dim_s[1] + self.mouse[1] * 14, 0, 0, 16, 16, 32, 0)
        else:
            pyxel.blt(self.dim_s[0] + self.mouse[0] * 18 + 8, self.dim_s[1] + self.mouse[1] * 14, 0, 0, 16, 16, 32, 0)
        
                
App()