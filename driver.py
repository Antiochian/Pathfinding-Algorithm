# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 22:21:57 2020

@author: Antiochian
"""


#2D pathfinding algorithm
import pygame
import sys
import random
import time
import math
from Cell_2D import Cell
from Cell_2D import make_grid, decorate_grid


#------------- USEFUL CONSTANTS ---------------
#Solarized color scheme by Ethan Schoonover
colordict = {
    'EMPTY_COL' : (255,255,255), #light
    'BLOCK_COL' : (0,43,54), #dark
    'ACTIVE_COL' : (133,200,0), #green
    'CLOSED_COL' : (250,50,47), #red
    'TARGET_COL' : (38 ,139,210), #blue
    'BG_COL' : (0,43,54)
    }

constants = {
    'TILESIZE' : 30,
    'MARGIN' : 3,
    'X' :20,
    'Y' : 20,
    'FPS' : 30,
    'SEARCH_SPEED' : 15,
    'COLORS' : colordict,
    'GOALPOS' : (18,5),
    'STARTPOS' :(2,5)
    }

#-------- A* ALGORITHM IMPLEMENTATION -----------

def choose_next(OPEN):
    """
    Given list of choices OPEN, choose the one with lowest f_cost (lowest h_cost as a tiebreak)
    """
    best = OPEN[0]
    for cell in OPEN[1:]:
        if cell.f_cost < best.f_cost:
            best = cell
        elif cell.f_cost == best.f_cost:
            if cell.h_cost < best.h_cost:
                best = cell
    return best
    
def algorithm_tick(OPEN,CLOSED,cell_list, surface, GOALPOS): 
    """"The actual A* Algorithm itsself"""
    current = choose_next(OPEN)
    OPEN.remove(current)
    CLOSED.append(current)
    current.update('closed',surface)
    if current.istarget:
        return [], CLOSED, current
    
    for neighbour in current.neighbours:
        if neighbour.status == 'blocked' or neighbour in CLOSED:
            pass
        elif neighbour.get_g(current) or (neighbour not in OPEN):
            neighbour.parent = current
            if neighbour not in OPEN:
                neighbour.update('active',surface)
                OPEN.append(neighbour)
    return OPEN, CLOSED, current

# ---------- SETUP OF GRID/PYGAME ENGINE ------------

def initial_setup(surface, STARTPOS,GOALPOS,cell_list, obstacle_list): 
    #intialise cell values, treat start and goal cells specially
    t0 = time.time()
    cell_list = decorate_grid(surface, cell_list,obstacle_list)
    cell_list[GOALPOS].istarget = True 
    cell_list[GOALPOS].draw_cell(surface)    
             
    for cell in cell_list:
        cell_list[cell].get_h(GOALPOS)
    cell_list[STARTPOS].g_cost = 0
    cell_list[STARTPOS].get_f()
    #print("Initial setup in ",round(time.time()-t0,3)," seconds")
    return cell_list

def refresh_cell_list(STARTPOS, GOALPOS, obstacle_list, surface, constants, cell_list, clean=True):
    #reset simulation
    if clean:
        #completely wipe everything
        cell_list = make_grid(constants,surface )
    else:
        #retain existing grid/obstacle_list
        for cell in cell_list:
            if cell_list[cell].status == 'start':
                cell_list[cell].update('closed',surface)
    cell_list = initial_setup(surface, STARTPOS,GOALPOS,cell_list, obstacle_list)
    if clean:
        cell_list[STARTPOS].update('start',surface)
    return cell_list

# --------------- ANIMATION LOOPS ----------------

