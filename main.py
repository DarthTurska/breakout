
import pygame
import pygame_gui
import colorsys
from level_loading import load_levels



class Brick(pygame.sprite.Sprite):
    def __init__(self, pos, w, h, color):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("ball.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.center = (self.x, self.y)


class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    def move_to(self, x, y):
        self.rect.center = (x, y)


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def draw():
    win.fill((0, 0, 0))

    all_sprites.draw(win)

    pygame.draw.rect(win, (255, 255, 255), paddle)
    for i in range(hp + 1):
        win.blit(heart, (WIN_WIDTH - i * 21 - 25, WIN_HEIGHT - 25))

def make_button(w, h, x, y, text):
    rect = pygame.Rect((0, 0), (w, h))
    rect.center = (x, y - rect.width)
    return pygame_gui.elements.UIButton(relative_rect=rect, text=text, manager=manager)

def createLevel(level):
    x = y = 0
    color = 0
    for row in level:
        for col in row:
            if col == "1":
                brick = Brick(
                    (x, y), WIN_WIDTH / len(row), 25, hsv2rgb(color / len(row), 1, 1)
                )
                bricks.add(brick)
                all_sprites.add(brick)
            x += WIN_WIDTH / len(row)
            color += 1
        y += 25
        x = 0



pygame.init()

WIN_WIDTH = 500
WIN_HEIGHT = 700

win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

pygame.display.set_caption("BREAKOUT")



heart = pygame.transform.scale2x(pygame.image.load("heart.png"))

levels = load_levels()
manager = pygame_gui.UIManager((WIN_WIDTH, WIN_HEIGHT), "theme.json")

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
                        paddle = Paddle(WIN_WIDTH / 2, WIN_HEIGHT-20, 70, 8)
                        ball = Ball(paddle.rect.centerx, paddle.rect.top-10)
                        hp = 2
                        bricks = pygame.sprite.Group()
                        all_sprites = pygame.sprite.Group(ball)
                        createLevel(levels[id])
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
                ballvel = pygame.math.Vector2(mpos[0] - ball.x, mpos[1] - ball.y)
                ballvel.scale_to_length(700)
                game_state = 2
        mpos = pygame.mouse.get_pos()
        draw()
        pygame.draw.aaline(win, (255, 255, 255), mpos, ball.rect.center)
        pygame.draw.rect(win, (255, 255, 255), (mpos[0] - 2, mpos[1] - 2, 4, 4))

    # main logic

    elif game_state == 2:
        mpos = pygame.mouse.get_pos()
        for brick in bricks:
            if brick.rect.colliderect(ball):
                dx = abs(brick.rect.centerx - ball.rect.centerx)
                dy = abs(brick.rect.centery - ball.rect.centery)
                if dy > dx:
                    ballvel.y = -ballvel.y
                else:
                    ballvel.x = -ballvel.x
                brick.kill()
                break


        if (
            paddle.rect.left <= ball.rect.right
            and paddle.rect.right >= ball.rect.left
            and ball.rect.bottom >= paddle.rect.top
        ):
            ballvel.x += paddle_vel*(1/time_delta)/10
            ballvel.y = -ballvel.y

        if ball.rect.right > WIN_WIDTH or ball.rect.left < 0:
            ballvel.x = -ballvel.x
        if ball.rect.top <= 0:
            ballvel.y = -ballvel.y
        if ball.rect.centery >= WIN_HEIGHT:
            if hp <= 0:
                game_state = 0
            else:
                game_state = 1
                ball.move(0, -20)
                hp -= 1

        paddle.move_to(mpos[0])
        paddle_vel = mpos[0] - lastx
        ball.move(ballvel.x * time_delta, ballvel.y * time_delta)
        lastx = paddle.rect.centerx
        draw()
    pygame.display.flip()
