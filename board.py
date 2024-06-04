import numpy as np
from square import *
from ship import *
from pygame import *
from button import *

class Board():
    def __init__(self,
            boardwidth,
            boardheight,
            screenwidth,
            screenheight,
            shipims,
            squareims = None,
            separation = 3,
            squarewidth = 25,
            squareheight = 25,
            numships = 5,
            shipcolour = (100,100,100),
            hovercolour = (175,175,0),
            seacolour = (0,157,196),
            hitcolour = (0,255,0),
            misscolour = (255,0,0),
            sunkcolour = (240,240,240),
            textcolour = (255,255,255),
            sunkshipcolour = (220,100,100)):

        #from inputs
        self.boardwidth = boardwidth
        self.boardheight = boardheight
        self.separation = separation
        self.squarewidth = squarewidth
        self.squareheight = squareheight
        self.screenwidth = screenwidth
        self.screenheight = screenheight
        self.numships = numships
        self.shipcolour = shipcolour
        self.hovercolour = hovercolour
        self.seacolour = seacolour
        self.hitcolour = hitcolour
        self.misscolour = misscolour
        self.sunkcolour = sunkcolour
        self.textcolour = textcolour
        self.sunkshipcolour = sunkshipcolour
        self.squareims = squareims
        self.shipims = shipims
        
        #internal variables
        self.board = np.zeros((boardheight,boardwidth),dtype = np.int8)
        self.ships = []
        self.setupdone = False
        self.shipsleft = self.numships
        self.gamewidth = self.boardwidth * squarewidth + (self.boardwidth-1)*separation
        self.gameheight = self.boardheight * squareheight + (self.boardheight-1)*separation
        self.left = (screenwidth - self.gamewidth)//2
        self.top = (screenheight - self.gameheight)//2
        self.squares = [[Square(squarewidth,squareheight,seacolour,ims = squareims) for i in range(self.boardwidth)] for j in range(self.boardheight)]
        for x in range(self.boardwidth):
            for y in range(self.boardheight):
                posx = self.left + x * (squarewidth+separation)
                posy = self.top + y * (squareheight+separation)
                self.squares[y][x].setpos(posx,posy)

        #set text for border of game
        """
        font = pygame.font.SysFont("Ubuntu",int(squarewidth * 3/4))
        letters = ['A','B','C','D','E','F','G','H','I','J']
        for y in range(self.boardheight-1):
            pos = self.squares[y][0].pos
            self.squares[y][0].__init__(squarewidth,
                                       squareheight,
                                       (0,0,0),
                                       pos = pos,
                                       text = letters[y],
                                       font = font)
        bottomleftsquarepos = self.squares[self.boardheight-1][0].pos
        self.squares[self.boardheight-1][0].__init__(squarewidth,
                                                     squareheight,
                                                     colour = (0,0,0),
                                                     text = " ",
                                                     font = font,
                                                     pos = bottomleftsquarepos)
        for x in range(1,self.boardwidth):
            pos = self.squares[self.boardwidth-1][x].pos
            self.squares[self.boardwidth-1][x].__init__(squarewidth,
                                                        squareheight,
                                                        (0,0,0),
                                                        pos = pos,
                                                        text = str(x),
                                                        font = font)
        
        """
        self.buttons = []
        for i,im in enumerate(shipims):
            self.buttons.append(Button(len(self.buttons),
                                       screenwidth-self.left+squarewidth,
                                       self.top+(self.gameheight-10*squareheight)//2+2*squareheight*len(self.buttons),
                                       squarewidth*6,
                                       2*squareheight,
                                       im = im,
                                       buttoncolour = (0,0,0),
                                       hovercolour = (150,150,170),
                                       hoverbordercolour = (240,200,240),
                                       clickedbordercolour = (240,200,240)))
        self.buttons[0].clicked = True

    def isonboard(self,pos):
        posx,posy = pos
        if posx < self.left:
            return False
        elif posx > self.left + self.gamewidth:
            return False
        elif posy < self.top:
            return False
        elif posy > self.top + self.gameheight:
            return False
        return True
    
    def isfieldonboard(self,field):
        for loc in field:
            if not self.isloconboard(loc):
                return False
        return True

    def isfieldonship(self,field):
        for loc in field:
            if self.isloconboard(loc):
                if self.boardval(loc) > 0:
                    return True
        return False

    def topleftposoffield(self,field,orientation):
        if orientation == 0 or orientation == 1:
            y,x = field[0]
        elif orientation == 2 or orientation == 3:
            y,x = field[-1]
        return self.squares[y][x].pos

    def isloconboard(self,loc):
        y,x = loc
        if y>=0 and y<self.boardheight and x>=0 and x < self.boardwidth:
            return True
        return False

    def boardval(self,loc):
        y,x = loc
        return self.board[y,x]

    def cropfield(self,field):
        toremove = []
        for (y,x) in field:
            if y < 0 or y >= self.boardheight or x < 0 or x >= self.boardwidth:
                toremove.append((y,x))
        for i in toremove:
            field.remove(i)
        return
            
    def getsquare(self,pos):
        posx,posy = pos
        posx -= self.left
        posy -= self.top
        tilex = posx // (self.squarewidth + self.separation)
        tiley = posy // (self.squareheight + self.separation)
        return (tiley,tilex)

    def resetcolour(self,field):
        for (y,x) in field:
            self.squares[y][x].reset_colour()
        return

    def setcolour(self,field,colour):
        for (y,x) in field:
            self.squares[y][x].set_colour(colour)
        return

    def setcolourhard(self,field,colour):
        for (y,x) in field:
            self.squares[y][x].set_colour_hard(colour)
        return

    def makefield(self,size,hoverloc,orientation):
        field = [hoverloc]
        y,x = hoverloc
        for i in range(1,size):
            if orientation == 0:
                field.append((y,x+i))
            elif orientation == 1:
                field.append((y+i,x))
            elif orientation == 2:
                field.append((y,x-i))
            elif orientation == 3:
                field.append((y-i,x))
        return field

    def placeship(self,shipid,field,orientation):
        if self.isfieldonboard(field) and not self.isfieldonship(field) and not self.setupdone:
            topleft = self.topleftposoffield(field,orientation)
            self.ships.append(Ship(shipid,field,topleft,self.shipims[shipid],orientation))
            self.buttons[shipid].buttoncolour = (150,150,170)
            self.buttons[shipid].hovercolour = self.buttons[shipid].clickedcolour
            self.buttons[shipid].hoverbordercolour = self.buttons[shipid].clickedbordercolour
            self.buttons[shipid].clicked = False
            for (y,x) in field:
                self.board[y,x] = len(self.ships)
            
            if len(self.ships) == self.numships:
                self.setupdone = True
            return True
        else:
            self.cropfield(field)
            self.setcolour(field,self.hovercolour)
            return False

    def hovership(self,field):
        self.cropfield(field)
        self.setcolour(field,self.hovercolour)
        return

    def attack(self,loc):
        y,x = loc
        hit = int(self.boardval(loc))
        self.board[y,x] = -1
        shipfield = loc #returns full ship loc if ship is sunk
        #hit a ship
        if hit > 0:
            retval = 1
            ship = self.ships[hit-1]
            ship.hit(loc)
            self.setcolourhard([loc],self.hitcolour)
            #if ship sunk
            if ship.sunk:
                self.shipsleft -= 1
                self.setcolourhard(ship.field,self.sunkcolour)
                self.buttons[ship.shipid].buttoncolour = self.sunkshipcolour
                retval = 2
                #stop showing explosion to display ship instead
                for loc in ship.field:
                    y,x = loc
                    self.squares[y][x].attacked = -1
            #if regular hit
            else:
                if self.squareims is not None:
                    self.squares[y][x].attacked = 1
        #miss
        elif hit == 0:
            retval = 0
            self.setcolourhard([loc],self.misscolour)
            if self.squareims is not None:
                self.squares[y][x].attacked = 0
        
        #previous guess
        else:
            retval = -1
        return retval, shipfield, self.shipsleft

    def render(self,screen,text,font,mousepos):
        screen.fill((0,0,0))
        for x in range(self.boardwidth):
            for y in range(self.boardheight):
                self.squares[y][x].render(screen)
        rtext = font.render(text,True,self.textcolour,(0,0,0)) 
        textrect = rtext.get_rect()
        textrect.center = (self.screenwidth // 2, self.top // 2) 
        screen.blit(rtext,textrect)
        for button in self.buttons:
            button.render(screen,mousepos)

        for ship in self.ships:
            ship.render(screen) #displays on screen if sunk

    def reset(self):
        self.board = np.zeros((self.boardheight,self.boardwidth),dtype = np.int8)
        self.ships = []
        self.setupdone = False
        self.shipsleft = self.numships
        for i,row in enumerate(self.squares):
            for j,square in enumerate(row):
                square.set_colour_hard(self.seacolour)
                square.attacked = -1
        for button in self.buttons:
            button.buttoncolour = (0,0,0)
            button.hovercolour = (150,150,170)
            button.hoverbordercolour = (240,200,240)
            button.clickedbordercolour = (240,200,240)
        self.buttons[0].clicked = True


