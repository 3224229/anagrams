import itertools
import random
import twl
from collections import Counter
import root
import time
from network import Network
import ast
import datetime

import api

import pygame, sys
from pygame.locals import *

print_check = True

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 640

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NAVYBLUE = (60, 60, 100)

BGCOLOR = WHITE
TEXTCOLOR = BLACK

print_check = False

letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
letter_freq = {'A': 13, 'B': 3, 'C': 3, 'D': 6, 'E': 18, 'F': 3, 'G': 4, 'H':3, 'I':12, 'J':2, 'K':2, 'L':5, 'M':3, 'N':8, 'O':11, 'P':3, 'Q':2, 'R':9, 'S':6, 'T':9, 'U': 6, 'V':3, 'W':3, 'X':2, 'Y':3, 'Z':2}
letter_keys = [K_a, K_b, K_c, K_d, K_e, K_d, K_e, K_f, K_g, K_h, K_i, K_j, K_k, K_l, K_m, K_n, K_o, K_p, K_q, K_r, K_s, K_t, K_u, K_t, K_v, K_w, K_x, K_y, K_z]

#  ________
# | LAYOUT |
#  --------

# 'Current'
font_current = 'freesansbold.ttf'
size_current = 32
color_current = BLACK
x_current = 10
y_current = 20

# Tiles
font_tile = 'freesansbold.ttf'
size_tile = 32
color_tile = BLACK
x_tile_0 = 150
y_tile_0 = 20
x_gap_tile = 30
y_gap_tile = 50

# 'Your Words'
font_your = 'freesansbold.ttf'
size_your = 32
color_your = BLACK
x_your = 10
y_your = 100
y_gap_your = 50

# Your Words
font_words = 'freesansbold.ttf'
size_words = 32
color_words = BLACK
x_words = 10
y_words = y_your + y_gap_your
x_gap_words = 100
y_gap_words = 50

# 'Opponent's Words'
font_opp = 'freesansbold.ttf'
size_opp = 32
color_opp = BLACK
x_opp = 300
y_opp = 100
y_gap_opp = 50

# Opponent's Words
font_opp_words = 'freesansbold.ttf'
size_opp_words = 32
color_opp_words = BLACK
x_opp_words = 300
y_opp_words = y_opp + y_gap_opp
x_gap_opp_words = 100
y_gap_opp_words = 50

# Guess
font_guess = 'freesansbold.ttf'
size_guess = 32
color_guess = BLACK
x_guess = 10
y_guess = 400

# Status
font_status = 'freesansbold.ttf'
size_status = 32
color_status = BLACK
x_status = 10
y_status = 500


