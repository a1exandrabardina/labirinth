import random
import csv
import pygame
import sys
import os
import math


def load_image(name, colorkey=None):  # функция загрузки изображения
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


def draw_text():  # функция побуквенного печатания
    font = pygame.font.Font('PressStart2P-Regular.ttf', 20)
    text_y = screen.get_height() - 150
    text_image = font.render(need_text[:now_text], True, (255, 255, 255))
    pygame.draw.rect(screen, (0, 0, 0), (0, text_y, screen.get_width(), 150))
    screen.blit(text_image, (0, text_y))


class Decor(pygame.sprite.Sprite):  # спрайт декораций в комнате
    def __init__(self, image_name, pos_x=0, pos_y=0):
        super().__init__(decors_group, all_sprites)
        self.image = load_image(image_name)
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Firefly(pygame.sprite.Sprite):  # спрайт светлячков
    def __init__(self):
        super().__init__(fireflies, all_sprites)
        self.image = load_image('firefly.png')
        self.rect = self.image.get_rect().move(random.randint(0, 800), random.randint(0, 600))
        self.direct = random.randint(0, 360)

    def update(self):  # перемещение светлячков
        # Выбор действия - двигаться в том же направлении или помнять его (1:30)
        to_do = random.randint(0, 30)
        if to_do == 0:
            # смена направления
            self.direct = random.randint(0, 360)
        # выбор скорости движения
        u = random.randrange(3)
        self.rect = self.rect.move(u * math.cos(self.direct), u * math.sin(self.direct))
        x, y = self.rect.topleft
        # появление в новом месте в случае выхода за предел экрана
        if (0 > x or x > 800) and (0 > y or y > 600):
            self.rect = self.image.get_rect().move(random.randint(0, 800), random.randint(0, 600))


class Player(pygame.sprite.Sprite):  # спрайт игрока
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Room:  # класс комнаты
    def __init__(self, self_id, decor='', text=''):  #
        self.self_id = self_id
        self.decor = decor
        self.neighbors = {0: (0, False, 0), 1: (0, False, 0), 2: (0, False, 0), 3: (0, False, 0)}
        self.text = text

    def entry(self):  # действие при входе в комнату
        global now_text, need_text, is_text_needing
        now_text = 0
        if self.text != '':
            # печатание текста при существовании такового
            need_text = self.text
            is_text_needing = True
        else:
            need_text = ''
            is_text_needing = False
        self.show_room()

    def add_parameters(self):
        pass

    def show_room(self):  # функция, вывода изображения комнаты с текущего ракурса на экран
        for item in decors_group:
            item.kill()
        screen.blit(load_image('rooms_view/room.png'), (0, 0))
        # добавление проходов на изображение
        if self.neighbors[direction][0] != 0:
            if self.neighbors[direction][1]:
                screen.blit(load_image('rooms_view/passage.png'), (0, 0))
            else:
                screen.blit(load_image('rooms_view/door.png'), (0, 0))
        if self.neighbors[(direction + 3) % 4][0] != 0:
            if self.neighbors[(direction + 3) % 4][1]:
                screen.blit(load_image('rooms_view/lpassage.png'), (0, 0))
            else:
                screen.blit(load_image('rooms_view/ldoor.png'), (0, 0))
        if self.neighbors[(direction + 1) % 4][0] != 0:
            if self.neighbors[(direction + 1) % 4][1]:
                screen.blit(load_image('rooms_view/rpassage.png'), (0, 0))
            else:
                screen.blit(load_image('rooms_view/rdoor.png'), (0, 0))
        # добавление декораций на экран
        if self.decor != '':
            Decor('decoration/' + self.decor)
        decors_group.draw(screen)
        player_group.draw(screen)

    def interact(self):
        pass

    def try_move(self):  # попытка перемещения в комнату впереди
        global now_room, now_text, need_text, is_text_needing
        if self.neighbors[direction][0] != 0:
            if self.neighbors[direction][1]:
                sound_of_steps.play()
                now_room = self.neighbors[direction][0]
                now_room.entry()
            else:
                # обработка закрытой двери
                if self.neighbors[direction][2] in bag:
                    sound_open_door.play()
                    now_room = self.neighbors[direction][0]
                    now_room.entry()
                    self.neighbors[direction] = (self.neighbors[direction][0], True, 0)
                else:
                    need_text = 'Дверь закрыта'
                    now_text = 0
                    is_text_needing = True

    def turn_left(self):  # смена направления (налево)
        global direction
        direction = (direction + 3) % 4
        self.show_room()

    def turn_right(self):  # смена направления (направо)
        global direction
        direction = (direction + 1) % 4
        self.show_room()

    def turn_back(self):  # смена направления (назад)
        global direction
        direction = (direction + 2) % 4
        self.show_room()

    def change_neighbor(self, direct, new_neighbor, id_key):  # функция добавления соседней комнаты и состоянии двери
        is_open = (id_key == 0)
        self.neighbors[direct] = (new_neighbor, is_open, id_key)


