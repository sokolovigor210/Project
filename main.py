import pygame
from random import choice

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
    """
    Конструктор класса Bullet (снаряды пушки).
    Содержит координаты, полуширину, полувысоту, цвет пули,
    а также индикатор того, что пуля находится в пределах экрана.
    """
    def __init__(self, screen, x, y):
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 8
        self.v = self.vy = 30
        self.color = choice(GAME_COLORS)
        self.outside = False

    def move(self, dt):
        """
        Осуществляет движение пули по экрану
        param dt: единица внутриигрового времени.
        """
        self.y -= self.vy * dt

    def draw_bul(self):
        """
        Осуществляет рисовку пули на экране.
        """
        pygame.draw.rect(self.screen, self.color,
                         (self.x - self.r, self.y - self.r,
                          2 * self.r, 2 * self.r), 2 * self.r)

    def deleting(self, obj):
        """
        Осуществляет удаление пуль, вылетевших за пределы экрана
        param obj: объект (пуля), который удаляется из общего массива.
        """
        if self.y + self.r < -2 * self.r:
            bullets.remove(obj)


class Gun:
    """
    Конструктор класса Gun (пушка).
    Содержит координаты оси симметрии пушки, скорость пушки, цвет всех
    её составляющих, параметры её колёс, дула и балки, соединяющей колёса.
    Помимо этого, содержит индикатор того, что пушка стреляет; поля, осуществляющие
    эффект стрельбы с задержкой.
    """
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
        self.state = False  # индикатор того, что пушка стреляет
        self.last = pygame.time.get_ticks() # временные индикаторы
        self.cooldown = 20                  # для задержки стрельбы
        self.health = 1  # здоровье пушки
        self.left_wheel = 0
        self.right_wheel = 0
        self.muzzle = 0

    def vis_parts(self):
        """
        Осуществление отрисовки частей пушки.
        """
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
        # проверка того, что пушка стреляет, для \
        # реализации физического эффекта
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
        """
        Осуществление движения пушки с помощью "стрелок" на клавиатуре.
        """
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
        """
        Осуществление стрельбы пушки при движении.
        """
        now = pygame.time.get_ticks()
        if now - self.last >= self.cooldown and self.state is True:
            self.last = now
            new_bul = Bullet(self.screen, self.x,
                             self.y + self.m_low - self.m_height + 10)
            bullets.append(new_bul)


class Aim:
    """
    Конструктор класса Aim (цель).
    Содержит начальные координаты цели (за пределами экрана), мгновенные
    координаты цели, её радиус, количество жизней, цвет, скорость, параметр затухания
    при соудареннии, а также индикатор того, что цель находится в пределах
    игрового поля, индикатор типа цели (основная или осколок), "стоимость" цели
    в очках.
    """
    def __init__(self, screen, x=choice(AIM_X), y=50):
        self.screen = screen
        self.x0 = x
        self.y0 = y
        self.x = self.x0
        self.y = self.y0
        self.r = 25
        self.color = RED
        self.health = 20
        self.g = 9.81
        self.vx = 4
        self.vy = 0
        self.ky = 0.999  # коэффициент затухания
        self.inside = False
        self.type = 'aim'
        self.last = pygame.time.get_ticks()
        self.cost = 500

    def check_coords(self):
        """
        Проверка, находится ли цель внутри игрового поля.
        """
        if self.x - self.r >= 0 or self.x + self.r <= WIDTH:
            self.inside = True
        else:
            self.inside = False

    def moving(self, dt, obj):
        """
        Осуществление движения целей в зависимости от места появления, а также её типа.
        Реализация отскоков от игрового поля.
        param dt: единица внутриигрового времени.
        param obj: объект, с координатами которого сравниваются координаты цели
                   для отскока
        """
        if self.x0 == -10 and self.type == 'aim':
            self.x += self.vx * dt
        if self.x0 == WIDTH + 40 and self.type == 'aim':
            self.x -= self.vx * dt
        if self.type == 'left_splinter':
            self.x -= self.vx * dt
        if self.type == 'right_splinter':
            self.x += self.vx * dt
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

    def if_player_lose(self, aims, gun):
        """
        Реализация проигрыша игрока при условии, что цель опустилась слишком низко.
        param aims: массив, где хранятся все основные цели
        param gun: пушка
        """
        global finished
        if (self.y - self.r) >= (gun.y - gun.muzzle.height) and abs(self.vy) <= 20:
            aims.remove(a)
            finished = True

    def draw_aim(self):
        """
        Реализация отрисовки целей.
        """
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r)
        m = pygame.font.SysFont("comicsansms", 16)
        value = m.render(str(round(self.health)), True, BLACK)
        screen.blit(value, [self.x - self.r / 2, self.y - self.r / 2])