class banana(object):
    def __init__(self):

        # -------- #
        #  BANANA  #
        # -------- #
        self.tiles = []
        for letter in letters:
            self.tiles = self.tiles + list(itertools.repeat(letter, letter_freq[letter]))

        random.shuffle(self.tiles)

        self.current = []

        self.playerwords = {}
        self.playerwords_list = []

        self.fontObj_current = pygame.font.Font(font_current, size_current)
        self.fontObj_tile = pygame.font.Font(font_tile, size_tile)
        self.fontObj_your = pygame.font.Font(font_your, size_your)
        self.fontObj_words = pygame.font.Font(font_words, size_words)
        self.fontObj_guess = pygame.font.Font(font_guess, size_guess)
        self.fontObj_status = pygame.font.Font(font_status, size_status)

        self.fontObj_opp = pygame.font.Font(font_your, size_your)
        self.fontObj_opp_words = pygame.font.Font(font_words, size_words)

        self.guess = ''
        self.previous_guess = ''
        self.fresh_take = False
        self.middle_used = []
        self.pre_take_word = ''

        self.status = ''
        self.last_update = datetime.datetime(1,1,1)

        self.net = Network()
        self.player2current = []
        self.player2words = {}
        self.player2words_list = []


    def send_data(self):
        data = str(self.net.id) + "|" + str(self.current) + "|" + str(self.playerwords) + "|" + str(self.playerwords_list) + "|" + str(self.player2words) + "|" + str(self.player2words_list) + "|" + str(self.last_update)
        reply = self.net.send(data)
        return reply


    @staticmethod
    def parse_data(data):
        try:
            split = data.split('|')
            current = ast.literal_eval(split[1])
            player2words = ast.literal_eval(split[2])
            player2words_list = ast.literal_eval(split[3])
            playerwords = ast.literal_eval(split[4])
            playerwords_list = ast.literal_eval(split[5])
            last_update = datetime.datetime.strptime(split[6], '%Y-%m-%d %H:%M:%S.%f')
            return current, player2words, player2words_list, playerwords, playerwords_list, last_update
        except:
            return None, {}, [], None, None, datetime.datetime(1,1,1,0,0)



    def flip(self):
        self.updated = True

        if not self.tiles:
            self.status = 'Banana is empty!'
            self.__display_text(self.status, x_status, y_status, self.fontObj_status, color_status)
            return None

        self.last_update = datetime.datetime.now()

        last = self.tiles.pop()
        self.current.append(last)

    def current(self):
        print(self.current)

    def __superset(self, word1, word2, strict = False):
        # Can word 1 take word 2?
        word1_counter = Counter(word1)
        word2_counter = Counter(word2)

        if strict:
            return (word1_counter - word2_counter and not (word2_counter - word1_counter))
        else:
            return (word1_counter - word2_counter and not(word2_counter - word1_counter)) or (not (word1_counter - word2_counter) and not (word2_counter - word1_counter))

    def __subtract(self, word1, word2):
        # Subtract word2 from word1 (e.g. 'test' - 'tst' = 'e')

        list1 = list(word1)
        for letter in word2:
            list1.remove(letter)

        # Turn list into string
        str = ''
        str = str.join(list1)

        return str



    def __display_text(self, text, x, y, fontObj, color):
        textSurfaceObj = fontObj.render(text, True, color)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.topleft = (x, y)
        DISPLAYSURF.blit(textSurfaceObj, textRectObj)


    def __check_steal(self, candidate, etyms_candidate, word_dict, is_opponent):
        # Check whether a steal happens
        # Input a candidate word (i.e. guess), its merriam stripped version,
        # a dictionary with the words to take from (plus their merriam stripped versions) and
        # a Boolean indicating whether we're checking a steal from the opponent

        # Returns whether stolen, what kind of steal or error, the taken word, and index of taken word

        # Set event_type to 'tiles' arbitrarily
        event_type = 'tiles'

        for i, word in enumerate(word_dict):
            # First, check if candidate is a superset of the current word
            if self.__superset(candidate, word, strict=True):

                # Then, check if the tiles needed to make candidate are in the middle
                if not self.__superset(self.current, self.__subtract(candidate, word)):
                    event_type = 'tiles'
                else:
                    etyms_word = word_dict[word]

                    try:
                        # Check for any common roots. If etymonline returns nothing, then assume there are no
                        # common roots
                        root_overlap = any(x in etyms_candidate for x in etyms_word)
                    except TypeError:
                        root_overlap = False

                    if root_overlap:
                        event_type = 'trivial'
                    else:
                        event_type = 'steal'
                        taken_word = word
                        taken_i = i
                        return True, event_type, taken_word, taken_i
        if not is_opponent and self.__superset(self.current, candidate, strict=False):
            # This is to check middle steals. We have "is_opponent" because we're running this current __check_steal
            # function twice, once for the opponent's words and once for your words, and we don't want it to check
            # for a middle steal twice. So we say that in the first go-through (opponent's words), don't check middle
            event_type = 'middle'
            return True, event_type, None, None
        else:
            return False, event_type, None, None

                # elif word in candidate and any(x in root.lookup(candidate) for x in root.lookup(word)):
                     # error_trivial_extension = True

                # If all of those check out, then it's a steal and record which word is being stolen


    def take(self, candidate):

        # First check if has 3 letters
        if len(candidate) < 3:
            self.previous_guess = self.guess
            self.status = "Word is too short! " + f"({self.previous_guess})"
            self.guess = ''
            return None

        # Then check if a word
        if len(candidate) < 10:
            is_word = twl.check(candidate.lower())
        else:
            is_word = api.get_word_data(candidate)
        if not is_word:
            # self.__display_text("Not a word!", 200, 400)
            self.previous_guess = self.guess
            self.status = "Not a word! " + f"({self.previous_guess})"
            self.guess = ''
            return None

        error_trivial_extension = False
        error_tiles = False

        etyms_candidate = api.get_etym(candidate)

        # Check if can take the other player's words (not checking middle steal)
        is_taken, event_type, taken_word, taken_i = self.__check_steal(candidate, etyms_candidate, self.player2words, True)

        if is_taken:
            # Get time of this steal
            self.last_update = datetime.datetime.now()

            if event_type == 'steal': # in theory, this if statement is unnecessary since there are no middle steals
                # Make the candidate word into a list to remove individual letters.
                candidate_list = list(candidate)

                # Delete the taken word from opponent's list, add it to your own dictionary and corresponding list (list for ordering purposes)
                del self.player2words[taken_word]
                self.player2words_list.remove(taken_word)

                self.playerwords.update({candidate: etyms_candidate})
                self.playerwords_list.append(candidate)

                # Figure out what tiles are used from the middle and remove those from self.current
                for letter in taken_word:
                    candidate_list.remove(letter)

                for letter in candidate_list:
                    self.current.remove(letter)
                self.previous_guess = self.guess
                self.status = "Success! " + f"({self.previous_guess})"
                self.fresh_take = True
                self.pre_take_word = taken_word
                self.middle_used = candidate_list

        else:
            # If no steal was triggered above, then couldn't steal opponent's words for one of the reasons below
            # (wait until you check whether you can take one of your own words to see if it was a failure overall)
            if event_type == 'trivial':
                error_trivial_extension = True
            elif event_type == 'tiles':
                error_tiles = True

        # if could not take the other player's words, check if can take one's own
        if not is_taken:
            self_is_taken, event_type, taken_word, taken_i = self.__check_steal(candidate, etyms_candidate, self.playerwords, False)

            if self_is_taken:
                self.last_update = datetime.datetime.now()
                self.updated = True
                if event_type == 'steal':
                    candidate_list = list(candidate)

                    del self.playerwords[taken_word]
                    self.playerwords.update({candidate: etyms_candidate})

                    self.playerwords_list[taken_i] = candidate

                    for letter in taken_word:
                        candidate_list.remove(letter)
                    for letter in candidate_list:
                        self.current.remove(letter)
                    self.previous_guess = self.guess
                    self.status = "Success! " + f"({self.previous_guess})"
                    self.fresh_take = True
                    self.pre_take_word = taken_word
                    self.middle_used = candidate_list

                elif event_type == 'middle':
                    candidate_list = list(candidate)

                    for letter in candidate_list:
                        self.current.remove(letter)
                    self.playerwords.update({candidate: etyms_candidate})
                    self.playerwords_list.append(candidate)

                    self.previous_guess = self.guess
                    self.status = "Success! " + f"({self.previous_guess})"
                    self.fresh_take = True
                    self.pre_take_word = taken_word
                    self.middle_used = candidate_list

                elif error_trivial_extension:
                    self.previous_guess = self.guess
                    self.status = "Same root! " + f"({self.previous_guess})"
                elif error_tiles:
                    self.previous_guess = self.guess
                    self.status = "Tiles aren't there! " + f"({self.previous_guess})"
                else:
                    self.previous_guess = self.guess
                    self.status = "Tiles aren't there! " + f"({self.previous_guess})"
        self.guess = ''

    def printstatus(self):

        # Send network stuff, outputs of this function are the stuff you receive from the other player
        self.player2current, player2words_recv, player2words_list_recv, playerwords_recv, playerwords_list_recv, self.player2_last_update = self.parse_data(self.send_data())

        # If it's a fresh take, check to see if the opponent's taken it first
        """
        if self.fresh_take:
            # Check if center tiles and taken word are still there:
            if not self.__superset(self.player2current, self.middle_used, strict=False) or (not self.pre_take_word in player2words_list_recv and not self.pre_take_word in playerwords_list_recv):
                print("OVERWRITING!!!!")
                self.current = self.player2current
                self.playerwords = playerwords_recv
                self.playerwords_list = playerwords_list_recv
                self.last_update = self.player2_last_update
                self.player2words = player2words_recv
                self.player2words_list = player2words_list_recv
        # Reset self.fresh_take
        self.fresh_take = False
        """

        # Check if other player has made a more recent update, meaning you would need to update your lists
        if self.player2_last_update > self.last_update:
            if print_check:
                print("UPDATING")
                print(f"Old Words: {self.playerwords}")
                print(f"New Words: {playerwords_recv}")
            self.current = self.player2current
            self.playerwords = playerwords_recv
            self.playerwords_list = playerwords_list_recv
            self.last_update = self.player2_last_update
            self.player2words = player2words_recv
            self.player2words_list = player2words_list_recv


        y_tile = y_tile_0
        x_tile = x_tile_0

        self.__display_text('Current: ', x_current, y_current, self.fontObj_current, color_current)

        """
        currentSurfaceObj = self.fontObj.render('Current:', True, BLACK)
        currentRectObj = currentSurfaceObj.get_rect()
        currentRectObj.topleft = (x_current, y_current)
        DISPLAYSURF.blit(currentSurfaceObj, currentRectObj)
        """

        for i, tile in enumerate(self.current):
            x_tile = x_tile + x_gap_tile

            self.__display_text(tile, x_tile, y_tile, self.fontObj_tile, color_tile)

            """
            tileSurfaceObj = self.fontObj.render(tile, True, BLACK)
            tileRectObj = tileSurfaceObj.get_rect()
            tileRectObj.topleft = (x_tile, y_tile)
            DISPLAYSURF.blit(tileSurfaceObj, tileRectObj)
            """

            if i % 10 == 9:
                y_tile = y_tile + y_gap_tile
                x_tile = x_tile_0



        self.__display_text('Your Words: ', x_your, y_your, self.fontObj_your, color_your)

        """
        wordsSurfaceObj = self.fontObj.render('Your Words:', True, BLACK)
        wordsRectObj = wordsSurfaceObj.get_rect()
        wordsRectObj.topleft = (x_words, y_words)
        DISPLAYSURF.blit(wordsSurfaceObj, wordsRectObj)
        """

        x_words_local = x_words
        y_words_local = y_words

        for i, word in enumerate(self.playerwords_list):

            self.__display_text(word, x_words_local, y_words_local, self.fontObj_words, color_words)


            """
            wordSurfaceObj = self.fontObj.render(word, True, BLACK)
            wordRectObj = wordSurfaceObj.get_rect()
            wordRectObj.topleft = (x_words, y_words)
            DISPLAYSURF.blit(wordSurfaceObj, wordRectObj)
            """

            if i % 10 == 9:
                x_words_local = x_words_local + x_gap_words

            y_words_local = y_words_local + y_gap_words


        self.__display_text('Take: ' + self.guess, x_guess, y_guess, self.fontObj_guess, color_guess)

        """
        guessSurfaceObj = self.fontObj.render('Guess: ' + self.guess, True, BLACK)
        guessRectObj = guessSurfaceObj.get_rect()
        guessRectObj.topleft = (x_guess, y_guess)
        DISPLAYSURF.blit(guessSurfaceObj, guessRectObj)
        """

        self.__display_text('Opponent\'s Words: ', x_opp, y_opp, self.fontObj_opp, color_opp)

        """
        wordsSurfaceObj = self.fontObj.render('Your Words:', True, BLACK)
        wordsRectObj = wordsSurfaceObj.get_rect()
        wordsRectObj.topleft = (x_words, y_words)
        DISPLAYSURF.blit(wordsSurfaceObj, wordsRectObj)
        """

        x_opp_words_local = x_opp_words
        y_opp_words_local = y_opp_words

        for i, word in enumerate(self.player2words_list):

            self.__display_text(word, x_opp_words_local, y_opp_words_local, self.fontObj_opp_words, color_opp_words)


            """
            wordSurfaceObj = self.fontObj.render(word, True, BLACK)
            wordRectObj = wordSurfaceObj.get_rect()
            wordRectObj.topleft = (x_words, y_words)
            DISPLAYSURF.blit(wordSurfaceObj, wordRectObj)
            """

            if i % 10 == 9:
                x_opp_words_local = x_opp_words_local + x_gap_opp_words

            y_opp_words_local = y_opp_words_local + y_gap_opp_words

        self.__display_text(self.status, x_status, y_status, self.fontObj_status, color_status)

def main():
    # Main game loop
    global FPSCLOCK, DISPLAYSURF
    pygame.init()

    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    pygame.display.set_caption('Anagrams')

    game = banana()

    while True: # main game loop
        DISPLAYSURF.fill(BGCOLOR)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    if game.guess == '':
                        pass
                    else:
                        # Delete one letter from the guess
                        game.guess = game.guess[:-1]

                elif event.key == K_SPACE:
                    # Don't do anything if input is a space
                    pass



                elif event.key == K_RETURN:
                    # if Return and no guess is present, then flip next tile. If guess is present, see if it's a take
                    if game.guess == '':
                        game.flip()
                    else:
                        game.take(game.guess.upper())

                elif event.key in letter_keys:
                    # if letter is typed then add it to the current guess
                    game.guess = game.guess + event.unicode.upper()



        game.printstatus()
        pygame.display.update()


if __name__ == "__main__":
    # execute only if run as a script
    main()
