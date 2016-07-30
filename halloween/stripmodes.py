import sys
import copy
import time
import random
import logging
from threading import Thread
from colors import Color

LOG = logging.getLogger(__name__)

def rand_sleep(max_sleep=3):
    time.sleep(random.randint(1,max_sleep))


class StripModes(Thread):

    def __init__(self, strip, stop, lock):
        super(StripModes, self).__init__()
        self.daemon = True
        self.strip = strip
        self.stop = stop
        self.lock = lock
        self.name = 'StripMode'


class Halloween(StripModes):
    MODE = 'Halloween'

    def run(self):
        LOG.debug("Running Halloween Mode")
        LOG.debug("Stip length : {}".format(self.strip.length))
        crange = [colors.AQUAMARINE, colors.BROWN, colors.CYAN, colors.DARKVIOLET, colors.RED, colors.DARKGREEN, colors.DARKBLUE, colors.YELLOW, colors.BLACK]
        while not self.stop.is_set():
            i = random.randint(0, 9)
            if i != random.choice([0, 9, 1, 8, 2, 7, 3, 6, 4, 5, 6, 4, 7, 3, 8, 2, 9, 1, 0]):
                color = random.choice(crange[:-1])
                for _ in '0110010110110011010101110111':
                    self.lock.acquire()
                    if _ == random.choice(['0', '1']):
                        self.strip.set_pixel(i, color=colors.BLACK)
                    else:
                        self.strip.set_pixel(i, color=color)
                    self.lock.release()
                    time.sleep(0.05)
            else:
                self.lock.acquire()
                if self.strip.pixels[i].rgb != colors.BLACK:
                    self.strip.set_pixel(i, color=colors.BLACK)
                else:
                    self.strip.set_pixel(i, color=random.choice(crange))
                self.lock.release()
            time.sleep(random.randint(2, 5) * 0.5)
        LOG.debug("Halloween Mode Stopped")
        self.strip.all_off()

class Disco(StripModes):
    MODE = 'Disco'
    def run(self):
        LOG.debug("Starting Disco Mode")
        LOG.debug("Stip length : {}".format(self.strip.length))
        while not self.stop.is_set():
            self.lock.acquire()
            for i in range(self.strip.length):
                self.strip.set_pixel(i, color=colors.RED)
            self.lock.release()
            time.sleep(1)
            self.lock.acquire()
            for i in range(self.strip.length):
                self.strip.set_pixel(i, color=colors.GREEN)
            self.lock.release()
            time.sleep(1)
            self.lock.acquire()
            for i in range(self.strip.length):
                self.strip.set_pixel(i, color=colors.BLUE)
            self.lock.release()
            time.sleep(1)
        LOG.debug("Disco Mode Stopped")
        self.strip.all_off()

class Smoothie(StripModes):
    MODE = 'Smoothie'
    def run(self):
        LOG.debug("Starting Smoothie Mode")
        LOG.debug("Stip length : {}".format(self.strip.length))
        while not self.stop.is_set():
            color = bytearray([0,0,0])
            for i in range(100):
                color[0] = i
                self.lock.acquire()
                for p in range(self.strip.length):
                    self.strip.set_pixel(p, color=color)
                self.lock.release()
                time.sleep(0.02)
            for i in reversed(range(100)):
                color[0] = i
                self.lock.acquire()
                for p in range(self.strip.length):
                    self.strip.set_pixel(p, color=color)
                self.lock.release()
                time.sleep(0.02)
        LOG.debug("Smoothie Stopped")
        self.strip.all_off()


class Washer(StripModes):
    MODE = "Washer"
    def run(self):
        LOG.debug("Starting Washer")
        i = 0
        color = bytearray([0,0,0])
        while not self.stop.is_set():
            i += 1
            alpha = 0.00001 * i
            alpha = 0.01 * i
            if alpha >= 360:
                i = 0
            val_red = self.alpha_calc(alpha, 0)
            val_green = self.alpha_calc(alpha, 90)
            val_blue = self.alpha_calc(alpha, 180)
            color[0] = val_red
            color[1] = val_green
            color[2] = val_blue
            for p in range(self.strip.length):
                self.strip.set_pixel(p, color=color)
            self.strip.show()
            time.sleep(0.3)
        LOG.debug("Washer Stopped")
        self.strip.all_off()

    @staticmethod
    def alpha_calc(alpha, phase):
        fun = math.sin(alpha + phase)
        fun = fun * 255
        value = int(fun)
        if value < 0:
            value = 0
        return value


