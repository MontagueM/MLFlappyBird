import pygame
import numpy as np

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_WIDTH = 750
SCREEN_HEIGHT = 500


class Player(pygame.sprite.Sprite):
    def __init__(self, fb_inst):
        super(Player, self).__init__()
        self.width = 25
        self.height = 25
        self.surf = pygame.Surface((self.width, self.height))
        self.surf.fill((0, 0, 0))
        self.rect = self.surf.get_rect()
        self.fb_inst = fb_inst
        #  How many pixels to fall per frame (should take ~1 second to fall from center to bottom)
        self.acceleration = int(60*fb_inst.velocity_const/(SCREEN_HEIGHT * 0.5)*0.1)

    # Move the sprite based on user keypresses
    def update(self, pressed_keys, b_network=False):
        if b_network:
            if pressed_keys['Up']:
                self.rect.move_ip(0, -4)
            if pressed_keys['Down']:
                self.rect.move_ip(0, 4)
        else:
            buttons = [K_UP, K_DOWN]
            if pressed_keys[buttons[0]]:
                self.rect.move_ip(0, -4)
            if pressed_keys[buttons[1]]:
                self.rect.move_ip(0, 4)

    def end_conditions(self):
        if self.rect.centery <= 0:
            print('End from top hit')
            return True
        elif self.rect.centery >= SCREEN_HEIGHT:
            print('End from bottom hit')
            return True
        # TODO case for pipe hit
        return False


class Pipe(pygame.sprite.Sprite):
    def __init__(self):
        super(Pipe, self).__init__()


class FlappyBird:
    def __init__(self):
        pygame.init()
        CENTER = np.array([int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2)])
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        self.clock = pygame.time.Clock()
        self.frame_count = 0
        self.velocity_const = 100

        self.player = Player(self)

        # self.walls = {'left': Wall(vertical=True), 'right': Wall(vertical=True),
        #          'top': Wall(vertical=False), 'bottom': Wall(vertical=False)}
        # self.walls['left'].rect.left = 0
        # self.walls['right'].rect.right = SCREEN_WIDTH
        # self.walls['top'].rect.top = 0
        # self.walls['bottom'].rect.bottom = SCREEN_HEIGHT

        self.player.rect.move_ip(CENTER - np.array([int(self.player.width/2), int(self.player.height/2)]))

        self.is_completed = False
        self.completion_state = []

    def frame(self):
        """
        Drawing
        """
        self.screen.fill((255, 255, 255))

        # Draw borders
        # for wall in self.walls.values():
        #     self.screen.blit(wall.surf, wall.rect)

        # Draw the player on the screen
        self.screen.blit(self.player.surf, self.player.rect)

        """
        Updating locations
        """
        if self.frame_count % 10 == 0:
            self.player.rect.move_ip(0, self.player.acceleration)

    def press_buttons(self, buttons, b_network=False):
        if b_network:
            self.player.update(buttons, b_network=b_network)
        else:
            self.player.update(buttons, b_network=b_network)

    def capture_screen(self):
        # Only capture every 5 frames or more as slow method
        pygame.image.save(self.screen, 'screen.png')

    def update_frame(self):
        # Updates the display with a new frame
        pygame.display.flip()
        self.frame_count += 1
        self.clock.tick(60*self.velocity_const)

    def run_normal(self):
        running = True
        while running:
            # Did the user click the window close button?
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if self.is_completed:
                running = False
            self.frame()
            pressed_keys = pygame.key.get_pressed()
            self.press_buttons(pressed_keys)
            self.update_frame()
            b_quit = self.player.end_conditions()
            if b_quit:
                running = False
        pygame.quit()


if __name__ == "__main__":
    fb = FlappyBird()
    fb.run_normal()
