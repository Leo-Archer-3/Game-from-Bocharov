import pygame
import os
import sys

pygame.init()
size = width, height = 700, 500

pygame.display.set_caption('New Mario')
pygame.key.set_repeat(200, 300)
FPS = 50
WIDTH = 1000
HEIGHT = 500
# STEP = 10
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

tile_width = tile_height = 60


hero_v_x = 15
hero_v_y = -90

icicle_v = 3
icicles = 10

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
'''


def generate_level(level):
    print(level)
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if(level[y][x] == '#'):
                Wall('wall', x, y)
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
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Новый Марио",
                  "стрелочки - ходить",
                  "f - кидать сосульки",
                  "жёлтые плиты меняют гравитацию",
                  "синие - размеры Марио",
                  "встнь на плиту, чтобы её активировать"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
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
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
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
        self.speed = 1


    def update(self):
        if(pygame.sprite.spritecollideany(self, plates_group)):
            self.gravity *= -1
            self.speed *= -1
        self.rect = self.rect.move(0, self.speed)
        if (pygame.sprite.spritecollideany(self, walls_group)):
            self.rect = self.rect.move(0, -self.speed)
            #self.speed = 0
        #else:
            #self.speed += self.gravity

    def run(self, x):
        self.rect = self.rect.move(x, 0)
        if (pygame.sprite.spritecollideany(self, walls_group)):
            self.rect = self.rect.move(-x, 0)
        if(x > 0):
            self.image = self.image_right
            self.direction_right = True
        else:
            self.image = self.image_left
            self.direction_right = False

    def jump(self, y):
        self.rect = self.rect.move(0, self.gravity)
        if (pygame.sprite.spritecollideany(self, walls_group)):
            self.rect = self.rect.move(0, y * self.gravity)
            if (pygame.sprite.spritecollideany(self, walls_group)):
                self.rect = self.rect.move(0, y * -self.gravity)

    def shoot(self):
        Icicle(self.rect.left + 10, self.rect.top + 25, self.direction_right)


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


# Класс стен
class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(walls_group, all_sprites)
        self.image = tile_images[tile_type]
        print(tile_width * pos_x, tile_height * pos_y)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


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
tile_images = {'wall': load_image('brick4.jpg')}
player_image = load_image('mar3.png', -1)
icicle_image = load_image('icicle.png', -1)
monster_image = load_image('monster2.png', -1)

# Генерация групп спрайтов и самих спрайтов
all_sprites = pygame.sprite.Group()

player_group = pygame.sprite.Group()
icicle_group = pygame.sprite.Group()

monsters_group = pygame.sprite.Group()

walls_group = pygame.sprite.Group()
plates_group = pygame.sprite.Group()




player, level_x, level_y = generate_level(load_level('map.txt'))




camera = Camera()
run = True
death = False
fire = 10
timer = 0
font = pygame.font.Font(None, 25)
while(run and not death):
    # Камера
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        key = pygame.key.get_pressed()
        if key[pygame.K_w]:
            player.jump(hero_v_y)
        if key[pygame.K_a]:
            player.run(-hero_v_x)
        if key[pygame.K_d]:
            player.run(hero_v_x)
        if key[pygame.K_s]:
            if(fire > 10):
                if(icicles > 0):
                    player.shoot()
                    icicles -= 1
                    fire = 0
    fire += 1

    if(pygame.sprite.spritecollideany(player, monsters_group)):
        death = True

    if(timer < 15):
        timer += 1
    else:
        timer = 0
        player.update()
        icicle_group.update()
        monsters_group.update()

    screen.fill((65, 105, 225))

    text = font.render('Сосулек осталось' + str(icicles), True, (0, 0, 0))
    screen.blit(text, (350, 100))

    walls_group.draw(screen)
    player_group.draw(screen)
    icicle_group.draw(screen)
    monsters_group.draw(screen)
    all_sprites.draw(screen)
    pygame.display.flip()



font = pygame.font.Font(None, 50)
text = font.render("You are death!", True, (0, 0, 0))

if(death):
    screen.fill((220, 20, 60))

    walls_group.draw(screen)
    player_group.draw(screen)
    monsters_group.draw(screen)
    all_sprites.draw(screen)
    screen.blit(text, (350, 100))
    pygame.display.flip()

    while(run):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

terminate()