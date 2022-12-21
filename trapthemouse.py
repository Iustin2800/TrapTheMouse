import pyxel
import os
import time
import sys

class App:
    def __init__(self,difficulty):
        """Initializes the game

        Args:
            difficulty (int): Difficulty of the AI (0-3), 0 means PvP and 1-3 PvE
        """
        pyxel.init(230, 180)
        pyxel.mouse(True)
        self.dim = (11, 11)
        self.dim_s = (10, 10)
        self.grid = []
        self.mouse = (5, 5)
        self.hover = (-1, -1)
        self.turn = 1
        self.difficulty = difficulty

        #init board
        for i in range(0, self.dim[0]):
            self.grid.append([])
            for j in range(0, self.dim[1]):
                if pyxel.rndi(1, self.dim[0] * self.dim[1]) <= 5 and self.mouse[0] != i and self.mouse[1] != j:
                    self.grid[i].append(-1)
                else:
                    self.grid[i].append(0)
        
        #loads resources
        pyxel.load("resources.pyxres")

        #runs game
        pyxel.run(self.update, self.draw)

    def possible_moves(self, y):
        """Gets all directions of movement on the grid table

        Args:
            y (int): position of the y axis on the grid

        Returns:
            a list of tuples made of 2 integers representing the directions
        """
        if y % 2 == 0:
            return [(-1,0),(1,0),(0,-1),(1,-1),(0,1),(1,1)]
        else:
            return [(-1,0),(1,0),(0,-1),(-1,-1),(0,1),(-1,1)]
                    

    def best_path(self, x, y):
        """Dijkstra's shortest path algorithm

        Args:
            x (int): position of the x axis on the grid
            y (int): position of the y axis on the grid

        Returns:
            a grid of weights which go from x and y to the nearest exit on the grid board
        """
        SPT = []
        sptSet = []

        #initializes the weight grid with large numbers
        for i in range(0, self.dim[0]):
            sptSet.append([])
            for j in range(0, self.dim[1]):
                sptSet[i].append(1000)
        sptSet[x][y] = 0
        SPT.append((x, y))

        #applies the first move
        moves = self.possible_moves(y)
        for move in moves:
            if 0 <= x + move[0] < self.dim[0] and 0 <= y + move[1] < self.dim[1] and self.grid[x + move[0]][y + move[1]] != -1:
                sptSet[x + move[0]][y + move[1]] = 1
        
        #runs the algorithm until it reaches an exit
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
            

    def update(self):
        """Update function
        """
        if pyxel.btnp(pyxel.KEY_Q):
             pyxel.quit()
        
        #checks over what hexagon the player is hovering over
        if (self.dim_s[1] + pyxel.mouse_y - 8) // 14 % 2 == 1:
            self.hover = ((self.dim_s[0] + pyxel.mouse_x - 8) // 18 - 1, (self.dim_s[1] + pyxel.mouse_y - 8) // 14 - 1)
        else:
            self.hover = ((self.dim_s[0] + pyxel.mouse_x - 0) // 18 - 1, (self.dim_s[1] + pyxel.mouse_y - 8) // 14 - 1)
        
        #player's hovering and turn
        if self.hover[0] >= 0 and self.hover[0] < self.dim[0] and self.hover[1] >= 0 and self.hover[1] < self.dim[1]:
            if self.grid[self.hover[0]][self.hover[1]] == -1 or self.hover[0] == self.mouse[0] and self.hover[1] == self.mouse[1]:
                self.hover = (-1, -1)
            elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.turn == 1:
                self.grid[self.hover[0]][self.hover[1]] = -1
                self.turn = 2

        #mouse' turn for other player
        if self.turn == 2 and self.difficulty == 0:
            if self.hover[0] >= 0 and self.hover[0] < self.dim[0] and self.hover[1] >= 0 and self.hover[1] < self.dim[1]:
                possible_moves = self.possible_moves(self.mouse[1])
                if self.grid[self.hover[0]][self.hover[1]] == -1 or self.hover[0] == self.mouse[0] and self.hover[1] == self.mouse[1]:
                    self.hover = (-1, -1)
                else:
                    ok = False
                    for move in possible_moves:
                        if self.mouse[0] + move[0] == self.hover[0] and self.mouse[1] + move[1] == self.hover[1]:
                            ok = True
                    if not ok:
                        self.hover = (-1, -1)
                if self.hover[0] != -1 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.mouse = self.hover
                    self.turn = 1
            ok = False
            possible_moves = self.possible_moves(self.mouse[1])
            for move in possible_moves:
                if self.grid[self.mouse[0] + move[0]][self.mouse[1] + move[1]] != -1:
                    ok = True
                if not 0 <= self.mouse[0] + move[0] < self.dim[0] or not 0 <= self.mouse[1] + move[1] < self.dim[1]:
                    print("PLAYER 2 WINS")
                    pyxel.quit()
            if not ok:
                print("PLAYER 1 WINS")
                pyxel.quit()
        
        #mouse' turn
        if self.turn == 2 and self.difficulty > 0:
            possible_moves = self.possible_moves(self.mouse[1])

            #check if a move is out of grid to end the game
            for move in possible_moves:
                if not 0 <= self.mouse[0] + move[0] < self.dim[0] or not 0 <= self.mouse[1] + move[1] < self.dim[1]:
                    print("YOU LOSE")
                    pyxel.quit()
            
            #runs the SP algorithm
            spt = self.best_path(self.mouse[0], self.mouse[1])

            #gets a goal tile that has been run by the SP algorithm that is in the spt grid
            target = None
            target_left = 1000
            for i in range(0, self.dim[0]):
                for j in range(0, self.dim[1]):
                    if (i == 0 or i == self.dim[0] - 1 or j == 0 or j == self.dim[1] - 1) and spt[i][j] != 1000 :
                        target = (i, j)
                        target_left = spt[i][j]
            
            #it runs from that goal to the mouse looking for the SP and stops 1 move before reaching the mouse' position
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

            #at difficulty of 1, it chooses a random next move
            #at difficulty of 2, it chooses the tile next to the best one
            #at difficulty of 3, it leaves the best tile as is
            if self.difficulty == 1 or target is None:
                possible_next_moves = []
                for move in possible_moves:
                    if 0 <= self.mouse[0] + move[0] < self.dim[0] and 0 <= self.mouse[1] + move[1] < self.dim[1] and self.grid[self.mouse[0] + move[0]][self.mouse[1] + move[1]] != -1:
                        possible_next_moves.append((self.mouse[0] + move[0], self.mouse[1] + move[1]))
                if len(possible_next_moves) > 0:
                    target = possible_next_moves[pyxel.rndi(0, len(possible_next_moves) - 1)]
            elif self.difficulty == 2:
                possible_next_moves = []
                for move in possible_moves:
                    if 0 <= self.mouse[0] + move[0] < self.dim[0] and 0 <= self.mouse[1] + move[1] < self.dim[1] and self.grid[self.mouse[0] + move[0]][self.mouse[1] + move[1]] != -1 and (abs(self.mouse[0] + move[0] - target[0]) <= 1 and abs(self.mouse[1] + move[1] - target[1]) <= 1):
                        possible_next_moves.append((self.mouse[0] + move[0], self.mouse[1] + move[1]))
                if len(possible_next_moves) > 0:
                    target = possible_next_moves[pyxel.rndi(0, len(possible_next_moves) - 1)]


            #if there is a next move, it will take it, if not, it will lose the game
            if target is not None:
                self.turn = 1
                self.mouse = target
            else:
                print("YOU WIN!")
                pyxel.quit()
        
            
    def draw(self):
        """Draw function of the app
        """
        pyxel.cls(0)

        #draws background
        for i in range(0, 240):
            if i % 2 == 0:
                pyxel.line(i, 0, i, 180, 1)
        
        #draws grid
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
        
        #draws mouse
        if self.mouse[1] % 2 == 1:
            pyxel.blt(self.dim_s[0] + self.mouse[0] * 18, self.dim_s[1] + self.mouse[1] * 14, 0, 0, 16, 16, 32, 0)
        else:
            pyxel.blt(self.dim_s[0] + self.mouse[0] * 18 + 8, self.dim_s[1] + self.mouse[1] * 14, 0, 0, 16, 16, 32, 0)
        

if len(sys.argv) > 1 and '0' <= sys.argv[1] <= '9':
    App(int(sys.argv[1]))