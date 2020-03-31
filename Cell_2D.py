# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 23:34:09 2020

@author: Hal
"""

import numpy as np
import pygame
import math

class Cell:
    def __init__(self,pos,status,constants,istarget=False):
        pos = np.array(pos)
        self.pos = pos
        self.status = status
        self.istarget = istarget
        self.tile_size = constants['TILESIZE']
        self.X = constants['X']
        self.Y = constants['Y']
        self.colors = constants['COLORS']
        
        margin = constants['MARGIN']
        realx = pos[0] * constants['TILESIZE']
        realy = pos[1] * constants['TILESIZE']
        self.rect = pygame.Rect(realx,realy,self.tile_size-margin,self.tile_size-margin)
        
        self.neighbours = None
        
        self.f_cost = None
        self.h_cost = None
        self.g_cost = None
        
    def add_neighbours(self,cell_list):
        #should only be called after all empty cells are initialised! (requires complete cell_list)
        coords = self.get_neighbour_coords()
        if self.neighbours:
            print("Warning: Existing neighbourlist being overwritten for cell #", self.pos)
        self.neighbours = []
        for c in coords:
            self.neighbours.append(cell_list[c])
        return

    def get_neighbour_coords(self):
        vectors = []
        for dx in (-1,0,+1):
            for dy in (-1,0,+1):
                if not (dx == 0 == dy):
                    neighbour = self.pos+np.array((dx,dy))
                    if self.in_bounds(neighbour):
                        vectors.append(tuple(neighbour))
        return vectors
    
    def in_bounds(self,pos):
        if 0 <= pos[0] < self.X and 0 <= pos[1] < self.Y:
            return True
        else:
            return False

    def update(self,new_status, surf):
        self.status = new_status
        self.draw_cell(surf)
        return
    
    def draw_cell(self,surf):
        if self.status == 'blocked':
            col = self.colors['BLOCK_COL']
        elif self.istarget:
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
        return
        

    def get_h(self,neighbour):
        neighbourpos = neighbour.pos
        dx = neighbourpos[0] - self.pos[0]
        dy = neighbourpos[1] - self.pos[1]
        self.ds = int(10*math.sqrt(dx**2 + dy**2))
        if self.h_cost == None:
            self.h_cost = neighbour.h_cost + self.ds
        else:
            self.g_cost = min(self.h_cost, neighbour.h_cost + self.ds)
        return
        
    def get_h_old(self,goalpos):
        if self.h_cost:
            print("Warning: Existing h-cost being overwritten")
        #by convention this is in units of deci-tiles
        dx = goalpos[0] - self.pos[0]
        dy = goalpos[1] - self.pos[1]
        
        #number of diagonal squares:
        diag = min(abs(dx),abs(dy))*14
        straight = abs(dx-dy)*10
        self.h_cost = diag + straight
        return
    
    def get_g(self,neighbour):
        neighbourpos = neighbour.pos
        dx = neighbourpos[0] - self.pos[0]
        dy = neighbourpos[1] - self.pos[1]
        self.ds = int(10*math.sqrt(dx**2 + dy**2))
        if self.g_cost == None:
            self.g_cost = neighbour.g_cost + self.ds
        else:
            self.g_cost = min(self.g_cost, neighbour.g_cost + self.ds)
        return
    
    def get_f(self):
        if self.g_cost == None:
            raise Exception ("No G value for pos ",self.pos)
        if self.h_cost == None:
            raise Exception ("No H value for pos ",self.pos)
            
        if self.f_cost == None:
            self.f_cost = self.g_cost + self.h_cost
        self.f_cost = min(self.f_cost, self.g_cost + self.h_cost)

        
        
        