class Portal(Room):  # класс комнаты с порталом
    def try_move(self):  # при движении отправляет в случайную комнату
        global now_room
        now_room = map_list[random.choice(list(map_list.keys()))]
        now_room.entry()


class Chest(Room):  # класс комнаты с сундуком
    def __init__(self, self_id, decor='', text=''):
        super().__init__(self_id, decor, text)
        self.is_something = True

    def add_parameters(self, direction_chest=0, key_id=-1, *items_id):  # добавление информации о ключе
        # и предметах в сундуке
        self.direction_chest = int(direction_chest)
        self.key_id = int(key_id)
        self.items_id = list(map(int, items_id))

    def interact(self):  # функция взаимодействия с сундуком
        global need_text, now_text, is_text_needing
        if self.is_something and self.key_id in bag:
            # получение предметов при наличии ключа
            sound_open_door.play()
            need_text = 'Вы получили ещё один ключ'
            now_text = 0
            is_text_needing = True
            bag.extend(self.items_id)
            self.is_something = False
        else:
            # реакция на попытку открыть без ключа
            need_text = 'Нужен ключ'
            now_text = 0
            is_text_needing = True
        self.show_room()

    def show_room(self):
        super().show_room()
        if direction == self.direction_chest:
            # рисование закрытого/открытого сундука в зависимости от состояния
            if self.is_something:
                Decor('decoration/chest.png')
            else:
                Decor('decoration/open_chest.png')
            decors_group.draw(screen)
            player_group.draw(screen)


class Item(Room):  # класс комнаты с предметами
    def __init__(self, self_id, decor='', text=''):
        super().__init__(self_id, decor, text)
        self.is_something = True

    def add_parameters(self, *items_id):  # добавление информации о предметах в комнате
        self.items_id = list(map(int, items_id))

    def interact(self):  # функция получения предметов из комнаты
        global now_room, need_text, is_text_needing, now_text
        if self.is_something:
            bag.extend(self.items_id)
            now_text = 0
            need_text = 'Вы подобрали ключ'
            is_text_needing = True
            self.decor = ''


class Exit(Room):  # Комната окончания игры
    def entry(self):  # при попадании завершает основной цикл уровня
        global play
        play = False


