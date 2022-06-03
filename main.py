import time
import pygame
import random
import math
import webbrowser
import pygame.freetype

pygame.init()
pygame.font.init()

width, height = 900, 900
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Sudoku")

resetBoard = False


def log(func):
    def wrapper(*args, **kwargs):
        st = time.time()
        val = func(*args, **kwargs)
        tt = (time.time() - st) * 1000
        logFile = open("log.txt","a")
        logFile.write(f"'{func.__name__}()' function with id: {args[-1]}, finished in {tt}ms with the parameters (args: {args[:-1]}, kwargs: {kwargs}) with the return value of {val}\n")
        logFile.close()
        return val
    return wrapper


@log
def solve(grid, r_id):
    i, j = grid.find_next_empty()
    if grid.visualize and (round(time.time() * 1000) / grid.speed).is_integer() and round(
            time.time() * 1000) - grid.startTime < 5000:
        redraw_window(grid, False)
        pygame.display.update()
        grid.stop_vis = False
    elif time.time() * 1000 - grid.startTime > 5000 and not grid.stop_vis:
        grid.stop_vis = True
        print("Stopping Visualization")
    if i is None and j is None:
        # completed
        return True
    s_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    if grid.random: random.shuffle(s_list)
    for k in s_list:
        if grid.check_valid(i, j, k):
            grid.add(i, j, k)
            if solve(grid, r_id):
                return True
            grid.remove(i, j)
    return False


def hide_squares(grid, difficulty='easy'):
    if difficulty == 'hard':
        squares = 81 - 17
    elif difficulty == 'medium':
        squares = 81 - 20
    else:
        squares = 81 - 25

    hidden = []
    for i in range(squares):
        choice = random.choice(range(9)), random.choice(range(9))
        while choice in hidden:
            choice = random.choice(range(9)), random.choice(range(9))
        else:
            hidden.append(choice)

    for j in hidden:
        grid.grid[j[0]][j[1]].value = None
    for i in range(grid.size[0]):
        for j in range(grid.size[1]):
            if grid.grid[i][j].pos in hidden:
                grid.grid[i][j].value = None
            else:
                grid.grid[i][j].original = True


