import pygame, pygameMenu
import copy, queue
import clue_tracker


class Button:
    def __init__(self, color, text, border_width=20, text_size=60, font=None):
        self.color = color
        self.text_size = text_size
        self.font_style = font
        self.font = pygame.font.SysFont(self.font_style, self.text_size)
        self.text_value = text
        self.text = self.font.render(self.text_value, False, (255, 255, 255))
        self.rect = self.text.get_rect()
        self.border_width = border_width
        self.active = True

    def draw_button(self, screen, location):
        self.rect.x, self.rect.y = location
        black_rect = copy.copy(self.rect)
        black_rect.x = self.rect.x + self.border_width
        black_rect.y = self.rect.y + self.border_width
        black_rect.w = self.rect.w - self.border_width * 2
        black_rect.h = self.rect.h - self.border_width * 2
        text_rect = self.text.get_rect(
            center=(self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2))
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (0,0,0), black_rect)
        screen.blit(self.text, text_rect)

    def clicked(self):
        return self.text_value

    def check_clicked(self, x_offset, y_offset):
        pos = pygame.mouse.get_pos()

        rect = self.rect
        if rect.x + x_offset + rect.w > pos[0] > rect.x + x_offset and rect.y + y_offset + rect.h > pos[1] > rect.y + y_offset:
            return True
        else:
            return False

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False

    def update_size(self, size):
        width = size[0]
        height = size[1]
        while self.rect.h < height - self.border_width * 2:
            self.text_size = self.text_size + 1
            self.font = pygame.font.SysFont(self.font_style, self.text_size)
            self.text = self.font.render(self.text_value, False, (255, 255, 255))
            self.rect.w = self.text.get_width() + self.border_width * 2
            self.rect.h = self.text.get_height() + self.border_width * 2
        while self.rect.h > height - self.border_width * 2:
            self.text_size = self.text_size - 1
            self.font = pygame.font.SysFont(self.font_style, self.text_size)
            self.text = self.font.render(self.text_value, False, (255, 255, 255))
            self.rect.w = self.text.get_width() + self.border_width * 2
            self.rect.h = self.text.get_height() + self.border_width * 2




