import pygame

class Ship():
    def __init__(self,shipid,field,topleft,im,orientation):
        self.shipid = shipid
        self.size = len(field)
        self.field = field
        self.sunk = False
        self.topleft = topleft 
        self.hitlocs = []
        self.im = im
        self.orientation = orientation

        if orientation == 1:
            self.im = pygame.transform.rotate(self.im,90)
        if orientation == 2:
            self.im = pygame.transform.rotate(self.im,180)
        if orientation == 3:
            self.im = pygame.transform.rotate(self.im,270)

    def hit(self,loc):
        self.hitlocs.append(loc)
        if len(self.hitlocs) == self.size:
            self.sunk = True

    def render(self,screen):
        if self.sunk:
            shiprect = self.im.get_rect(topleft = self.topleft)
            screen.blit(self.im,shiprect)
