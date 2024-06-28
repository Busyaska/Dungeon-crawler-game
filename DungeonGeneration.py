from random import randint
from Entities import Entity
from Components import PositionComponent, BackgroundImageComponent, HitBoxComponent, TypeComponent, CollisionComponent
from WorldInfo import WorldInfo

class Room:

    def __init__(self, start_x: int, start_y: int, width: int, height: int, center: (int, int)):
        self.__start_x = start_x
        self.__start_y = start_y
        self.__width = width
        self.__height = height
        self.__center = center

    def get_room_info(self) -> (int, int, int, int):
        return self.__start_x, self.__start_y, self.__width, self.__height

    def get_room_center(self) -> (int, int):
        return self.__center


class BinaryTree:

    def __init__(self, start_x: int, start_y: int, width: float, height: float):
        self.__start_x = start_x
        self.__start_y = start_y
        self.__width = width
        self.__height = height
        self.__center = (start_x + width // 2, start_y + height // 2)
        self.__room = None
        self.__first_part = None
        self.__second_part = None
        self.__is_separated = False

    def __separate_vertically(self, minimal_room_size: int) -> bool:
        partition_size = randint(3, 7)
        first_part_start_x = self.__start_x
        first_part_start_y = self.__start_y
        first_part_width = self.__width * partition_size // 10
        first_part_height = self.__height
        second_part_start_x = self.__start_x + first_part_width
        second_part_start_y = self.__start_y
        second_part_width = self.__width - first_part_width
        second_part_height = self.__height
        if first_part_height <= minimal_room_size or first_part_width <= minimal_room_size or second_part_width <= minimal_room_size or second_part_height <= minimal_room_size:
            return False
        self.__first_part = BinaryTree(first_part_start_x, first_part_start_y, first_part_width, first_part_height)
        self.__second_part = BinaryTree(second_part_start_x, second_part_start_y, second_part_width, second_part_height)
        return True

    def __separate_horizontally(self, minimal_room_size: int) -> bool:
        partition_size = randint(3, 7)
        first_part_start_x = self.__start_x
        first_part_start_y = self.__start_y
        first_part_width = self.__width
        first_part_height = self.__height * partition_size // 10
        second_part_start_x = self.__start_x
        second_part_start_y = self.__start_y + first_part_height
        second_part_width = self.__width
        second_part_height = self.__height - first_part_height
        if first_part_height <= minimal_room_size or first_part_width <= minimal_room_size or second_part_width <= minimal_room_size or second_part_height <= minimal_room_size:
            return False
        self.__first_part = BinaryTree(first_part_start_x, first_part_start_y, first_part_width, first_part_height)
        self.__second_part = BinaryTree(second_part_start_x, second_part_start_y, second_part_width, second_part_height)
        return True

    def __separate(self, minimal_room_size: int):
        if not self.__is_separated:
            vertical_separation = randint(0, 1)
            if vertical_separation == 1:
                if self.__separate_vertically(minimal_room_size):
                    self.__is_separated = True
                elif self.__separate_horizontally(minimal_room_size):
                    self.__is_separated = True
                else:
                    self.__is_separated = False
            else:
                if self.__separate_horizontally(minimal_room_size):
                    self.__is_separated = True
                elif self.__separate_vertically(minimal_room_size):
                    self.__is_separated = True
                else:
                    self.__is_separated = False
        if not self.__is_separated:
            return
        self.__first_part.__separate(minimal_room_size)
        self.__second_part.__separate(minimal_room_size)

    def __create_room_on_world_map(self, x: int, y: int, width: int, height: int, world_map: list[list[int]]) -> (int, int):
        room_x = x + randint(2, width // 4)
        room_y = y + randint(2, height // 4)
        room_width = width - (room_x - x)
        room_width = room_width - randint(2, room_width // 4)
        room_height = height - (room_y - y)
        room_height = room_height - randint(2, room_height // 4)
        room_center = (room_x + room_width/2, room_y + room_height/2)
        for h in range(room_height):
            for w in range(room_width):
                current_x = room_x + w
                current_y = room_y + h
                world_map[current_y][current_x] = 2
        room = Room(room_x, room_y, room_width, room_height, room_center)
        self.__room = room

    def __create_corridor_on_world_map(self, first_center: (int, int), second_center: (int, int), world_map: list[list[int]]):
        corridor_width = 5
        one_side_corridor_width = corridor_width // 2
        start_x, start_y = first_center
        delta_x = second_center[0] - first_center[0]
        delta_y = second_center[1] - first_center[1]
        if delta_x != 0:
            for w in range(corridor_width):
                for l in range(delta_x):
                    current_x = start_x + l
                    current_y = start_y + w - one_side_corridor_width
                    world_map[current_y][current_x] = 2
        elif delta_y != 0:
            for l in range(delta_y):
                for w in range(corridor_width):
                    current_x = start_x + w - one_side_corridor_width
                    current_y = start_y + l
                    world_map[current_y][current_x] = 2

    def __create_rooms(self, world_map: list[list[int]]):
        if not self.__is_separated:
            self.__create_room_on_world_map(self.__start_x, self.__start_y, self.__width, self.__height, world_map)
        else:
            self.__first_part.__create_rooms(world_map)
            self.__second_part.__create_rooms(world_map)

    def __create_corridors(self, world_map: list[list[int]]) -> (int, int):
        if not self.__is_separated:
            return self.__center
        else:
            first_center = self.__first_part.__create_corridors(world_map)
            second_center = self.__second_part.__create_corridors(world_map)
            self.__create_corridor_on_world_map(first_center, second_center, world_map)
            return self.__center

    def __create_walls(self, world_map: list[list[int]]):
        world_map_height = len(world_map)
        world_map_width = len(world_map[0])
        for y in range(1, world_map_height-1):
            for x in range(1, world_map_width-1):
                if (world_map[y + 1][x + 1] == 2 or world_map[y + 1][x] == 2 or world_map[y + 1][x] == 2 or
                        world_map[y][x + 1] == 2 or world_map[y][x - 1] == 2 or world_map[y - 1][x + 1] == 2 or
                    world_map[y - 1][x] == 2 or world_map[y - 1][x - 1] == 2 or world_map[y + 1][x - 1] == 2) and world_map[y][x] == 0:
                    world_map[y][x] = 1

    def __calculate_coordinates(self, x: int, y: int) -> list[(int, int)]:
        block_size = WorldInfo.get_block_size()
        half_of_block_size = block_size // 2
        current_center_x_position, current_center_y_position = (x * block_size) + half_of_block_size, (y * block_size) + half_of_block_size
        top_left = (current_center_x_position - half_of_block_size, current_center_y_position - half_of_block_size)
        top_right = (current_center_x_position + half_of_block_size, current_center_y_position - half_of_block_size)
        bottom_right = (current_center_x_position + half_of_block_size, current_center_y_position + half_of_block_size)
        bottom_left = (current_center_x_position - half_of_block_size, current_center_y_position + half_of_block_size)
        return [current_center_x_position, current_center_y_position, top_left, top_right, bottom_right, bottom_left]

    def __calculate_hit_box(self, start_x: int, start_y: int, end_x: int, end_y: int) -> list[(int, int)]:
        block_size = WorldInfo.get_block_size()
        top_left = (start_x * block_size, start_y * block_size)
        top_right = (end_x * block_size + block_size, start_y * block_size)
        bottom_left = (start_x * block_size, end_y * block_size + block_size)
        bottom_right = (end_x * block_size + block_size, end_y * block_size + block_size)
        center = (top_right[0] - top_left[0]) / 2 + top_left[0], (bottom_left[1] - top_left[1]) / 2 + top_left[1]
        width = top_right[0] - top_left[0]
        height = bottom_left[1] - top_left[1]
        return [center, top_left, top_right, bottom_right, bottom_left, (width, height)]

    def __create_wall_hit_box(self, start_x: int, start_y: int, end_x: int, end_y: int, entities_with_collision: list[Entity]):
        center, top_left, top_right, bottom_right, bottom_left, size = self.__calculate_hit_box(start_x, start_y, end_x, end_y)
        is_player, is_character, is_bullet, is_wall, is_enemy = False, False, False, True, False
        wall_hit_box = Entity()
        wall_hit_box.add_component(TypeComponent(is_player, is_character, is_bullet, is_wall, is_enemy))
        wall_hit_box.add_component(PositionComponent(center[0], center[1]))
        wall_hit_box.add_component(CollisionComponent())
        wall_hit_box.add_component(HitBoxComponent(top_left, top_right, bottom_left, bottom_right))
        entities_with_collision.append(wall_hit_box)

    def __process_walls(self, x: int, y: int, world_map: list[list[int]], entities_with_collision: list[Entity], background_entities: list[Entity]):
        start_x, start_y = x, y
        if world_map[y][x+1] == 1:
            while world_map[y][x] not in [0, 2] and world_map[y][x] == 1:
                center_x, center_y, top_left, top_right, bottom_right, bottom_left = self.__calculate_coordinates(x, y)
                entity_image_path = 'textures/background/wall.png'
                wall = Entity()
                wall.add_component(PositionComponent(center_x, center_y))
                wall.add_component(BackgroundImageComponent(entity_image_path))
                wall.add_component(HitBoxComponent(top_left, top_right, bottom_left, bottom_right))
                background_entities.append(wall)
                world_map[y][x] = 0
                x += 1
            self.__create_wall_hit_box(start_x, start_y, x-1, y, entities_with_collision)
        elif world_map[y+1][x] == 1:
            while world_map[y][x] not in [0, 2] and world_map[y][x] == 1:
                center_x, center_y, top_left, top_right, bottom_right, bottom_left = self.__calculate_coordinates(x, y)
                entity_image_path = 'textures/background/wall.png'
                wall = Entity()
                wall.add_component(PositionComponent(center_x, center_y))
                wall.add_component(BackgroundImageComponent(entity_image_path))
                wall.add_component(HitBoxComponent(top_left, top_right, bottom_left, bottom_right))
                background_entities.append(wall)
                world_map[y][x] = 0
                y += 1
            self.__create_wall_hit_box(start_x, start_y, x, y-1, entities_with_collision)
        else:
            center_x, center_y, top_left, top_right, bottom_right, bottom_left = self.__calculate_coordinates(x, y)
            entity_image_path = 'textures/background/wall.png'
            wall = Entity()
            wall.add_component(PositionComponent(center_x, center_y))
            wall.add_component(BackgroundImageComponent(entity_image_path))
            wall.add_component(HitBoxComponent(top_left, top_right, bottom_left, bottom_right))
            background_entities.append(wall)
            world_map[y][x] = 0
            y += 1
            self.__create_wall_hit_box(start_x, start_y, x, y, entities_with_collision)

    def __process_world_map(self, world_map: list[list[int]], entities_with_collision: list[Entity], background_entities: list[Entity], is_hub: bool = False):
        world_map_height = len(world_map)
        world_map_width = len(world_map[0])
        for y in range(world_map_height):
            for x in range(world_map_width):
                if world_map[y][x] == 2:
                    center_x, center_y, top_left, top_right, bottom_right, bottom_left = self.__calculate_coordinates(x, y)
                    if is_hub:
                        entity_image_path = 'textures/background/hub_floor.png'
                    else:
                        entity_image_path = 'textures/background/dungeon_floor.png'
                    floor = Entity()
                    floor.add_component(PositionComponent(center_x, center_y))
                    floor.add_component(BackgroundImageComponent(entity_image_path))
                    floor.add_component(HitBoxComponent(top_left, top_right, bottom_left, bottom_right))
                    background_entities.append(floor)
                elif world_map[y][x] == 1:
                    self.__process_walls(x, y, world_map, entities_with_collision, background_entities)

    def __find_room_centers(self, rooms: list[Room]):
        if not self.__is_separated:
            rooms.append(self.__room)
        else:
            self.__first_part.__find_room_centers(rooms)
            self.__second_part.__find_room_centers(rooms)

    def __create_hub_room_on_map(self, hub_map: list[list[int]]):
        hub_height = len(hub_map)
        hub_width = len(hub_map[0])
        for h in range(2, hub_height-2):
            for w in range(2, hub_width-2):
                hub_map[h][w] = 2

    def create_dungeon(self, entities_with_collision: list[Entity], background_entities: list[Entity], world_map: list[list[int]], minimal_room_size: int, rooms: list[Room]):
        self.__separate(minimal_room_size)
        self.__create_rooms(world_map)
        self.__create_corridors(world_map)
        self.__create_walls(world_map)
        self.__process_world_map(world_map, entities_with_collision, background_entities)
        self.__find_room_centers(rooms)

    def create_hub(self, entities_with_collision: list[Entity], background_entities: list[Entity], hub_map: list[list[int]]):
        self.__create_hub_room_on_map(hub_map)
        self.__create_walls(hub_map)
        self.__process_world_map(hub_map, entities_with_collision, background_entities, True)
