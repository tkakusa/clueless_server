import pygame
from options_menu import Button
from player import Player
import os, re

class CharacterSelect:
    def __init__(self):
        self.width = int(400)
        self.height = int(300)
        self.character_select_screen = pygame.Surface((self.width, self.height))
        self.character_select_screen.fill((0, 0, 0))
        # self.character_select_screen.set_alpha(200)
        self.active = False
        self.root_screen_width = None
        self.root_screen_height = None

        # Selection variables
        self.left_arrow_clicked = False
        self.right_arrow_clicked = False
        self.select_clicked = False
        self.back_clicked = False

        # Setup the header text
        self.font_style = None
        self.arrow_font_style = 'stencil'
        self.font = pygame.font.Font(self.font_style, 50)
        self.text = self.font.render("Choose Character", True, (255, 255, 255))
        text_size = self.text.get_size()
        text_rect = self.text.get_rect(center=(self.width / 2, text_size[1] / 2))

        # Load Room image
        self.room_image = pygame.image.load('images\single_room.png')
        y_location = (self.height - text_size[1]) / 2
        self.room_rect = self.room_image.get_rect(center=(self.width / 2, y_location))

        ## Setup the buttons ##
        # Left arrow button
        self.left_arrow = Button((255, 0, 0), "<-", border_width=0, text_size=30, font=self.arrow_font_style)
        self.left_arrow.rect.w = self.width / 6;
        self.left_arrow.rect.h = self.height / 12;
        self.left_arrow.draw_button(self.character_select_screen, (20, self.height / 2 - text_size[1]))
        print("Rect: ", self.left_arrow.rect)

        # Right arrow button
        self.right_arrow = Button((255, 0, 0), "->", border_width=0, text_size=30, font=self.arrow_font_style)
        self.right_arrow.rect.w = self.width / 6;
        self.right_arrow.rect.h = self.height / 12;
        self.right_arrow.draw_button(self.character_select_screen,
                                     (self.width - self.right_arrow.rect.w - 20, self.height / 2 - text_size[1]))

        # Select button
        self.select_button = Button((0, 0, 255), "Select", border_width=10, text_size=30, font=self.font_style)
        self.select_button.rect.w = self.width / 2 - 40;
        self.select_button.rect.h = self.height - self.room_rect.bottom - 20;
        self.select_button.draw_button(self.character_select_screen,
                                       (self.width - self.select_button.rect.w - 20, self.room_rect.bottom + 10))

        # back button
        self.back_button = Button((255, 0, 0), "Back", border_width=10, text_size=30, font=self.font_style)
        self.back_button.rect.w = self.width / 2 - 40;
        self.back_button.rect.h = self.height - self.room_rect.bottom - 20;
        self.back_button.draw_button(self.character_select_screen,
                                       (20, self.room_rect.bottom + 10))


        # Load the player
        cwd = os.getcwd()
        self.player = Player(cwd + "\\images\\players\\big_demon",None, None, None, None)
        self.player_iter = 0
        file_list = os.listdir(cwd + "\\images\\players")
        self.player_file_locations = []
        for file in file_list:
            self.player_file_locations.append(cwd + "\\images\\players\\" + file)
        self.update_player()

        self.character_select_screen.blit(self.text, text_rect)
        self.character_select_screen.blit(self.room_image, self.room_rect)


    def update_player(self):
        player_x = self.room_rect.left + self.room_rect.width / 2
        player_y = self.room_rect.top + self.room_rect.height / 2 + self.player.sprite_height / 2
        if self.player.sprite_type == "LARGE":
            self.player.sprite_width = int(self.room_rect.width / 4)
        else:
            self.player.sprite_width = int(self.room_rect.width / 8)
        self.player.sprite_height = int(self.player.sprite_width * self.player.size_ratio)
        for i in range(0, len(self.player.sprites)):
            self.player.sprites[i] = pygame.transform.scale(self.player.sprites[i],
                                                            (self.player.sprite_width, self.player.sprite_height))
        self.player.set_location((player_x, player_y))
        self.player.bool_is_active = True
        self.player.animate(True, self.character_select_screen)

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False

    def change_player(self, increase):
        if increase:
            self.player_iter = self.player_iter + 1
            if self.player_iter >= len(self.player_file_locations):
                self.player_iter = 0
            self.player = Player(self.player_file_locations[self.player_iter], None, None, None, None)
            self.update_player()
        else:
            self.player_iter = self.player_iter - 1
            if self.player_iter < 0:
                self.player_iter = len(self.player_file_locations) - 1
            self.player = Player(self.player_file_locations[self.player_iter], None, None, None, None)
            self.update_player()

    def draw(self, screen, bool_animate, screen_widtth, screen_height):
        self.root_screen_width = screen_widtth
        self.root_screen_height = screen_height
        self.character_select_screen.blit(self.room_image, self.room_rect)
        self.player.animate(bool_animate, self.character_select_screen)

        rect = self.character_select_screen.get_rect(
            center=(screen_widtth / 2, screen_height / 2))
        screen.blit(self.character_select_screen, rect)

    def mainloop(self, events, sio):
        if self.active:
            for event in events:
                # Mouse click events
                if event.type == pygame.MOUSEBUTTONUP:
                    x_offset = self.root_screen_width / 2 - self.width / 2
                    y_offset = self.root_screen_height / 2 - self.height / 2
                    # Check right arrow
                    if self.right_arrow.check_clicked(x_offset, y_offset):
                        self.right_arrow_clicked = True

                    # Check left arrow
                    if self.left_arrow.check_clicked(x_offset, y_offset):
                        self.left_arrow_clicked = True

                    # Check the select button
                    if self.select_button.check_clicked(x_offset, y_offset):
                        self.select_clicked = True

                    # Check the back button
                    if self.back_button.check_clicked(x_offset, y_offset):
                        self.back_clicked = True

                # Check if a key was pressed
                if event.type == pygame.KEYDOWN:
                    # Check if the return / enter key was pressed
                    if event.key == pygame.K_RETURN:
                        self.select_clicked = True

                    # Check right arrow
                    elif event.key == pygame.K_RIGHT:
                        self.right_arrow_clicked = True

                    # Check left arrow
                    elif event.key == pygame.K_LEFT:
                        self.left_arrow_clicked = True

                    # Check back key
                    elif event.key == pygame.K_BACKSPACE:
                        self.back_clicked = True

            # Check if any statuses were changed
            if self.left_arrow_clicked:
                self.left_arrow_clicked = False
                self.change_player(False)
            elif self.right_arrow_clicked:
                self.right_arrow_clicked = False
                self.change_player(True)