class Grid:
    def __init__(self, size):
        self.size = size
        self.cubeSize = width // self.size[0], height // self.size[1]
        self.grid = [[Square((i, j), (255, 255, 255)) for j in range(size[1])] for i in range(size[0])]
        self.strikes = 0
        self.visualize = False
        self.speed = 3
        self.random = False
        self.startTime = None
        self.removals = []
        self.stop_vis = False

    def draw(self):
        valSize = int((self.cubeSize[0] + self.cubeSize[1]) * 0.35)
        tempValSize = int((self.cubeSize[0] + self.cubeSize[1]) * 0.25)
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.grid[i][j].selected and self.grid[i][j] not in self.removals: self.grid[i][j].col = (
                    200, 200, 200)
                pos = self.grid[i][j].pos[0] * self.cubeSize[0], self.grid[i][j].pos[1] * self.cubeSize[1]
                pygame.draw.rect(win, self.grid[i][j].col, (pos[0], pos[1],
                                                            pos[0] + self.cubeSize[0], pos[1] + self.cubeSize[1]))
                if self.grid[i][j].value is not None:
                    if self.grid[i][j].original:
                        col = (0, 0, 0)
                    else:
                        col = (255, 128, 255)
                    font = pygame.font.SysFont("freesansbold.ttf", valSize)
                    text = font.render(str(self.grid[i][j].value), True, col)
                    win.blit(text, (pos[0] + self.cubeSize[0] * 0.38, pos[1] + self.cubeSize[1] * 0.28))
                if self.grid[i][j].tempValue is not None:
                    font = pygame.font.SysFont("freesansbold.ttf", tempValSize)
                    text = font.render(str(self.grid[i][j].tempValue), True, (170, 170, 170))
                    win.blit(text, (pos[0] + self.cubeSize[0] * 0.8, pos[1]))

    def draw_lines(self):
        for i in range(self.size[0] + 1):
            curXLine = i * self.cubeSize[0]
            if (i / 3).is_integer():
                pygame.draw.line(win, 0, (curXLine, 0), (curXLine, height), 4)
            else:
                pygame.draw.line(win, 0, (curXLine, 0), (curXLine, height), 2)
        for j in range(self.size[1] + 1):
            curYLine = j * self.cubeSize[1]
            if (j / 3).is_integer():
                pygame.draw.line(win, 0, (0, curYLine), (height, curYLine), 4)
            else:
                pygame.draw.line(win, 0, (0, curYLine), (height, curYLine), 2)

    def draw_strikes(self):
        mid = width // 2
        gap = 100
        if self.strikes == 1:
            pos = [mid]
        elif self.strikes == 2:
            pos = [mid - (gap / 2), mid + (gap / 2)]
        elif self.strikes == 3:
            pos = [mid - gap, mid, mid + gap]
        else: pos = 0

        for cur in pos:
            rectDim = 15, 60

            angle = 45
            rect_surf = pygame.Surface(rectDim, pygame.SRCALPHA)
            rect_surf.fill((255, 0, 0))
            rotatedRect = pygame.transform.rotate(rect_surf, angle)
            win.blit(rotatedRect, (cur - rectDim[0] // 2 - 18, height // 2 - rectDim[1] // 2 + 4))

            angle = 135
            rect_surf = pygame.Surface(rectDim, pygame.SRCALPHA)
            rect_surf.fill((255, 0, 0))
            rotatedRect = pygame.transform.rotate(rect_surf, angle)
            win.blit(rotatedRect, (cur - rectDim[0] // 2 - 18, height // 2 - rectDim[1] // 2 + 3))

    def find_next_empty(self):
        for j in range(self.size[1]):
            for i in range(self.size[0]):
                if self.visualize:
                    if self.grid[i][j].selected: self.grid[i][j].selected = False
                    self.grid[i][j].col = (0, 255, 255)
                if self.grid[i][j].value is None:
                    return i, j
        return None, None

    def add(self, i, j, value):
        self.grid[i][j].value = value
        if self.visualize: self.grid[i][j].col = (0, 255, 255)

    def remove(self, i, j):
        self.grid[i][j].value = None
        if self.visualize: self.grid[i][j].col = (128, 128, 255)

    def check_valid(self, x, y, value):
        # check row
        for i in range(self.size[0]):
            if self.grid[i][y].value == value and i != x:
                if not self.visualize:
                    for k in range(self.size[0]):
                        self.grid[k][y].col = (255, 128, 128)
                        self.removals.append(self.grid[k][y])
                    self.grid[i][y].col = (128, 0, 0)
                return False
        # check col
        for j in range(self.size[1]):
            if self.grid[x][j].value == value and j != y:
                if not self.visualize:
                    for k in range(self.size[1]):
                        self.grid[x][k].col = (255, 128, 128)
                        self.removals.append(self.grid[x][k])
                    self.grid[x][j].col = (128, 0, 0)
                return False
        # check sector
        sector = x // 3, y // 3
        for i in range(3):
            for j in range(3):
                if self.grid[sector[0] * 3 + i][sector[1] * 3 + j].value == value and i != x and j != y:
                    if not self.visualize:
                        for k in range(3):
                            for m in range(3):
                                self.grid[sector[0] * 3 + k][sector[1] * 3 + m].col = (255, 128, 128)
                                self.removals.append(self.grid[sector[0] * 3 + k][sector[1] * 3 + m])
                        self.grid[sector[0] * 3 + i][sector[1] * 3 + j].col = (128, 0, 0)
                    return False
        # valid number
        return True


class Square:
    def __init__(self, pos, col):
        self.pos = pos
        self.col = col
        self.value = None
        self.tempValue = None
        self.selected = False
        self.original = False


def game_over(grid):
    for i in range(grid.size[0]):
        for j in range(grid.size[1]):
            if grid.grid[j][i].selected: grid.grid[j][i].selected = False
            grid.grid[j][i].col = (255, 0, 0)
            grid.grid[j][i].tempValue = None
            if not grid.grid[j][i].original: grid.grid[j][i].value = None
            redraw_window(grid, False)
            pygame.display.update()

    for p in range(128):
        for i in range(grid.size[0]):
            for j in range(grid.size[1]):
                if grid.grid[j][i].selected: grid.grid[j][i].selected = False
                grid.grid[j][i].col = (255 - p * 2, 0, 0)
        redraw_window(grid, False)
        pygame.display.update()

    font = pygame.font.SysFont("franklingothicmedium", 100)
    text = font.render("GAME OVER", True, (255, 0, 0))
    win.blit(text, (200, 380))
    pygame.display.update()
    time.sleep(3)


def redraw_window(grid, draw_strikes):
    grid.draw()
    grid.draw_lines()
    if draw_strikes: grid.draw_strikes()


def main():
    clock = pygame.time.Clock()

    grid = Grid((9, 9))
    hoveringCube = 0, 0
    lastSel = None
    drawStrikes = False
    timeDrawnStrikes = 0
    done = False
    global resetBoard

    board = [[None for _ in range(9)] for _ in range(9)]

    for i in range(grid.size[0]):
        for j in range(grid.size[1]):
            grid.grid[i][j].value = board[j][i]
            if board[j][i] is not None: grid.grid[i][j].original = True

    grid.random = True
    grid.startTime = round(time.time() * 1000)
    r_id = rand_n_digits(10)
    solve(grid, r_id)
    hide_squares(grid)
    grid.random = False
    for removal in grid.removals:
        removal.col = (255, 255, 255)
    grid.removals = []

    run = True
    while run:
        clock.tick(60)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                if event.key == pygame.K_SPACE:
                    for i in range(grid.size[0]):
                        for j in range(grid.size[1]):
                            if not grid.grid[i][j].original: grid.grid[i][j].value = None
                            grid.grid[i][j].col = (255, 255, 255)
                    grid.visualize = True
                    grid.startTime = round(time.time() * 1000)
                    r_id = rand_n_digits(10)
                    if not solve(grid, r_id):
                        print("No solutions found")
                    else:
                        done = True
                    grid.visualize = False
                if event.key == pygame.K_r:
                    resetBoard = True
                    return True
                if lastSel is not None:
                    if event.key == pygame.K_1: lastSel.tempValue = 1
                    if event.key == pygame.K_2: lastSel.tempValue = 2
                    if event.key == pygame.K_3: lastSel.tempValue = 3
                    if event.key == pygame.K_4: lastSel.tempValue = 4
                    if event.key == pygame.K_5: lastSel.tempValue = 5
                    if event.key == pygame.K_6: lastSel.tempValue = 6
                    if event.key == pygame.K_7: lastSel.tempValue = 7
                    if event.key == pygame.K_8: lastSel.tempValue = 8
                    if event.key == pygame.K_9: lastSel.tempValue = 9
                    if event.key == pygame.K_BACKSPACE: lastSel.tempValue = None
                    if event.key == pygame.K_RETURN:
                        if lastSel.tempValue is not None:
                            if grid.check_valid(lastSel.pos[0], lastSel.pos[1], lastSel.tempValue):
                                lastSel.value = lastSel.tempValue
                                lastSel.tempValue = None
                                if grid.find_next_empty() == (None, None):
                                    for i in range(grid.size[0]):
                                        for j in range(grid.size[1]):
                                            if grid.grid[j][i].selected: grid.grid[j][i].selected = False
                                            grid.grid[j][i].col = (0, 255, 255)
                                            grid.grid[j][i].tempValue = None
                                            redraw_window(grid, False)
                                            pygame.display.update()
                            elif lastSel.tempValue is not None:
                                grid.strikes += 1
                                drawStrikes = True
                                timeDrawnStrikes = 0
                                lastSel.tempValue = None
                    if event.key == pygame.K_LEFT:
                        if 0 <= lastSel.pos[0] - 1 <= 8:
                            if not grid.grid[lastSel.pos[0] - 1][lastSel.pos[1]].original:
                                lastSel.col = (255, 255, 255)
                                lastSel.selected = False
                                lastSel = grid.grid[lastSel.pos[0] - 1][lastSel.pos[1]]
                                lastSel.selected = True
                    if event.key == pygame.K_RIGHT:
                        if 0 <= lastSel.pos[0] + 1 <= 8:
                            if not grid.grid[lastSel.pos[0] + 1][lastSel.pos[1]].original:
                                lastSel.col = (255, 255, 255)
                                lastSel.selected = False
                                lastSel = grid.grid[lastSel.pos[0] + 1][lastSel.pos[1]]
                                lastSel.selected = True
                    if event.key == pygame.K_UP:
                        if 0 <= lastSel.pos[1] - 1 <= 8:
                            if not grid.grid[lastSel.pos[0]][lastSel.pos[1] - 1].original:
                                lastSel.selected = False
                                lastSel.col = (255, 255, 255)
                                lastSel = grid.grid[lastSel.pos[0]][lastSel.pos[1] - 1]
                                lastSel.selected = True
                    if event.key == pygame.K_DOWN:
                        if 0 <= lastSel.pos[1] + 1 <= 8:
                            if not grid.grid[lastSel.pos[0]][lastSel.pos[1] + 1].original:
                                lastSel.col = (255, 255, 255)
                                lastSel.selected = False
                                lastSel = grid.grid[lastSel.pos[0]][lastSel.pos[1] + 1]
                                lastSel.selected = True

            elif event.type == pygame.QUIT:
                run = False

        mousePos = pygame.mouse.get_pos()
        lastHov = hoveringCube
        if not done and grid.grid[lastHov[0]][lastHov[1]] not in grid.removals:
            grid.grid[lastHov[0]][lastHov[1]].col = (255, 255, 255)
        hoveringCube = mousePos[0] // grid.cubeSize[0], mousePos[1] // grid.cubeSize[1]
        if pygame.mouse.get_focused() and not done and grid.grid[lastHov[0]][lastHov[1]] not in grid.removals:
            grid.grid[hoveringCube[0]][hoveringCube[1]].col = (230, 230, 230)

        if pygame.mouse.get_pressed(3)[0]:
            if grid.grid[hoveringCube[0]][hoveringCube[1]].original is False and not done:
                if lastSel is not None:
                    lastSel.selected = False
                    lastSel.col = (255, 255, 255)
                grid.grid[hoveringCube[0]][hoveringCube[1]].selected = True
                lastSel = grid.grid[hoveringCube[0]][hoveringCube[1]]

        if drawStrikes: timeDrawnStrikes += 1
        if timeDrawnStrikes == 90:
            drawStrikes = False
            for removal in grid.removals:
                removal.col = (255, 255, 255)
            timeDrawnStrikes = 0
            grid.removals = []
        if grid.strikes >= 3:
            redraw_window(grid, drawStrikes)
            pygame.display.update()
            time.sleep(1)
            game_over(grid)
            return True

        redraw_window(grid, drawStrikes)
        pygame.display.update()


class Button():
    def __init__(self, pos=(0,0), shape='rect', col=(180,180,180), hoverCol=(140,140,140),clickedCol=(0,0,0),
                 radius=None, width=25, height=20, text=None, icon=None, border=False, borderCol=(180,180,180),
                 borderWidth=2, clickEvent=None, adjustments=(0.0, 0.0),textSize=10):
        self.pos = pos
        self.shape = shape
        self.originalCol, self.col = col, col
        self.hoverCol = hoverCol
        self.clickedCol = clickedCol
        if radius == None: self.radius = max(width,height)
        else: self.radius = radius
        self.width = width
        self.height = height
        self.hoverBool = False
        self.clickedBool = False
        self.icon = icon
        self.text = text
        self.border = border
        self.borderCol = borderCol
        self.borderWidth = borderWidth
        self.clickEvent = clickEvent
        self.adjustments = adjustments
        self.textSize = textSize

    def draw(self):
        if self.shape == 'rect':
            if self.border: pygame.draw.rect(win,self.borderCol,(self.pos[0]-self.borderWidth,
                self.pos[1]-self.borderWidth,self.width + self.borderWidth*2,self.height + self.borderWidth*2))
            pygame.draw.rect(win,self.col,(self.pos[0],self.pos[1],self.width,self.height))
            if self.icon != None:
                icon = pygame.transform.scale(pygame.image.load(self.icon).convert(),(self.width, self.height))
                if self.hoverBool:
                    icon.fill(
                    (round(self.hoverCol[0] * 0.25), round(self.hoverCol[1] * 0.25),round(self.hoverCol[2] * 0.25)),
                    special_flags=pygame.BLEND_SUB)
                win.blit(icon,(self.pos[0], self.pos[1], self.width, self.height))
            elif self.text != None:
                font = pygame.font.SysFont("freesansbold.ttf",self.radius//self.textSize)
                text = font.render(self.text,True,(75,75,75))
                win.blit(text,(self.pos[0]+self.width*self.adjustments[0],self.pos[1]+self.height*self.adjustments[1]))
        elif self.shape == 'square':
            if self.border: pygame.draw.rect(win, self.borderCol, (self.pos[0]-self.borderWidth,
                self.pos[1]-self.borderWidth, self.radius + self.borderWidth*2, self.radius + self.borderWidth*2))
            pygame.draw.rect(win, self.col, (self.pos[0], self.pos[1], self.radius, self.radius))
            if self.icon != None:
                icon = pygame.transform.scale(pygame.image.load(self.icon).convert(), (self.radius, self.radius))
                if self.hoverBool:
                    icon.fill(
                            (round(self.hoverCol[0]*0.25),round(self.hoverCol[1]*0.25),round(self.hoverCol[2]*0.25)),
                            special_flags=pygame.BLEND_SUB)
                win.blit(icon,(self.pos[0], self.pos[1]))
            elif self.text != None:
                font = pygame.font.SysFont("freesansbold.ttf",self.radius)
                text = font.render(self.text,True,(0,0,0))
                win.blit(text,(self.pos[0]-self.radius/1.15,self.pos[1]-self.radius/3.3))
        elif self.shape == 'circle':
            if self.border: pygame.draw.circle(win,self.borderCol,self.pos,self.radius+self.borderWidth)
            pygame.draw.circle(win,self.col,self.pos,self.radius)
            if self.icon != None:
                icon = pygame.image.load(self.icon).convert()
                win.blit(icon,(self.pos[0]-self.radius, self.pos[1]-self.radius, self.radius,self.radius))
            elif self.text != None:
                font = pygame.font.SysFont("comicsans",self.radius)
                text = font.render(self.text,True,(0,0,0))
                win.blit(text,(self.pos[0]-self.radius/1.15,self.pos[1]-self.radius/3.3))

    def hover(self, mousePos):
        if math.hypot(mousePos[0]-self.pos[0], mousePos[1]-self.pos[1]) < self.radius \
                and self.shape == 'circle': self.hoverBool = True
        elif mousePos[0] > self.pos[0] and mousePos[1] > self.pos[1] and self.shape == 'rect' \
                and mousePos[0] < self.pos[0] + self.width \
                and mousePos[1] < self.pos[1] + self.height: self.hoverBool = True
        elif mousePos[0] > self.pos[0] and mousePos[1] > self.pos[1] and self.shape == 'square' \
                and mousePos[0] < self.pos[0] + self.radius \
                and mousePos[1] < self.pos[1] + self.radius: self.hoverBool = True
        else: self.hoverBool = False
        if self.hoverBool: self.col = self.hoverCol
        else: self.col = self.originalCol

    def clicked(self, mousePos):
        #checks circle
        if math.hypot(mousePos[0]-self.pos[0], mousePos[1]-self.pos[1]) < self.radius \
                and self.shape == 'circle': self.clickedBool = True
        elif mousePos[0] > self.pos[0] and mousePos[1] > self.pos[1]and self.shape == 'rect' \
                and mousePos[0] < self.pos[0] + self.width \
                and mousePos[1] < self.pos[1] + self.height: self.clickedBool = True
        elif mousePos[0] > self.pos[0] and mousePos[1] > self.pos[1] and self.shape == 'square' \
                and mousePos[0] < self.pos[0] + self.radius \
                and mousePos[1] < self.pos[1] + self.radius: self.clickedBool = True
        else: self.clickedBool = False
        if self.clickedBool:
            self.col = self.clickedCol
            return eval(self.clickEvent+'()')
        else: self.col = self.originalCol


def quit():
    pygame.quit()


def website():
    webbrowser.open('http://google.com')


def rand_n_digits(n):
    start = 10**(n-1)
    end = (10**n)-1
    return random.randint(start, end)


def controls():
    clock = pygame.time.Clock()


    fontsize = 36
    margin_y = 10
    spacing_y = 4
    font = pygame.freetype.SysFont("freesansbold.ttf", fontsize)

    sample_text = ("\n\n\nHOW TO PLAY\n\n" +
                   "Click On A Square To Select It\n" +
                   "Press a Number To Pencil It In\n" +
                   "Press Backspace To Remove It\n" +
                   "Press Enter to Confirm Number\n" +
                   "You Have 3 Attempts Before Game Over\n" +
                   "Press Space To Solve\n" +
                   "Press R To Reset Board\n\n\n" +
                   "RULES\n\n" +
                   "An Entered Number Cannot Have\n" +
                   "A Duplicate In A Row, Column Or Box\n" +
                   "To Win You Have To Fill All Squares")

    rendered_fonts = []
    for i, line in enumerate(sample_text.split('\n')):
        if line.isupper(): txt_surf, txt_rect = font.render(line, (0,0,0))
        else: txt_surf, txt_rect = font.render(line, (128,128,128))

        margin_x = width * 0.5 - txt_rect.size[0] // 2
        txt_rect.topleft = (margin_x, margin_y + i * (fontsize + spacing_y))
        rendered_fonts.append((txt_surf, txt_rect))

    back_button = Button(col=(200, 200, 200), pos=(width*0.8,height*0.9), width=155, height=30, text="ESC - BACK",
                         hoverCol=(180, 180, 180), clickedCol=(160, 160, 160), clickEvent='main_menu',
                         adjustments=(0.11, 0.22), textSize=5)

    # main loop
    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        win.fill((230,230,230))
        for txt_surf, txt_rect in rendered_fonts:
            win.blit(txt_surf, txt_rect)

        mouse = pygame.mouse.get_pos()
        back_button.draw()
        back_button.hover(mouse)

        if pygame.mouse.get_pressed(3)[0]: back_button.clicked(mouse)

        clock.tick(60)
        pygame.display.flip()
    return


def main_menu():
    global resetBoard
    clock = pygame.time.Clock()
    buttonDim = round(width * 0.7), round(height * 0.1)
    gap = round(height * 0.05)
    sudoku_logo = Button(pos=(round(width * 0.31), round(height*0.05)),radius=350,icon='icon_large.png',
                         hoverCol=(180, 180, 180),clickedCol=(160, 160, 160),clickEvent='website',shape='square',
                         border=True,borderWidth=15,borderCol=(0,0,0))
    start_button = Button(col=(200,200,200), pos=(width // 2 - buttonDim[0] // 2,
                        round(height*0.7)-gap-round(buttonDim[1]*1.5)), width=buttonDim[0], height=buttonDim[1],
                        text="START", hoverCol=(180, 180, 180), clickedCol=(160, 160, 160),clickEvent='main',
                        adjustments=(0.4, 0.28))
    continue_button = Button(col=(200, 200, 200), pos=(width // 2 - buttonDim[0] // 2,
                        round(height*0.7)-buttonDim[1]//2), width=buttonDim[0], height=buttonDim[1],
                        text="HOW TO PLAY", hoverCol=(180, 180, 180), clickedCol=(160, 160, 160), clickEvent='controls',
                        adjustments=(0.28, 0.28))
    quit_button = Button(col=(200, 200, 200), pos=(width // 2 - buttonDim[0] // 2,
                        round(height*0.7)+gap+buttonDim[1]//2), width=buttonDim[0], height=buttonDim[1],
                        text="QUIT", hoverCol=(180, 180, 180), clickedCol=(160, 160, 160), clickEvent='quit',
                        adjustments=(0.43, 0.28))

    run = True
    #print(pygame.font.get_default_font())
    while run:
        clock.tick(60)
        win.fill((230,230,230))
        mouse = pygame.mouse.get_pos()
        start_button.draw()
        start_button.hover(mouse)
        continue_button.draw()
        continue_button.hover(mouse)
        quit_button.draw()
        quit_button.hover(mouse)
        sudoku_logo.draw()
        sudoku_logo.hover(mouse)
        if pygame.mouse.get_pressed(3)[0]:
            start_button.clicked(mouse)
            continue_button.clicked(mouse)
            quit_button.clicked(mouse)
            sudoku_logo.clicked(mouse)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
            elif event.type == pygame.QUIT:
                pygame.quit()

        if  (x := width//2-buttonDim[0]//2) < mouse[0] < x + buttonDim[0] and \
            (y := round(height * 0.7) - gap - round(buttonDim[1] * 1.5)) < mouse[1] < y + buttonDim[1]:
            startButtonCol = (220,220,220)
        else: startButtonCol = (200, 200, 200)

        if resetBoard:
            resetBoard = False
            main()

        pygame.display.update()


if __name__ == "__main__":
    while main_menu(): pass
    pygame.quit() 