import pygame
from pygame.locals import *

class Button():
    def __init__(self,
            buttonid,
            left,
            top,
            width,
            height,
            text = "",
            font = None,
            im = None,
            rounded = True,
            displayed = True,
            borderwidth = 2,
            fontcolour = (0,0,0),
            hovercolour = (180,180,200),
            buttoncolour = (150,150,170),
            clickedcolour = (180,180,200),
            bordercolour = (0,0,0),
            hoverbordercolour = (0,0,0),
            clickedbordercolour = (0,0,0)):
        
        self.buttonid = buttonid
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.im = im
        self.rounded = rounded
        self.borderwidth = borderwidth
        self.fontcolour = fontcolour
        self.hovercolour = hovercolour
        self.buttoncolour = buttoncolour
        self.clickedcolour = clickedcolour
        self.bordercolour = bordercolour
        self.hoverbordercolour = hoverbordercolour
        self.clickedbordercolour = clickedbordercolour
        self.button = pygame.Rect(left,top,width,height)
        self.clicked = False
        self.displayed = displayed
        if self.font is None:
            self.font = pygame.font.SysFont("Ubuntu",30)

    def ison(self,mousepos):
        return self.button.collidepoint(mousepos)

    def drawrect(self,screen,colour,bordercolour,l,t,w,h):
        if self.rounded:
            pygame.draw.rect(screen,colour,[l,t,w,h],0,10)
            pygame.draw.rect(screen,bordercolour,[l,t,w,h],self.borderwidth,10)
        else:
            pygame.draw.rect(screen,colour,[l,t,w,h],0)
            pygame.draw.rect(screen,bordercolour,[l,t,w,h],self.borderwidth)
    
    def drawim(self,screen,l,t,w,h):
        if self.im is not None:
            imrect = self.im.get_rect(center = (l+w//2,t+h//2))
            screen.blit(self.im,imrect)

    def drawtext(self,screen,colour,l,t,w,h):
        if self.text != "":
            text = self.font.render(self.text,True,self.fontcolour,colour)
            textrect = text.get_rect(center = (l+w//2,t+h//2))
            screen.blit(text,textrect)

    def render(self,screen,mousepos):
        if self.displayed:
            if self.ison(mousepos):
                self.drawrect(screen,self.hovercolour,self.hoverbordercolour,self.left,self.top,self.width,self.height)    
                self.drawim(screen,self.left,self.top,self.width,self.height)
                self.drawtext(screen,self.hovercolour,self.left,self.top,self.width,self.height)
            elif self.clicked:
                self.drawrect(screen,self.clickedcolour,self.clickedbordercolour,self.left,self.top,self.width,self.height)
                self.drawim(screen,self.left,self.top,self.width,self.height)
                self.drawtext(screen,self.clickedcolour,self.left,self.top,self.width,self.height)
            else:
                self.drawrect(screen,self.buttoncolour,self.bordercolour,self.left,self.top,self.width,self.height)
                self.drawim(screen,self.left,self.top,self.width,self.height)
                self.drawtext(screen,self.buttoncolour,self.left,self.top,self.width,self.height)
        
        