class Mover(StripModes):
    MODE = 'Mover'
    def run(self):
        LOG.debug("Starting Mover")
        colors = Color()
        f = [val for attr, val in colors.__dict__.items()]
        #f = [colors.AQUAMARINE, colors.RED, colors.GREEN, colors.GREENYELLOW, colors.YELLOW, colors.WHITE, colors.ROSYBROWN, colors.PURPLE, colors.PINK]
        while not self.stop.is_set():
            for p in range(self.strip.length):
                color = random.choice(f)
                self.strip.set_pixel(p, color=color)
            self.strip.show()
            time.sleep(1)
        LOG.debug("Mover Stopped")
        self.strip.all_off()


class Mycolor(StripModes):
    MODE='MyColor'
    def run(self):
        def check(color, avr, dif):
            c = 0 + color
            if c < avr:
                c += dif
            else:
                c -= dif
            if c < 0:
                c = random.randint(0, 255)
            if c > 255:
                c = random.randint(0, 255)
            return c

        neighbours = {
                0: [1, 5],
                1: [0, 2, 3, 4],
                2: [1, 3],
                3: [2, 4, 8],
                4: [1, 3, 5, 7],
                5: [0, 4, 6],
                6: [5, 7],
                7: [6, 4, 8],
                8: [3, 7]
                }
        LOG.debug("Starting MyColor")
        for led in range(self.strip.length):
            rred = random.randint(0, 255)
            rgreen = random.randint(0, 255)
            rblue = random.randint(0, 255)
            color = bytearray([rred, rgreen, rblue])
            self.strip.set_pixel(led, color=color)
        self.strip.show()
        led = 0
        while not self.stop.is_set():
            for led in range(self.strip.length):
                ncount = len(neighbours[led])
                total_red = 0
                total_green = 0
                total_blue = 0
                for pix in neighbours[led]:
                    ncolor = self.strip.get_pixel(pix)
                    total_red += ncolor[0]
                    total_green += ncolor[1]
                    total_blue += ncolor[2]

                avr_red = total_red / ncount
                avr_green = total_green / ncount
                avr_blue = total_blue / ncount
                dif_red = color[0] - avr_red
                dif_green = color[1] - avr_green
                dif_blue = color[2] - avr_blue

                color[0] = check(color[0], avr_red, dif_red)
                color[1] = check(color[1], avr_green, dif_green)
                color[2] = check(color[2], avr_blue, dif_blue)

                self.strip.set_pixel(led, color=color)
            self.strip.show()
            time.sleep(1)
        LOG.debug("MyColor Stopped")
        self.strip.all_off()


