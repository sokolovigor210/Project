import pygame
import time
from random import choice
import math

WIDTH = 1000
HEIGHT = 800
RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
BROWN = (100, 40, 0)
GAME_COLORS = [YELLOW, GREEN, MAGENTA, CYAN]
AIM_X = [-10, WIDTH + 40]


class Bullet:
    def __init__(self, screen, x, y):
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 8
        self.v = self.vy = 30
        self.color = choice(GAME_COLORS)
        self.outside = False

    def move(self, dt):
        self.y -= self.vy * dt

    def draw_bul(self):
        pygame.draw.rect(self.screen, self.color,
                         (self.x - self.r, self.y - self.r,
                          2 * self.r, 2 * self.r), 2 * self.r)

    def deleting(self, obj):
        if self.y + self.r < -2 * self.r:
            bullets.remove(obj)


class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.x = WIDTH / 2
        self.y = HEIGHT - 50
        self.v = 17
        self.wh_col = GREY
        self.bar_col = BROWN
        self.wh_R = 30
        self.wh_a = self.wh_R * (2 ** 0.5)
        self.wh_l = self.wh_R * 1.25
        self.m_col = RED
        self.m_height = 80
        self.m_width = 40
        self.m_low = 10
        self.state = False
        self.last = pygame.time.get_ticks()
        self.cooldown = 20
        self.health = 1
        self.left_wheel = 0
        self.right_wheel = 0
        self.muzzle = 0

    def vis_parts(self):
        self.left_wheel = pygame.Rect(self.x - self.wh_l -
                                      self.wh_R / (2 ** 0.5),
                                      self.y - self.wh_R / (2 ** 0.5),
                                      self.wh_a, self.wh_a)
        self.right_wheel = pygame.Rect(self.x + self.wh_l -
                                       self.wh_R / (2 ** 0.5),
                                       self.y - self.wh_R / (2 ** 0.5),
                                       self.wh_a, self.wh_a)
        pygame.draw.circle(self.screen, self.wh_col,
                           self.right_wheel.center, self.wh_R)
        pygame.draw.circle(self.screen, self.wh_col,
                           self.left_wheel.center, self.wh_R)
        pygame.draw.line(self.screen, self.bar_col,
                         (self.x - self.wh_l, self.y),
                         (self.x + self.wh_l, self.y), 8)

        if self.state is True:
            self.muzzle = pygame.Rect(self.x - self.m_width / 2,
                                      self.y + self.m_low - self.m_height,
                                      self.m_width, self.m_height)
            pygame.draw.rect(self.screen, self.m_col, self.muzzle)
        else:
            self.muzzle = pygame.Rect(self.x - self.m_width / 2,
                                      self.y - self.m_height,
                                      self.m_width, self.m_height)
            pygame.draw.rect(self.screen, self.m_col, self.muzzle)

    def motion(self):
        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT] and (self.x - self.wh_l - self.wh_R) > 0:
            self.x -= self.v
            self.state = True
        if key[pygame.K_RIGHT] and (self.x + self.wh_l + self.wh_R) < WIDTH:
            self.x += self.v
            self.state = True
        if True not in key:
            self.state = False

    def shooting(self):
        now = pygame.time.get_ticks()
        if now - self.last >= self.cooldown and self.state is True:
            self.last = now
            new_bul = Bullet(self.screen, self.x,
                             self.y + self.m_low - self.m_height + 10)
            bullets.append(new_bul)


