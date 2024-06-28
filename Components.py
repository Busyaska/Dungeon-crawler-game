import pygame
import os
import re
from abc import ABC
from Actions import Action
from Weapons import Handgun, Shotgun, Rifle


class Component(ABC):
    pass


class TypeComponent(Component):

    def __init__(self, is_player: bool, is_character: bool, is_bullet: bool, is_wall: bool, is_enemy: bool, is_interactive_object: bool = False):
        self.__is_player = is_player
        self.__is_character = is_character
        self.__is_bullet = is_bullet
        self.__is_wall = is_wall
        self.__is_enemy = is_enemy
        self.__is_interactive_object = is_interactive_object

    def check_interactive_condition(self):
        return self.__is_interactive_object

    def get_type(self) -> (bool, bool, bool):
        return self.__is_character, self.__is_bullet, self.__is_wall

    def get_character_type(self) -> (bool, bool):
        return self.__is_player, self.__is_enemy


class MovingDistanceComponent(Component):

    def __init__(self, distance: int):
        self.__moving_distance = distance

    def get_moving_distance(self) -> int:
        return self.__moving_distance


class PositionComponent(Component):

    def __init__(self, x_coordinate: float, y_coordinate: float):
        self.__x_position = x_coordinate
        self.__y_position = y_coordinate

    def get_position(self) -> (float, float):
        return self.__x_position, self.__y_position

    def update_position(self, delta_x: float, delta_y: float):
        self.__x_position += delta_x
        self.__y_position += delta_y


class HealthComponent(Component):

    def __init__(self, health: int):
        self.__health = health
        self.__max_health = health
        self.__is_alive = True

    def get_health(self) -> int:
        return self.__health

    def get_max_health(self) -> int:
        return self.__max_health

    def update_health(self, delta_health: int):
        self.__health -= delta_health
        if self.__health <= 0:
            self.__is_alive = False

    def get_living_condition(self) -> bool:
        return self.__is_alive

    def upgrade_max_health(self):
        self.__max_health += 100
        self.__health = self.__max_health

    def resurrect(self):
        self.__health = self.__max_health
        self.__is_alive = True


class DamageComponent(Component):

    def __init__(self, damage: int):
        self.__damage = damage

    def get_damage(self) -> int:
        return self.__damage


class AnimationComponent(Component):

    def __init__(self, right_moving_folder_path: str, left_moving_folder_path: str):
        self.__is_move_right = True
        self.__is_animating = False
        self.__frame_duration = 0.100
        self.__time_accumulator = 0.0
        self.__moving_right = []
        self.__moving_left = []
        self.__current_image_index = 0

        self.__load_images(self.__moving_right, right_moving_folder_path)
        self.__load_images(self.__moving_left, left_moving_folder_path)
        self.__image_height = self.__moving_right[0].get_height()
        self.__image_width = self.__moving_right[0].get_width()

    def __load_images(self, lst: list, path: str):
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith('.png'):
                image = pygame.image.load(file_path).convert_alpha()
                lst.append(image)

    def increase_image_index(self):
        current_image_index = self.__current_image_index
        new_image_index = (current_image_index + 1) % len(self.__moving_left)
        self.__current_image_index = new_image_index

    def get_image_width(self) -> int:
        return self.__image_width

    def get_image_height(self) -> int:
        return self.__image_height

    def get_frame_duration(self) -> float:
        return self.__frame_duration

    def get_time_accumulator(self) -> float:
        return self.__time_accumulator

    def set_time_accumulator(self, time: float):
        self.__time_accumulator = time

    def switch_moving_direction(self):
        self.__is_move_right = not self.__is_move_right
        self.__is_move_left = not self.__is_move_left

    def get_moving_direction(self) -> (bool, bool):
        return self.__is_move_left, self.__is_move_right

    def activate_animation(self):
        self.__is_animating = True

    def deactivate_animation(self):
        self.__is_animating = False

    def get_image(self, left: bool, right: bool) -> pygame.image:
        if not self.__is_animating:
            image_number = 0
        else:
            image_number = self.__current_image_index
        if right:
            image = self.__moving_right[image_number]
        elif left:
            image = self.__moving_left[image_number]
        return image


class BulletImageComponent(Component):

    def __init__(self, bullet_image_path: str, angel: float):
        self.__image = pygame.transform.rotate(pygame.image.load(bullet_image_path).convert_alpha(), angel)

    def get_image(self) -> pygame.image:
        return self.__image


class BulletDirectionComponent(Component):

    def __init__(self, x_coord: float, y_coord: float):
        self.__x_direction = x_coord
        self.__y_direction = y_coord

    def get_direction(self) -> (float, float):
        return self.__x_direction, self.__y_direction


class SightComponent(Component):

    def __init__(self):
        self.__right = True
        self.__left = False

    def get_sights(self) -> (bool, bool):
        return self.__left, self.__right

    def switch_sight(self):
        self.__right = not self.__right
        self.__left = not self.__left