def continue_level():  # загрузка последнего выбранного уровня и прогресса в нем
    global bag, direction, room_id
    with open('save.csv', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        line = list(reader)[0]
    room_id = int(line[0])
    level_name = line[1]
    direction = int(line[2])
    if len(line) > 3:
        bag = list(map(int, line[3:]))
    else:
        bag = list()
    level(level_name)


def save(level_name):  # сохранение текущего прогресса и последнего выбранного уровня
    with open('save.csv', 'w', encoding="utf8") as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"')
        data = [now_room.self_id, level_name, direction, *bag]
        print(data)
        writer.writerow(data)


def load_map(file_name):  # функция загрузки карты для уровня
    global map_list
    map_list = dict()
    # открыть карту csv файл
    with open(file_name, encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        reader = {int(i[0]): i for i in reader}
    # обработка каждой строчки
    for i in reader.values():
        if int(i[0]) not in map_list.keys():
            # создание новой комнаты или её подкласса на основе информации из файла
            _locals = locals()
            exec('room = ' + str(i[1]) + "(" + str(i[0]) + ', "' + str(i[2]) + '", "' + str(i[7]) + '")', globals(),
                 _locals)
            room = _locals['room']
            map_list[int(i[0])] = room
        else:
            # присовоение текущей комнаты из уже сущетствующих
            room = map_list[int(i[0])]
        for j in range(3, 7):
            if int(i[j]) != 0:
                # добавление соседа
                if int(i[j]) not in map_list.keys():
                    # создание новой комнаты соседа
                    _locals = locals()
                    exec('neighbour_room = ' + str(reader[int(i[j])][1]) + "(" + str(i[j]) + ', "' +
                         reader[int(i[j])][2] + '", "' + reader[int(i[j])][7] + '")', globals())
                    room.change_neighbor(j - 3, neighbour_room, int(i[j + 5]))
                    map_list[int(i[j])] = neighbour_room
                else:
                    room.change_neighbor(j - 3, map_list[int(i[j])], int(i[j + 5]))
        if len(i) > 12:
            # добавление особых параметров при их наличии
            room.add_parameters(*i[12:])


def level(name):  # функция основного уровня
    global now_room, now_text, need_text, is_text_needing, direction, bag, play
    # добавление события раз в 0.1 сек
    my_event_type = pygame.USEREVENT + 1
    pygame.time.set_timer(my_event_type, 100)
    # присваивание начальных параметров
    play = True
    now_text = 0
    need_text = ''
    load_map('maps/' + name)
    now_room = map_list[room_id]
    now_room.entry()
    sound_open_door.play()
    while True:
        # основной цикл уровня
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  #
                terminate()
            if play:
                # обработка нажатий на клавиатуру и мышку
                if event.type == pygame.KEYUP:
                    if event.key == 1073741906:
                        # перемещение вперед на стрелку вверх
                        now_room.try_move()
                    elif event.key == 1073741905:
                        # поворот назад на стрелку вниз
                        now_room.turn_back()
                    elif event.key == 1073741904:
                        # поворот налево на стрелку влево
                        now_room.turn_left()
                    elif event.key == 1073741903:
                        # поворот на право при стрелке вправо
                        now_room.turn_right()
                    elif event.key == 101:
                        # обработка взаимодействия при кнопке 'E'
                        now_room.interact()
                    elif event.key == 115:
                        # обработка охранения при кнопке 'S'
                        save(name)
                if ((event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or
                        (event.type == pygame.KEYUP and event.key == 32)):
                    # моментальный вывод текста или закрыть текст при нажатии на пробел или левую кнопку мыши
                    if is_text_needing:
                        now_text = len(need_text)
                        draw_text()
                        is_text_needing = False
                    else:
                        now_room.show_room()
                if is_text_needing and event.type == my_event_type:
                    # продолжения посимвольного печатания или его завершение
                    now_text += 1
                    draw_text()
                    if now_text == len(need_text):
                        now_text = 0
                        need_text = ''
                        is_text_needing = False
            else:
                # экран завершения игры
                screen.fill(pygame.Color('black'))
                some_text = pygame.transform.scale(load_image('end_of_level.png'), (800, 600))
                screen.blit(some_text, (0, 0))
                if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONDOWN:
                    # возвращение в главное меню
                    return
        pygame.display.flip()
        clock.tick(FPS)


def choose_level():  # экран выбора уровня
    global bag, direction, room_id
    all_files = os.listdir('maps/')
    screen.fill(pygame.Color('black'))
    buttons = len(all_files)
    button_w, button_h = 550, 56
    # рисование кнопок
    button = pygame.transform.scale(load_image('back.png'), (112, 56))
    screen.blit(button, (5, 5))
    for i in range(buttons):
        button = pygame.transform.scale(load_image('button.png'), (button_w, button_h))
        font = pygame.font.Font('PressStart2P-Regular.ttf', 20)
        text_image = font.render(str(i + 1) + '. ' + all_files[i][:-4], True, pygame.Color('#9D0019'))
        screen.blit(button, (25, 100 + (button_h + 10) * i))
        screen.blit(text_image, (35, 110 + (button_h + 10) * i))
    result = ''
    not_found = True
    # обработка нажатия на кнопки
    while not_found:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # обработка выхода из игры
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # проверка нажатия на кнопки
                x, y = event.pos
                if 5 < x < 117 and 5 < y < 61:
                    return
                if 25 < x < 575:
                    for i in range(buttons):
                        if 100 + (button_h + 10) * i < y < (button_h + 100) + (button_h + 10) * i:
                            # сохранение уровня при выборе из списка
                            result = all_files[i]
                            not_found = False
                            break
        pygame.display.flip()
        clock.tick(FPS)
    # загрузка выбранного уровня
    bag = []
    direction = 2
    room_id = 1
    level(result)


# константы
FPS = 50
size = 800, 600
pygame.init()
screen = pygame.display.set_mode(size)
player = None
# группы спрайтов
all_sprites = pygame.sprite.Group()
decors_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
fireflies = pygame.sprite.Group()
player_image = load_image('character.png')
Player(320, 300)
for _ in range(10):
    Firefly()
# инициализация переменнных
map_list = dict()
bag = list()
direction = 0
now_room = 0
now_text = 0
need_text = ''
room_id = 1
play = True
is_text_needing = False
# добавление времени
clock = pygame.time.Clock()
# добавление звуков и музыки
pygame.mixer.music.load('sound/main_music.mp3')
pygame.mixer.music.play()
sound_open_door = pygame.mixer.Sound('sound/door_open.wav')
sound_of_steps = pygame.mixer.Sound('sound/steps.wav')
# загрузка основных изображений
exit_image = pygame.transform.scale(load_image('exit.png'), (242, 59))
level_menu_image = pygame.transform.scale(load_image('level_menu.png'), (242, 93))
continue_button = pygame.transform.scale(load_image('continue.png'), (242, 65))
fon = pygame.transform.scale(load_image('fon.jpg'), (512, 512))
while True:
    # основной цикл
    screen.fill(pygame.Color('black'))
    screen.blit(fon, (288, 0))
    screen.blit(exit_image, (23, 400))
    screen.blit(continue_button, (23, 300))
    screen.blit(level_menu_image, (23, 200))
    fireflies.draw(screen)
    fireflies.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # выход из игры
            terminate()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            if 23 < x < 265 and 400 < y < 459:
                # кнопка выхода из игры
                terminate()
            elif 23 < x < 265 and 300 < y < 465:
                # кнопка продолжения игры
                continue_level()
            elif 23 < x < 265 and 200 < y < 293:
                # меню выбора уровня
                choose_level()
    pygame.display.flip()
    clock.tick(FPS)
