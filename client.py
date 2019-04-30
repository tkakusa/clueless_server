import pygame, pygameMenu
import os, json
from player import Player
from character_select import CharacterSelect
import options_menu
import random
import socketio


# Global variables
connected = False
message_received = False
message = None

sio = socketio.Client()


@sio.on('connect')
def on_connect():
    global connected
    print('Connected to server')
    connected = True


@sio.on('my message')
def on_message(data):
    global message_received
    global message
    print('received message type: ', data["message_type"])
    message_received = True
    message = data


@sio.on('disconnect')
def on_disconnect():
    global connected
    print('Disconnected from server')
    connected = False


class Clueless:
    def __init__(self):
        # Initialize the pygame module
        pygame.init()

        # Set the title of the screen
        pygame.display.set_caption("The Game of Clue-Less")

        # Create the actual screen
        self.screen = pygame.display.set_mode((2560, 1440), pygame.RESIZABLE)

        # Create the options menu
        self.options = options_menu.Options()
        self.options.init_accusation_menu(self.screen)
        self.options.init_move_menu(self.screen, ["NONE"])
        self.options.init_suspect_menu(self.screen, "None", "none", ["None"])
        self.options.init_name_selection_menu(self.screen)

        # Load Images
        self.logo_image = pygame.image.load('images\logo2.png')
        self.house_image = pygame.image.load('images\house.jpg')
        self.start_image = pygame.image.load('images\start.png').convert_alpha()
        self.map_image = pygame.image.load('images\map3.png')

        # Color variables
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        
        # Variables
        self.SCREEN_WIDTH = 2560
        self.SCREEN_HEIGHT = 1440
        self.ROOM_DIMENSIONS = 200
        self.MAP_WIDTH = self.ROOM_DIMENSIONS * 5
        self.MAP_HEIGHT = self.ROOM_DIMENSIONS * 5
        self.MAP_SIZE = self.map_image.get_size()
        self.SCREEN_DIVIDER_START = self.ROOM_DIMENSIONS/2 + self.MAP_SIZE[0] + self.ROOM_DIMENSIONS/2
        self.OPTIONS_WIDTH = self.SCREEN_WIDTH - self.SCREEN_DIVIDER_START
        self.MAP_X = (self.SCREEN_DIVIDER_START - self.MAP_SIZE[0]) / 3
        self.MAP_Y = (self.SCREEN_HEIGHT - self.MAP_SIZE[1]) / 3
        self.PLAYER_COUNT = 5
        self.ACTIVE_PLAYERS = 5
        self.screen_opacity = 0
        self.start_opacity = 150
        self.question_order = []
        self.current_responder = None
        self.who_accusation = None
        self.what_accusation = None
        self.where_accusation = None
        self.actual_who = None
        self.actual_what = None
        self.actual_where = None
        self.remove_player = False
        self.player_total_count = 0
        self.player_ready_count = 0
        self.card_list = None

        # Action variables
        self.start_button_clicked = False

        self.MAP_LOCATIONS = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        self.MAP_DICT = None

        # Create the start button
        self.start_button = options_menu.Button(self.GREEN, "Connect", font=None)

        # Initialize the map dict
        self.init_map_dict()

        # Update the map locations
        self.update_map_locations()

        # Initialize the character select screen
        self.character_select = CharacterSelect()

        # Initialize clock and timer
        self.clock = pygame.time.Clock()
        pygame.time.set_timer(pygame.USEREVENT, 100)

        # # Load the players
        # cwd = os.getcwd()
        self.player_number = None
        self.current_player = None
        self.this_player = None
        self.player_detail_list = []
        self.player_list = []


        # Screen fade parameters
        self.fade = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.fade.fill(self.BLACK)

        # State enums
        self.program_state = "MENU"
        self.menu_state = "INIT"
        self.game_state = "INIT"
        self.suspect_loop = "INIT"
        self.opacity_direction = "UP"

    def init_player_cards(self):
        who_cards = [
            'Miss Scarlet',
            'Prof. Plum',
            'Col. Mustard',
            'Mrs. Peacock',
            'Mr. Green',
            'Mrs. White'
        ]

        what_cards = [
            'Candlestick',
            'Knife',
            'Lead Pipe',
            'Revolver',
            'Rope',
            'Wrench'
        ]

        where_cards = [
            'Ballroom',
            'Billiard Room',
            'Conservatory',
            'Dining Room',
            'Hall',
            'Kitchen',
            'Library',
            'Study'
        ]
        location = random.randint(0, len(who_cards)-1)
        self.actual_who = who_cards[location]
        who_cards.pop(location)
        location = random.randint(0, len(who_cards) - 1)
        self.actual_what = what_cards[location]
        what_cards.pop(location)
        location = random.randint(0, len(who_cards) - 1)
        self.actual_where = where_cards[location]
        where_cards.pop(location)
        cards_list = who_cards + what_cards + where_cards
        count = 0
        print(self.actual_who, " ", self.actual_what, " ", self.actual_where)
        while True:
            player = self.player_list[count]
            location = random.randint(0, len(cards_list)-1)
            card = cards_list[location]
            cards_list.pop(location)
            if card in who_cards:
                player.update_cards("WHO", card)
            if card in what_cards:
                player.update_cards("WHAT", card)
            if card in where_cards:
                player.update_cards("WHERE", card)
            count = count + 1
            if not cards_list:
                break
            if count == self.PLAYER_COUNT:
                count = 0
    def init_map_dict(self):
        with open("map_dict.json", "r") as map_dict_file:
            self.MAP_DICT = json.load(map_dict_file)

    def blit_alpha(self, target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)
        target.blit(temp, location)

    def update_map_locations(self):
        divisor = self.MAP_SIZE[0] / 10
        row = divisor
        col = divisor
        for i in range(0, 5):
            for j in range(0, 5):
                self.MAP_LOCATIONS[i][j] = [int(col + self.MAP_X), int(row + self.MAP_Y)]
                if i == 0 and j == 0:
                    self.MAP_DICT["STUDY"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 1 and j == 0:
                    self.MAP_DICT["H0"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 2 and j == 0:
                    self.MAP_DICT["HALL"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 3 and j == 0:
                    self.MAP_DICT["H1"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 4 and j == 0:
                    self.MAP_DICT["LOUNGE"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 0 and j == 1:
                    self.MAP_DICT["H2"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 2 and j == 1:
                    self.MAP_DICT["H3"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 4 and j == 1:
                    self.MAP_DICT["H4"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 0 and j == 2:
                    self.MAP_DICT["LIBRARY"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 1 and j == 2:
                    self.MAP_DICT["H5"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 2 and j == 2:
                    self.MAP_DICT["BILLIARD_ROOM"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 3 and j == 2:
                    self.MAP_DICT["H6"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 4 and j == 2:
                    self.MAP_DICT["DINING_ROOM"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 0 and j == 3:
                    self.MAP_DICT["H7"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 2 and j == 3:
                    self.MAP_DICT["H8"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 4 and j == 3:
                    self.MAP_DICT["H9"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 0 and j == 4:
                    self.MAP_DICT["CONSERVATORY"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 1 and j == 4:
                    self.MAP_DICT["H10"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 2 and j == 4:
                    self.MAP_DICT["BALLROOM"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 3 and j == 4:
                    self.MAP_DICT["H11"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                elif i == 4 and j == 4:
                    self.MAP_DICT["KITCHEN"]["LOCATION"] = self.MAP_LOCATIONS[i][j]
                row = row + 2 * divisor
            row = divisor
            col = col + 2 * divisor

    def update_images(self):
        ## Transform images ##
        # Logo image
        width = int(self.SCREEN_WIDTH * .6)
        height = int(width / 7)
        self.logo_image = pygame.transform.scale(self.logo_image, (width, height))

        # House image
        self.house_image = pygame.transform.scale(self.house_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Start Button
        width = int(self.SCREEN_WIDTH / 4)
        height = int(width / 4)
        self.start_button.update_size((width, height))
        # self.start_button.rect.w = width
        # self.start_button.rect.h = height
        # self.start_image = pygame.transform.scale(self.start_image, (width, height))

        # Map image
        # width = int(self.SCREEN_WIDTH * 1 / 2)
        height = int(self.SCREEN_HEIGHT * 9 / 10)
        width = height
        self.map_image = pygame.transform.scale(self.map_image, (width, height))
        self.ROOM_DIMENSIONS = int(width / 5)

        # Sprites
        for player in self.player_list:
            player.transform_sprites(self.SCREEN_WIDTH)

        ## UPdate image locations ##
        # Logo location parameters
        self.LOGO_SIZE = self.logo_image.get_size()
        self.LOGO_X = (self.SCREEN_WIDTH - self.LOGO_SIZE[0]) / 2
        self.LOGO_Y = (self.SCREEN_HEIGHT - self.LOGO_SIZE[1]) / 2

        # Start location parameters
        self.START_SIZE = self.start_image.get_size()
        self.START_X = (self.SCREEN_WIDTH - self.start_button.rect.w ) / 2
        self.START_Y = (self.SCREEN_HEIGHT - self.start_button.rect.h - 100)

        # Map location parameters
        self.MAP_SIZE = self.map_image.get_size()
        self.SCREEN_DIVIDER_START = self.ROOM_DIMENSIONS/2 + self.MAP_SIZE[0] + self.ROOM_DIMENSIONS/2
        self.OPTIONS_WIDTH = self.SCREEN_WIDTH - self.SCREEN_DIVIDER_START
        map_rect = self.map_image.get_rect(
            center=(self.SCREEN_DIVIDER_START / 2, self.SCREEN_HEIGHT / 2))
        self.MAP_X = map_rect.x
        self.MAP_Y = map_rect.y

        ## Options Menu ##
        self.update_options_menu()



    def update_options_menu(self):
        # Title screen
        title_ratio = self.options.title_surface.get_rect().h / self.options.title_surface.get_rect().w
        width = int(self.OPTIONS_WIDTH)
        title_height = int(width * title_ratio)
        self.options.title_surface = pygame.transform.scale(self.options.title_surface, (width, title_height))

        # Options player info
        width = int(self.OPTIONS_WIDTH / 3)
        height = int(width * self.options.PLAYER_INFO_SURFACE_RATIO)
        self.options.update_clue_tracker()
        self.options.update_scaled_values(width, height)
        self.options.player_info_surface = pygame.transform.scale(self.options.player_info_surface, (width, height))

        # Options status info
        width = int(self.OPTIONS_WIDTH)
        height = int(width * self.options.STATUS_INFO_SURFACE_RATIO)
        self.options.status_info_surface = pygame.transform.scale(self.options.status_info_surface, (width, height))

        # Options clue tracker
        height = int((self.SCREEN_HEIGHT - title_height) * 3 / 4)
        width = int(height * self.options.CLUETRACTER_SURFACE_RATIO)
        self.options.update_tracker_scaled_values(width, height)
        self.options.clue_tracker_surface = pygame.transform.scale(self.options.clue_tracker_surface, (width, height))

        # Option menu updates
        # self.options.init_accusation_menu(self.screen)
        self.options.init_illegal_move_menu(self.screen, 0)

    def message_loop(self):
        global message_received
        if message_received:
            # General messages
            if message["message_type"] == "player_count":
                self.player_total_count = message["player_count"]
                self.player_ready_count = message["player_ready_count"]

            if self.program_state == "MENU":
                if message["message_type"] == "game_start":
                    sio.emit('my message',
                             {
                                "message_type": "game_start",
                                "player_number": self.player_number
                             })

                if message["message_type"] == "game_info":
                    self.player_detail_list = message["player_list"]
                    self.card_list = message["card_list"]
                    self.menu_state = "FADE_OUT"

                if message["message_type"] == "name_already_chosen":
                    self.print_error_message(6)
                    self.options.name_selection_menu.enable()

                if message["message_type"] == "update_player_number":
                    if self.player_number == message["player_number"]:
                        self.player_number = None
                    elif self.player_number > message["player_number"]:
                        self.player_number = self.player_number - 1

                if message["message_type"] == "player_name_updated":
                    self.character_select.active = True
                    self.menu_state = "CHOOSE_CHARACTER"

                if message["message_type"] == "player_character_updated":
                    self.character_select.active = False
                    sio.emit("my message",
                             {
                                 "message_type": "player_ready"
                             })
                    self.menu_state = "WAITING"

                if message["message_type"] == "player_number":
                    self.player_number = message["player_number"]
                    self.options.init_name_selection_menu(self.screen)
                    self.options.name_selection_menu.enable()
                    self.menu_state = "CHOOSE_NAME"

            elif self.program_state == "GAME":
                if message["message_type"] == "move_player":
                    self.current_player.bool_is_active = False
                    self.current_player = self.player_list[message["player_number"] - 1]
                    self.current_player.bool_is_active = True
                    move_direction = message["direction"]
                    new_room = message["new_room"]
                    self.current_player.move(move_direction, self.MAP_DICT[new_room]["LOCATION"], new_room, self.ROOM_DIMENSIONS)
                    self.game_state = "MOVE_PLAYER"

                elif message["message_type"] == "current_player":
                    player_number = message["player_number"]
                    self.current_player.bool_is_active = False
                    self.current_player = self.player_list[player_number - 1]
                    self.current_player.bool_is_active = True
                    if self.this_player == self.current_player:
                        self.options.update_status_info(status="Status: Your Move")
                    else:
                        self.options.update_status_info(status="Status: Waiting for Player " + str(player_number))
                    self.game_state = "WAITING"

                elif message["message_type"] == "init_suspect_loop" or message["message_type"] == "next_responder":
                    self.current_responder = message["current_responder"]
                    self.who_accusation = message["who_accusation"]
                    self.what_accusation = message["what_accusation"]
                    self.where_accusation = message["where_accusation"]
                    self.suspect_loop = "INIT"
                    self.game_state = "SUSPECT_LOOP"

                elif message["message_type"] == "suspect_loop_done":
                    sio.emit("my message",
                             {
                                 "message_type": "get_current_player"
                             })
                    self.game_state = "CHANGE_PLAYER"

                elif message["message_type"] == "responder_pass":
                    self.current_responder = message["current_responder"]
                    self.suspect_loop = "CHOOSE_RESPONDER"

                elif message["message_type"] == "card_given":
                    if message["inquisition_player"] == self.player_number:
                        self.print_general_message(0, [message["current_responder"], message["card_given"]])
                    else:
                        self.print_general_message(5, message["current_responder"])

                    sio.emit("my message",
                             {
                                 "message_type": "get_current_player"
                             })

                    self.game_state = "CHANGE_PLAYER"

                elif message["message_type"] == "out_of_turn":
                    self.print_error_message(5)

            message_received = False


    def main_loop(self):
        global message_received, message
        # Mutable variables
        running = True

        while running:
            # Boolean Variables
            bool_update_opacity = False
            bool_animate = False

            # event handler
            events = pygame.event.get()
            for event in events:
                # Timer events
                if event.type == pygame.USEREVENT:
                    bool_update_opacity = True
                    bool_animate = True
                # Resize the window in case of a resize event
                if event.type == pygame.VIDEORESIZE:
                    self.SCREEN_WIDTH = event.w
                    self.SCREEN_HEIGHT = event.h
                    self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)

                    # Update the images
                    self.update_images()

                    # Update the map locations
                    self.update_map_locations()
                    for player in self.player_list:
                        player.set_location(self.MAP_DICT[player.sprite_room]["LOCATION"])

                    if self.program_state == "GAME":
                        # Draw the map
                        self.draw_map()

                # Mouse click events
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    response = self.options.check_button_clicked(pos, (self.SCREEN_DIVIDER_START + 10,
                                                                       self.options.title_surface.get_size()[1]))
                    # Check if the start button is active
                    if self.start_button.active:
                        # Check if the start button is clicked
                        if self.start_button.check_clicked(0, 0):
                            self.start_button_clicked = True

                    self.update_options_menu()
                    if response == "Move":
                        self.options.init_move_menu(self.screen,
                                                    self.MAP_DICT[self.this_player.sprite_room]["DIRECTIONS"])
                        self.options.move_menu.enable()
                    elif response == "Accuse / Suspect":
                        self.options.accusation_menu.enable()
                    elif response == "Pass":
                        sio.emit("my message",
                                 {
                                     "message_type": "player_pass",
                                     "player_number": self.player_number
                                 })
                        self.game_state = "CHANGE_PLAYER"

                # Check if a key was pressed
                if event.type == pygame.KEYDOWN:
                    # Check if the return / enter key was pressed
                    if event.key == pygame.K_RETURN:
                        if self.start_button.active:
                            self.start_button_clicked = True

                # Quit game in the case of a quit event
                if event.type == pygame.QUIT:
                    # Exit the main loop
                    running = False

            # Loop through received messages
            self.message_loop()

            # Go to appropriate game loop
            if self.program_state == "MENU":
                self.menu_loop(bool_animate, events)
            elif self.program_state == "GAME":
                self.game_loop(bool_animate)

            self.options.accusation_menu.mainloop(events)
            self.options.move_menu.mainloop(events)
            self.options.suspect_menu.mainloop(events)
            self.options.name_selection_menu.mainloop(events)

            pygame.display.update()

    def update_opacity(self, bool_update_opacity):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if self.START_X < mouse[0] < self.START_X + self.START_SIZE[0] and self.START_Y < mouse[1] < self.START_Y + self.START_SIZE[1]:
            self.start_opacity = 255

            # Check if the button is clicked
            if click[0] == 1:
                self.screen_opacity = 0
                sio.emit("my message",
                         {
                             "message_type": "request_number"
                         })

        elif bool_update_opacity:
            if self.opacity_direction == "UP":
                self.start_opacity = self.start_opacity + 5
                if self.start_opacity > 200:
                    self.opacity_direction = "DOWN"
            else:
                self.start_opacity = self.start_opacity - 5
                if self.start_opacity < 100:
                    self.opacity_direction = "UP"

    def fade_screen(self, opacity):
        fade = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        fade.fill(self.BLACK)
        fade.set_alpha(opacity)
        self.screen.blit(fade, (0, 0))
        #pygame.display.update()


    def menu_loop(self, bool_animate, events):

        # Initialize values
        if self.menu_state == "INIT":
            self.options.disable_buttons()
            # Start to establish the connection
            sio.connect('http://localhost:5000')

            self.screen_opacity = 255
            self.menu_state = "FADE_IN"

        # Fade into the opening
        if self.menu_state == "FADE_IN":
            self.screen_opacity = self.screen_opacity - 10
            self.screen.blit(self.house_image, (0, 0))
            self.fade_screen(self.screen_opacity)
            if self.screen_opacity < 0:
                self.screen_opacity = 0
                self.menu_state = "START"

        # Wait for the start button to be pressed
        elif self.menu_state == "START":
            # Draw the background
            self.screen.blit(self.house_image, (0,0))
            # Draw the logo
            self.screen.blit(self.logo_image, [self.LOGO_X, 20])
            # Draw the start button
            self.start_button.draw_button(self.screen, (self.START_X, self.START_Y))
            # Check if the button has been clicked
            if self.start_button_clicked:
                self.start_button_clicked = False
                sio.emit("my message",
                         {
                             "message_type": "request_number"
                         })
                self.start_button.disable()

        # Player chooses the name that they want to use
        elif self.menu_state == "CHOOSE_NAME":
            # Draw the background
            self.screen.blit(self.house_image, (0, 0))
            # Draw the logo
            self.screen.blit(self.logo_image, [self.LOGO_X, 20])

            # Check to see if the name was chosen
            if self.options.name_selection_done:
                self.options.name_selection_done = False
                self.options.name_selection_menu.disable()
                self.options.enable_buttons()
                sio.emit('my message',
                         {
                             "message_type": "update_player_name",
                             "player_number": self.player_number,
                             "player_name": self.options.name_selected
                         })

            # Check if the name selection was canceled
            elif self.options.name_selection_canceled:
                self.options.name_selection_canceled = False
                self.options.name_selection_menu.disable()
                self.options.enable_buttons()
                self.start_button.enable()
                sio.emit("my message",
                         {
                             "message_type": "return_number",
                             "player_number": self.player_number
                         })
                self.menu_state = "START"

        # Player chooses the character they want to use
        elif self.menu_state == "CHOOSE_CHARACTER":
            # Draw the background
            self.screen.blit(self.house_image, (0, 0))
            # Draw the logo
            self.screen.blit(self.logo_image, [self.LOGO_X, 20])
            # Draw the character select menu
            self.character_select.draw(self.screen, bool_animate, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            # Run through the event loop for the character select
            self.character_select.mainloop(events, sio)
            # Check if a character was selected
            if self.character_select.select_clicked:
                self.character_select.select_clicked = False
                file_loc = self.character_select.player_file_locations[self.character_select.player_iter]
                name = file_loc.split("\\")[-1].replace("_", " ").title()
                print(name)
                sio.emit("my message",
                         {
                             "message_type": "update_player_character",
                             "player_number": self.player_number,
                             "character_file": file_loc,
                             "character_name": name
                         })

            # Check if the back button was selected
            if self.character_select.back_clicked:
                self.character_select.back_clicked = False
                sio.emit("my message",
                         {
                             "message_type": "remove_player_name",
                             "player_number": self.player_number,
                         })
                self.options.name_selection_menu.enable()
                self.character_select.disable()
                self.menu_state = "CHOOSE_NAME"


        # Wait for the start button to be pressed
        elif self.menu_state == "WAITING":
            # Draw the background
            self.screen.blit(self.house_image, (0,0))
            # Draw the logo
            self.screen.blit(self.logo_image, [self.LOGO_X, 20])
            # Print the number of players waiting
            font = pygame.font.Font(None, 100)
            temp_string = "Waiting for " + str(self.player_total_count - self.player_ready_count) + " player(s) out of " + str(self.player_total_count)
            text = font.render(temp_string, True, self.WHITE)
            text_rect = text.get_rect(center=(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2))
            self.screen.blit(text, text_rect)



        # Fade out to start the game
        elif self.menu_state == "FADE_OUT":
            global connected
            # Start to fade out
            self.screen_opacity = self.screen_opacity + 10
            self.screen.blit(self.house_image, (0, 0))
            self.fade_screen(self.screen_opacity)
            if self.screen_opacity >= 255:
                self.menu_state = "INIT"
                self.options.enable_buttons()
                self.program_state = "GAME"



    def game_loop(self, bool_animate):
        if self.game_state == "INIT":
            # Load the players
            for player_detail in self.player_detail_list:
                self.player_list.append(Player(player_detail[0],
                                               player_detail[1],
                                               player_detail[2],
                                               player_detail[3],
                                               player_detail[4]))

            # Update the images
            self.update_images()

            # Update player locations
            for player in self.player_list:
                player.set_location(self.MAP_DICT[player.sprite_room]["LOCATION"])

            # Initialize the player cards
            self.this_player = self.player_list[self.player_number - 1]
            for key, values in self.card_list.items():
                self.this_player.update_cards(key.upper(), values)

            # Initialize players options menu
            self.current_player = self.player_list[0]
            self.current_player.bool_is_active = True

            self.options.update_clue_tracker()
            self.options.update_player_info(
                self.this_player.player_number,
                self.this_player.player_name,
                self.this_player.character,
                self.this_player.who_cards,
                self.this_player.what_cards,
                self.this_player.where_cards
            )
            self.update_options_menu()

            self.screen_opacity = 255
            self.game_state = "FADE_IN"
        elif self.game_state == "FADE_IN":
            self.screen_opacity = self.screen_opacity - 10
            self.draw_map()
            self.fade_screen(self.screen_opacity)
            if self.screen_opacity < 0:
                self.options.clue_tracker.update_checkboxes(self.current_player.clue_grid)
                self.game_state = "WAITING"
        elif self.game_state == "WAITING":
            self.update_options_menu()
            # Draw the map
            self.draw_map()

            # Draw the players
            for player in self.player_list:
                if not player == self.current_player:
                    player.animate(bool_animate, self.screen)
            self.current_player.animate(bool_animate, self.screen)

            # Check for a movement action
            move_direction = None
            if self.options.move_chosen:
                if self.check_collision():
                    self.print_error_message(0)
                else:
                    self.options.move_menu.disable()
                    self.options.enable_buttons()
                    move_direction = self.options.move_direction
                    self.options.move_chosen = False
            # Check for an accusation action
            if self.options.accuse_chosen:
                self.options.accuse_chosen = False
                self.options.accusation_menu.disable()
                self.options.enable_buttons()
                if self.options.bool_accuse:
                    sio.emit('my message',
                             {
                                 "message_type": "accuse",
                                 "current_player": self.player_number,
                                 "who_accusation": self.options.who_accusation,
                                 "what_accusation": self.options.what_accusation,
                                 "where_accusation": self.options.where_accusation
                             })
                    # if self.options.who_accusation == self.actual_who and self.options.what_accusation == self.actual_what and self.options.where_accusation == self.actual_where:
                    #     self.print_general_message(1)
                    #     self.game_state = "INIT"
                    #     self.menu_state = "INIT"
                    #     self.program_state = "MENU"
                    # else:
                    #     self.print_general_message(2)
                    #     self.remove_player = True
                    #     self.game_state = "CHANGE_PLAYER"

                else:
                    self.options.bool_accuse = False
                    room_name = self.current_player.sprite_room.replace("_"," ").lower()
                    if self.has_number(self.current_player.sprite_room):
                        self.print_error_message(2)
                    elif room_name != self.options.where_accusation.lower():
                        self.print_error_message(1)
                    else:
                        sio.emit('my message',
                                 {
                                     "message_type": "start_suspect_loop",
                                     "current_player": self.player_number,
                                     "who_accusation": self.options.who_accusation,
                                     "what_accusation": self.options.what_accusation,
                                     "where_accusation": self.options.where_accusation
                                 })
            if move_direction:
                direction_index = self.MAP_DICT[self.this_player.sprite_room]["DIRECTIONS"].index(move_direction)
                new_room = self.MAP_DICT[self.this_player.sprite_room]["ROOMS"][direction_index]

                sio.emit("my message",
                         {
                             "message_type": "move_player",
                             "player_number": self.player_number,
                             "direction": move_direction,
                             "new_room": new_room
                         })
                # self.current_player.move(move_direction, self.MAP_DICT[new_room]["LOCATION"], new_room, self.ROOM_DIMENSIONS)
                # self.game_state = "MOVE_PLAYER"
        elif self.game_state == "MOVE_PLAYER":
            self.draw_map()
            for player in self.player_list:
                player.animate(bool_animate, self.screen)
            if self.current_player.sprite_state == "WAIT":
                self.current_player.bool_is_active = False
                sio.emit("my message",
                         {
                             "message_type": "get_current_player"
                         })
                self.game_state = "CHANGE_PLAYER"
        elif self.game_state == "CHANGE_PLAYER":
            # Draw the map
            self.draw_map()

            # Draw the players
            for player in self.player_list:
                if not player == self.current_player:
                    player.animate(bool_animate, self.screen)
            self.current_player.animate(bool_animate, self.screen)
        elif self.game_state == "SUSPECT_LOOP":
            if self.suspect_loop == "INIT":
                self.question_order = []
                for player in self.player_list:
                    if player.player_name == self.who_accusation:
                        player.set_location(self.MAP_DICT[self.where_accusation.upper().replace(" ", "_")]["LOCATION"])
                        player.sprite_room = self.where_accusation.upper().replace(" ", "_")
                        break

                # Drwaw the map
                self.draw_map()

                # Draw the players
                for player in self.player_list:
                    if not player == self.current_player:
                        player.animate(bool_animate, self.screen)
                self.suspect_loop = "CHOOSE_RESPONDER"
            elif self.suspect_loop == "CHOOSE_RESPONDER":
                responder = self.player_list[self.current_responder - 1]
                cards = responder.who_cards + responder.what_cards + responder.where_cards
                card_list = []
                for card in cards:
                    card_list.append((card, card))
                if self.current_responder == self.player_number:
                    self.options.init_suspect_menu(self.screen,
                                                   self.current_player.player_name,
                                                   responder.player_name,
                                                   card_list)
                    self.options.suspect_menu.enable()
                else:
                    self.print_general_message(6,
                                               [self.current_player.player_number,
                                                self.who_accusation,
                                                self.where_accusation,
                                                self.what_accusation
                                                ],
                                               bool_wait=False)

                self.suspect_loop = "WAIT_FOR_RESPONSE"
            elif self.suspect_loop == "WAIT_FOR_RESPONSE":
                if self.current_responder == self.player_number:
                    if self.options.passed:
                        self.options.passed = False
                        #responder = self.player_list[self.question_order[0]]
                        responder = self.this_player
                        if (self.who_accusation in responder.who_cards or
                                self.what_accusation in responder.what_cards or
                                self.where_accusation in responder.where_cards):
                            self.print_error_message(4)
                        else:
                            self.options.suspect_menu.disable()
                            self.options.enable_buttons()
                            sio.emit("my message",
                                     {
                                         "message_type": "responder_pass"
                                     })
                    elif self.options.card_given:
                        self.options.card_given = False
                        chosen_card = self.options.card_to_give
                        if chosen_card == self.where_accusation or chosen_card == self.what_accusation or chosen_card == self.who_accusation:
                            self.options.suspect_menu.disable()
                            self.options.enable_buttons()
                            sio.emit("my message",
                                     {
                                         "message_type": "responder_give",
                                         "responder_number": self.player_number,
                                         "card_given": chosen_card
                                     })
                        else:
                            self.print_error_message(3)
                else:
                    self.print_general_message(6,
                                               [self.current_player.player_number,
                                                self.who_accusation,
                                                self.where_accusation,
                                                self.what_accusation
                                                ],
                                               bool_wait=False)

    def print_error_message(self, message_number):
        self.options.init_illegal_move_menu(self.screen, message_number)
        self.options.illegal_move_menu.draw()
        self.options.move_chosen = False
        pygame.display.update()
        pygame.time.wait(3000)

    def print_general_message(self, message_number, param=None, bool_wait=True):
        self.options.init_general_message_menu(self.screen, message_number, param)
        self.options.general_message_menu.draw()
        self.update_options_menu()
        pygame.display.update()
        if bool_wait:
            pygame.time.wait(3000)

    def has_number(self, string):
        return any(i.isdigit() for i in string)

    def check_collision(self):
        move_direction = self.options.move_direction
        current_room = self.this_player.sprite_room
        next_room_index = self.MAP_DICT[current_room]["DIRECTIONS"].index(move_direction)
        next_room = self.MAP_DICT[current_room]["ROOMS"][next_room_index]
        if self.has_number(next_room):
            for player in self.player_list:
                if player.sprite_room == next_room:
                    return True
        return False

    def draw_map(self):
        # Clear the screen
        self.screen.fill(self.BLACK)

        # Draw the map
        self.screen.blit(self.map_image, (self.MAP_X, self.MAP_Y))

        # Draw the options screen
        text_rect = self.options.title_surface.get_rect(center=(self.SCREEN_DIVIDER_START + self.OPTIONS_WIDTH / 2, self.options.title_surface.get_size()[1] / 2))
        self.screen.blit(self.options.title_surface, text_rect)

        options_row = self.options.title_surface.get_size()[1]
        self.screen.blit(self.options.player_info_surface, (self.SCREEN_DIVIDER_START + 10, options_row))
        self.screen.blit(self.options.clue_tracker_surface,
                         (self.SCREEN_DIVIDER_START + 40 + self.options.player_info_surface.get_rect().w, options_row))
        self.screen.blit(self.options.status_info_surface,
                         (self.SCREEN_DIVIDER_START + 10,
                          options_row + self.options.clue_tracker_surface.get_height() + 10)
                         )

        # Print screen separator
        line_start = (self.SCREEN_DIVIDER_START, 0)
        line_end = (self.SCREEN_DIVIDER_START, self.SCREEN_HEIGHT)
        pygame.draw.line(self.screen, self.WHITE, line_start, line_end, 5)

if __name__ == '__main__':
    game = Clueless()
    game.main_loop()