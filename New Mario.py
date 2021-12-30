import pygame
import os
import sys

pygame.init()
size = width, height = 700, 500

pygame.display.set_caption('New Mario')
pygame.key.set_repeat(200, 300)
FPS = 100
WIDTH = 1000
HEIGHT = 500
# STEP = 10
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

tile_width = tile_height = 50


hero_v_x = 20
hero_v_y = -10


def load_level(filename):
    global level_map
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    print(level)
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Hero(x, y)
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


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        print(tile_width * pos_x, tile_height * pos_y)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Hero(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y)
        self.x = pos_x * tile_width
        self.y = pos_y * tile_height
        self.speed = 0

    def update(self, x):
        #if(pygame.sprite.spritecollideany(self, walls_group)):
        #    self.speed = 0
        #else:
        self.rect = self.rect.move(0, self.speed)
        self.speed -= 4


    def run(self, x):
        self.rect = self.rect.move(x, 0)

    def jump(self, y):
        self.rect = self.rect.move(0, y)


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
tile_images = {'wall': load_image('brick2.jpg'), 'empty': load_image('sky.jpg')}
player_image = load_image('mar1.png', -1)

# Генерация групп спрайтов и самих спрайтов
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()

player, level_x, level_y = generate_level(load_level('map.txt'))
camera = Camera()
run = True

while(run):
    camera.update(player)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        key = pygame.key.get_pressed()
        if key[pygame.K_w]:
            player.jump(hero_v_y)
        if key[pygame.K_a]:
            player.update(-hero_v_x)
        if key[pygame.K_d]:
            player.update(hero_v_x)
    screen.fill((0, 0, 0))
    tiles_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()



terminate()