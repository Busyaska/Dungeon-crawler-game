import pygame


class Weapon:

    def __init__(self, damage: int, right_img_path: str, left_img_path: str, magazine_size: int, bullet_speed: int,
                 bullet_image_path: str, bullet_size: (int, int), reload_duration: int, gauss_accuracy: float,
                 multiple_bullet_condition: bool):
        self.__damage = damage
        self.__image_R: pygame.image = pygame.image.load(right_img_path).convert_alpha()
        self.__image_L: pygame.image = pygame.image.load(left_img_path).convert_alpha()
        self.__weapon_muzzle_x_coord: float = self.__image_R.get_width()
        self.__weapon_muzzle_y_coord: float = self.__image_R.get_height() / 2
        self.__image_width: int = self.__image_R.get_width()
        self.__image_height: int = self.__image_R.get_height()
        self.__angle: float = 0.0
        self.__magazine_size: int = magazine_size
        self.__current_magazine_size: int = magazine_size
        self.__is_able_to_fire: bool = True
        self.__bullet_speed: int = bullet_speed
        self.__bullet_image_path: str = bullet_image_path
        self.__bullet_size = bullet_size
        self.__reload_duration: int = reload_duration
        self.__gauss_accuracy: float = gauss_accuracy
        self.__is_reloading: bool = False
        self.__multiple_bullet_condition: bool = multiple_bullet_condition

    def get_damage(self) -> int:
        return self.__damage

    def get_image_width(self) -> int:
        return self.__image_width

    def get_image_height(self) -> int:
        return self.__image_height

    def get_image(self, left: bool, right: bool) -> pygame.image:
        if right:
            return pygame.transform.rotate(self.__image_R, -self.__angle)
        elif left:
            return pygame.transform.rotate(self.__image_L, -self.__angle - 180)

    def get_weapon_muzzle_coord(self) -> (float, float):
        return self.__weapon_muzzle_x_coord, self.__weapon_muzzle_y_coord

    def set_weapon_muzzle_coord(self, x_coord: float, y_coord: float):
        self.__weapon_muzzle_x_coord = x_coord
        self.__weapon_muzzle_y_coord = y_coord

    def update_weapon_muzzle_coord(self, delta_x: float, delta_y: float):
        self.__weapon_muzzle_x_coord += delta_x
        self.__weapon_muzzle_y_coord += delta_y

    def get_angle(self) -> float:
        return self.__angle

    def set_angle(self, angel: float):
        self.__angle = angel

    def reload(self):
        self.__current_magazine_size = self.__magazine_size

    def get_fire_condition(self) -> bool:
        return self.__is_able_to_fire

    def switch_fire_condition(self, condition: bool):
        self.__is_able_to_fire = condition

    def get_current_magazine_size(self) -> int:
        return self.__current_magazine_size

    def get_magazine_size(self) -> int:
        return self.__magazine_size

    def reduce_current_magazine_size(self):
        self.__current_magazine_size -= 1

    def get_bullet_speed(self) -> int:
        return self.__bullet_speed

    def get_bullet_image_path(self) -> str:
        return self.__bullet_image_path

    def get_bullet_size(self) -> (int, int):
        return self.__bullet_size

    def get_reload_duration(self) -> int:
        return self.__reload_duration

    def get_gauss_accuracy(self) -> float:
        return self.__gauss_accuracy

    def get_reload_condition(self) -> bool:
        return self.__is_reloading

    def switch_reload_condition(self):
        self.__is_reloading = not self.__is_reloading

    def get_multiple_bullet_condition(self) -> bool:
        return self.__multiple_bullet_condition


class Handgun(Weapon):

    def __init__(self):
        damage = 35
        right_image_path = 'textures/weapons/handgun_R.png'
        left_image_path = 'textures/weapons/handgun_L.png'
        magazine_size = 12
        bullet_speed = 700
        bullet_image_path = 'textures/weapons/handgun_bullet.png'
        bullet_size = (22, 11)
        reload_duration = 1000
        gauss_accuracy = 2
        multiple_bullet_condition = False
        super().__init__(damage, right_image_path, left_image_path, magazine_size, bullet_speed, bullet_image_path,
                         bullet_size, reload_duration, gauss_accuracy, multiple_bullet_condition)


class Rifle(Weapon):

    def __init__(self):
        damage = 80
        right_image_path = 'textures/weapons/rifle_R.png'
        left_image_path = 'textures/weapons/rifle_L.png'
        magazine_size = 7
        bullet_speed = 1200
        bullet_image_path = 'textures/weapons/rifle_bullet.png'
        bullet_size = (35, 8)
        reload_duration = 2000
        gauss_accuracy = 0.7
        multiple_bullet_condition = False
        super().__init__(damage, right_image_path, left_image_path, magazine_size, bullet_speed, bullet_image_path,
                         bullet_size, reload_duration, gauss_accuracy, multiple_bullet_condition)


class Shotgun(Weapon):

    def __init__(self):
        damage = 30
        right_image_path = 'textures/weapons/shotgun_R.png'
        left_image_path = 'textures/weapons/shotgun_L.png'
        magazine_size = 5
        bullet_speed = 800
        bullet_image_path = 'textures/weapons/shotgun_bullet.png'
        bullet_size = (25, 25)
        reload_duration = 1300
        gauss_accuracy = 1
        multiple_bullet_condition = True
        super().__init__(damage, right_image_path, left_image_path, magazine_size, bullet_speed, bullet_image_path,
                         bullet_size, reload_duration, gauss_accuracy, multiple_bullet_condition)
