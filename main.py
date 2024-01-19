import random
import csv
import pygame
import sys
import os


def load_image(name, colorkey=None):
    fullname = os.path.join('', 'image/' + name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def draw_text():
    font = pygame.font.Font('PressStart2P-Regular.ttf', 20)
    text_y = screen.get_height() - 150
    text_image = font.render(need_text[:now_text], True, (255, 255, 255))
    pygame.draw.rect(screen, (0, 0, 0), (0, text_y, screen.get_width(), 150))
    screen.blit(text_image, (0, text_y))


class Tile(pygame.sprite.Sprite):
    def __init__(self, image_name, pos_x=0, pos_y=0):
        super().__init__(tiles_group, all_sprites)
        self.image = load_image(image_name)
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Room:
    def __init__(self, self_id, decor='', text=''):
        self.self_id = self_id
        self.decor = decor
        self.neighbors = {0: (0, False, 0), 1: (0, False, 0), 2: (0, False, 0), 3: (0, False, 0)}
        self.text = text

    def entry(self):
        global now_text, need_text, is_text_needing
        now_text = 0
        if self.text != '':
            need_text = self.text
            is_text_needing = True
        else:
            need_text = ''
            is_text_needing = False
        self.show_room()

    def add_parameters(self):
        pass

    def show_room(self):
        for item in tiles_group:
            item.kill()
        res = ''
        if self.neighbors[direction][0] == 0:
            res += '0'
        else:
            res += '1'
        if self.neighbors[(direction + 3) % 4][0] == 0:
            res += '0'
        else:
            res += '1'
        if self.neighbors[(direction + 1) % 4][0] == 0:
            res += '0'
        else:
            res += '1'
        screen.blit(load_image('rooms_view/' + res + '.png'), (0, 0))
        if self.decor != '':
            Tile('decoration/' + self.decor)
        tiles_group.draw(screen)
        player_group.draw(screen)

    def interact(self):
        pass

    def try_move(self):
        global now_room
        if self.neighbors[direction][0] != 0:
            if self.neighbors[direction][1] or self.neighbors[direction][2] in bag:
                now_room = self.neighbors[direction][0]
                now_room.entry()


    def turn_left(self):
        global direction
        direction = (direction + 3) % 4
        self.show_room()

    def turn_right(self):
        global direction
        direction = (direction + 1) % 4
        self.show_room()

    def turn_back(self):
        global direction
        direction = (direction + 2) % 4
        self.show_room()

    def change_neighbor(self, direct, new_neighbor, id_key):
        is_open = (id_key == 0)
        self.neighbors[direct] = (new_neighbor, is_open, id_key)


class Portal(Room):
    def try_move(self):
        global now_room
        now_room = map_list[random.randint(0, 40)]
        now_room.show_room()


class Chest(Room):
    def __init__(self, self_id, decor='', text=''):
        super().__init__(self_id, decor, text)
        self.is_something = True

    def add_parameters(self, direction_chest=0, key_id=-1, *items_id):
        self.direction_chest = int(direction_chest)
        self.key_id = int(key_id)
        self.items_id = list(map(int, items_id))

    def interact(self):
        global need_text, now_text, is_text_needing
        if self.is_something and self.key_id in bag:
            bag.extend(self.items_id)
            self.is_something = False
        else:
            need_text = 'Нужен ключ'
            now_text = 0
            is_text_needing = True
        self.show_room()

    def show_room(self):
        super().show_room()
        if direction == self.direction_chest:
            if self.is_something:
                Tile('decoration/chest.png')
            else:
                Tile('decoration/open_chest.png')
            tiles_group.draw(screen)
            player_group.draw(screen)



class Item(Room):
    def __init__(self, self_id, decor='', text=''):
        super().__init__(self_id, decor, text)
        self.is_something = True

    def add_parameters(self, *items_id):
        self.items_id = list(map(int, items_id))

    def interact(self):
        global now_room, need_text, is_text_needing
        if self.is_something:
            bag.extend(self.items_id)
            now_text = 0
            need_text = 'Вы подобрали ключ'
            is_text_needing = True


class Exit(Room):
    def entry(self):
        global play
        play = False



def load_map(file_name):
    global map_list
    map_list = dict()
    with open(file_name, encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        reader = list(reader)
    for i in reader:
        if int(i[0]) not in map_list.keys():
            _locals = locals()
            exec('room = ' + str(i[1]) + "(" + str(i[0]) + ', "' + str(i[2]) + '", "' + str(i[7]) + '")', globals(),
                 _locals)
            room = _locals['room']
            map_list[int(i[0])] = room
        else:
            room = map_list[int(i[0])]
        for j in range(3, 7):
            if int(i[j]) != 0:
                if int(i[j]) not in map_list.keys():
                    _locals = locals()
                    exec('neighbour_room = ' + str(reader[int(i[j]) - 1][1]) + "(" + str(i[j]) + ', "' +
                         reader[int(i[j]) - 1][2] + '", "' + reader[int(i[j]) - 1][7] + '")', globals())
                    room.change_neighbor(j - 3, neighbour_room, int(i[j + 5]))
                    map_list[int(i[j])] = neighbour_room
                else:
                    room.change_neighbor(j - 3, map_list[int(i[j])], int(i[j + 5]))
        if len(i) > 12:
            room.add_parameters(*i[12:])


def level(number):
    global now_room, now_text, need_text, is_text_needing, direction, bag, play
    bag = [2]
    direction = 2
    now_room = 0
    now_text = 0
    need_text = ''
    load_map('map.csv')
    now_room = map_list[23]
    my_event_type = pygame.USEREVENT + 1
    pygame.time.set_timer(my_event_type, 100)
    now_room.entry()
    play = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if play:
                if event.type == pygame.KEYUP:
                    if event.key == 1073741906:
                        now_room.try_move()
                    elif event.key == 1073741905:
                        now_room.turn_back()
                    elif event.key == 1073741904:
                        now_room.turn_left()
                    elif event.key == 1073741903:
                        now_room.turn_right()
                    elif event.key == 101:
                        now_room.interact()
                    print(direction, now_room.self_id, try_get_id(now_room.neighbors[0][0]),
                          try_get_id(now_room.neighbors[1][0]),
                          try_get_id(now_room.neighbors[2][0]), try_get_id(now_room.neighbors[3][0]), now_room)
                if ((event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or
                        (event.type == pygame.KEYUP and event.key == 32)):
                    if is_text_needing:
                        now_text = len(need_text)
                        draw_text()
                        is_text_needing = False
                    else:
                        now_room.show_room()
                if is_text_needing and event.type == my_event_type:
                    now_text += 1
                    draw_text()
                    if now_text == len(need_text):
                        now_text = 0
                        need_text = ''
                        is_text_needing = False
            else:
                screen.fill(pygame.Color('black'))
                some_text = pygame.transform.scale(load_image('end_of_level.png'), (800, 600))
                screen.blit(some_text, (0, 0))
                if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONDOWN:
                    return
        pygame.display.flip()
        clock.tick(FPS)




def try_get_id(room):
    if room == 0:
        return 0
    else:
        return room.self_id


FPS = 50
size = 800, 600
pygame.init()
screen = pygame.display.set_mode(size)
player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player_image = load_image('character.png')
Player(320, 300)
map_list = dict()
bag = list()
direction = 0
now_room = 0
now_text = 0
need_text = ''
play = True
is_text_needing = False
clock = pygame.time.Clock()
fon = pygame.transform.scale(load_image('fon.jpg'), (512, 512))
screen.blit(fon, (288, 0))
Tile('exit.png', 23, 400)
Tile('level_menu.png', 23, 300)
while True:
    tiles_group.draw(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = event.pos
                if 23 < x < 265 and 400 < y < 459:
                    terminate()
                elif 23 < x < 265 and 300 < y < 393:
                    level(1)
                    screen.fill(pygame.Color('black'))
                    fon = pygame.transform.scale(load_image('fon.jpg'), (512, 512))
                    screen.blit(fon, (288, 0))
                    Tile('exit.png', 23, 400)
                    Tile('level_menu.png', 23, 300)
    pygame.display.flip()
    clock.tick(FPS)
