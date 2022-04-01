import pygame
import pygame_gui
import colorsys
from level_loading import load_levels
import os


class Brick(pygame.sprite.Sprite):
    def __init__(self, pos, size, color, groups):
        super().__init__(groups)
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)
        self.old_rect = self.rect.copy()
        self.destructible = True


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load(os.path.join("data", "ball.png"))
        self.rect = self.image.get_rect(center=pos)
        self.old_rect = self.rect.copy()
        self.vel = pygame.math.Vector2(0, 0)
        self.pos = pygame.math.Vector2(self.rect.topleft)

    def collision(self, direction):
        collision_sprites = pygame.sprite.spritecollide(self, obstacle_sprites, False)
        if collision_sprites:
            if direction == "horizontal":
                for sprite in collision_sprites:
                    if (
                        self.rect.right >= sprite.rect.left
                        and self.old_rect.right <= sprite.old_rect.left
                    ):
                        self.rect.right = sprite.rect.left - 1
                        self.pos.x = self.rect.x
                        self.vel.x *= -1

                    if (
                        self.rect.left <= sprite.rect.right
                        and self.old_rect.left >= sprite.old_rect.right
                    ):
                        self.rect.left = sprite.rect.right + 1
                        self.vel.x *= -1
                    if sprite.destructible:
                        sprite.kill()

        if direction == "vertical":
            for sprite in collision_sprites:
                if (
                    self.rect.bottom >= sprite.rect.top
                    and self.old_rect.bottom <= sprite.old_rect.top
                ):
                    self.rect.bottom = sprite.rect.top
                    self.pos.y = self.rect.y
                    self.vel.y *= -1

                if (
                    self.rect.top <= sprite.rect.bottom
                    and self.old_rect.top >= sprite.old_rect.bottom
                ):
                    self.rect.top = sprite.rect.bottom
                    self.pos.y = self.rect.y
                    self.vel.y *= -1

                if sprite.destructible:
                    sprite.kill()
                    break

    def window_collision(self, direction):
        global hp, game_state
        if direction == "horizontal":
            if self.rect.left < 0:
                self.rect.left = 0
                self.pos.x = self.rect.x
                self.vel.x *= -1
            if self.rect.right > WIN_WIDTH:
                self.rect.right = WIN_WIDTH
                self.pos.x = self.rect.x
                self.vel.x *= -1

        if direction == "vertical":
            if self.rect.top < 0:
                self.rect.top = 0
                self.pos.y = self.rect.y
                self.vel.y *= -1
            if self.rect.bottom > WIN_HEIGHT:
                self.rect.bottom = WIN_HEIGHT
                if hp <= 0:
                    game_state = 0
                else:
                    game_state = 1
                    self.pos.y -= 20
                    hp -= 1

    def update(self, dt):
        self.old_rect = self.rect.copy()

        self.pos.x += self.vel.x * dt
        self.rect.x = round(self.pos.x)
        self.collision("horizontal")
        self.window_collision("horizontal")
        self.pos.y += self.vel.y * dt
        self.rect.y = round(self.pos.y)
        self.collision("vertical")
        self.window_collision("vertical")


class Paddle(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups):
        super().__init__(groups)
        self.image = pygame.Surface(size)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=pos)
        self.old_rect = self.rect.copy()
        self.destructible = False

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.rect.centerx = pygame.mouse.get_pos()[0]


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def draw():
    win.fill((0, 0, 0))
    all_sprites.draw(win)
    for i in range(hp):
        win.blit(heart, (WIN_WIDTH - i * 21 - 25, WIN_HEIGHT - 25))


def make_button(w, h, x, y, text):
    rect = pygame.Rect((0, 0), (w, h))
    rect.center = (x, y - rect.width)
    return pygame_gui.elements.UIButton(relative_rect=rect, text=text, manager=manager)


def create_level(level):
    x = y = 0
    color = 0
    for row in level:
        for char in row:
            if char == "1":
                Brick(
                    (x, y),
                    (WIN_WIDTH / len(row), 25),
                    hsv2rgb(color / len(row), 1, 1),
                    (obstacle_sprites, all_sprites),
                )
            x += WIN_WIDTH / len(row)
            color += 1
        y += 25
        x = 0


pygame.init()

WIN_WIDTH = 500
WIN_HEIGHT = 700

win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

pygame.display.set_caption("BREAKOUT")

heart = pygame.transform.scale2x(pygame.image.load(os.path.join("data", "heart.png")))

levels = load_levels()
manager = pygame_gui.UIManager(
    (WIN_WIDTH, WIN_HEIGHT), os.path.join("data", "theme.json")
)

buttons = [
    make_button(100, 50, WIN_WIDTH / 2, WIN_HEIGHT / 2 - 100, "Level 1"),
    make_button(100, 50, WIN_WIDTH / 2, WIN_HEIGHT / 2, "Level 2"),
    make_button(100, 50, WIN_WIDTH / 2, WIN_HEIGHT / 2 + 100, "Level 3"),
]

is_running = True
game_state = 0

clock = pygame.time.Clock()

while is_running:
    time_delta = clock.tick(240) / 1000.0
    if pygame.event.get(eventtype=pygame.QUIT):
        is_running = False
    # level select
    if game_state == 0:
        for event in pygame.event.get():
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                for id, button in enumerate(buttons):
                    if event.ui_element == button:
                        obstacle_sprites = pygame.sprite.Group()
                        all_sprites = pygame.sprite.Group()
                        paddle = Paddle(
                            (WIN_WIDTH / 2, WIN_HEIGHT - 20),
                            (70, 8),
                            (all_sprites, obstacle_sprites),
                        )
                        ball = Ball(
                            (paddle.rect.centerx, paddle.rect.top - 10), all_sprites
                        )
                        hp = 3
                        create_level(levels[id])
                        game_state = 1
                        lastx = paddle.rect.centerx

            manager.process_events(event)

        manager.update(time_delta)
        win.fill((0, 0, 0))
        manager.draw_ui(win)

    # Shooting the ball

    elif game_state == 1:
        mpos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                ball.vel = pygame.math.Vector2(
                    mpos[0] - ball.pos.x, mpos[1] - ball.pos.y
                )
                ball.vel.scale_to_length(500)
                game_state = 2
        draw()
        pygame.draw.aaline(win, (255, 255, 255), mpos, ball.rect.center)

    # main logic

    elif game_state == 2:
        all_sprites.update(time_delta)
        lastx = paddle.rect.centerx
        draw()
    pygame.display.update()
