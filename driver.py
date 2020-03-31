# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 22:21:57 2020

@author: Hal
"""


#2D pathfinding algorithm
import numpy as np
import pygame
import sys
import random
import time
from Cell_2D import Cell

# ALLOWED STATUSES
# blocked
# active
# empty
# start
# target

#initialise empty grid
def make_grid(constants):
    cell_list = {}
    for x in range(constants['X']):
        for y in range(constants['Y']):
            cell_list[(x,y)] = ( Cell( (x,y),'empty',constants) )     
    #build graph datastructure
    for pos in cell_list:
        cell_list[pos].add_neighbours(cell_list)
    return cell_list

def decorate_grid(cell_list, STARTPOS, GOALPOS):
    cell_list[(3,2)].status = 'blocked'
    cell_list[(3,3)].status = 'blocked'
    cell_list[(3,4)].status = 'blocked'
    cell_list[(3,4)].status = 'blocked'



    cell_list[(6,5)].status = 'blocked'
    cell_list[(6,6)].status = 'blocked'
    cell_list[(6,7)].status = 'blocked'
    cell_list[(6,8)].status = 'blocked'
    cell_list[(6,9)].status = 'blocked'
    # cell_list[(9,9)].status = 'blocked'
    # cell_list[(9,10)].status = 'blocked'
    # cell_list[(9,11)].status = 'blocked'
    # cell_list[(10,9)].status = 'blocked'
    # cell_list[(10,11)].status = 'blocked'
    # cell_list[(11,9)].status = 'blocked'
    # cell_list[(11,10)].status = 'blocked'
    #cell_list[(11,11)].status = 'blocked'
    
    cell_list[GOALPOS].istarget = True    
    
    cell_list[STARTPOS].g_cost = 0
    return cell_list

def choose_next(OPEN):
    best = OPEN[0]
    for cell in OPEN[1:]:
        if cell.f_cost < best.f_cost:
            best = cell
        elif cell.f_cost == best.f_cost:
            if cell.h_cost < best.h_cost:
                best = cell
            #best = min( (best,cell), key = lambda x : x.h_cost)  #TIEBREAKER
    return best
    
def algorithm_tick(OPEN,CLOSED,cell_list, surface):              
    current = choose_next(OPEN)
    if current.istarget:
        return  OPEN, CLOSED #end early, we are already done
    # print(current.pos, " = ",current.f_cost," chosen (g_cost/h_cost: ",current.g_cost,current.h_cost,")")
    OPEN.remove(current)
    CLOSED.append(current)
    current.update('closed', surface)
    for neighbour in current.neighbours:
        if neighbour in CLOSED or neighbour.status == 'blocked':
            pass
        else:
            neighbour.get_g(current)
            neighbour.get_f()
            #if not in open add to open and make active
            if neighbour not in OPEN:
                OPEN.append(neighbour)
                neighbour.update('active',surface)
    return OPEN, CLOSED

def populate_h_values(cell_list, GOALPOS):
    cell_list[GOALPOS].h_cost = 0
    OPEN = [cell_list[GOALPOS]]
    CLOSED = []
    count = 0
    t0 = time.time()
    while OPEN:
        count += 1
        current = OPEN[0] #take first value (precise order doesn't really matter I guess)
        OPEN.remove(current)
        CLOSED.append(current)
        for neighbour in current.neighbours:
            if neighbour in CLOSED or neighbour.status == 'blocked':
                pass
            else:
                neighbour.get_h(current)
                if neighbour not in OPEN:
                    OPEN.append(neighbour)
    print(count, " cells preprocessed in ", round(time.time()-t0,3), " seconds")
    return cell_list

def startup():
    colordict = {
        'EMPTY_COL' : (255,255,255),
        'BLOCK_COL' : (20,20,20),
        'ACTIVE_COL' : (0,255,0),
        'CLOSED_COL' : (255,0,0),
        'TARGET_COL' : (0,0,255),
        'BG_COL' : (0,0,0)
        }
    
    constants = {
        'TILESIZE' : 32,
        'MARGIN' : 2,
        'X' : 13,
        'Y' : 13,
        'COLORS' : colordict
        }
    
    FPS = 3
    Nx = constants['X']*constants['TILESIZE']
    Ny = constants['Y']*constants['TILESIZE']
    
    pygame.init()
    screen = pygame.display.set_mode((Nx,Ny))
    screen.fill(constants['COLORS']['BG_COL'])
    pygame.display.set_caption("Pathfinder")
    clock = pygame.time.Clock()
    
    
    cell_list = make_grid(constants)
    # #add terrain
    STARTPOS = (2,2)
    GOALPOS = (10,10)
    
    cell_list = decorate_grid(cell_list,STARTPOS, GOALPOS)
    cell_list = populate_h_values(cell_list, GOALPOS)    
    
    for cell in cell_list:
        cell_list[cell].draw_cell(screen)

    cell_list[STARTPOS].get_f()

    OPEN = [cell_list[STARTPOS]]
    current = OPEN[0]
    CLOSED = []
    searching = True
    while True:
        clock.tick(FPS)
        for event in pygame.event.get(): #detect events
            if event.type == pygame.QUIT or pygame.key.get_pressed()[27]: #detect attempted exit
                pygame.quit()
                sys.exit() 

        #ALGORITHM CODE GOES HERE
        OPEN, CLOSED = algorithm_tick(OPEN,CLOSED,cell_list, screen)                    
        
        #------------------------
        pygame.display.flip()
    return cell_list
debug = startup()