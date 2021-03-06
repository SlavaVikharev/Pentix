#!/usr/bin/env python3
import pygame
from pygame.locals import *
import pentix
import figure
from button import draw_button
import json


class Game:

    def __init__(self, fullscreen=False, screen=(800, 600),
                 width=10, height=20):
        pygame.display.set_caption("Pentix")
        self.fullscreen = fullscreen
        self.screen_size = screen
        self.width = width
        self.height = height
        self.block_size = 0
        self.surface = None
        self.screen = None
        self.paused = False
        self.quit = False
        self.level = [[0 for _ in range(width)] for _ in range(height)]
        self.current = figure.Figure(self)
        self.fpsClock = pygame.time.Clock()
        self.score = 0
        self.lvl = 1
        self.highscore = 0
        self.draw_main()
        self.draw()
        pygame.time.set_timer(pentix.FALLING, 270 // self.lvl)
        pygame.time.set_timer(pentix.BOOSTING, 60)

    # logics
    #
    def start(self, lvl):
        self.lvl = lvl
        self.paused = False
        pygame.time.set_timer(pentix.FALLING, 270 // self.lvl)
        pygame.time.set_timer(pentix.BOOSTING, 60)
        pygame.event.post(pygame.event.Event(pentix.START))

    def playpause(self):
        self.paused = not self.paused

    def stop(self):
        self.paused = True
        pygame.time.set_timer(pentix.FALLING, 0)
        pygame.time.set_timer(pentix.BOOSTING, 0)
        self.highscore = max(self.score, self.highscore)

    def save(self):
        with open('saving.json', 'w') as f:
            data = {
                'score': self.score,
                'highscore': self.highscore,
                'current': self.current,
                'level': self.level
            }
            json.dump(data, f, default=lambda o: o.__dict__)

    def load(self):
        try:
            with open('saving.json', 'r') as f:
                data = json.load(f)
                self.score = data['score']
                self.highscore = data['highscore']
                self.current.x = data['current']['x']
                self.current.y = data['current']['y']
                self.current.figure = data['current']['figure']
                self.level = data['level']
        except IOError:
            print('You must have saving.json file')

    def exit(self):
        self.quit = True

    def toggle_fullscreen(self):
        self.screen_size = (1024, 768)
        self.fullscreen = not self.fullscreen
        self.draw_main()

    def del_rows(self):
        for i in range(len(self.level)):
            if self.level[i] == [1] * len(self.level[0]):
                self.score += len(self.level[0])
                for j in range(i, 0, -1):
                    self.level[j] = self.level[j - 1].copy()
                self.draw_level()

    def fix_current(self):
        for i in range(len(self.current.figure)):
            for j in range(len(self.current.figure[0])):
                if self.current.y + i >= 0 and self.current.figure[i][j]:
                    self.score += 1
                    self.level[self.current.y + i][self.current.x + j] =\
                        self.current.figure[i][j]
        self.current = figure.Figure(self)
        self.del_rows()

    # graphics
    #
    def draw_main(self):
        self.block_size = int(self.screen_size[1] * .04)
        if self.fullscreen:
            self.screen_size = pygame.display.list_modes()[0]
            self.block_size = int(self.screen_size[1] * .04)
            self.surface = pygame.display.set_mode(
                self.screen_size, FULLSCREEN)
        else:
            self.surface = pygame.display.set_mode(
                self.screen_size, RESIZABLE)
        self.screen = pygame.Surface((self.width * self.block_size,
                                      self.height * self.block_size), 0, 32)

    def draw(self):
        self.surface.fill((0, 174, 240))
        self.draw_buttons()
        self.draw_grid()
        self.draw_cur()
        self.draw_level()
        self.draw_score()
        x = self.surface.get_width() // 2 - self.screen.get_width() // 2
        y = self.surface.get_height() // 2 - self.screen.get_height() // 2
        pygame.draw.rect(self.surface, (30, 30, 30),
                         (x - 5, y + 5,
                          self.width * self.block_size,
                          self.height * self.block_size))
        pygame.draw.rect(self.surface, (30, 30, 30),
                         (x - 1, y - 1,
                          self.width * self.block_size + 2,
                          self.height * self.block_size + 2), 1)
        self.surface.blit(self.screen, (x, y))

    def draw_grid(self):
        self.screen.fill((255, 255, 255))
        color = (50, 50, 50)
        for i in range(10):
            start = (self.block_size * i - 2, 0)
            end = (self.block_size * i - 2, self.height * self.block_size)
            pygame.draw.line(self.screen, color, start, end, 2)
        for i in range(20):
            start = (0, self.block_size * i - 2)
            end = (self.height * self.block_size, self.block_size * i - 2)
            pygame.draw.line(self.screen, color, start, end, 2)

    def draw_level(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.level[i][j]:
                    pygame.draw.rect(self.screen, (30, 30, 30),
                                     ((j * self.block_size + 2,
                                       i * self.block_size + 1),
                                      (self.block_size - 5,
                                       self.block_size - 5)))

    def draw_buttons(self):
        font_color = (255, 255, 255)
        common_color = (19, 104, 234)
        hover_color = (23, 92, 196)
        font_size = int(self.screen_size[1] * .03)
        font = pygame.font.SysFont("Arial", int(self.screen_size[1] * .05))
        text = font.render("New game: ", True, (255, 255, 255))
        self.surface.blit(text, (self.screen_size[0] * .1,
                                 self.screen_size[1] * .125))
        if self.paused:
            text = font.render("Pause", True, (255, 255, 255))
            self.surface.blit(text, (self.screen_size[0] * .1,
                                     self.screen_size[1] * .5))
        draw_button(self.surface,
                    "Easy", font_size, font_color,
                    self.screen_size[0] * .135,
                    self.screen_size[1] * .2,
                    self.screen_size[0] * .11,
                    self.screen_size[1] * .04,
                    common_color, hover_color, self.start, (1,))
        draw_button(self.surface,
                    "Medium", font_size, font_color,
                    self.screen_size[0] * .135,
                    self.screen_size[1] * .25,
                    self.screen_size[0] * .11,
                    self.screen_size[1] * .04,
                    common_color, hover_color, self.start, (2,))
        draw_button(self.surface,
                    "Hard", font_size, font_color,
                    self.screen_size[0] * .135,
                    self.screen_size[1] * .3,
                    self.screen_size[0] * .11,
                    self.screen_size[1] * .04,
                    common_color, hover_color, self.start, (3,))
        draw_button(self.surface,
                    "Load", font_size, font_color,
                    self.screen_size[0] * .7,
                    self.screen_size[1] * .75,
                    self.screen_size[0] * .11,
                    self.screen_size[1] * .04,
                    common_color, hover_color, self.load)
        draw_button(self.surface,
                    "Save", font_size, font_color,
                    self.screen_size[0] * .7,
                    self.screen_size[1] * .8,
                    self.screen_size[0] * .11,
                    self.screen_size[1] * .04,
                    common_color, hover_color, self.save)
        font_size = int(self.screen_size[1] * .04)
        draw_button(self.surface,
                    "Play/Pause", font_size, font_color,
                    self.screen_size[0] * .115,
                    self.screen_size[1] * .6,
                    self.screen_size[0] * .15,
                    self.screen_size[1] * .06,
                    common_color, hover_color, self.playpause)
        draw_button(self.surface,
                    "Fullscreen", font_size, font_color,
                    self.screen_size[0] * .115,
                    self.screen_size[1] * .7,
                    self.screen_size[0] * .15,
                    self.screen_size[1] * .06,
                    common_color, hover_color, self.toggle_fullscreen)
        draw_button(self.surface,
                    "Quit", font_size, font_color,
                    self.screen_size[0] * .115,
                    self.screen_size[1] * .8,
                    self.screen_size[0] * .15,
                    self.screen_size[1] * .06,
                    common_color, hover_color, self.exit)

    def draw_cur(self):
        for i in range(len(self.current.figure)):
            for j in range(len(self.current.figure[0])):
                if self.current.figure[i][j]:
                    pygame.draw.rect(self.screen, (30, 30, 30),
                                     (((self.current.x + j) *
                                       self.block_size + 2,
                                       (self.current.y + i) *
                                       self.block_size + 1),
                                      (self.block_size - 5,
                                       self.block_size - 5)))

    def draw_score(self):
        color = (255, 255, 255)
        font = pygame.font.SysFont("Arial", int(self.screen_size[1] * .06))
        text = font.render("Score: " + str(self.score), True, color)
        self.surface.blit(text, (self.screen_size[0] * .675,
                                 self.screen_size[1] * .2))
        text = font.render("Highscore: " + str(self.highscore), True, color)
        self.surface.blit(text, (self.screen_size[0] * .675,
                                 self.screen_size[1] * .3))
