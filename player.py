import numpy as np
import matplotlib.pyplot as plt

class Player():
    def __init__(self,
            playerid,
            difficulty,
            boardwidth,
            boardheight,
            samplesize = 20000):
        
        #from inputs
        self.playerid = playerid
        self.difficulty = difficulty
        self.boardwidth = boardwidth
        self.boardheight = boardheight
        self.samplesize = samplesize
        self.posterior = None

        #internal variable
        shipsizes = np.array([5,4,3,3,2])
        self.ships = np.zeros((len(shipsizes),self.boardwidth,self.boardheight))
        self.shipconfigs = [self.get_all_ship_configs(shipsize) for shipsize in shipsizes]
        self.allshipconfigs = [oneshipsampling(ship_configs) for ship_configs in self.shipconfigs]
        self.revealedships = np.ma.masked_all((len(self.shipconfigs),)+self.shipconfigs[0][0].shape)
        self.turn_revealed = []
        self.updateposterior()
        self.generateheatmap()
        self.attacking_scores = []

    def loadboard(self,board):
        for i in range(len(self.ships)):
            self.ships[i][board == i+1] = 1

    def getshipplacement(self,board,shiplen,seed = 0):
        np.random.seed(seed)
        #Random player
        if self.difficulty >= 0:
            orientation = np.random.randint(4)
            if orientation%2 == 0: #horizontal
                startx = np.random.randint(self.boardwidth-shiplen+1)
                starty = np.random.randint(self.boardheight)
            else:
                startx = np.random.randint(self.boardwidth)
                starty = np.random.randint(self.boardheight-shiplen+1)

            #to ensure field is completely on board if in left or up orientation
            if orientation == 2:
                startx = self.boardwidth-startx
            if orientation == 3:
                startx = self.boardheight-starty

            field = board.makefield(shiplen,(startx,starty),orientation)
            return field, orientation

        #Medium AI player
        if self.difficulty == 1:
            pass

    def guess(self,attacking_scores = None):
        #print("revealed\n",self._revealed())
        #Random player
        if self.difficulty == 0:
            xs,ys = np.where(self._revealed())
            ind = np.random.randint(len(xs))
            return (xs[ind],ys[ind])

        #matches users play level
        if self.difficulty == 1:
            if len(attacking_scores) == 0 or attacking_scores is None:
                return self.argmax_2d(self.posterior)
            else:
                avg_attack_score = np.mean(attacking_scores)
                print("Avg attack score:",avg_attack_score)
                scoreind = int((self.posterior.count()-1) * avg_attack_score)
                sortedflat = np.argsort(self.posterior.flatten())
                ind = sortedflat[scoreind]
                guess = np.unravel_index(ind,self.posterior.shape)
                return guess

        #Hard AI player - best probabilistic pla
        if self.difficulty == 2:
            #print("posterior\n", self.posterior)
            return self.argmax_2d(self.posterior)

    def updateposterior(self):
        self.posterior = np.ma.masked_array(
                         self.sample_posterior(), 
                         mask = ~self._revealed().mask)

    def generateheatmap(self):
        plt.close('all')
        params = {'ytick.color':'w',
                  'xtick.color':'w',
                  'axes.labelcolor':'w',
                  'axes.edgecolor':'w'}

        plt.rcParams.update(params)

        fig,ax = plt.subplots(figsize = (4,4))
        fig.patch.set_facecolor('black')
        #set hits and misses to max and min in heat map
        heatmap = self.posterior.copy().filled(999)
        fillvals = self.ships.sum(axis = 0)[self.posterior.mask]
        fillvals[fillvals == 0] = self.posterior.min()
        fillvals[fillvals == 1] = self.posterior.max()
        heatmap[heatmap == 999] = fillvals
        im = ax.imshow(heatmap,cmap = 'hot',interpolation = 'nearest')
        ax.set_xticks(range(10))
        ax.set_yticks(range(10))
        ax.set_xticklabels(range(1,11))
        ax.set_yticklabels(['A','B','C','D','E','F','G','H','I','J'])
        cbar = fig.colorbar(im,orientation = "horizontal",ticks = [self.posterior.min(),self.posterior.max()])
        cbar.ax.set_xticklabels(['low','high'])
        plt.savefig(f'./images/player{self.playerid}heatmap.png',bbox_inches = 'tight',dpi = 100)

    def argmax_2d(self,dist):
        maxrow = dist.max(axis = 1).argmax()
        maxcol = dist[maxrow].argmax()
        return (maxrow,maxcol)

    def sample_posterior(self):
        all_compatible_configs = [
                shipconfig.compatible_ships(seen_ships)
                for (shipconfig, seen_ships) in zip(self.allshipconfigs, self.revealedships)]
        
        samples = self.sample_n_ships(all_compatible_configs,self._revealed())
        #samples = self.sample_compatible_ships(all_compatible_configs,self._revealed())
        return samples.sum(axis = 1).mean(axis = 0)

    def sample_n_ships(self,possible_ships,revealed):
        samples = []
        while len(samples) == 0:
            samples = self.get_samples(possible_ships,revealed)
        return samples

    def get_samples(self, possible_ships,revealed):
        randnumgen = np.random.default_rng()
        print([ships.shape for ships in possible_ships])
        samples = np.stack([randnumgen.choice(ships,
                                             size = self.samplesize,
                                             shuffle = False)
                            for ships in possible_ships],axis = 1)
        valid_samples = samples[self.validate_samples(samples)]
        
        if revealed.mask.all():
            return valid_samples
        else:
            compatible = (valid_samples.sum(axis = 1) == revealed).all(axis = (-2,-1))
            return valid_samples[compatible]

    def generate_compatible_ships(self,possible_ships,revealed):
        while True:
            yield from self.sample_n_ships(possible_ships,revealed)

    def sample_ships(self,possible_ships):
        empty = np.ma.masked_all_like(self.shipconfigs[0][0])
        return self.sample_compatible_ships(possible_ships,empty)
    
    def sample_compatible_ships(self,possible_ships,revealed):
        generated_compatible_ships = self.generate_compatible_ships(possible_ships,revealed)
        return np.array([x for _,x in zip(range(self.samplesize),generated_compatible_ships)])

    def validate_samples(self,samples, ship_axis = 1, board_axis = (-2,-1)):
        return (samples.sum(axis = ship_axis).max(axis = board_axis) == 1)

    def get_all_ship_configs(self, shipsize):
        configs1d = self.get_all_ship_configs_1d(shipsize)
        rows, _ = configs1d.shape
        y = np.arange(self.boardheight)
        boards = np.zeros((rows,self.boardwidth,self.boardwidth,self.boardheight))
        boards[:,y,y,:] = configs1d[:,np.newaxis]
        board_configs = boards.reshape((-1, self.boardwidth,self.boardheight))
        return np.concatenate((board_configs,board_configs.transpose(0,2,1)))

    def get_all_ship_configs_1d(self, shipsize):
        x,y = np.indices((self.boardwidth,self.boardwidth))[:,:-shipsize+1]
        return 1 * (x <= y) & (y < x + shipsize)

    def updaterevealed(self,retval,field,make_heatmap = True):
        row,col = field
        prev_sunk = self._sunk()
        next_ships = self._revealed_ships().copy()
        next_ships[:,row,col] = self.ships[:,row,col]
        self.turn_revealed.append(next_ships)
        curr_sunk = self._sunk()

        if (curr_sunk == prev_sunk).all():
            sunk = None
        else:
            sunk = (curr_sunk & ~prev_sunk).argmax() 
        if self.ships.sum(axis = 0)[row,col] == 0 or sunk is not None:
            self.revealedships[:,row,col] = 0
            if sunk is not None:
                self.revealedships[sunk,row,col] = 1

        print("revealedships",self.revealedships)
        print("revealed",self._revealed())
        print("sunk",self._sunk())
        print("_revealed_ships",self._revealed_ships())

        #calculate guess score
        guess_prob = self.posterior[row,col]
        attacking_score = (np.searchsorted(np.sort(self.posterior[~self.posterior.mask].flatten()),
                                          guess_prob))/(self.posterior.count()-1)
        self.attacking_scores.append(attacking_score)

        self.updateposterior()
        if make_heatmap:
            self.generateheatmap()

    #Some dynamic properties
    def _is_solved(self):
        return self._revealed.sum() == (self.ships.sum(axis = 0)).sum()

    def _revealed(self):
        return self._revealed_ships().sum(axis = 0)

    def _sunk(self):
        ship_sizes = self.ships.sum(axis = (1,2))
        revealed_ship_sizes = (self._revealed_ships().sum(axis = (1,2)).filled(0))
        return ship_sizes == revealed_ship_sizes
    
    def _revealed_ships(self):
        if self._turns() > 0:
            return self.turn_revealed[-1]
        else:
            return np.ma.masked_all_like(self.ships)

    def _turns(self):
        return len(self.turn_revealed)

    def _turn_revealed(self): #his is turn_revealed, and other one is _turn_revealed
        return [np.ma.masked_all_like(self._board())]+[revealed.sum(axis = 0) for revealed in self.turn_revealed]

class oneshipsampling():
    def __init__(self, ship_configs):
        self.ship_configs = ship_configs

    def compatible_ships(self, revealed):
        if revealed.mask.all():
            return self.ship_configs
        else:
            compatible_configs = self.get_compatible_configs(self.ship_configs,revealed)
            return self.ship_configs[compatible_configs]

    def get_compatible_configs(self,ship_configs,revealed):
        return (ship_configs == revealed).all(axis = (-2,-1))
