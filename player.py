import glob
import pygame
import copy
from clue_tracker import Checkbox

class Player:

    def __init__(self, sprite_file, room, number, name, character):
        ## Variables ##
        self.current_sprite = 0
        self.sprites = []
        self.sprite_state = "WAIT"
        self.sprite_direction = "RIGHT"
        self.sprite_location = [0, 0]
        self.start_location = [0, 0]
        self.final_location = [0, 0]
        self.sprite_width = 16
        self.sprite_height = 32
        self.sprite_room = room
        self.vertical_adjust = 0
        self.size_ratio = 0
        self.sprite_type = "SMALL"
        self.player_number = number
        self.player_name = name
        self.character = character
        self.bool_is_active = False
        self.bool_still_playing = True
        self.room_size = 0
        self.warped = False
        self.who_cards = []
        self.where_cards = []
        self.what_cards = []
        self.clue_grid = []

        # Font
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.player_label = self.font.render(self.player_name, False, (255, 255, 255))

        # Load sprites
        location_list = glob.glob(sprite_file + "\\*")

        for location in location_list:
            self.sprites.append(pygame.image.load(location))

        temp_size = self.sprites[0].get_size()

        if temp_size[0] > 16:
            self.sprite_type = "LARGE"
        self.size_ratio = temp_size[1] / temp_size[0]

        # Init clue grid
        self.init_clue_grid()

    def init_clue_grid(self):
        for row in range(0, 25):
            row_array = []
            for col in range(0, 6):
                row_array.append(Checkbox([row, col]))
            self.clue_grid.append(row_array)

    def update_cards(self, card_type, cards):
        if card_type == "WHO":
            self.who_cards = cards
        if card_type == "WHERE":
            self.where_cards = cards
        if card_type == "WHAT":
            self.what_cards = cards

    def stop(self):
        self.current_sprite = 0
        self.sprite_state = "WAIT"

    def move(self, direction, final_location, new_room, room_size):
        self.start_location = copy.copy(self.sprite_location)
        if final_location[0] < self.sprite_location[0]:
            self.current_sprite = 8
        else:
            self.current_sprite = 4
        self.sprite_state = "MOVE"
        self.sprite_direction = direction
        if direction == "DOWN":
            self.vertical_adjust = self.vertical_adjust + self.sprite_height / 10
        elif direction == "UP":
            self.vertical_adjust = self.vertical_adjust - self.sprite_height / 10
        sprite_adjust = [final_location[0] - self.sprite_width / 2, final_location[1] - self.sprite_height - self.vertical_adjust]
        self.final_location = sprite_adjust
        self.sprite_room = new_room
        self.room_size = room_size
        self.warped = False

    def set_location(self, location):
        sprite_adjust = [location[0] - self.sprite_width/2, location[1] - self.sprite_height - self.vertical_adjust]
        self.sprite_location = sprite_adjust

    def get_location(self):
        return copy.copy(self.sprite_location)

    def transform_sprites(self, screen_width):
        if self.sprite_type == "LARGE":
            self.sprite_width = int(screen_width / 45)
            self.sprite_height = int(self.size_ratio * self.sprite_width)
        else:
            self.sprite_width = int(screen_width / 90)
            self.sprite_height = int(self.size_ratio * self.sprite_width)
        for i in range(0, len(self.sprites)):
            self.sprites[i] = pygame.transform.scale(self.sprites[i], (self.sprite_width, self.sprite_height))

        label_ratio = self.player_label.get_rect().h / self.player_label.get_rect().w
        label_width = int(screen_width / 25)
        label_height = int(label_width * label_ratio)
        self.player_label = pygame.transform.scale(self.player_label, (label_width, label_height))

    def animate(self, bool_animate, screen):
        if bool_animate and self.bool_is_active:
            if self.sprite_state == "WAIT":
                self.current_sprite = self.current_sprite + 1
                if self.current_sprite > 3:
                    self.current_sprite = 0
            if self.sprite_state == "MOVE":
                if self.sprite_direction == "RIGHT":
                    self.current_sprite = self.current_sprite + 1
                    if self.current_sprite > 7:
                        self.current_sprite = 4

                    self.sprite_location[0] = self.sprite_location[0] + 5

                    if self.sprite_location[0] >= self.final_location[0]:
                        self.sprite_location[0] = self.final_location[0]
                        self.current_sprite = 0
                        self.sprite_state = "WAIT"

                elif self.sprite_direction == "LEFT":
                    self.current_sprite = self.current_sprite + 1
                    if self.current_sprite > 11:
                        self.current_sprite = 8

                    self.sprite_location[0] = self.sprite_location[0] - 5

                    if self.sprite_location[0] <= self.final_location[0]:
                        self.sprite_location[0] = self.final_location[0]
                        self.current_sprite = 0
                        self.sprite_state = "WAIT"

                elif self.sprite_direction == "DOWN":
                    self.current_sprite = self.current_sprite + 1
                    if self.current_sprite > 7:
                        self.current_sprite = 4

                    self.sprite_location[1] = self.sprite_location[1] + 5

                    if self.sprite_location[1] >= self.final_location[1]:
                        self.sprite_location = self.final_location
                        self.current_sprite = 0
                        self.sprite_state = "WAIT"

                elif self.sprite_direction == "UP":
                    self.current_sprite = self.current_sprite + 1
                    if self.current_sprite > 7:
                        self.current_sprite = 4

                    self.sprite_location[1] = self.sprite_location[1] - 5

                    if self.sprite_location[1] <= self.final_location[1]:
                        self.sprite_location = self.final_location
                        self.current_sprite = 0
                        self.sprite_state = "WAIT"
                elif self.sprite_direction == "DIAG_RD":
                    self.current_sprite = self.current_sprite + 1
                    if self.current_sprite > 7:
                        self.current_sprite = 4

                    self.sprite_location[1] = self.sprite_location[1] + 5
                    self.sprite_location[0] = self.sprite_location[0] + 5

                    if self.sprite_location[0] + self.sprite_width >= self.start_location[0] + self.room_size / 2 and not self.warped:
                        warp_location = [self.final_location[0] - self.room_size/2 + self.sprite_width,
                                         self.final_location[1] - self.room_size/2 + self.sprite_height]
                        self.sprite_location = warp_location
                        self.warped = True

                    if self.sprite_location[1] >= self.final_location[1]:
                        self.sprite_location = self.final_location
                        self.current_sprite = 0
                        self.sprite_state = "WAIT"
                elif self.sprite_direction == "DIAG_RU":
                    self.current_sprite = self.current_sprite + 1
                    if self.current_sprite > 7:
                        self.current_sprite = 4

                    self.sprite_location[1] = self.sprite_location[1] - 5
                    self.sprite_location[0] = self.sprite_location[0] + 5

                    if self.sprite_location[0] + self.sprite_width >= self.start_location[0] + self.room_size / 2 and not self.warped:
                        warp_location = [self.final_location[0] - self.room_size/2,
                                         self.final_location[1] + self.room_size/2]
                        self.sprite_location = warp_location
                        self.warped = True

                    if self.sprite_location[0] >= self.final_location[0]:
                        self.sprite_location = self.final_location
                        self.current_sprite = 0
                        self.sprite_state = "WAIT"
                elif self.sprite_direction == "DIAG_LD":
                    self.current_sprite = self.current_sprite + 1
                    if self.current_sprite > 7:
                        self.current_sprite = 4

                    self.sprite_location[1] = self.sprite_location[1] + 5
                    self.sprite_location[0] = self.sprite_location[0] - 5

                    if self.sprite_location[0] <= self.start_location[0] - self.room_size / 2 and not self.warped:
                        warp_location = [self.final_location[0] + self.room_size/2 - self.sprite_width,
                                         self.final_location[1] - self.room_size/2 + self.sprite_height]
                        self.sprite_location = warp_location
                        self.warped = True

                    if self.sprite_location[0] <= self.final_location[0]:
                        self.sprite_location = self.final_location
                        self.current_sprite = 0
                        self.sprite_state = "WAIT"
                elif self.sprite_direction == "DIAG_LU":
                    self.current_sprite = self.current_sprite + 1
                    if self.current_sprite > 7:
                        self.current_sprite = 4

                    self.sprite_location[1] = self.sprite_location[1] - 5
                    self.sprite_location[0] = self.sprite_location[0] - 5

                    if self.sprite_location[0] <= self.start_location[0] - self.room_size / 2 and not self.warped:
                        warp_location = [self.final_location[0] + self.room_size/2 - self.sprite_width,
                                         self.final_location[1] + self.room_size/2]
                        self.sprite_location = warp_location
                        self.warped = True

                    if self.sprite_location[0] <= self.final_location[0]:
                        self.sprite_location = self.final_location
                        self.current_sprite = 0
                        self.sprite_state = "WAIT"

        current_sprite = self.sprites[self.current_sprite]
        sprite_rect = current_sprite.get_rect()
        if self.player_name:
            text_rect = self.player_label.get_rect(
                center=(self.sprite_location[0] + sprite_rect.w / 2, self.sprite_location[1] + self.player_label.get_rect()[1] / 2))
            pygame.draw.rect(screen, (0,0,0), text_rect)
            screen.blit(self.player_label, text_rect)
        screen.blit(self.sprites[self.current_sprite], self.sprite_location)