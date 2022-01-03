import pygame
import os
import sys

# Создание и настройка окна
pygame.init()
size = width, height = 700, 500

pygame.display.set_caption('New Mario')
pygame.key.set_repeat(200, 300)
FPS = 50
WIDTH = 1000
HEIGHT = 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

# размеры 1 плитки(квадрата для изображения)
tile_width = tile_height = 60

# Скорость игрока
hero_v_x = 15
hero_v_y = -90

# Скорость и кол-во сосулек
icicle_v = 3


# количество уровней
level = 1
max_level = 2

# счётчики смертей и собранных монет
number_of_deaths = 0
total_money = 0

def load_level(filename):
    global level_map
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# обозначения в файле карты:
'''
"#" - стена
"." - пустота
"@" - Марио
"*" - монстр
"-" и "_" - нажимная плита
"$" - монета
'''


def generate_level(level):
    goldens_total = 0
    new_player, home, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if(level[y][x] == '#'):
                walls_group.add(Building('wall', x, y))
            elif(level[y][x] == '@'):
                new_player = Hero(x, y)
            elif(level[y][x] == '*'):
                Monster(x, y)
            elif(level[y][x] == '_'):
                Plate(tile_width * x, tile_height * (y + 1) - 3)
                Plate(tile_width * x + tile_width // 2, tile_height * (y + 1) - 3)
            elif (level[y][x] == '-'):
                Plate(tile_width * x, tile_height * y)
                Plate(tile_width * x + tile_width // 2, tile_height * y)
            elif(level[y][x] == '$'):
                golden_group.add(Building('golden', x, y))
                goldens_total += 1
            elif (level[y][x] == '^'):
                home = Building('home', x, y - 5)
    return new_player, home, x, y, goldens_total


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Новый Марио",
                  "нажмите на пробел для продолжения",
                  "постарайся дойти до домика",
                  "и не попасться монстрам;",
                  "a, d, w - движение;",
                  "s - кидать сосульки;",
                  "чёрные плиты меняют гравитацию,",
                  "встнь на плиту,",
                  "чтобы её активировать;"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 20
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            key = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                terminate()
            elif key[pygame.K_SPACE] or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def try_move(obj, group, x, y):
    obj.rect = obj.rect.move(x, y)
    if(x > 0):
        a = -1
        b = 0
    elif(x < 0):
        a = 1
        b = 0
    elif(y > 0):
        a = 0
        b = -1
    else:
        a = 0
        b = 1
    while(pygame.sprite.spritecollideany(obj, group)):
        obj.rect = obj.rect.move(a, b)


# класс главного героя
class Hero(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image_right = player_image
        self.image_left = pygame.transform.flip(player_image, True, False)
        self.image = self.image_right
        self.direction_right = True
        self.x = tile_width * pos_x
        self.y = tile_height * pos_y - 4
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y - 4)

        self.gravity = 1
        self.speed = 2

    def update(self):
        if(pygame.sprite.spritecollideany(self, plates_group)):
            self.gravity *= -1
            self.speed *= -1
        try_move(self, walls_group, 0, self.speed)

    def run(self, x):
        try_move(self, walls_group, x, 0)
        if(x > 0):
            self.image = self.image_right
            self.direction_right = True
        else:
            self.image = self.image_left
            self.direction_right = False

    def jump(self, y):
        self.rect = self.rect.move(0, self.gravity)
        if (pygame.sprite.spritecollideany(self, walls_group)):
            try_move(self, walls_group, 0, y * self.gravity)

    def shoot(self):
        Icicle(self.rect.left + 10, self.rect.top + 25, self.direction_right)


# Класс сосулек (снарядов)
class Icicle(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, direction_right):
        super().__init__(icicle_group, all_sprites)
        if(direction_right):
            self.image = icicle_image
            self.speed = icicle_v
        else:
            self.image = pygame.transform.flip(icicle_image, True, False)
            self.speed = -icicle_v
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update(self):
        self.rect = self.rect.move(self.speed, 0)
        if (pygame.sprite.spritecollideany(self, walls_group)):
            self.kill()


# Класс монстра
class Monster(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(monsters_group, all_sprites)
        self.image = monster_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y + 10)
        self.monster_v = 3

    def update(self):
        if(pygame.sprite.spritecollideany(self, icicle_group)):
            self.kill()

        self.rect = self.rect.move(self.monster_v, 0)
        if (pygame.sprite.spritecollideany(self, walls_group)):
            self.rect = self.rect.move(-self.monster_v, 0)
            self.monster_v *= -1


# Класс стен, монет и домика
class Building(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# Класс нажимной плиты
class Plate(pygame.sprite.Sprite):
    def __init__(self, x,  y):
        super().__init__(all_sprites)
        self.add(plates_group)
        self.image = pygame.Surface([tile_width // 2 - 2, 2])
        self.rect = pygame.Rect(x, y, 2, tile_width // 2 - 2)


# Класс камеры
class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


# Заставка
start_screen()

# Загрузка изображений
tile_images = {'wall': load_image('brick.jpg'),
               'golden': load_image('golden.png', -1),
               'home': load_image('home.png', -1)}
player_image = load_image('mar.png', -1)
icicle_image = load_image('icicle.png', -1)
monster_image = load_image('monster.png', -1)


# Фоновая музыка
pygame.mixer.music.load(os.path.join('data', 'saundtrek.mp3'))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Музыка победы
sound_win = pygame.mixer.Sound(os.path.join('data', 'win.mp3'))

# Музыка смерти
sound_death = pygame.mixer.Sound(os.path.join('data', 'death.mp3'))

# Музыка монетки
sound_golden = pygame.mixer.Sound(os.path.join('data', 'golden.mp3'))

# Время в момент начала игры
start_time = pygame.time.get_ticks()

while(level <= max_level):
    # Генерация групп спрайтов
    all_sprites = pygame.sprite.Group()

    player_group = pygame.sprite.Group()
    icicle_group = pygame.sprite.Group()

    monsters_group = pygame.sprite.Group()

    walls_group = pygame.sprite.Group()
    golden_group = pygame.sprite.Group()
    plates_group = pygame.sprite.Group()

    # Генерация спрайтов
    map_name = 'map' + str(level) + '.txt'
    player, home, level_x, level_y, goldens_total = generate_level(load_level(map_name))
    camera = Camera()

    death = False
    win = False
    money = 0
    fire = 10
    timer = 0
    font = pygame.font.Font(None, 25)

    # Выдача сосулек игроку
    icicles = 10

    while(not death and not win):
        # Камера
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            key = pygame.key.get_pressed()
            if key[pygame.K_w]:
                player.jump(hero_v_y)
            if key[pygame.K_a]:
                player.run(-hero_v_x)
            if key[pygame.K_d]:
                player.run(hero_v_x)
            if key[pygame.K_f]:
                if(fire > 10):
                    if(icicles > 0):
                        player.shoot()
                        icicles -= 1
                        fire = 0
        fire += 1
        # проверка на столкновение игрока с монстром
        if(pygame.sprite.spritecollideany(player, monsters_group)):
            number_of_deaths += 1
            death = True

        # проверка на то, что игрок прошёл уровень
        if (pygame.sprite.spritecollideany(home, player_group)):
            win = True

        # проверка на то, что игрок подобрал монетку
        if (pygame.sprite.spritecollide(player, golden_group, True)):
            sound_golden.play()
            money += 1
            total_money += 1

        if(timer < 15):
            timer += 1
        else:
            timer = 0
            player.update()
            icicle_group.update()
            monsters_group.update()
        golden_group.update()
        screen.fill((65, 105, 225))



        all_sprites.draw(screen)
        text1 = font.render('Монет собрано ' + str(money) + ' из ' + str(goldens_total), True, (255, 215, 0))
        text2 = font.render('Сосулек осталось' + str(icicles), True, (64, 224, 208))
        screen.blit(text1, (350, 70))
        screen.blit(text2, (350, 100))
        pygame.display.flip()


    # если ты умер или прошёл уровень
    pygame.mixer.music.pause()
    font = pygame.font.Font(None, 50)
    text_death = font.render("You are dead!", True, (0, 0, 0))
    text_win = font.render("You won!", True, (0, 0, 0))

    if(death):
        sound_death.play()
        screen.fill((220, 20, 60))
        write_text = text_death
        x = 350
    else:
        sound_win.play()
        level += 1
        screen.fill((0, 255, 255))
        write_text = text_win
        x = 250

    walls_group.draw(screen)
    player_group.draw(screen)
    monsters_group.draw(screen)
    all_sprites.draw(screen)
    screen.blit(write_text, (x, 100))

    run = True
    while(run):
        for event in pygame.event.get():
            key = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                terminate()
            elif key[pygame.K_SPACE] or event.type == pygame.MOUSEBUTTONDOWN:
                run = False
        pygame.display.flip()
        clock.tick(FPS)
    pygame.mixer.music.unpause()


pygame.mixer.music.pause()
game_time = (pygame.time.get_ticks() - start_time) // 1000
game_time_min = game_time // 60
game_time_sec = game_time % 60
intro_text = ["Новый Марио",
              "",
              "Время игры: " + str(game_time_min) + " мин " + str(game_time_sec) + " сек",
              "Количество смертей: " + str(number_of_deaths),
              "Монет собрано: " + str(total_money)]
screen.fill((0, 0, 0))
font = pygame.font.Font(None, 30)
text_coord = 20
for line in intro_text:
    string_rendered = font.render(line, 1, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    text_coord += 10
    intro_rect.top = text_coord
    intro_rect.x = 10
    text_coord += intro_rect.height
    screen.blit(string_rendered, intro_rect)

pygame.display.flip()
while True:
    for event in pygame.event.get():
        key = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            terminate()
        elif key[pygame.K_SPACE] or event.type == pygame.MOUSEBUTTONDOWN:
            terminate()