class Game(StripModes):
    '''
    Tic-Tac-Toe class.
    This class holds the user interaction, and game logic
    '''
    MODE = 'TICTACTOE'
    def __init__(self, strip, stop, lock):
        super(Game, self).__init__(strip, stop, lock)
        self.board = [' '] * 9
        self.player_name = ''
        self.player_marker = ''
        self.bot_name = 'TBot'
        self.bot_marker = ''
        self.winning_combos = (
            [6, 7, 8], [3, 4, 5], [0, 1, 2], [0, 5, 6], [1, 4, 7], [2, 3, 8],
            [0, 4, 8], [2, 4, 6],
        )
        self.corners = [0,2,6,8]
        self.sides = [1,3,5,7]
        self.middle = 4

        self.form = '''
           \t| %s | %s | %s |
           \t-------------
           \t| %s | %s | %s |
           \t-------------
           \t| %s | %s | %s |
           '''
        self.bot_color = Color.random_color()
        self.player_color = Color.random_color(ignore=self.bot_color)
        LOG.debug("TicTacToe init")

    def run(self):
        LOG.debug("Running TicTacToe Mode")
        LOG.debug("Stip length : {}".format(self.strip.length))
        player = "h"
        while not self.stop.is_set():
            player = self.endless_game_loop(player)
            self.__init__(self.strip, self.stop, self.lock)
        LOG.debug("TicTacToe Mode Stopped")
        self.strip.all_off()

    def print_board(self,board = None):
        "Display board on screen"
        if board is None:
            print(self.form % tuple(self.board[6:9] + self.board[3:6] + self.board[0:3]))
            for index, field in enumerate(self.board):
                if field == 'x':
                    self.strip.set_pixel(index, color=self.player_color)
                elif field == 'o':
                    self.strip.set_pixel(index, color=self.bot_color)
                else:
                    self.strip.set_pixel(index, color=Color().BLACK)
        else:
            # when the game starts, display numbers on all the grids
            print(self.form % tuple(board[6:9] + board[3:6] + board[0:3]))

            for index, field in enumerate(board):
                self.strip.set_pixel(index, color=Color().BLACK)
        self.strip.show()


    def get_marker(self):
        marker = raw_input("Would you like your marker to be X or Y?: ").upper() 
        while marker not in ["x","o"]:
            marker = raw_input("Would you like your marker to be X  or Y? :").upper()
        if marker == "X":
            return ('x', 'o')
        else:
            return ('o','x')

    def quit_game(self):
        "exits game"
        self.print_board
        print("\n\t Thanks for playing :-) \n\t Come play again soon!\n")
        sys.exit()

    def is_winner(self, board, marker):
        '''
        check if this marker will win the game
        '''
        for combo in self.winning_combos:
            if (board[combo[0]] == board[combo[1]] == board[combo[2]] == marker):
                return True
        return False

    def fill_winning_board(self, winner):
        '''
        fill de board with the winning color
        :param winner: winning marker
        :return:
        '''
        color = self.player_color if winner == self.player_marker else self.bot_color
        marker = self.player_marker if winner == self.player_marker else self.bot_marker
        for index, field in enumerate(self.board):
            if field == ' ':
                self.strip.set_pixel(index, color=Color().BLACK)
            elif field != winner:
                time.sleep(1)
                self.strip.set_pixel(index, color=self.player_color)

                self.board[index] = winner
            self.print_board()
        print(self.strip)
        return

    def get_bot_move(self):
        '''
        find the best space on the board for the bot. Objective
        is to find a winning move, a blocking move or an equalizer move. 
        Bot must always win
        '''
        # check if bot can win in the next move
        rand_sleep()
        for i in range(0,len(self.board)):
            board_copy = copy.deepcopy(self.board)
            if self.is_space_free(board_copy, i):
                self.make_move(board_copy,i,self.bot_marker)
                if self.is_winner(board_copy, self.bot_marker):
                    return i
        # check if player could win on his next move
        for i in range(0,len(self.board)):
            board_copy = copy.deepcopy(self.board)
            if self.is_space_free(board_copy, i):
                self.make_move(board_copy,i,self.player_marker)
                if self.is_winner(board_copy, self.player_marker):
                    return i
        # check for space in the corners, and take it
        move = random.randint(0, 8)
        while not self.is_space_free(self.board, move):
            move = random.randint(0, 8)
        if move != None:
            return move

        # If the middle is free, take it
        if self.is_space_free(self.board,self.middle):
            return self.middle

        # else, take one free space on the sides
        return self.choose_random_move(self.sides)

    def is_space_free(self, board, index):
        "checks for free space of the board"
        # print "SPACE %s is taken" % index
        return board[index] == ' '

    def is_board_full(self):
        "checks if the board is full"
        for i in range(1,9):
            if self.is_space_free(self.board, i):
                return False
        return True

    def make_move(self,board,index,move):
        board[index] =  move

    def choose_random_move(self, move_list):
        possible_winning_moves = []
        for index in move_list:
            if self.is_space_free(self.board, index):
                possible_winning_moves.append(index)
                if len(possible_winning_moves) != 0:
                    return random.choice(possible_winning_moves)
                else:
                    return None
       
    def start_game(self):
       "welcomes user, prints help message and hands over to the main game loop"
       # welcome user 
       print ('''\n\t-----------------------------------
                \n\t   TIC-TAC-TOE by Mawuli Adzaku
                \n\t------------------------------------
             ''')
       self.print_board(range(1,10))

       # get user's preferred marker 
       #self.player_marker, self.bot_marker = self.get_marker()
       self.player_marker, self.bot_marker = ('x','o')
       # randomly decide who can play first
       if random.randint(0,1) == 0:
           print("I will go first")
          # self.make_move(self.board,random.choice(self.corners), self.bot_marker)
           #self.print_board()
           self.enter_game_loop('b')
       else:
           print("You will go first")
           # now, enter the main game loop
           self.enter_game_loop('h')


    def get_player_move(self):
        move = int(input("Pick a spot to move: (1-9) "))
        while move not in [1,2,3,4,5,6,7,8,9] or not self.is_space_free(self.board,move-1) :
            move = int(input("Invalid move. Please try again: (1-9) "))
        return move - 1

    def get_player_name(self):
        return raw_input("Hi, i am %s" % self.bot_name + ". What is your name? ")


    def endless_game_loop(self, player='h'):
        '''
        endless game loop for ws2801 stripe
        :return:
        '''
        player = player
        is_running = True
        self.player_marker, self.bot_marker = ('x','o')
        while is_running:
            if player == 'h':
                user_input = self.get_bot_move()
                self.make_move(self.board,user_input, self.player_marker)
                if(self.is_winner(self.board, self.player_marker)):
                    self.print_board()
                    LOG.debug("\n\tCONGRATULATIONS %s, YOU HAVE WON THE GAME!!! \\tn" % self.player_name)
                    self.fill_winning_board(self.player_marker)

                    #self.incr_score(self.player_name)
                    is_running = False
                    player = 'h'
                else:
                    if self.is_board_full():
                        self.print_board()
                        LOG.info("\n\t-- Match Draw --\t\n")
                        is_running = False
                    else:
                        self.print_board()
                        player = 'b'
            # bot's turn to play
            else:
                bot_move =  self.get_bot_move()
                self.make_move(self.board, bot_move, self.bot_marker)
                if (self.is_winner(self.board, self.bot_marker)):
                    self.print_board()
                    LOG.info("\n\t%s HAS WON!!!!\t\n" % self.bot_name)
                    #self.incr_score(self.bot_name)
                    self.fill_winning_board(self.bot_marker)
                    is_running = False
                    player = 'b'
                    break
                else:
                    if self.is_board_full():
                        self.print_board()
                        LOG.info("\n\t -- Match Draw -- \n\t")
                        is_running = False
                    else:
                        self.print_board()
                        player = 'h'
        return player



    def enter_game_loop(self,turn):
       "starts the main game loop"
       is_running = True
       player = turn #h for human, b for bot
       while is_running:
           if player == 'h':
               user_input = self.get_player_move()
               self.make_move(self.board,user_input, self.player_marker)
               if(self.is_winner(self.board, self.player_marker)):
                   self.print_board()
                   print("\n\tCONGRATULATIONS %s, YOU HAVE WON THE GAME!!! \\tn" % self.player_name)
                   #self.incr_score(self.player_name)
                   is_running = False
                   #break
               else:
                   if self.is_board_full():
                       self.print_board()
                       print("\n\t-- Match Draw --\t\n")
                       is_running = False
                       #break
                   else:
                       self.print_board()
                       player = 'b'
           # bot's turn to play
           else:
              bot_move =  self.get_bot_move()
              self.make_move(self.board, bot_move, self.bot_marker)
              if (self.is_winner(self.board, self.bot_marker)):
                  self.print_board()
                  print("\n\t%s HAS WON!!!!\t\n" % self.bot_name)
                  #self.incr_score(self.bot_name)
                  is_running = False
                  break
              else:
                  if self.is_board_full():
                      self.print_board()
                      print("\n\t -- Match Draw -- \n\t")
                      is_running = False
                      #break
                  else:
                      self.print_board()
                      player = 'h'

       # when you break out of the loop, end the game
       self.end_game()

    def end_game(self):
       play_again = raw_input("Would you like to play again? (y/n): ").lower()
       if play_again == 'y':
           self.__init__() # necessary for re-initialization of the board etc
           self.endless_game_loop()
           #self.start_game()
       else:
           print("\n\t-- GAME OVER!!!--\n\t")
           LOG.debug("Game Over")
           self.quit_game()