class Aim:
    def __init__(self, screen):
        self.screen = screen
        self.x0 = choice(AIM_X)
        self.y0 = 50
        self.x = self.x0
        self.y = self.y0
        self.r = 25
        self.color = RED
        self.health = 20
        self.g = 9.81
        self.vx = 4
        self.vy = 0
        self.ky = 0.99
        self.inside = False
        self.last = pygame.time.get_ticks()
        self.cooldown = 150
        self.cost = 500

    def check_coords(self):
        if self.x - self.r >= 0 or self.x + self.r <= WIDTH:
            self.inside = True
        else:
            self.inside = False

    def moving(self, dt, obj):
        if self.x0 == -10:
            self.x += self.vx * dt
        if self.x0 == WIDTH + 40:
            self.x -= self.vx * dt
        self.vy += self.g * dt
        self.y += self.vy * dt
        if self.inside:
            if self.y + self.r >= obj.y + obj.right_wheel.height / 2:
                self.vy = -self.vy * self.ky
                self.y -= self.y + self.r - (obj.y + obj.right_wheel.height / 2)
            if self.x + self.r >= WIDTH:
                self.vx = -self.vx
                self.x -= self.x + self.r - WIDTH
            if self.x < self.r:
                self.vx = -self.vx
                self.x += self.r - self.x

    def creation(self):
        now = pygame.time.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            new_aim = Aim(self.screen)
            aims.append(new_aim)

    def if_player_lose(self, aims, gun):
        global finished
        if (self.y - self.r) >= (gun.y - gun.muzzle.height) and abs(self.vy) <= 20:
            aims.remove(a)
            finished = True

    def draw_aim(self):
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r)
        m = pygame.font.SysFont("comicsansms", 16)
        value = m.render(str(round(self.health)), True, BLACK)
        screen.blit(value, [self.x - self.r / 2, self.y - self.r / 2])


def collision(aims, bullets):
    for a in aims:
        for b in bullets:
            rect1 = pygame.Rect(b.x, b.y, 2 * b.r, 2 * b.r)
            rect2 = pygame.Rect(a.x - a.r / (2 ** 0.5),
                                a.y - a.r / (2 ** 0.5),
                                a.r * (2 ** 0.5), a.r * (2 ** 0.5))
            if rect1.colliderect(rect2):
                a.health -= 1
                bullets.remove(b)


def death_gun(gun, aims):
    for a in aims:
        rect = pygame.Rect(a.x - a.r / (2 ** 0.5),
                           a.y - a.r / (2 ** 0.5),
                           a.r * (2 ** 0.5), a.r * (2 ** 0.5))
        if rect.colliderect(gun.muzzle) or \
                rect.colliderect(gun.left_wheel) or \
                rect.colliderect(gun.right_wheel):
            return True


def print_score(score):
    m = pygame.font.SysFont("comicsansms", 18)
    value = m.render("Ваш счёт: " + str(round(score)), True, RED)
    screen.blit(value, [10, 10])

def update_score(a):
    global score
    score += a.cost

def delete_dead_aims_and_update(aims):
    for a in aims:
        if a.health <= 0:
            update_score(a)
            aims.remove(a)
            update_time()

def update_time():
    global dt
    dt *= 1.1

def save_last_result(name, score, counter):
    with open ('last result.txt', 'w') as file:
        file.write('Имя игрока:' + name)
        file.write('Результат:' + str(score))
        file.write('Время игровой сессии:' + str(counter))
        print('Ваш результат:', score)
        print('Время Вашей игровой сессии:', counter,  'секунд(-ы)')


pygame.init()
name = input('Введите ваше имя: ')
screen = pygame.display.set_mode((WIDTH, HEIGHT))
img = pygame.image.load('work_screen.jpg').convert()
pygame.display.set_caption('Ball Blast')

clock = pygame.time.Clock()
FPS = 30
dt = clock.tick(FPS) / 100
finished = False
gun = Gun(screen)
bullets = []
aims = []
count = 0
counter = 0
score = 0

first_aim = Aim(screen)
aims.append(first_aim)

sec = pygame.font.SysFont("comicsansms", 18)
time_text = sec.render("Время игры: " + str(counter), True, RED)
timer_event = pygame.USEREVENT + 1
pygame.time.set_timer(timer_event, 1000)

while not finished:
    screen.blit(img, (0, 0))
    gun.shooting()
    delete_dead_aims_and_update(aims)
    print_score(score)

    gun.vis_parts()
    gun.motion()
    for b in bullets:
        b.draw_bul()
        b.move(dt)
        b.deleting(b)

    for a in aims:
        a.draw_aim()
        a.check_coords()
        a.moving(dt, gun)
        a.if_player_lose(aims, gun)

    count += 1

    collision(aims, bullets)

    if death_gun(gun, aims):
        finished = True

    if count % 125 == 0:
        i = Aim(screen)
        aims.append(i)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        if event.type == timer_event:
            counter += 1
            time_text = sec.render("Время игры: " + str(counter), True, RED)

    screen.blit(time_text, [10, 30])

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()

save_last_result(name, score, counter)