class WeaponComponent(Component):

    def __init__(self, weapons_list: list[bool]):
        self.__handgun, self.__riffle, self.__shotgun = weapons_list
        if self.__handgun:
            self.__weapon = Handgun()
        elif self.__riffle:
            self.__weapon = Rifle()
        elif self.__shotgun:
            self.__weapon = Shotgun()

    def get_damage(self) -> int:
        return self.__weapon.get_damage()

    def get_image_width(self) -> int:
        return self.__weapon.get_image_width()

    def get_image_height(self) -> int:
        return self.__weapon.get_image_height()

    def get_image(self, left: bool, right: bool) -> pygame.image:
        return self.__weapon.get_image(left, right)

    def get_weapon_muzzle_coord(self) -> (float, float):
        return self.__weapon.get_weapon_muzzle_coord()

    def set_weapon_muzzle_coord(self, x_coord: float, y_coord: float):
        self.__weapon.set_weapon_muzzle_coord(x_coord, y_coord)

    def update_weapon_muzzle_coord(self, delta_x: float, delta_y: float):
        self.__weapon.update_weapon_muzzle_coord(delta_x, delta_y)

    def get_angle(self) -> float:
        return self.__weapon.get_angle()

    def set_angle(self, angel: float):
        self.__weapon.set_angle(angel)

    def reload(self):
        self.__weapon.reload()

    def get_fire_condition(self) -> bool:
        return self.__weapon.get_fire_condition()

    def set_fire_condition(self, condition: bool):
        self.__weapon.switch_fire_condition(condition)

    def get_current_magazine_size(self) -> int:
        return self.__weapon.get_current_magazine_size()

    def get_magazine_size(self) -> int:
        return self.__weapon.get_magazine_size()

    def reduce_current_magazine_size(self):
        self.__weapon.reduce_current_magazine_size()

    def get_bullet_speed(self) -> int:
        return self.__weapon.get_bullet_speed()

    def get_bullet_image_path(self) -> str:
        return self.__weapon.get_bullet_image_path()

    def get_bullet_size(self) -> (int, int):
        return self.__weapon.get_bullet_size()

    def get_reload_duration(self) -> int:
        return self.__weapon.get_reload_duration()

    def get_gauss_accuracy(self) -> float:
        return self.__weapon.get_gauss_accuracy()

    def get_reload_condition(self) -> bool:
        return self.__weapon.get_reload_condition()

    def switch_reload_condition(self):
        self.__weapon.switch_reload_condition()

    def get_multiple_bullet_condition(self) -> bool:
        return self.__weapon.get_multiple_bullet_condition()

    def set_handgun_active(self):
        self.__handgun = True
        self.__riffle = False
        self.__shotgun = False
        self.__weapon = Handgun()

    def set_riffle_active(self):
        self.__riffle = True
        self.__handgun = False
        self.__shotgun = False
        self.__weapon = Rifle()

    def set_shotgun_active(self):
        self.__shotgun = True
        self.__handgun = False
        self.__riffle = False
        self.__weapon = Shotgun()

    def get_current_weapon(self) -> (bool, bool, bool):
        return self.__handgun, self.__riffle, self.__shotgun


class HitBoxComponent(Component):

    def __init__(self, top_left: [float, float], top_right: [float, float], bottom_left: [float, float], bottom_right: [float, float], is_rotated: bool = False):
        self.__top_left = top_left
        self.__top_right = top_right
        self.__bottom_left = bottom_left
        self.__bottom_right = bottom_right
        self.__is_rotated = is_rotated

    def get_rotation_condition(self) -> bool:
        return self.__is_rotated

    def get_hit_box(self) -> list[(float, float)]:
        return [self.__top_left, self.__top_right, self.__bottom_right, self.__bottom_left]

    def get_top_left(self) -> (float, float):
        return self.__top_left

    def update_coordinates(self, delta_x: float, delta_y: float):
        self.__top_right[0] += delta_x
        self.__top_right[1] += delta_y
        self.__top_left[0] += delta_x
        self.__top_left[1] += delta_y
        self.__bottom_right[0] += delta_x
        self.__bottom_right[1] += delta_y
        self.__bottom_left[0] += delta_x
        self.__bottom_left[1] += delta_y


class ActiveHandComponent(Component):

    def __init__(self, left_hand: list[int, int], right_hand: list[int, int]):
        self.__right_active_hand_coord = right_hand
        self.__left_active_hand_coord = left_hand

    def get_hand_coordinate(self, left: bool, right: bool) -> [float, float]:
        if right:
            return self.__right_active_hand_coord
        elif left:
            return self.__left_active_hand_coord

    def update_coordinates(self, delta_x: float, delta_y: float):
        self.__right_active_hand_coord[0] += delta_x
        self.__right_active_hand_coord[1] += delta_y
        self.__left_active_hand_coord[0] += delta_x
        self.__left_active_hand_coord[1] += delta_y


class CollisionComponent(Component):

    def __init__(self):
        self.__is_collided = False

    def get_collision_condition(self) -> bool:
        return self.__is_collided

    def switch_collision_condition(self):
        self.__is_collided = not self.__is_collided


class BulletStatusComponent(Component):

    def __init__(self):
        self.__is_exists = True

    def get_bullet_status(self) -> bool:
        return self.__is_exists

    def switch_bullet_status(self):
        self.__is_exists = not self.__is_exists