def draw_mode(clock,surface,initial_coord, constants, cell_list, obstacle_list):
    #while the user is pressing a mousebutton, draw walls/spaces accordingly
    FPS = constants['FPS']
    mouse_mode = cell_list[initial_coord].status
    if mouse_mode == 'blocked':
        mouse_mode = 'empty' #tile you will draw
        target_modes = ('blocked') #tiles you are allowed to overwrite
    else:
        mouse_mode = 'blocked' #readability
        target_modes = ('empty', 'active', 'closed')
    changed = []
    prevcoord = None #keep track if mouse has changed tile or not
    while True:
        clock.tick(FPS)
        mousepos = pygame.mouse.get_pos()
        coord = (mousepos[0]//constants['TILESIZE'] ,mousepos[1]//constants['TILESIZE'])
        if coord != prevcoord and coord not in changed:
            prevcoord = coord
            if coord not in changed and cell_list[coord].status in target_modes:
                changed.append(coord)
                if mouse_mode == 'blocked':
                    obstacle_list.append(coord)
                    cell_list[coord].update('blocked',surface)
                else:
                    obstacle_list.remove(coord)
                    cell_list[coord].update('empty',surface)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                #when user lets go of mouse button
                return obstacle_list

def search_animation(cell_list, screen, constants,clock, obstacle_list, STARTPOS, GOALPOS):
    #the beefiest animation loop, showing the algorithm doing its thing
    OPEN = [cell_list[STARTPOS]]
    current = cell_list[STARTPOS]
    CLOSED = []
    FPS = constants['FPS']
    search_speed = constants['SEARCH_SPEED']
    searching = False
    pending_changes = False
    frac = 0 #fraction of a frame
    while True:
        clock.tick(FPS)
        frac = (frac+1)%(FPS//search_speed) #regulates animation speed to slow it down
        
        for event in pygame.event.get(): #detect events
            if event.type == pygame.QUIT or pygame.key.get_pressed()[27]: #exit or ESCAPE keypress to quit
                pygame.quit()
                sys.exit() 
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousepos = pygame.mouse.get_pos()
                mousecoords = mousepos[0]//constants['TILESIZE'] ,mousepos[1]//constants['TILESIZE']
                if event.button == 3: #RIGHT CLICK to move start tile
                    cell_list[STARTPOS].update('empty',screen)
                    cell_list[mousecoords].update('start',screen)
                    STARTPOS = mousecoords
                    pending_changes = True
                elif event.button == 1: #LEFT CLICK to draw
                    #get new obstacle_list    
                    obstacle_list = draw_mode(clock,screen,mousecoords, constants, cell_list,obstacle_list)
                    STARTPOS = current.pos
                    #refresh cell list
                    pending_changes = True
                
            if pygame.key.get_pressed()[32]: #SPACE BAR keypress to pause/play
                searching = not searching
                print("Paused: ", not searching)
        
        if searching and pending_changes:
            pending_changes = False
            cell_list = refresh_cell_list(STARTPOS, GOALPOS, obstacle_list, screen, constants, cell_list, False)
            OPEN = [cell_list[STARTPOS]]
            CLOSED = []     
        #ALGORITHM CODE GOES HERE
        if searching and not frac:
            OPEN, CLOSED, current = algorithm_tick(OPEN,CLOSED,cell_list, screen, GOALPOS)                     
        if not OPEN:
            return cell_list, current, obstacle_list

def traceback_animation(final_cell, surface, constants, clock):
    #follow back shortest path
    FPS = constants['FPS']
    playback_speed = FPS
    current = final_cell
    frac = 0 #fraction of a frame
    seen = []
    while current.parent and current not in seen:
        clock.tick(FPS)
        frac = (frac+1)%(FPS//playback_speed)
        if not frac:
            seen.append(current)
            current = current.parent
            current.status = 'start'
            current.draw_cell(surface)
    return

def wait_for_input(clock):
    #timewaster loop
    while True:
        clock.tick(120)
        for event in pygame.event.get(): #detect events
            if event.type == pygame.QUIT or pygame.key.get_pressed()[27]: #detect attempted exit
                pygame.quit()
                sys.exit() 
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
            
#-------------- DRIVER FUNCTIONS ---------------

def main(constants):
    Nx = constants['X']*constants['TILESIZE']
    Ny = constants['Y']*constants['TILESIZE']
    pygame.init()
    screen = pygame.display.set_mode((Nx,Ny))
    screen.fill(constants['COLORS']['BG_COL'])
    pygame.display.set_caption("Pathfinder")
    clock = pygame.time.Clock()
    cell_list = make_grid(constants,screen)
    STARTPOS = constants['STARTPOS']
    GOALPOS = constants['GOALPOS']
    obstacle_list = []
    #MANUAL DEBUG OBSTACLES
    # for y in range(7,14):
    #     obstacle_list.append((10,y))
    #     pass
    # for y in range(5,11):
    #     obstacle_list.append((6,y))
    cell_list = initial_setup(screen, STARTPOS,GOALPOS,cell_list, obstacle_list)
    cell_list[STARTPOS].update('start',screen)        
    while True:
        #cycle between mainloops
        cell_list, final_cell, obstacle_list = search_animation(cell_list,screen,constants,clock, obstacle_list, STARTPOS, GOALPOS)
        traceback_animation(final_cell, screen, constants,clock)
        wait_for_input(clock)
        cell_list = refresh_cell_list(STARTPOS, GOALPOS, obstacle_list, screen, constants, cell_list, True)
    return

if __name__ == "__main__":
    main(constants)
