import time
import os
import ctypes
import sys
import pygame
from math import ceil

"""
--------------- Conway's game of life -----------------
Author: Mounir LBATH
Version: 1.0
Creation Date: 2020
-----------------------------------------------------------
"""


def setCursor():
    cursor_text = (
    'X                       ',
    'XX                      ',
    'X.X                     ',
    'X..X                    ',
    'X...X                   ',
    'X....X                  ',
    'X.....X                 ',
    'X......X                ',
    'X.......X               ',
    'X........X              ',
    'X.........X             ',
    'X..........X            ',
    'X......XXXXX            ',
    'X...X..X                ',
    'X..X X..X               ',
    'X.X  X..X               ',
    'XX    X..X              ',
    '      X..X              ',
    '       XX               ',
    '                        ',
    '                        ',
    '                        ',
    '                        ',
    '                        ')
    cs, mask = pygame.cursors.compile(cursor_text)
    cursor = ((24, 24), (0, 0), cs, mask)
    pygame.mouse.set_cursor(*cursor)

def DrawRoundRect(surface, color, rect, width, xr, yr):
    clip = surface.get_clip()
    
    # left and right
    surface.set_clip(clip.clip(rect.inflate(0, -yr*2)))
    pygame.draw.rect(surface, color, rect.inflate(1-width,0), width)

    # top and bottom
    surface.set_clip(clip.clip(rect.inflate(-xr*2, 0)))
    pygame.draw.rect(surface, color, rect.inflate(0,1-width), width)

    # top left corner
    surface.set_clip(clip.clip(rect.left, rect.top, xr, yr))
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.left, rect.top, 2*xr, 2*yr), width)

    # top right corner
    surface.set_clip(clip.clip(rect.right-xr, rect.top, xr, yr))
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.right-2*xr, rect.top, 2*xr, 2*yr), width)

    # bottom left
    surface.set_clip(clip.clip(rect.left, rect.bottom-yr, xr, yr))
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.left, rect.bottom-2*yr, 2*xr, 2*yr), width)

    # bottom right
    surface.set_clip(clip.clip(rect.right-xr, rect.bottom-yr, xr, yr))
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.right-2*xr, rect.bottom-2*yr, 2*xr, 2*yr), width)

    surface.set_clip(clip)


class Clickable:
    def __init__(self, pos, size, color, radius, screen, text):
        self.pos = pos
        self.size = size
        self.color = color
        self.radius = radius
        self.screen = screen
        self.originColor = color
        self.text = text

        self.drawSelf()

    def displayText(self, text):
        font = pygame.font.Font('freesansbold.ttf', 15)
        textSurf = font.render(text, True, (0,0,0))
        textRect = textSurf.get_rect()
        textRect.center = (self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2)
        self.screen.blit(textSurf, textRect)

    def changeColor(self, newColor):
        self.color = newColor
        self.drawSelf()

    def drawSelf(self):
        DrawRoundRect(self.screen, self.color, pygame.Rect(self.pos[0], self.pos[1],self.size[0],self.size[1]),0,self.radius,self.radius)
        self.displayText(self.text)

    def hover(self):
        mousePos = pygame.mouse.get_pos()
        if mousePos[0] >= self.pos[0] and\
            mousePos[0] <= self.pos[0] + self.size[0] and\
                mousePos[1] >= self.pos[1] and\
                    mousePos[1] <= self.pos[1] + self.size[1]:
            return True
        
        return False

class TextInput(Clickable):
    def __init__(self, pos, size, color, radius, screen):
        super().__init__(pos, size, color, radius, screen, "")
        self.is_active= False

    def updateText(self, event):
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            self.is_active = False
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-2]
            self.text += "|"
        elif len(self.text) <= 5 and event.unicode.isnumeric():
            self.text = self.text[:-1]
            self.text += event.unicode + "|"

        self.drawSelf()

class Grid:

    def __init__(self, x, y, zoom):
        self.x = ceil(x/zoom)
        self.y = ceil(y/zoom)
        self.zoom = zoom
        self.resetGrid()

    def resetGrid(self):
        self.grid = [[False] * self.x for i in range(self.y)]

    # posx > 0 and posx < self.x - 1, same thing for posy
    def neighBorhood(self, posx, posy):
        out = 0
        for i in range(-1,2):
            for j in range(-1,2):
                if not(i == 0 and j == 0) and self.grid[posy+i][posx+j] == True:
                    out += 1
        return out
                    
    
    def lifeGame(self, screen, nbSteps, speed,orientation = 1):
        clock = pygame.time.Clock()
        a = 1
        while True:            
            new_grid = [[False] * self.x for i in range(self.y)]
            for i in range(1,self.x-1):
                for j in range(1,self.y-1):
                    neigh = self.neighBorhood(i,j)
                    new_grid[j][i] =(neigh == 3) or (self.grid[j][i] == True and neigh == 2)
            
            self.grid = new_grid

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:   # Close pygame
                    pygame.quit()
                    sys.exit() 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE: # Pause animation if spacebar is pressed
                        return
            #Clear screen
            screen.fill((230,230,230))
            self.pyGameOut(screen, orientation)

            if speed != 0:
                clock.tick(speed)
            
            if nbSteps != 0 and nbSteps == a:
                break
            a += 1

    def pyGameOut(self, screen, orientation):
               
        a = 0 if orientation > 0 else self.y-1
        b = -1 if orientation < 0 else self.y

        for y in range(self.y):
            for x in range(self.x):
                if self.grid[y][x] == True:
                    self.drawPixel((0,0,0), screen, (x,y if orientation > 0 else (self.y - y - 1)))

        pygame.display.update()
        
    def drawPixel(self, color, screen, pos):
        screen.fill(color, ((self.zoom*pos[0], self.zoom*pos[1]), (self.zoom, self.zoom)))

def main():

    width = 1000
    height = 600
    
    my_grid = Grid(width,height, 10)

    running = True
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # centers the window
    screen = pygame.display.set_mode((width,height))
    pygame.display.set_caption('Game of life')
    setCursor()
    pygame.init()
    try:
        icon = pygame.image.load('./Clown.png')
        pygame.display.set_icon(icon)
    except:
        pass

    nbIterTxt = TextInput((10,10),(90,35), (240,240,240),5, screen)

    while running:
        # Before start -> Initialisation
        while running:
            screen.fill((255,255,255))
            if nbIterTxt.is_active:
                nbIterTxt.drawSelf()
            my_grid.pyGameOut(screen,1)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:   # Close pygame
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if nbIterTxt.is_active:
                        nbIterTxt.updateText(event)
                    elif event.key == pygame.K_SPACE: # Starts animation if spacebar is pressed
                        running = False
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE or event.key == pygame.K_ESCAPE:
                        my_grid.resetGrid()
                    elif event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                        nbIterTxt.is_active = True

            if pygame.mouse.get_pressed()[0]:
                try:
                    pos = pygame.mouse.get_pos()
                    my_grid.grid[pos[1]//my_grid.zoom][pos[0]//my_grid.zoom] = True
                    
                except AttributeError:
                    pass
            elif pygame.mouse.get_pressed()[2]:
                try:
                    pos = pygame.mouse.get_pos()
                    my_grid.grid[pos[1]//my_grid.zoom][pos[0]//my_grid.zoom] = False
                except AttributeError:
                    pass
                    
            # Update screen
            if running:
                pygame.display.update()

        #Run animation
        try:
            my_grid.lifeGame(screen,int(nbIterTxt.text[:-1]),40,1)
        except:
            my_grid.lifeGame(screen,0,40,1)


        running = True

main()
