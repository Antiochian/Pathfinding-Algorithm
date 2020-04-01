# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 23:34:09 2020

@author: Antiochian

2D "Node" class for pathfinder
Could easily be generalised to higher dimensions just by adding an extra coordinate to the "pos" attribute and redefining the neighborhood
"""

import numpy as np
import pygame
import math
import time
# ALLOWED STATUSES
# blocked - impassable wall
# active - being considered (green)
# closed - already considered (red)
# empty - empty space (white)
# start - blue (also used for traceback)


class Cell:
    def __init__(self,pos,status,constants,istarget=False):
        self.pos = pos
        self.status = status
        self.istarget = istarget
        
        self.tile_size = constants['TILESIZE']
        self.X = constants['X']
        self.Y = constants['Y']
        self.colors = constants['COLORS']

        #screen geometry object        
        margin = constants['MARGIN']
        realx = pos[0] * constants['TILESIZE']
        realy = pos[1] * constants['TILESIZE']
        self.rect = pygame.Rect(realx,realy,self.tile_size-margin,self.tile_size-margin)
        
        self.neighbours = None
        self.parent = None
        
        self.f_cost = math.inf
        self.h_cost = math.inf
        self.g_cost = math.inf
        
    def add_neighbours(self,cell_list):
        #self explanatory
        #should only be called after all empty cells are initialised! (requires complete cell_list)
        coords = self.get_neighbour_coords()
        if self.neighbours:
            print("Warning: Existing neighbourlist being overwritten for cell #", self.pos)
        self.neighbours = []
        for c in coords:
            self.neighbours.append(cell_list[c])
        return

    def get_neighbour_coords(self):
        #defines a Moore neighbourhood by default
        vectors = []
        for dx in (-1,0,+1):
            for dy in (-1,0,+1):
                if not (dx == 0 == dy):
                    neighbour = np.array(self.pos)+np.array((dx,dy))
                    if self.in_bounds(neighbour):
                        vectors.append(tuple(neighbour))
        return vectors
    
    def in_bounds(self,pos):
        #check if in bounds
        if 0 <= pos[0] < self.X and 0 <= pos[1] < self.Y:
            return True
        else:
            return False

    def update(self,new_status, surf):
        #update self AND redraw if necessary
        if self.status != new_status:
            self.status = new_status
            self.draw_cell(surf)
        return
    
    def draw_cell(self,surf):
        if self.status == 'blocked':
            col = self.colors['BLOCK_COL']
        elif self.istarget or self.status == 'start':
            col = self.colors['TARGET_COL']
        elif self.status == 'active':
            col = self.colors['ACTIVE_COL']
        elif self.status == 'empty':
            col = self.colors['EMPTY_COL']
        elif self.status == 'closed':
            col = self.colors['CLOSED_COL']
        else:
            raise Exception("Invalid Status Type: ", self.status)
        pygame.draw.rect(surf, col, self.rect)
        pygame.display.update(self.rect) #only update a single tile to save space
        return
        
    def get_h(self,GOALPOS):
        #manhattanesque heuristic
        dx = abs(GOALPOS[0] - self.pos[0])
        dy = abs(GOALPOS[1] - self.pos[1])
        diags = min(dx,dy)
        self.h_cost = 14*diags + 10*abs(dx-dy)
        self.get_f()
        return
        
    def get_g(self,neighbour):
        neighbourpos = neighbour.pos
        dx = abs(neighbourpos[0] - self.pos[0])
        dy = abs(neighbourpos[1] - self.pos[1])
        ds = int(10*math.sqrt(dx**2 + dy**2))
        if neighbour.g_cost  < self.g_cost:
            self.g_cost = neighbour.g_cost + ds
            self.get_f()
            return True #if a change has happened
        else:
            self.get_f()
            return False #if it hasnt
    
    def get_f(self):
        self.f_cost = self.g_cost + self.h_cost    

def make_grid(constants,surface):
    t0 = time.time()
    cell_list = {}
    for x in range(constants['X']):
        for y in range(constants['Y']):
            cell_list[(x,y)] = ( Cell( (x,y),'empty',constants) )     
    #build graph datastructure
    for cell in cell_list:
        cell_list[cell].add_neighbours(cell_list)
        cell_list[cell].draw_cell(surface)
    print("Grid made in ",round(time.time()-t0,3), " seconds")
    return cell_list

def decorate_grid(surface, cell_list, obstacle_list):
    #place obstacles in grid
    if obstacle_list:
        for pos in obstacle_list:
            cell_list[pos].update('blocked', surface)
    return cell_list
        
        
        