class Options:
    def __init__(self):

        # Variables
        self.TITLE_HEIGHT = 0
        self.TITLE_WIDTH = 0
        self.PLAYER_INFO_HEIGHT = 0
        self.PLAYER_INFO_WIDTH = 0
        self.PLAYER_INFO_SURFACE_RATIO = 0
        self.STATUS_INFO_SURFACE_RATIO = 0
        self.CLUETRACKER_WIDTH = 0
        self.CLUETRACKER_HEIGHT = 0
        self.CLUETRACTER_SURFACE_RATIO = 0
        self.SCALED_WIDTH = 0
        self.SCALED_HEIGHT = 0
        self.STATUS_SCALED_WIDTH = 0
        self.STATUS_SCALED_HEIGHT = 0
        self.TRACKER_SCALED_WIDTH = 180
        self.TRACKER_SCALED_HEIGHT = 180
        self.button_starts = [0, 0, 0]
        self.card_given = False
        self.passed = False
        self.card_to_give = None
        self.status = None
        self.last_message = None
        self.recent_messages = []

        # Response variables
        self.name_selection_done = False
        self.name_selection_canceled = False

        # Move parameters
        self.move_direction = None
        self.move_chosen = False

        # Accusation variables
        self.who_accusation = None
        self.what_accusation = None
        self.where_accusation = None
        self.bool_accuse = False
        self.accuse_chosen = False
        self.name_selection_done = False

        self.error_messages = [
            "Illegal move, cannot move to a hallway with someone already present",
            "You can only suspect the room you are currently in",
            "You must be in a room before you can suspect anyone",
            "The card you are trying to give is not one of the suspected cards",
            "Your hand contains one of the cards in the inquiry, you must give a card",
            "You are attempting to play out of turn. Please wait for your turn.",
            "This name has already been chosen"
        ]

        self.general_messages = [
            " gave the following card: ",
            "CONGRATULATIONS YOU WIN!!!!",
            "Sorry, you lose and are out of the game",
            "Everyone has been eliminated. No one has won the game",
            "Waiting for player to respond",
            "displayed a card in response to the suspicion",
            "Suspect message"
        ]

        # Fonts
        self.text_font_style = 'stencil'
        self.title_font = pygame.font.SysFont('goudy', 100)
        self.category_font = pygame.font.SysFont('stencil', 80)
        self.text_font = pygame.font.SysFont(self.text_font_style, 60)
        self.status_font = pygame.font.SysFont('stencil', 75)

        self.player_info_surface = None
        self.player_info = []
        self.status_info_surface = None
        self.status_info = []
        self.clue_tracker_surface = None

        # Menus
        self.accusation_menu = None
        self.move_menu = None
        self.illegal_move_menu = None
        self.suspect_menu = None
        self.illegal_suspection_menu = None
        self.general_message_menu = None
        self.name_selection_menu = None
        self.menu_list = []

        # Create Clue tracker
        self.clue_tracker = clue_tracker.ClueTracker()
        self.update_clue_tracker()

        # Update title surface
        self.title_surface = self.title_font.render('THE CLUE-LESS GAME', False, (255, 255, 255))
        self.TITLE_WIDTH, self.TITLE_HEIGHT = self.title_surface.get_size()

        # Create the buttons
        self.buttons = []
        self.buttons.append(Button((0, 255, 0), "Move", font=self.text_font_style))
        self.buttons.append(Button((255, 0, 0), "Accuse / Suspect", font=self.text_font_style))
        self.buttons.append(Button((0, 0, 255), "Pass", font=self.text_font_style))

        # Update the player info screen
        self.update_player_info(1, "Miss Scarlet", "Red Demon", "Col. Mustard", "Rope", "Study")

        # Update the status info screen
        self.update_status_info("Status: Waiting for Player 1", "Recent: No new messages to be found")


    def update_clue_tracker(self):
        box_size = self.clue_tracker.BOX_SIZE
        row_count = self.clue_tracker.ROW_SIZE
        col_count = self.clue_tracker.COL_SIZE

        self.clue_tracker.draw()
        self.CLUETRACKER_WIDTH = box_size * col_count + 200
        self.CLUETRACKER_HEIGHT = box_size * row_count
        self.CLUETRACTER_SURFACE_RATIO = self.CLUETRACKER_WIDTH/ self.CLUETRACKER_HEIGHT
        self.clue_tracker_surface = pygame.Surface((self.CLUETRACKER_WIDTH, self.CLUETRACKER_HEIGHT))
        self.clue_tracker_surface.blit(self.clue_tracker.clue_tracker_surface, [0,0])



    def update_player_info(self, player_number, player_name, character, suspects, weapons, rooms):
        self.player_info = []
        self.player_info.append(self.category_font.render('PLAYER INFO', False, (255, 255, 255)))
        self.player_info.append(self.text_font.render(' ', False, (255, 255, 255)))
        self.player_info.append(self.text_font.render('Player Number: ' + str(player_number), False, (255, 255, 255)))
        self.player_info.append(self.text_font.render(' ', False, (255, 255, 255)))
        self.player_info.append(self.text_font.render('Player Name:       ' + player_name, False, (255, 255, 255)))
        self.player_info.append(self.text_font.render(' ', False, (255, 255, 255)))
        self.player_info.append(self.text_font.render('Character:          ' + character, False, (255, 255, 255)))
        self.player_info.append(self.text_font.render(' ', False, (255, 255, 255)))
        self.player_info.append(self.text_font.render('Starting Cards:', False, (255, 255, 255)))
        self.player_info.append(self.text_font.render(' ', False, (255, 255, 255)))
        if suspects:
            self.player_info.append(self.text_font.render('          Suspects:    ' + suspects[0], False, (255, 255, 255)))
            for i in range(1, len(suspects)):
                self.player_info.append(
                    self.text_font.render('                                   ' + suspects[i], False, (255, 255, 255)))
        if weapons:
            self.player_info.append(self.text_font.render('          Weapons:     ' + weapons[0], False, (255, 255, 255)))
            for i in range(1, len(weapons)):
                self.player_info.append(
                    self.text_font.render('                                   ' + weapons[i], False, (255, 255, 255)))
        if rooms:
            self.player_info.append(self.text_font.render('          Rooms:          ' + rooms[0], False, (255, 255, 255)))
            for i in range(1, len(rooms)):
                self.player_info.append(
                    self.text_font.render('                                   ' + rooms[i], False, (255, 255, 255)))
        self.player_info.append(self.text_font.render(' ', False, (255, 255, 255)))

        self.PLAYER_INFO_HEIGHT = 0
        self.PLAYER_INFO_WIDTH = 1000
        temp_surface = pygame.Surface((2560, 2560))
        for info in self.player_info:
            rect = info.get_size()
            temp_surface.blit(info, (0, self.PLAYER_INFO_HEIGHT))
            self.PLAYER_INFO_HEIGHT = self.PLAYER_INFO_HEIGHT + rect[1]

        count = 0
        for button in self.buttons:
            self.button_starts[count] = self.PLAYER_INFO_HEIGHT
            button.rect.w = self.PLAYER_INFO_WIDTH
            button.rect.h = button.text.get_rect().h * 4
            button.draw_button(temp_surface, (0, self.PLAYER_INFO_HEIGHT))
            self.PLAYER_INFO_HEIGHT = self.PLAYER_INFO_HEIGHT + button.rect.h + 40
            count = count + 1

        self.PLAYER_INFO_SURFACE_RATIO = self.PLAYER_INFO_HEIGHT / self.PLAYER_INFO_WIDTH
        self.player_info_surface = pygame.Surface((self.PLAYER_INFO_WIDTH, self.PLAYER_INFO_HEIGHT))
        self.player_info_surface.blit(temp_surface, (0, 0))

    # draw some text into an area of a surface
    # automatically wraps words
    # returns any text that didn't get blitted
    def draw_text(self, surface, text_array, color, rect, font, aa=False, bkg=None):
        rect = pygame.Rect(rect)
        y = rect.top
        lineSpacing = -2

        # get the height of the font
        fontHeight = font.size("Tg")[1]

        for text in text_array:
            while text:
                i = 1

                # determine if the row of text will be outside our area
                if y + fontHeight > rect.bottom:
                    break

                # determine maximum width of line
                while font.size(text[:i])[0] < rect.width and i < len(text):
                    i += 1

                # if we've wrapped the text, then adjust the wrap to the last word
                if i < len(text):
                    i = text.rfind(" ", 0, i) + 1

                # render the line and blit it to the surface
                if bkg:
                    image = font.render(text[:i], 1, color, bkg)
                    image.set_colorkey(bkg)
                else:
                    image = font.render(text[:i], aa, color)

                surface.blit(image, (rect.left, y))
                y += fontHeight + lineSpacing

                # remove the text we just blitted
                text = text[i:]

        return text

    def update_status_info(self, status=None, last_message=None):
        self.status_info = []
        if status:
            self.status = status
        if last_message:
            if len(self.recent_messages):
                if not (last_message == self.recent_messages[0]):
                    self.recent_messages.insert(0, last_message)
                    self.last_message = last_message
            else:
                self.recent_messages.insert(0, last_message)
                self.last_message = last_message
        self.status_info.insert(0, self.status)
        status_length = 0
        if len(self.recent_messages) > 5:
            status_length = 5
        else:
            status_length = len(self.recent_messages)
        for i in range(0, status_length):
            self.status_info.append(self.recent_messages[i])
        # self.status_info.append(self.status_font.render(self.status, False, (255, 255, 255)))
        # self.status_info.append(self.status_font.render(self.last_message, False, (255, 255, 255)))

        self.STATUS_INFO_HEIGHT = 2560
        self.STATUS_INFO_WIDTH = 2560
        temp_surface = pygame.Surface((2560, 2560))
        rect = temp_surface.get_rect()
        self.draw_text(temp_surface,
                       self.status_info,
                       (255, 255, 255),
                       rect,
                       self.status_font)
        # for info in self.status_info:
        #     rect = info.get_size()
        #     temp_surface.blit(info, (0, self.STATUS_INFO_HEIGHT))
        #     self.STATUS_INFO_HEIGHT = self.STATUS_INFO_HEIGHT + rect[1]

        self.STATUS_INFO_SURFACE_RATIO = self.STATUS_INFO_HEIGHT / self.STATUS_INFO_WIDTH
        self.status_info_surface = pygame.Surface((self.STATUS_INFO_WIDTH, self.STATUS_INFO_HEIGHT))
        self.status_info_surface.blit(temp_surface, (0, 0))

    def update_scaled_values(self, width, height):
        self.SCALED_WIDTH = width
        self.SCALED_HEIGHT = height

    def update_status_scaled_values(self, width, height):
        self.STATUS_SCALED_WIDTH = width
        self.STATUS_SCALED_HEIGHT = height

    def update_tracker_scaled_values(self, width, height):
        self.TRACKER_SCALED_WIDTH = width
        self.TRACKER_SCALED_HEIGHT = height

    def check_button_clicked(self, position, offset):
        count = 0
        scaled_ratio = self.SCALED_HEIGHT / self.PLAYER_INFO_HEIGHT
        for button in self.buttons:
            if not self.menus_active():
                rect = button.text.get_rect()
                rect_x = rect.x + offset[0]
                rect_y = rect.y + offset[1] + int(self.button_starts[count] * scaled_ratio)
                rect_w = self.SCALED_WIDTH
                rect_h = int(rect.h * 4 * scaled_ratio)
                if rect_x + rect_w > position[0] > rect_x and rect_y + rect_h > position[1] > rect_y:
                    print("button clicked: ", button.clicked())
                    return button.clicked()
                count = count + 1

        offset2 = [offset[0] + self.SCALED_WIDTH + 40, offset[1]]
        self.clue_tracker.clicked(position, offset2, self.TRACKER_SCALED_HEIGHT, self.TRACKER_SCALED_WIDTH)
        self.update_clue_tracker()

        return "None"

    def init_suspect_menu(self, screen, initiator, responder, cards):
        screen_width, screen_height = screen.get_size()
        text_menu = pygameMenu.TextMenu(screen,
                                        dopause=False,
                                        font=pygameMenu.fonts.FONT_FRANCHISE,
                                        menu_color=(30, 50, 107),  # Background color
                                        menu_color_title=(120, 45, 30),
                                        menu_width=600,
                                        menu_height=300,
                                        onclose=pygameMenu.locals.PYGAME_MENU_CLOSE,  # Pressing ESC button does nothing
                                        title='Suspection',
                                        window_height=screen_height,
                                        window_width=screen_width
                                        )
        text_menu.add_line(responder.upper())
        line_1 = "The player " + initiator.upper() + " has accused " + self.who_accusation.upper() + " of the"
        line_2 = "murder in the " + self.where_accusation.upper() + " with the " + self.what_accusation.upper()
        text_menu.add_line(line_1)
        text_menu.add_line(line_2)
        text_menu.add_option('Back', pygameMenu.locals.PYGAME_MENU_BACK)

        self.suspect_menu = pygameMenu.Menu(screen,
                                               dopause=False,
                                               enabled=False,
                                               font=pygameMenu.fonts.FONT_NEVIS,
                                               menu_alpha=85,
                                               menu_color=(0, 0, 0),  # Background color
                                               menu_color_title=(255, 0, 0),
                                               menu_height=400,
                                               menu_width=1200,
                                               onclose=pygameMenu.locals.PYGAME_MENU_CLOSE,
                                               # If this menu closes (press ESC) back to main
                                               title=responder.upper() + ': Suspection',
                                               title_offsety=5,  # Adds 5px to title vertical position
                                               window_height=screen_height,
                                               window_width=screen_width
                                               )
        self.suspect_menu.add_option('View Suspection', text_menu)
        self.suspect_menu.add_selector('Give card?',
                               cards,
                               onchange=self.update_card_given,
                               onreturn=self.update_card_given,
                               default=1
                               )
        self.suspect_menu.add_option('Give', self.give_card)
        self.suspect_menu.add_option('Pass', self.pass_turn)
        self.menu_list.append(self.suspect_menu)

    def init_move_menu(self, screen, directions):
        H_SIZE = 600
        W_SIZE = 600
        screen_width, screen_height = screen.get_size()
        formatted_directions = []
        for direction in directions:
            formatted_directions.append((direction, direction))

        self.move_menu = pygameMenu.Menu(screen,
                                         dopause=False,
                                         enabled=False,
                                         font=pygameMenu.fonts.FONT_NEVIS,
                                         menu_alpha=85,
                                         menu_color=(0, 0, 0),  # Background color
                                         menu_color_title=(0, 0, 255),
                                         menu_height=int(H_SIZE / 2),
                                         menu_width=W_SIZE,
                                         onclose=pygameMenu.locals.PYGAME_MENU_CLOSE,
                                         # If this menu closes (press ESC) back to main
                                         title='Move',
                                         title_offsety=10,  # Adds 5px to title vertical position
                                         window_height=screen_height,
                                         window_width=screen_width
                                         )

        self.move_menu.add_selector('Move to?',
                                    formatted_directions,
                                    onchange=self.update_move_direction,
                                    onreturn=self.update_move_direction,
                                    default=1
                                    )
        self.move_menu.add_option('Done', self.movement_chosen)
        self.move_menu.add_option('Cancel', pygameMenu.locals.PYGAME_MENU_CLOSE)
        self.menu_list.append(self.move_menu)

    def init_name_selection_menu(self, screen):
        H_SIZE = 800
        W_SIZE = 800
        screen_width, screen_height = screen.get_size()
        self.name_selection_menu = pygameMenu.Menu(screen,
                                               dopause=False,
                                               enabled=False,
                                               font=pygameMenu.fonts.FONT_NEVIS,
                                               menu_alpha=85,
                                               menu_color=(0, 0, 0),  # Background color
                                               menu_color_title=(255, 0, 0),
                                               menu_height=int(H_SIZE / 2),
                                               menu_width=W_SIZE,
                                               onclose=pygameMenu.locals.PYGAME_MENU_CLOSE,
                                               # If this menu closes (press ESC) back to main
                                               title='Choose a name',
                                               title_offsety=5,  # Adds 5px to title vertical position
                                               window_height=screen_height,
                                               window_width=screen_width
                                               )

        self.name_selection_menu.add_selector('Name:',
                                          [('Miss Scarlet', 'Miss Scarlet'),
                                           ('Prof. Plum', 'Prof. Plum'),
                                           ('Col. Mustard', 'Col. Mustard'),
                                           ('Mrs. Peacock', 'Mrs. Peacock'),
                                           ('Mr. Green', 'Mr. Green'),
                                           ('Mrs. White', 'Mrs. White'),
                                           ],
                                          onchange=self.update_name_selection,
                                          onreturn=self.update_name_selection,
                                          default=1
                                          )
        self.name_selection_menu.add_option('Done', self.done_selecting_name)
        self.name_selection_menu.add_option('Cancel', self.cancel_selectiong_name)
        self.menu_list.append(self.name_selection_menu)

    def init_accusation_menu(self, screen):
        H_SIZE = 800
        W_SIZE = 800
        screen_width, screen_height = screen.get_size()
        self.accusation_menu = pygameMenu.Menu(screen,
                                               dopause=False,
                                               enabled=False,
                                               font=pygameMenu.fonts.FONT_NEVIS,
                                               menu_alpha=85,
                                               menu_color=(0, 0, 0),  # Background color
                                               menu_color_title=(255, 0, 0),
                                               menu_height=int(H_SIZE / 2),
                                               menu_width=W_SIZE,
                                               onclose=pygameMenu.locals.PYGAME_MENU_CLOSE,
                                               # If this menu closes (press ESC) back to main
                                               title='Suspect / Accuse',
                                               title_offsety=5,  # Adds 5px to title vertical position
                                               window_height=screen_height,
                                               window_width=screen_width
                                               )

        self.accusation_menu.add_selector('Who?',
                                          [('Miss Scarlet', 'Miss Scarlet'),
                                           ('Prof. Plum', 'Prof. Plum'),
                                           ('Col. Mustard', 'Col. Mustard'),
                                           ('Mrs. Peacock', 'Mrs. Peacock'),
                                           ('Mr. Green', 'Mr. Green'),
                                           ('Mrs. White', 'Mrs. White'),
                                           ],
                                          onchange=self.update_who_accusation,
                                          onreturn=self.update_who_accusation,
                                          default=1
                                          )

        self.accusation_menu.add_selector('What?',
                                          [('Candlestick', 'Candlestick'),
                                           ('Knife', 'Knife'),
                                           ('Lead Pipe', 'Lead Pipe'),
                                           ('Revolver', 'Revolver'),
                                           ('Rope', 'Rope'),
                                           ('Wrench', 'Wrench'),
                                           ],
                                          onchange=self.update_what_accusation,
                                          onreturn=self.update_what_accusation,
                                          default=1
                                          )

        self.accusation_menu.add_selector('Where?',
                                          [('Ballroom', 'Ballroom'),
                                           ('Billiard Room', 'Billiard Room'),
                                           ('Conservatory', 'Conservatory'),
                                           ('Dining Room', 'Dining Room'),
                                           ('Hall', 'Hall'),
                                           ('Kitchen', 'Kitchen'),
                                           ('Library', 'Library'),
                                           ('Lounge', 'Lounge'),
                                           ('Study', 'Study'),
                                           ],
                                          onchange=self.update_where_accusation,
                                          onreturn=self.update_where_accusation,
                                          default=1
                                          )
        self.accusation_menu.add_selector('Accuse?',
                                          [('Accuse', 'Accuse'),
                                           ('Suspect', 'Suspect'),
                                           ],
                                          onchange=self.accuse_supect,
                                          onreturn=self.accuse_supect,
                                          default=1
                                          )
        self.accusation_menu.add_option('Done', self.done_accusing)
        self.accusation_menu.add_option('Cancel', pygameMenu.locals.PYGAME_MENU_CLOSE)
        self.menu_list.append(self.accusation_menu)

    def init_illegal_move_menu(self, screen, message_number):
        screen_width, screen_height = screen.get_size()
        self.illegal_move_menu = pygameMenu.TextMenu(screen,
                                dopause=False,
                                font=pygameMenu.fonts.FONT_FRANCHISE,
                                menu_color=(30, 50, 107),  # Background color
                                menu_color_title=(120, 45, 30),
                                menu_width=600,
                                menu_height=200,
                                onclose=pygameMenu.locals.PYGAME_MENU_CLOSE,  # Pressing ESC button does nothing
                                title='Illegal Move',
                                window_height=screen_height,
                                window_width=screen_width
                                )
        self.illegal_move_menu.add_line(self.error_messages[message_number])
        # self.menu_list.append(self.illegal_move_menu)

    def init_general_message_menu(self, screen, message_number, param=None):
        screen_width, screen_height = screen.get_size()
        self.general_message_menu = pygameMenu.TextMenu(screen,
                                                        dopause=False,
                                                        font=pygameMenu.fonts.FONT_FRANCHISE,
                                                        menu_color=(30, 50, 107),  # Background color
                                                        menu_color_title=(120, 45, 30),
                                                        menu_width=600,
                                                        menu_height=200,
                                                        onclose=pygameMenu.locals.PYGAME_MENU_CLOSE,
                                                        # Pressing ESC button does nothing
                                                        title='General Message',
                                                        window_height=screen_height,
                                                        window_width=screen_width
                                                        )

        message = self.general_messages[message_number]
        if message_number == 0:
            message = "Player " + str(param[0]) + message + str(param[1])
            self.general_message_menu.add_line(message)

            # Update the last message
            self.update_status_info(last_message="Recent: " + message)

        elif message_number == 5:
            message = "Player " + str(param) + " " + message
            self.general_message_menu.add_line(message)

            # Update the last message
            self.update_status_info(last_message="Recent: " + message)

        elif message_number == 6:
            line_1 = "Player " + str(param[0]) + " has accused " + str(param[1]) + " of the"
            line_2 = "murder in the " + str(param[2]) + " with the " + str(param[3]) + "."
            line_3 = "Waiting for other players to respond"
            full_message = line_1 + " " + line_2
            self.general_message_menu.add_line(line_1)
            self.general_message_menu.add_line(line_2)
            self.general_message_menu.add_line(line_3)

            # Update the last message
            self.update_status_info(last_message="Recent: " + full_message)

        else:
            self.general_message_menu.add_line(message)

        # self.menu_list.append(self.general_message_menu)

    def menus_active(self):
        for menu in self.menu_list:
            if menu and menu.is_enabled():
                return True
        return False

    def enable_buttons(self):
        for button in self.buttons:
            button.enable()

    def disable_buttons(self):
        for button in self.buttons:
            button.disable()

    def update_name_selection(self, c, **kwargs):
        self.name_selected = c

    def update_move_direction(self, c, **kwargs):
        self.move_direction = c

    def update_who_accusation(self, c, **kwargs):
        self.who_accusation = c

    def update_what_accusation(self, c, **kwargs):
        self.what_accusation = c

    def update_where_accusation(self, c, **kwargs):
        self.where_accusation = c

    def update_card_given(self, c, **kwargs):
        self.card_to_give = c

    def give_card(self):
        self.card_given = True

    def pass_turn(self):
        self.passed = True

    def accuse_supect(self, c, **kwargs):
        if c == "Accuse":
            self.bool_accuse = True
        else:
            self.bool_accuse = False

    def done_accusing(self):
        self.accuse_chosen = True

    def done_selecting_name(self):
        self.name_selection_done = True

    def cancel_selectiong_name(self):
        self.name_selection_canceled = True

    def movement_chosen(self):
        self.move_chosen = True