def collision(aims, bullets):
    """
    Реализация уничтожения пулями целей.
    param aims: массив, где хранятся все основные цели
    param bullets: массив, где хранятся все пули
    """
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
    """
    Реализация уничтожения пулями пушки.
    param aims: массив, где хранятся все основные цели
    param gun: пушка
    """
    for a in aims:
        rect = pygame.Rect(a.x - a.r / (2 ** 0.5),
                           a.y - a.r / (2 ** 0.5),
                           a.r * (2 ** 0.5), a.r * (2 ** 0.5))
        if rect.colliderect(gun.muzzle) or \
                rect.colliderect(gun.left_wheel) or \
                rect.colliderect(gun.right_wheel):
            return True


def creating_splinters(a):
    """
    Создание двух осколков при уничтожении основной цели.
    """
    splinter1 = Aim(screen, a.x - a.r, a.y)
    splinter1.vy = -70
    splinter1.health = 10
    splinter1.inside = True
    splinter1.type = 'left_splinter'
    splinters.append(splinter1)
    splinter2 = Aim(screen, a.x + a.r, a.y)
    splinter2.vy = -70
    splinter2.health = 10
    splinter2.inside = True
    splinter1.type = 'right_splinter'
    splinters.append(splinter2)


def print_score(score):
    """
    Создание интерфейса счёта игрока.
    param score: счёт игрока
    """
    m = pygame.font.SysFont("comicsansms", 18)
    value = m.render("Ваш счёт: " + str(round(score)), True, RED)
    screen.blit(value, [10, 10])


def update_score(a):
    """
    Обновление счёта игрока при уничтожении цели.
    param score: счёт игрока
    """
    global score
    score += a.cost


def update_time():
    """
    Ускорение игры при каждом уничтожении пули.
    """
    global dt
    dt *= 1.01


def delete_dead_aims_and_update(massive):
    """
    Функция реализует обновление ряда параметров при уничтожении основной цели:
    - убирает уничтоженную цель из массива;
    - вызывает функцию обновления счёта;
    - вызывает функцию ускорения игры;
    - вызывает функцию создания осколков.
    param massive: массив с целями
    """
    for a in massive:
        if a.health <= 0:
            update_score(a)
            massive.remove(a)
            update_time()
            creating_splinters(a)


def delete_dead_splinters_and_update(massive):
    """
    Функция реализует обновление ряда параметров при уничтожении осколка:
    - убирает уничтоженный осколок из массива;
    - вызывает функцию обновления счёта;
    - вызывает функцию ускорения игры;
    param massive: массив с осколками
    """
    for s in massive:
        if s.health <= 0:
            update_score(s)
            massive.remove(s)
            update_time()


def save_last_result(name, score, counter):
    """
    Записывает в текстовый файл информацию о последней игре
    param name: имя игрока
    param score: результат игрока
    param counter: время игровой сессии игрока
    """
    with open ('last result.txt', 'w') as file:
        file.write("%s\n" % ('Имя игрока: ' + name))
        file.write("%s\n" % ('Результат: ' + str(score) + str(' (') + 'целей уничтожено: '
                             + str(round(score / 500)) + ')'))
        file.write("%s\n" % ('Время игровой сессии: ' + str(counter)))
        print('Результат: ' + str(score) + str(' (') + 'целей уничтожено: '
                             + str(round(score / 500)) + ')')
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
splinters = []
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
    delete_dead_splinters_and_update(splinters)
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

    for s in splinters:
        s.draw_aim()
        s.moving(dt, gun)
        s.if_player_lose(aims, gun)

    count += 1

    collision(aims, bullets)
    collision(splinters, bullets)

    if death_gun(gun, aims) or death_gun(gun, splinters):
        finished = True

    if count % 300 == 0:
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