class BackgroundImageComponent(Component):

    def __init__(self, path: str):
        self.__image = pygame.image.load(path).convert_alpha()

    def get_image(self) -> pygame.image:
        return self.__image


class EnemyConditionComponent(Component):

    def __init__(self, patrol_points: list[(int, int)], is_melee: bool):
        self.__is_angry = False
        self.__patrol_points = patrol_points
        self.__current_point = 0
        self.__is_melee = is_melee
        if is_melee:
            self.__anger_range = 450
            self.__alert_range = 150
        else:
            self.__anger_range = 400
            self.__alert_range = 300

    def get_status(self) -> bool:
        return self.__is_angry

    def set_anger(self):
        self.__is_angry = True

    def get_patrol_point(self) -> (int, int):
        return self.__patrol_points[self.__current_point]

    def switch_to_next_point(self):
        current_point = self.__current_point
        next_point = (current_point + 1) % len(self.__patrol_points)
        self.__current_point = next_point

    def get_anger_range(self) -> int:
        return self.__anger_range

    def get_alert_range(self) -> int:
        return self.__alert_range

    def get_melee_condition(self) -> bool:
        return self.__is_melee


class OwnDamageComponent(Component):

    def __init__(self):
        self.__owm_damage = 25
        self.__is_exploded = False

    def get_own_damage(self) -> int:
        return self.__owm_damage

    def get_explosion_condition(self) -> bool:
        return self.__is_exploded

    def switch_explosion_condition(self):
        self.__is_exploded = not self.__is_exploded


class BelongingComponent(Component):

    def __init__(self, belong_to_player: bool, belong_to_enemy: bool):
        self.__belong_to_player = belong_to_player
        self.__belong_to_enemy = belong_to_enemy

    def get_belonging(self) -> (bool, bool):
        return self.__belong_to_player, self.__belong_to_enemy


class EnemyActionQueueComponent(Component):

    def __init__(self):
        self.__queue_in = []
        self.__queue_out = []

    def insert_action(self, action: Action):
        self.__queue_in.append(action)

    def get_current_action(self) -> Action | None:
        if not self.__queue_out:
            if not self.__queue_in:
                return None
            while self.__queue_in:
                action = self.__queue_in.pop()
                self.__queue_out.append(action)
        current_action = self.__queue_out[-1]
        return current_action

    def remove_current_action(self):
        if self.__queue_out:
            self.__queue_out.pop()


class MenuEntityTypeComponent(Component):

    def __init__(self, is_background: bool, is_button: bool):
        self.__is_background = is_background
        self.__is_button = is_button

    def get_type(self) -> (bool, bool):
        return self.__is_background, self.__is_button


class SingleImageComponent(Component):

    def __init__(self, path: str, size: (int, int) = None):
        if not size:
            self.__image = pygame.image.load(path).convert_alpha()
        else:
            self.__image = pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)

    def get_image(self) -> pygame.image:
        return self.__image


class SingeAnimationComponent(Component):

    def __init__(self, path: str, needed_size: (int, int) = None):
        self.__images = []
        self.__animation_duration = 0.030
        self.__time_accumulator = 0.0
        self.__image_index = 0
        self.__load_images(path, needed_size)

    def __load_images(self, path: str, needed_size: (int, int)):

        def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]

        image_files = [file for file in os.listdir(path) if file.endswith('.png')]
        image_files.sort(key=natural_sort_key)
        for image_path in image_files:
            final_path = f'{path}/{image_path}'
            if needed_size:
                image = pygame.transform.scale(pygame.image.load(final_path).convert_alpha(), needed_size)
            else:
                image = pygame.image.load(final_path).convert_alpha()
            self.__images.append(image)

    def get_image(self) -> pygame.image:
        return self.__images[self.__image_index]

    def get_animation_duration(self) -> float:
        return self.__animation_duration

    def get_time_accumulator(self) -> float:
        return self.__time_accumulator

    def increase_image_index(self):
        self.__image_index = (self.__image_index + 1) % len(self.__images)

    def set_time_accumulator(self, time):
        self.__time_accumulator = time


class ActionComponent(Component):

    def __init__(self, actions: list, is_ready: bool = True):
        self.__actions = actions
        self.__is_ready = is_ready

    def get_action_readiness(self) -> bool:
        return self.__is_ready

    def set_action_readiness(self, value: bool):
        self.__is_ready = value

    def action(self):
        for action in self.__actions:
            action()


class AnimationConditionComponent(Component):

    def __init__(self, has_animation: bool):
        self.__has_animation = has_animation

    def get_animation_condition(self):
        return self.__has_animation


class MoneyCollectionComponent(Component):

    def __init__(self, money: int = 0):
        self.__amount_of_money = money

    def get_amount_of_money(self) -> int:
        return self.__amount_of_money

    def set_amount_of_money(self, money: int):
        self.__amount_of_money = money


class ExistenceConditionComponent(Component):

    def __init__(self, disappear_after_interation: bool = False):
        self.__disappear_after_interation = disappear_after_interation

    def get_existence_condition(self) -> bool:
        return self.__disappear_after_interation

