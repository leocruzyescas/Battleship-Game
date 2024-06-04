import pygame
from pygame.locals import *

class Square(pygame.sprite.Sprite):
    def __init__(self,width,height,colour = (0,200,255),pos = (0,0),ims = (None,None,None),font = None,text = ""):
        super(Square, self).__init__()
        self.width = width
        self.height = height
        self.colour = colour
        self.pos = pos
        self.surf = pygame.Surface((width,height))
        self.surf.fill(self.colour)
        self.rect = self.surf.get_rect()
        self.attacked = -1
        self.hovered = True
        self.font = font
        self.text = text
        dark = pygame.Surface((width,height)).convert_alpha() #to darken the water texture
        darkp = 0.5
        dark.fill((1,1,1,int(darkp*255)))
        red = pygame.Surface((width,height)).convert_alpha()
        redp = 0.0
        red.fill((1,0,0,int(redp*255)))
        self.waterim, self.hitim, self.missim = ims
        self.redim = self.waterim
        if self.waterim is not None:
            self.waterim = self.waterim.convert_alpha()
            self.waterim.blit(dark, (0,0),special_flags=pygame.BLEND_RGBA_SUB)
            self.redim = self.redim.convert_alpha()
            self.redim.blit(red,(0,0),special_flags = pygame.BLEND_RGBA_SUB)
        self.hitcrops = [(0+width*i,0,width,height) for i in range(12)]#l,t,w,h, 12 images
        self.misscrops = [(0+width*i,0,width,height) for i in range(4)]

    def set_colour(self,newcolour):
        self.surf.fill(newcolour)
        self.hovered = True

    def set_colour_hard(self,newcolour):
        self.surf.fill(newcolour)
        self.colour = newcolour

    def reset_colour(self):
        self.surf.fill(self.colour)

    def setpos(self,x,y):
        self.pos = (x,y)

    def drawtext(self,screen):
        if self.text != "":
            l,t = self.pos
            text = self.font.render(self.text,True,(255,255,255),(0,0,0))
            rect = text.get_rect(center = (l+self.width//2,t+self.height//2))
            screen.blit(text,rect)

    def render(self,screen):
        if self.waterim is not None:
            imrect = self.waterim.get_rect(topleft = self.pos)
            #if self.hovered:
            #    screen.blit(self.redim,imrect)
            #else:
            #    screen.blit(self.waterim,imrect)
            screen.blit(self.waterim,imrect)
            self.hovered = False
        elif self.font is not None:
            self.drawtext(screen)
        else:
            screen.blit(self.surf,self.pos)
        if self.font is None:
            if self.attacked == 0:
                if self.missim is not None:
                    screen.blit(self.missim,self.pos,self.misscrops[3])
            elif self.attacked == 1:
                if self.hitim is not None:
                    screen.blit(self.hitim,self.pos,self.hitcrops[4])


