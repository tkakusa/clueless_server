import pygame
import math

class Checkbox:
    def __init__(self, location):
        self.location = location
        self.checked = False

    def click(self):
        if self.checked:
            self.checked = False
        else:
            self.checked = True



class ClueTracker:
    def __init__(self):
        # # Initialize the pygame module
        # pygame.init()

        self.ROW_SIZE = 25
        self.COL_SIZE = 6
        self.BOX_SIZE = 30
        self.TEXT_SIZE = 40
        self.CLUETRACKER_WIDTH = self.BOX_SIZE * self.COL_SIZE
        self.CLUETRACKER_HEIGHT = self.BOX_SIZE * self.ROW_SIZE
        self.CLUETRACKER_LOCATION = [0,0]
        self.checkboxes = []
        self.clue_tracker_surface = None

        self.row_text = ["PLAYERS",
                         "WHO?",
                         "Scarlet",
                         "Plum",
                         "Mustard",
                         "Peacock",
                         "Green",
                         "White",
                         "WHAT?",
                         "Candlestick",
                         "Dagger",
                         "Pistol",
                         "Lead Pipe",
                         "Rope",
                         "Wrench",
                         "WHERE?",
                         "Study",
                         "Hall",
                         "Lounge",
                         "Library",
                         "Billiard Room",
                         "Dining Room",
                         "Conservatory",
                         "Ballroom",
                         "Kitchen"
                         ]

        # Text variables
        self.font = pygame.font.SysFont('goudy', self.TEXT_SIZE)

        # Initialize checkboxes
        self.init_checkboxes()

        self.draw()


        # # Set the title of the screen
        # pygame.display.set_caption("The Game of Clue-Less")
        #
        # # Create the actual screen
        # self.screen = pygame.display.set_mode((2560, 1440), pygame.RESIZABLE)
        #
        # running = True
        # while running:
        #     self.screen.fill((0, 0, 0))
        #     # event handler
        #     events = pygame.event.get()
        #     for event in events:
        #         # Quit game in the case of a quit event
        #         if event.type == pygame.QUIT:
        #             # Exit the main loop
        #             running = False
        #         # Mouse click events
        #         elif event.type == pygame.MOUSEBUTTONUP:
        #             pos = pygame.mouse.get_pos()
        #             self.clicked(pos)
        #             self.draw()
        #
        #     self.screen.blit(self.clue_tracker_surface, [0,0])
        #     pygame.display.update()

    def init_checkboxes(self):
        for row in range(0, 25):
            row_array = []
            for col in range(0, 7):
                row_array.append(Checkbox([row, col]))
            self.checkboxes.append(row_array)
    def update_checkboxes(self, player_clue_grid):
        self.checkboxes = player_clue_grid

    def clicked(self, pos, offset, scaled_height, scaled_width):
        scaled_box_height = scaled_height / self.ROW_SIZE
        scaled_box_width = scaled_box_height #(scaled_width - 200) / self.COL_SIZE
        x_pos = math.floor((pos[0] - offset[0]) / scaled_box_width)
        y_pos = math.floor((pos[1] - offset[1]) / scaled_box_height)

        if x_pos < self.COL_SIZE and x_pos >= 0 and y_pos < self.ROW_SIZE and y_pos >= 0:
            self.checkboxes[y_pos][x_pos].click()


    def draw(self):
        self.clue_tracker_surface = pygame.Surface((2560, 1440))
        player_count = 0
        for row in range(0, self.ROW_SIZE):
            row_adjusted = row * self.BOX_SIZE
            for col in range(0, self.COL_SIZE):
                col_adjusted = col * self.BOX_SIZE
                if row in [1, 8, 15]:
                    rect = pygame.Rect(col_adjusted, row_adjusted, self.BOX_SIZE + 2, self.BOX_SIZE)
                    pygame.draw.rect(self.clue_tracker_surface, (255, 255, 255), rect)
                else:
                    rect = pygame.Rect(col_adjusted, row_adjusted, self.BOX_SIZE, self.BOX_SIZE)
                    pygame.draw.rect(self.clue_tracker_surface, (255, 255, 255), rect, 2)
                if row == 0:
                    player_count = player_count + 1
                    number_surface = self.font.render(str(player_count), False, (255, 255, 255))
                    number_rect = number_surface.get_rect(center=(col_adjusted + self.BOX_SIZE / 2,
                                                                  row_adjusted + self.BOX_SIZE / 2))
                    self.clue_tracker_surface.blit(number_surface, number_rect)

                if self.checkboxes[row][col].checked:
                    pygame.draw.line(self.clue_tracker_surface,
                                     (255,255,255),
                                     [col_adjusted, row_adjusted],
                                     [col_adjusted + self.BOX_SIZE, row_adjusted +self.BOX_SIZE],
                                     3)
                    pygame.draw.line(self.clue_tracker_surface,
                                     (255, 255, 255),
                                     [col_adjusted + self.BOX_SIZE, row_adjusted],
                                     [col_adjusted, row_adjusted + self.BOX_SIZE],
                                     3)
            text_surface = self.font.render(self.row_text[row], False, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.COL_SIZE * self.BOX_SIZE + 100, row_adjusted + 2 + 10))
            if row in [0, 1, 8, 15]:
                self.clue_tracker_surface.blit(text_surface, (self.COL_SIZE * self.BOX_SIZE, row_adjusted + 2))
            else:
                self.clue_tracker_surface.blit(text_surface, text_rect)
