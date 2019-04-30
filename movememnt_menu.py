import pygame

class Button:
    def __init__(self, color, text):
        self.color = color
        self.font = pygame.font.SysFont('stencil', 60)
        self.text = self.font.render(text, False, (255, 255, 255))
        self.rect = self.text.get_rect()

class Actions:
    def __init__(self):
        # Initialize the pygame module
        pygame.init()

        # Set the title of the screen
        pygame.display.set_caption("Movement menu test")

        # Create the actual screen
        self.screen = pygame.display.set_mode((2560, 1440), pygame.RESIZABLE)

        # Create labels
        self.label_font = pygame.font.SysFont('goudy', 80)
        self.move_label = self.label_font.render("Move:")

        # Create the buttons
        self.movement_button = Button((255, 0, 0), "Move")

        running = True
        while running:
            for event in pygame.event.get():
                # Quit game in the case of a quit event
                if event.type == pygame.QUIT:
                    # Exit the main loop
                    running = False

            self.screen.fill((0,0,0))
            self.draw_button(self.movement_button, (0,0))
            pygame.display.update()

    def draw_button(self, button, location):
        button.rect.x, button.rect.y = location
        pygame.draw.rect(self.screen, button.color, button.rect)
        self.screen.blit(self.movement_button.text, location)

Actions()