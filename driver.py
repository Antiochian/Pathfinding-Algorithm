# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 22:21:57 2020

@author: Antiochian

Note: lots of vestigial code here. Need to clean up.
"""


#2D pathfinding algorithm
import numpy as np
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
    'TILESIZE' : 18,
    'MARGIN' : 2,
    'X' :24,
    'Y' : 24,
    'FPS' : 30,
    'SEARCH_SPEED' : 10,
    'COLORS' : colordict
    }

#-------- A* ALGORITHM IMPLEMENTATION -----------

def choose_next(OPEN, GOALPOS):
    best = OPEN[0]
    for cell in OPEN[1:]:
        if cell.f_cost < best.f_cost:
            best = cell
        elif cell.f_cost == best.f_cost:
            if cell.actual_distance(GOALPOS) < best.actual_distance(GOALPOS):
                best = cell
    return best
    
def algorithm_tick(OPEN,CLOSED,cell_list, surface, GOALPOS): 
    current = choose_next(OPEN,GOALPOS)
    if current.istarget: 
        return  [], CLOSED, current #end early, we are already done
    OPEN.remove(current)
    CLOSED.append(current)
    current.update('closed', surface)   
    for neighbour in current.neighbours:
        if neighbour.status == 'blocked':
            pass
        elif neighbour in CLOSED:   
            if neighbour.get_f():
                current.parent = neighbour  
        elif neighbour in OPEN:
            if neighbour.get_g(current):
                neighbour.parent = current
            neighbour.get_f() 
        else:
            OPEN.append(neighbour)
            neighbour.update('active',surface)
    return OPEN, CLOSED, current


# ---------- SETUP OF GRID/PYGAME ENGINE ------------

def initial_setup(surface, STARTPOS,GOALPOS,cell_list, obstacle_list): 
    t0 = time.time()
    cell_list = decorate_grid(surface, cell_list,obstacle_list)
    cell_list[GOALPOS].istarget = True 
    cell_list[GOALPOS].draw_cell(surface)
    cell_list = populate_h_values(cell_list, GOALPOS)    
             
    for cell in cell_list:
        cell_list[cell].g_cost = math.inf
    cell_list[STARTPOS].g_cost = 0
    cell_list[STARTPOS].get_f()
    print("Initial setup in ",round(time.time()-t0,3)," seconds")
    return cell_list

def populate_h_values(cell_list, GOALPOS):
    for cell in cell_list:
        cell_list[cell].h_cost = cell_list[cell].actual_distance(GOALPOS)
    return cell_list

def refresh_cell_list(STARTPOS, GOALPOS, obstacle_list, surface, constants, cell_list, clean=True):
    if clean:
        cell_list = make_grid(constants,surface )
    else:
        for cell in cell_list:
            if cell_list[cell].status == 'start':
                cell_list[cell].update('closed',surface)
    cell_list = initial_setup(surface, STARTPOS,GOALPOS,cell_list, obstacle_list)
    if clean:
        cell_list[STARTPOS].update('start',surface)
    return cell_list

# --------------- ANIMATION LOOPS ----------------

def draw_mode(clock,surface,initial_coord, constants, cell_list, obstacle_list):
    FPS = constants['FPS']
    mouse_mode = cell_list[initial_coord].status
    if mouse_mode == 'blocked':
        mouse_mode = 'empty'
        target_modes = ('blocked')
    else:
        mouse_mode = 'blocked' #readability
        target_modes = ('empty', 'active', 'closed') #tiles you are allowed to draw on


    changed = []
    prevcoord = None
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
                return obstacle_list

def search_animation(cell_list, screen, constants,clock, obstacle_list, STARTPOS, GOALPOS):
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
        frac = (frac+1)%(FPS//search_speed)
        
        for event in pygame.event.get(): #detect events
            if event.type == pygame.QUIT or pygame.key.get_pressed()[27]: #exit or ESCAPE keypress
                pygame.quit()
                sys.exit() 
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousepos = pygame.mouse.get_pos()
                mousecoords = mousepos[0]//constants['TILESIZE'] ,mousepos[1]//constants['TILESIZE']
                if event.button == 3: #RIGHT CLICK
                    cell_list[STARTPOS].update('empty',screen)
                    cell_list[mousecoords].update('start',screen)
                    STARTPOS = mousecoords
                    pending_changes = True
                elif event.button == 1: #LEFT CLICK
                    #get new obstacle_list    
                    obstacle_list = draw_mode(clock,screen,mousecoords, constants, cell_list,obstacle_list)
                    STARTPOS = current.pos
                    #refresh cell list
                    pending_changes = True
                
            if pygame.key.get_pressed()[32]: #SPACE BAR keypress
                searching = not searching #alternate pause/play
                print("Searching: ", searching)
        
        if searching and pending_changes:
            pending_changes = False
            cell_list = refresh_cell_list(STARTPOS, GOALPOS, obstacle_list, screen, constants, cell_list, False)
            OPEN = [cell_list[STARTPOS]]
            CLOSED = []
            # pygame.display.flip()
        #ALGORITHM CODE GOES HERE
        if searching and not frac:
            OPEN, CLOSED, current = algorithm_tick(OPEN,CLOSED,cell_list, screen, GOALPOS)                     
        
        #pygame.display.flip() we actually dont need this, amazingly
        if not OPEN:
            return cell_list, current, obstacle_list

def traceback_animation(final_cell, surface, constants, clock):
    FPS = constants['FPS']
    playback_speed = constants['SEARCH_SPEED'] * 3
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
    # #add terrain
    STARTPOS = (3,3)
    GOALPOS = (20,20)
    obstacle_list = []
    #MANUAL DEBUG OBSTACLES
    for y in range(1,6):
        obstacle_list.append((4,y))
    for y in range(5,11):
        obstacle_list.append((6,y))
    cell_list = initial_setup(screen, STARTPOS,GOALPOS,cell_list, obstacle_list)
    cell_list[STARTPOS].update('start',screen)        
    while True:
        #flip between 3 mainloops
        cell_list, final_cell, obstacle_list = search_animation(cell_list,screen,constants,clock, obstacle_list, STARTPOS, GOALPOS)
        traceback_animation(final_cell, screen, constants,clock)
        wait_for_input(clock)
        cell_list = refresh_cell_list(STARTPOS, GOALPOS, obstacle_list, screen, constants, cell_list, True)
    return

if __name__ == "__main__":
    main(constants)
