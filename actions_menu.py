import pygame

class Button:
    def __init__(self, color, text, ):
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.text = self.font.render(text, False, (0, 0, 0))
        self.rect = pygame.Rect((0, 0), self.text.get_rect())
        self.color = color

class Actions:
    def __init__(self):
        red_button = Button((255, 0, 0))

        # Initialize the pygame module
        pygame.init()

        # Set the title of the screen
        pygame.display.set_caption("Actions menu test")

        # Create the actual screen
        self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)

        while True:
            # event handler
            for event in pygame.event.get():
                # Quit game in the case of a quit event
                if event.type == pygame.QUIT:
                    # Exit the main loop
                    running = False

            self.screen.fill((0,0,0))
            pygame.draw.rect(self.screen, red_button.color, red_button.rect)
            pygame.display.update()

Actions()