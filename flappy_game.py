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

        # units per frame
        self.velocity = 0
        #  How many pixels to fall per frame (should take ~1 second to fall from center to bottom)
        # Actually make this acceleration, not a velocity
        self.fall_acceleration = int((SCREEN_HEIGHT * 0.5)/(60))*0.07
        self.can_move = True

    # Move the sprite based on user keypresses
    def update(self, pressed_keys, b_network=False):
        if b_network:
            if pressed_keys['Up']:
                if self.can_move:
                    # self.rect.move_ip(0, -4)
                    self.velocity -= 10
                    self.can_move = False
            else:
                self.can_move = True
        else:
            if pressed_keys[K_UP]:
                if self.can_move:
                    # self.rect.move_ip(0, -4)
                    self.velocity -= 10
                    self.can_move = False
            else:
                self.can_move = True

    def end_conditions(self):
        if self.rect.centery <= 0:
            print('End from top hit')
            return True
        elif self.rect.centery >= SCREEN_HEIGHT:
            print('End from bottom hit')
            return True
        elif pygame.sprite.spritecollideany(self, self.fb_inst.pipes):
            return True
        return False


class Pipe(pygame.sprite.Sprite):
    def __init__(self):
        super(Pipe, self).__init__()
        self.width = 25
        self.height = int(SCREEN_HEIGHT/2)
        self.surf = pygame.Surface((self.width, self.height))
        self.surf.fill((0, 0, 0))
        self.rect = self.surf.get_rect()


class FlappyBird:
    def __init__(self):
        pygame.init()
        CENTER = np.array([int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2)])
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        self.clock = pygame.time.Clock()
        self.frame_count = 0
        self.frame_speed = 100

        self.player = Player(self)

        # self.walls = {'left': Wall(vertical=True), 'right': Wall(vertical=True),
        #          'top': Wall(vertical=False), 'bottom': Wall(vertical=False)}
        # self.walls['left'].rect.left = 0
        # self.walls['right'].rect.right = SCREEN_WIDTH
        # self.walls['top'].rect.top = 0
        # self.walls['bottom'].rect.bottom = SCREEN_HEIGHT

        self.player.rect.move_ip(CENTER - np.array([int(self.player.width/2), int(self.player.height/2)]))

        self.pipe1 = Pipe()
        self.pipe2 = Pipe()
        self.pipes = pygame.sprite.Group()
        self.pipes.add(self.pipe1)
        self.pipes.add(self.pipe2)
        self.pipe1.rect.move_ip(CENTER + np.array([int(SCREEN_WIDTH/4), - CENTER[1]*1.3]))
        self.pipe2.rect.move_ip(CENTER + np.array([int(SCREEN_WIDTH/4), int(CENTER[1]/2)]))

        self.is_completed = False

    def frame(self):
        """
        Drawing
        """
        self.screen.fill((255, 255, 255))

        # Draw pipes
        # for wall in self.walls.values():
        #     self.screen.blit(wall.surf, wall.rect)
        self.screen.blit(self.pipe1.surf, self.pipe1.rect)
        self.screen.blit(self.pipe2.surf, self.pipe2.rect)



        # Draw the player on the screen
        self.screen.blit(self.player.surf, self.player.rect)

        """
        Updating locations
        """
        self.player.rect.move_ip(0, self.player.velocity)
        self.pipe1.rect.move_ip(-2, 0)
        self.pipe2.rect.move_ip(-2, 0)

        """
        Updating velocity
        """
        self.player.velocity += self.player.fall_acceleration

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
        self.clock.tick(60*self.frame_speed)

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
            self.is_completed = self.player.end_conditions()
            if self.is_completed:
                running = False
            self.update_frame()
        pygame.quit()


if __name__ == "__main__":
    fb = FlappyBird()
    fb.run_normal()
