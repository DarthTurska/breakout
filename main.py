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


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load(os.path.join("data", "ball.png"))
        self.rect = self.image.get_rect(center=pos)
        self.old_rect=self.rect.copy()
        self.vel = pygame.math.Vector2(0, 0)       
        self.pos = pygame.math.Vector2(self.rect.topleft)

    def update(self, dt):
        self.pos+=self.vel*dt
        self.rect.topleft=(round(self.pos.x), round(self.pos.y))

class Paddle(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups):
        super().__init__(groups)
        self.image = pygame.Surface(size)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=pos)
    def setX(self, x):
        self.rect.centerx = x


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
                Brick((x, y), (WIN_WIDTH / len(row), 25), hsv2rgb(color / len(row), 1, 1), (bricks, all_sprites))
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
manager = pygame_gui.UIManager((WIN_WIDTH, WIN_HEIGHT), os.path.join("data", "theme.json"))

buttons = [
    make_button(100, 50, WIN_WIDTH / 2, WIN_HEIGHT / 2 - 100, "Level 1"),
    make_button(100, 50, WIN_WIDTH / 2, WIN_HEIGHT / 2, "Level 2"),
    make_button(100, 50, WIN_WIDTH / 2, WIN_HEIGHT / 2 + 100, "Level 3"),
]

is_running = True
game_state = 0

clock = pygame.time.Clock()

while is_running:
    mpos = pygame.mouse.get_pos()
    time_delta = clock.tick(240) / 1000.0
    if pygame.event.get(eventtype=pygame.QUIT):
        is_running = False
    # level select
    if game_state == 0:
        for event in pygame.event.get():
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                for id, button in enumerate(buttons):
                    if event.ui_element == button:
                        bricks = pygame.sprite.Group()
                        all_sprites = pygame.sprite.Group()
                        paddle = Paddle((WIN_WIDTH / 2, WIN_HEIGHT-20), (70, 8), all_sprites)
                        ball = Ball((paddle.rect.centerx, paddle.rect.top-10), all_sprites)
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
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                ball.vel= pygame.math.Vector2(mpos[0] - ball.pos.x, mpos[1] - ball.pos.y)                 
                ball.vel.scale_to_length(500)
                game_state = 2
        
        draw()
        pygame.draw.aaline(win, (255, 255, 255), mpos, ball.rect.center)

    # main logic

    elif game_state == 2:

        for brick in bricks:
            if brick.rect.colliderect(ball):
                dx = abs(brick.rect.centerx - ball.rect.centerx)
                dy = abs(brick.rect.centery - ball.rect.centery)
                if dy > dx:
                    ball.vel.y = -ball.vel.y
                else:
                    ball.vel.x = -ball.vel.x
                brick.kill()
                break


        if (
            paddle.rect.left <= ball.rect.right
            and paddle.rect.right >= ball.rect.left
            and ball.rect.bottom >= paddle.rect.top
        ):
            ball.vel.x += paddle_vel*(1/time_delta)/20
            ball.vel.y = -ball.vel.y

        if ball.rect.right > WIN_WIDTH or ball.rect.left < 0:
            ball.vel.x = -ball.vel.x
        if ball.rect.top <= 0:
            ball.vel.y = -ball.vel.y
        if ball.rect.centery >= WIN_HEIGHT:
            if hp <= 0:
                game_state = 0
            else:
                game_state = 1
                ball.pos.y-=30
                hp -= 1

        paddle.setX(mpos[0])
        paddle_vel = mpos[0] - lastx
        ball.update(time_delta)
        lastx = paddle.rect.centerx
        draw()
    pygame.display.update()
