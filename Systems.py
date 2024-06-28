import pygame
import sys
import json
from math import degrees, atan2, sin, cos, radians, sqrt
from random import gauss, randint, choice
from abc import ABC
from Components import (BulletImageComponent, PositionComponent, MovingDistanceComponent, BulletDirectionComponent,
                        AnimationComponent, WeaponComponent, HitBoxComponent, TypeComponent, DamageComponent,
                        ActiveHandComponent, CollisionComponent, HealthComponent, SightComponent, OwnDamageComponent,
                        BulletStatusComponent, BackgroundImageComponent, EnemyConditionComponent, BelongingComponent,
                        EnemyActionQueueComponent, MenuEntityTypeComponent, ActionComponent, SingleImageComponent,
                        SingeAnimationComponent, AnimationConditionComponent, MoneyCollectionComponent,
                        ExistenceConditionComponent)
from Entities import Entity
from QuadTree import QuadTree, Rectangle, Point
from DungeonGeneration import BinaryTree
from WorldInfo import WorldInfo
from Actions import WaitAction, MoveAction, ShootAction


class IconsCoordinates:
    __HEALTH_X_COORDINATE = 10
    __HEALTH_Y_COORDINATE = 10
    __COIN_X_COORDINATE = 1200
    __COIN_Y_COORDINATE = 10
    __RELOAD_X_COORDINATE = 10
    __RELOAD_Y_COORDINATE = 676
    __ENEMY_X_COORDINATE = 1200
    __ENEMY_Y_COORDINATE = 676
    __FREE_SPACE_SIZE = 5

    @staticmethod
    def get_health_icon_coordinates() -> (int, int, int):
        return IconsCoordinates.__HEALTH_X_COORDINATE, IconsCoordinates.__HEALTH_Y_COORDINATE, IconsCoordinates.__FREE_SPACE_SIZE

    @staticmethod
    def get_enemy_icon_coordinates() -> (int, int, int):
        return IconsCoordinates.__ENEMY_X_COORDINATE, IconsCoordinates.__ENEMY_Y_COORDINATE, IconsCoordinates.__FREE_SPACE_SIZE

    @staticmethod
    def get_reload_icon_coordinates() -> (int, int, int):
        return IconsCoordinates.__RELOAD_X_COORDINATE, IconsCoordinates.__RELOAD_Y_COORDINATE, IconsCoordinates.__FREE_SPACE_SIZE

    @staticmethod
    def get_coin_icon_coordinates() -> (int, int):
        return IconsCoordinates.__COIN_X_COORDINATE, IconsCoordinates.__COIN_Y_COORDINATE, IconsCoordinates.__FREE_SPACE_SIZE


class CameraOffsetCalculation:

    @staticmethod
    def calculate_camera_offset(player: Entity) -> (float, float):
        position_component = player.get_component(PositionComponent)
        player_x, player_y = position_component.get_position()
        display_width, display_height = RenderSystem.get_display_size()
        half_width = display_width // 2
        half_height = display_height // 2
        camera_offset_x = player_x - half_width
        camera_offset_y = player_y - half_height
        return camera_offset_x, camera_offset_y


class System(ABC):
    pass


class UpgradeSystem(System):

    def __init__(self):
        self.__upgrade_cost = 200
        self.__player = None

    def save_player(self, player: Entity):
        self.__player = player

    def upgrade_health(self):
        health_component = self.__player.get_component(HealthComponent)
        money_collection_component = self.__player.get_component(MoneyCollectionComponent)
        amount_of_money = money_collection_component.get_amount_of_money()
        if amount_of_money - self.__upgrade_cost >= 0:
            health_component.upgrade_max_health()
            money_collection_component.set_amount_of_money(amount_of_money - self.__upgrade_cost)


class SavingSystem(System):

    def __init__(self):
        self.__player = None

    def save_player(self, player: Entity):
        self.__player = player

    def save_data(self):
        health_component = self.__player.get_component(HealthComponent)
        weapon_component = self.__player.get_component(WeaponComponent)
        money_collection_component = self.__player.get_component(MoneyCollectionComponent)
        max_health = health_component.get_max_health()
        handgun_is_active, riffle_is_active, shotgun_is_active = weapon_component.get_current_weapon()
        amount_of_money = money_collection_component.get_amount_of_money()
        data = {
            'health' : max_health,
            'current_weapon' : [handgun_is_active, riffle_is_active, shotgun_is_active],
            'amount_of_money' : amount_of_money
        }
        with open('save/game_data.json', 'w') as file:
            json.dump(data, file, indent=4)

    def load_data(self) -> (int, list[bool], int):
        with open('save/game_data.json', 'r') as file:
            data = json.load(file)
        health = data['health']
        current_weapon = data['current_weapon']
        amount_of_money = data['amount_of_money']
        return health, current_weapon, amount_of_money


class MenuSystem(System):

    def __init__(self, menu_entities: list[Entity], new_game_button_actions: list, load_game_button_actions: list, main_menu_button_actions: list, upgrade_health_button_action: list, save_action):
        self.__is_active = True
        self.__is_main_menu_active = True
        self.__menu_entities = menu_entities
        self.__new_game_button_actions = new_game_button_actions
        self.__load_game_button_actions = load_game_button_actions
        self.__main_menu_button_actions = main_menu_button_actions
        self.__upgrade_health_button_action = upgrade_health_button_action
        self.__save_action = save_action
        self.__player = None

    def save_player(self, player: Entity):
        self.__player = player

    def __clear_menu_entities(self):
        self.__menu_entities.clear()

    def create_main_menu(self):
        self.set_menu_condition(True)
        self.set_main_menu_condition(True)
        self.__clear_menu_entities()

        background_top_left = (0, 0)
        background_top_right = (1280, 0)
        background_bottom_right = (1280, 720)
        background_bottom_left = (0, 720)
        background_animation = 'textures/menu/menu_background'
        background_size = (1280, 720)
        background_is_background, background_is_button = True, False
        background_has_animation = True
        background = Entity()
        background.add_component(HitBoxComponent(background_top_left, background_top_right, background_bottom_left, background_bottom_right))
        background.add_component(MenuEntityTypeComponent(background_is_background, background_is_button))
        background.add_component(SingeAnimationComponent(background_animation, background_size))
        background.add_component(AnimationConditionComponent(background_has_animation))

        new_game_button_top_left = (512, 175)
        new_game_button_top_right = (768, 175)
        new_game_button_bottom_right = (768, 265)
        new_game_button_bottom_left = (512, 265)
        new_game_button_image = 'textures/menu/buttons/new_game_button.png'
        button_is_background, button_is_button = False, True
        new_game_button = Entity()
        new_game_button.add_component(HitBoxComponent(new_game_button_top_left, new_game_button_top_right, new_game_button_bottom_left, new_game_button_bottom_right))
        new_game_button.add_component(SingleImageComponent(new_game_button_image))
        new_game_button.add_component(MenuEntityTypeComponent(button_is_background, button_is_button))
        new_game_button.add_component(ActionComponent(self.__new_game_button_actions))

        load_game_button_top_left = (512, 315)
        load_game_button_top_right = (768, 315)
        load_game_button_bottom_right = (768, 405)
        load_game_button_bottom_left = (512, 405)
        load_game_button_image = 'textures/menu/buttons/load_game_button.png'
        button_is_background, button_is_button = False, True
        load_game_button = Entity()
        load_game_button.add_component(HitBoxComponent(load_game_button_top_left, load_game_button_top_right,
                                                      load_game_button_bottom_left, load_game_button_bottom_right))
        load_game_button.add_component(SingleImageComponent(load_game_button_image))
        load_game_button.add_component(MenuEntityTypeComponent(button_is_background, button_is_button))
        load_game_button.add_component(ActionComponent(self.__load_game_button_actions))

        exit_button_top_left = (512, 455)
        exit_button_top_right = (768, 455)
        exit_button_bottom_right = (768, 545)
        exit_button_bottom_left = (512, 545)
        exit_button_image = 'textures/menu/buttons/exit_button.png'
        button_is_background, button_is_button = False, True
        exit_button = Entity()
        exit_button.add_component(HitBoxComponent(exit_button_top_left, exit_button_top_right, exit_button_bottom_left, exit_button_bottom_right))
        exit_button.add_component(SingleImageComponent(exit_button_image))
        exit_button.add_component(MenuEntityTypeComponent(button_is_background, button_is_button))
        exit_button.add_component(ActionComponent([self.__exit]))

        self.__menu_entities.append(background)
        self.__menu_entities.append(load_game_button)
        self.__menu_entities.append(new_game_button)
        self.__menu_entities.append(exit_button)

    def create_in_game_menu(self):
        resume_button_top_left = (512, 175)
        resume_button_top_right = (768, 175)
        resume_button_bottom_right = (768, 265)
        resume_button_bottom_left = (512, 265)
        resume_button_image = 'textures/menu/buttons/resume_button.png'
        button_is_background, button_is_button = False, True
        resume_button = Entity()
        resume_button.add_component(HitBoxComponent(resume_button_top_left, resume_button_top_right,
                                                    resume_button_bottom_left, resume_button_bottom_right))
        resume_button.add_component(SingleImageComponent(resume_button_image))
        resume_button.add_component(MenuEntityTypeComponent(button_is_background, button_is_button))
        resume_button.add_component(ActionComponent([self.resume_game]))

        main_menu_button_top_left = (512, 315)
        main_menu_button_top_right = (768, 315)
        main_menu_button_bottom_right = (768, 405)
        main_menu_button_bottom_left = (512, 405)
        main_menu_button_image = 'textures/menu/buttons/main_menu_button.png'
        button_is_background, button_is_button = False, True
        main_menu_button_actions = self.__main_menu_button_actions
        main_menu_button_actions.append(self.create_main_menu)
        main_menu_button_actions.append(self.__save_action)
        main_menu_button = Entity()
        main_menu_button.add_component(HitBoxComponent(main_menu_button_top_left, main_menu_button_top_right,
                                                       main_menu_button_bottom_left, main_menu_button_bottom_right))
        main_menu_button.add_component(SingleImageComponent(main_menu_button_image))
        main_menu_button.add_component(MenuEntityTypeComponent(button_is_background, button_is_button))
        main_menu_button.add_component(ActionComponent(main_menu_button_actions))

        exit_button_top_left = (512, 455)
        exit_button_top_right = (768, 455)
        exit_button_bottom_right = (768, 545)
        exit_button_bottom_left = (512, 545)
        exit_button_image = 'textures/menu/buttons/exit_button.png'
        button_is_background, button_is_button = False, True
        actions = [self.__exit, self.__save_action]
        exit_button = Entity()
        exit_button.add_component(HitBoxComponent(exit_button_top_left, exit_button_top_right, exit_button_bottom_left, exit_button_bottom_right))
        exit_button.add_component(SingleImageComponent(exit_button_image))
        exit_button.add_component(MenuEntityTypeComponent(button_is_background, button_is_button))
        exit_button.add_component(ActionComponent(actions))

        self.__menu_entities.append(resume_button)
        self.__menu_entities.append(main_menu_button)
        self.__menu_entities.append(exit_button)

    def __process_weapon_component(self):

        def create_active_button(handgun_is_active: bool, riffle_is_active: bool, shotgun_is_active: bool):
            if handgun_is_active:
                min_y_coord, max_y_coord = 230, 280
            elif riffle_is_active:
                min_y_coord, max_y_coord = 390, 440
            else:
                min_y_coord, max_y_coord = 530, 580
            active_button_top_left = (1100, min_y_coord)
            active_button_top_right = (1150, min_y_coord)
            active_button_bottom_right = (1150, max_y_coord)
            active_button_bottom_left = (1100, max_y_coord)
            active_button_image = 'textures/menu/buttons/full_cell.png'
            active_button_is_background, active_button_is_button = True, False
            active_button_has_animation = False
            active_button = Entity()
            active_button.add_component(HitBoxComponent(active_button_top_left, active_button_top_right,
                                                            active_button_bottom_left, active_button_bottom_right))
            active_button.add_component(SingleImageComponent(active_button_image))
            active_button.add_component(MenuEntityTypeComponent(active_button_is_background, active_button_is_button))
            active_button.add_component(AnimationConditionComponent(active_button_has_animation))
            self.__menu_entities.append(active_button)

        def create_inactive_handgun_button(weapon_component):
            handgun_inactive_button_top_left = (1100, 230)
            handgun_inactive_button_top_right = (1150, 230)
            handgun_inactive_button_bottom_right = (1150, 280)
            handgun_inactive_button_bottom_left = (1100, 280)
            handgun_inactive_button_image = 'textures/menu/buttons/empty_cell.png'
            handgun_inactive_button_is_background, handgun_inactive_button_is_button = False, True
            handgun_inactive_button_has_animation = False
            handgun_inactive_button = Entity()
            handgun_inactive_button.add_component(HitBoxComponent(handgun_inactive_button_top_left, handgun_inactive_button_top_right,
                                                        handgun_inactive_button_bottom_left, handgun_inactive_button_bottom_right))
            handgun_inactive_button.add_component(SingleImageComponent(handgun_inactive_button_image))
            handgun_inactive_button.add_component(MenuEntityTypeComponent(handgun_inactive_button_is_background, handgun_inactive_button_is_button))
            handgun_inactive_button.add_component(AnimationConditionComponent(handgun_inactive_button_has_animation))
            handgun_inactive_button.add_component(ActionComponent([weapon_component.set_handgun_active, self.create_upgrade_menu]))
            self.__menu_entities.append(handgun_inactive_button)

        def create_inactive_riffle_button(weapon_component):
            riffle_inactive_button_top_left = (1100, 390)
            riffle_inactive_button_top_right = (1150, 390)
            riffle_inactive_button_bottom_right = (1150, 440)
            riffle_inactive_button_bottom_left = (1100, 440)
            riffle_inactive_button_image = 'textures/menu/buttons/empty_cell.png'
            riffle_inactive_button_is_background, riffle_inactive_button_is_button = False, True
            riffle_inactive_button_has_animation = False
            riffle_inactive_button = Entity()
            riffle_inactive_button.add_component(HitBoxComponent(riffle_inactive_button_top_left, riffle_inactive_button_top_right,
                                                        riffle_inactive_button_bottom_left, riffle_inactive_button_bottom_right))
            riffle_inactive_button.add_component(SingleImageComponent(riffle_inactive_button_image))
            riffle_inactive_button.add_component(MenuEntityTypeComponent(riffle_inactive_button_is_background, riffle_inactive_button_is_button))
            riffle_inactive_button.add_component(AnimationConditionComponent(riffle_inactive_button_has_animation))
            riffle_inactive_button.add_component(ActionComponent([weapon_component.set_riffle_active, self.create_upgrade_menu]))
            self.__menu_entities.append(riffle_inactive_button)

        def create_inactive_shotgun_button(weapon_component):
            shotgun_inactive_button_top_left = (1100, 530)
            shotgun_inactive_button_top_right = (1150, 530)
            shotgun_inactive_button_bottom_right = (1150, 580)
            shotgun_inactive_button_bottom_left = (1100, 580)
            shotgun_inactive_button_image = 'textures/menu/buttons/empty_cell.png'
            shotgun_inactive_button_is_background, shotgun_inactive_button_is_button = False, True
            shotgun_inactive_button_has_animation = False
            shotgun_inactive_button = Entity()
            shotgun_inactive_button.add_component(HitBoxComponent(shotgun_inactive_button_top_left, shotgun_inactive_button_top_right,
                                                        shotgun_inactive_button_bottom_left, shotgun_inactive_button_bottom_right))
            shotgun_inactive_button.add_component(SingleImageComponent(shotgun_inactive_button_image))
            shotgun_inactive_button.add_component(MenuEntityTypeComponent(shotgun_inactive_button_is_background, shotgun_inactive_button_is_button))
            shotgun_inactive_button.add_component(AnimationConditionComponent(shotgun_inactive_button_has_animation))
            shotgun_inactive_button.add_component(ActionComponent([weapon_component.set_shotgun_active, self.create_upgrade_menu]))
            self.__menu_entities.append(shotgun_inactive_button)

        weapon_component = self.__player.get_component(WeaponComponent)
        handgun_is_active, riffle_is_active, shotgun_is_active = weapon_component.get_current_weapon()
        if handgun_is_active:
            create_active_button(handgun_is_active, riffle_is_active, shotgun_is_active)
        else:
            create_inactive_handgun_button(weapon_component)
        if riffle_is_active:
            create_active_button(handgun_is_active, riffle_is_active, shotgun_is_active)
        else:
            create_inactive_riffle_button(weapon_component)
        if shotgun_is_active:
            create_active_button(handgun_is_active, riffle_is_active, shotgun_is_active)
        else:
            create_inactive_shotgun_button(weapon_component)

    def __close_update_menu(self):
        self.set_menu_condition(False)
        self.set_main_menu_condition(False)
        self.__clear_menu_entities()
        self.create_in_game_menu()
        self.__save_action()

    def create_upgrade_menu(self):
        self.set_menu_condition(True)
        self.set_main_menu_condition(True)
        self.__clear_menu_entities()

        background_size = (1280, 720)
        background_top_left = (0, 0)
        background_top_right = (0, 1280)
        background_bottom_right = (1280, 720)
        background_bottom_left = (0, 720)
        background_image = 'textures/menu/upgrade_menu_background.png'
        background_is_background, background_is_button = True, False
        background_has_animation = False

        background = Entity()
        background.add_component(HitBoxComponent(background_top_left, background_top_right,
                                                 background_bottom_left, background_bottom_right))
        background.add_component(SingleImageComponent(background_image, background_size))
        background.add_component(MenuEntityTypeComponent(background_is_background, background_is_button))
        background.add_component(AnimationConditionComponent(background_has_animation))

        background_health_size = (96, 84)
        background_health_top_left = (100, 80)
        background_health_top_right = (196, 80)
        background_health_bottom_right = (196, 164)
        background_health_bottom_left = (100, 164)
        background_health_image = 'textures/interface/heart.png'
        background_health_is_background, background_health_is_button = True, False
        background_health_has_animation = False

        background_health = Entity()
        background_health.add_component(HitBoxComponent(background_health_top_left, background_health_top_right,
                                                        background_health_bottom_left, background_health_bottom_right))
        background_health.add_component(SingleImageComponent(background_health_image, background_health_size))
        background_health.add_component(MenuEntityTypeComponent(background_health_is_background, background_health_is_button))
        background_health.add_component(AnimationConditionComponent(background_health_has_animation))

        background_handgun_size = (99, 63)
        background_handgun_top_left = (100, 230)
        background_handgun_top_right = (199, 230)
        background_handgun_bottom_right = (199, 296)
        background_handgun_bottom_left = (100, 296)
        background_handgun_image = 'textures/weapons/handgun_R.png'
        background_handgun_is_background, background_handgun_is_button = True, False
        background_handgun_has_animation = False

        background_handgun = Entity()
        background_handgun.add_component(HitBoxComponent(background_handgun_top_left, background_handgun_top_right,
                                                         background_handgun_bottom_left, background_handgun_bottom_right))
        background_handgun.add_component(SingleImageComponent(background_handgun_image, background_handgun_size))
        background_handgun.add_component(MenuEntityTypeComponent(background_handgun_is_background, background_handgun_is_button))
        background_handgun.add_component(AnimationConditionComponent(background_handgun_has_animation))

        background_riffle_size = (195, 57)
        background_riffle_top_left = (100, 400)
        background_riffle_top_right = (295, 400)
        background_riffle_bottom_right = (295, 457)
        background_riffle_bottom_left = (100, 457)
        background_riffle_image = 'textures/weapons/rifle_R.png'
        background_riffle_is_background, background_riffle_is_button = True, False
        background_riffle_has_animation = False

        background_riffle = Entity()
        background_riffle.add_component(HitBoxComponent(background_riffle_top_left, background_riffle_top_right,
                                                        background_riffle_bottom_left, background_riffle_bottom_right))
        background_riffle.add_component(SingleImageComponent(background_riffle_image, background_riffle_size))
        background_riffle.add_component(MenuEntityTypeComponent(background_riffle_is_background, background_riffle_is_button))
        background_riffle.add_component(AnimationConditionComponent(background_riffle_has_animation))

        background_shotgun_size = (165, 63)
        background_shotgun_top_left = (100, 530)
        background_shotgun_top_right = (265, 530)
        background_shotgun_bottom_right = (265, 593)
        background_shotgun_bottom_left = (100, 593)
        background_shotgun_image = 'textures/weapons/shotgun_R.png'
        background_shotgun_is_background, background_shotgun_is_button = True, False
        background_shotgun_has_animation = False

        background_shotgun = Entity()
        background_shotgun.add_component(HitBoxComponent(background_shotgun_top_left, background_shotgun_top_right,
                                                        background_shotgun_bottom_left, background_shotgun_bottom_right))
        background_shotgun.add_component(SingleImageComponent(background_shotgun_image, background_shotgun_size))
        background_shotgun.add_component(MenuEntityTypeComponent(background_shotgun_is_background, background_shotgun_is_button))
        background_shotgun.add_component(AnimationConditionComponent(background_shotgun_has_animation))

        close_button_image = 'textures/menu/buttons/close_button.png'
        close_button_size = (50, 50)
        close_button_top_left = (1200, 30)
        close_button_top_right = (1250, 30)
        close_button_button_right = (1250, 80)
        close_button_button_left = (1200, 80)
        close_button_is_background, close_button_is_button = False, True

        close_button = Entity()
        close_button.add_component(HitBoxComponent(close_button_top_left, close_button_top_right, close_button_button_left, close_button_button_right))
        close_button.add_component(SingleImageComponent(close_button_image, close_button_size))
        close_button.add_component(MenuEntityTypeComponent(close_button_is_background, close_button_is_button))
        close_button.add_component(ActionComponent([self.__close_update_menu]))

        health_upgrade_button_top_left = (1050, 100)
        health_upgrade_button_top_right = (1200, 100)
        health_upgrade_button_bottom_right = (1200, 200)
        health_upgrade_button_bottom_left = (1050, 200)
        health_upgrade_button_image = 'textures/menu/buttons/health_upgrade.png'
        health_upgrade_button_is_background, health_upgrade_button_is_button = False, True
        health_upgrade_button_has_animation = False
        health_upgrade_button = Entity()
        health_upgrade_button.add_component(HitBoxComponent(health_upgrade_button_top_left, health_upgrade_button_top_right,
                                                    health_upgrade_button_bottom_left, health_upgrade_button_bottom_right))
        health_upgrade_button.add_component(SingleImageComponent(health_upgrade_button_image))
        health_upgrade_button.add_component(MenuEntityTypeComponent(health_upgrade_button_is_background, health_upgrade_button_is_button))
        health_upgrade_button.add_component(AnimationConditionComponent(health_upgrade_button_has_animation))
        health_upgrade_button.add_component(ActionComponent(self.__upgrade_health_button_action))

        self.__menu_entities.append(background)
        self.__menu_entities.append(background_health)
        self.__menu_entities.append(background_handgun)
        self.__menu_entities.append(background_riffle)
        self.__menu_entities.append(background_shotgun)
        self.__menu_entities.append(close_button)
        self.__menu_entities.append(health_upgrade_button)

        self.__process_weapon_component()

    def __exit(self):
        pygame.quit()
        sys.exit()

    def resume_game(self):
        self.set_menu_condition(False)

    def is_menu_active(self) -> bool:
        return self.__is_active

    def is_main_menu_active(self) -> bool:
        return self.__is_main_menu_active

    def set_menu_condition(self, condition: bool):
        self.__is_active = condition

    def set_main_menu_condition(self, condition: bool):
        self.__is_main_menu_active = condition

    def __check_collision(self, mouse_pos, hit_box_component) -> bool:
        top_left, top_right, bottom_right, bottom_left = hit_box_component.get_hit_box()
        mouse_x, mouse_y = mouse_pos
        if top_left[0] <= mouse_x <= top_right[0] and top_left[1] <= mouse_y <= bottom_left[1]:
            return True
        return False

    def check_buttons(self):
        for entity in self.__menu_entities:
            entity_type_component = entity.get_component(MenuEntityTypeComponent)
            entity_is_background, entity_is_button = entity_type_component.get_type()
            if entity_is_button:
                mouse_position = pygame.mouse.get_pos()
                hit_box_component = entity.get_component(HitBoxComponent)
                if self.__check_collision(mouse_position, hit_box_component):
                    button_action_component = entity.get_component(ActionComponent)
                    button_action_component.action()


class RenderSystem(System):
    __DISPLAY_WIDTH = 1280
    __DISPLAY_HEIGHT = 720

    def __init__(self, main_entities: list[Entity], background_entities: list[Entity], enemies: list[Entity], menu_entities: list[Entity]):
        pygame.init()
        self.__display = pygame.display.set_mode((RenderSystem.__DISPLAY_WIDTH, RenderSystem.__DISPLAY_HEIGHT))
        self.__bullet_icon = pygame.image.load('textures/interface/interface_bullet.png').convert_alpha()
        self.__reload_icon = pygame.image.load('textures/interface/reload_icon.png').convert_alpha()
        self.__health_icon = pygame.image.load('textures/interface/heart.png').convert_alpha()
        self.__enemy_icon = pygame.image.load('textures/interface/enemy_icon.png').convert_alpha()
        self.__coin_icon = pygame.image.load('textures/interface/coin_icon.png').convert_alpha()
        self.__loading_icon = pygame.image.load('textures/interface/loading_icon.png').convert_alpha()
        self.__crosshair_image = pygame.image.load('textures/interface/crosshair.png').convert_alpha()
        self.__rotation_angle: int = 30
        self.__cursor_image = pygame.transform.rotate(pygame.image.load('textures/interface/cursor.png').convert_alpha(), self.__rotation_angle)
        self.__reload_icon_rotation_number = 0
        self.__reload_icon_rotation_duration = 0.150
        self.__reload_icon_rotation_accumulator = 0
        self.__main_entities = main_entities
        self.__background_entities = background_entities
        self.__enemies = enemies
        self.__menu_entities = menu_entities

        self.__camera_top_left = pygame.math.Vector2(0, 0)
        self.__camera_top_right = pygame.math.Vector2(1280, 0)
        self.__camera_bottom_right = pygame.math.Vector2(1280, 720)
        self.__camera_bottom_left = pygame.math.Vector2(0, 720)

    @staticmethod
    def get_display_size() -> (int, int):
        return RenderSystem.__DISPLAY_WIDTH, RenderSystem.__DISPLAY_HEIGHT

    def draw_loading_screen(self):
        display_width, display_height = RenderSystem.get_display_size()
        self.__display.fill('black')
        loading_icon = self.__loading_icon
        loading_icon_rect = loading_icon.get_rect(center=(display_width//2, display_height//2))
        self.__display.blit(loading_icon, loading_icon_rect)
        pygame.display.flip()

    def create_dungeon_render(self):
        capacity = WorldInfo.get_render_capacity()
        world_size = WorldInfo.get_world_size()
        boundary = Rectangle(0, 0, world_size, world_size)
        self.__quadtree = QuadTree(boundary, capacity)

    def create_hub_render(self):
        capacity = WorldInfo.get_render_capacity()
        hub_width = WorldInfo.get_hub_width()
        hub_height = WorldInfo.get_hub_height()
        boundary = Rectangle(0, 0, hub_width, hub_height)
        self.__quadtree = QuadTree(boundary, capacity)

    def __render_reload_icon(self, player: Entity, font: pygame.font, color: (int, int, int), scaled_time: float):
        x, y, extra_space = IconsCoordinates.get_reload_icon_coordinates()
        weapon_component = player.get_component(WeaponComponent)
        reload_condition = weapon_component.get_reload_condition()
        magazine_size = weapon_component.get_magazine_size()
        current_magazine_size = weapon_component.get_current_magazine_size()
        text = font.render(f'{current_magazine_size}/{magazine_size}', True, color)
        text_rect = text.get_rect(topleft=(x, y))
        text_rect_width = text_rect.width
        bullet_icon_rect = self.__bullet_icon.get_rect(topleft=(x + text_rect_width + extra_space, y))
        bullet_icon_rect_width = bullet_icon_rect.width
        self.__display.blit(text, text_rect)
        self.__display.blit(self.__bullet_icon, bullet_icon_rect)
        if reload_condition:
            self.__reload_icon_rotation_accumulator += scaled_time
            if self.__reload_icon_rotation_accumulator >= self.__reload_icon_rotation_duration:
                self.__reload_icon_rotation_accumulator -= self.__reload_icon_rotation_duration
                self.__reload_icon_rotation_number += 1
            reload_image = pygame.transform.rotate(self.__reload_icon, self.__rotation_angle * self.__reload_icon_rotation_number)
            reload_image_center = (x + text_rect_width + extra_space + bullet_icon_rect_width + extra_space + self.__reload_icon.get_width() / 2,
                                    y + self.__reload_icon.get_height() / 2)
            self.__display.blit(reload_image, reload_image.get_rect(center=reload_image_center))

    def __render_health_icon(self, player: Entity, font: pygame.font, color: (int, int, int)):
        x, y, extra_space = IconsCoordinates.get_health_icon_coordinates()
        health_component = player.get_component(HealthComponent)
        player_health = health_component.get_health()
        text = font.render(f'{player_health}', True, color)
        text_rect = text.get_rect(topleft=(x, y))
        text_rect_width = text_rect.width
        health_icon_rect = self.__health_icon.get_rect(topleft=(x + text_rect_width + extra_space, y))
        self.__display.blit(text, text_rect)
        self.__display.blit(self.__health_icon, health_icon_rect)

    def __render_enemy_icon(self, font: pygame.font, color: (int, int, int)):
        enemy_number = len(self.__enemies)
        if enemy_number != 0:
            x, y, extra_space = IconsCoordinates.get_enemy_icon_coordinates()
            text = font.render(f'{enemy_number}', True, color)
            text_rect = text.get_rect(topleft=(x, y))
            text_rect_width = text_rect.width
            enemy_icon_rect = self.__enemy_icon.get_rect(topleft=(x + text_rect_width + extra_space, y))
            self.__display.blit(text, text_rect)
            self.__display.blit(self.__enemy_icon, enemy_icon_rect)

    def __render_coin_icon(self, player: Entity, font: pygame.font, color: (int, int, int)):
        money_collection_component = player.get_component(MoneyCollectionComponent)
        amount_of_money = money_collection_component.get_amount_of_money()
        x, y, extra_space = IconsCoordinates.get_coin_icon_coordinates()
        text = font.render(f'{amount_of_money}', True, color)
        text_rect = text.get_rect(topleft=(x, y))
        text_rect_width = text_rect.width
        coin_icon_rect = self.__coin_icon.get_rect(topleft=(x + text_rect_width + extra_space, y))
        self.__display.blit(text, text_rect)
        self.__display.blit(self.__coin_icon, coin_icon_rect)

    def __render_interface(self, player: Entity, scaled_time: float):
        white_colour = (255, 255, 255)
        font_name = 'calibri'
        font_size = 34
        font = pygame.font.SysFont(font_name, font_size)
        self.__render_reload_icon(player, font, white_colour, scaled_time)
        self.__render_health_icon(player, font, white_colour)
        self.__render_enemy_icon(font, white_colour)
        self.__render_coin_icon(player, font, white_colour)

    def insert_background_entities(self):
        for entity in self.__background_entities:
            position_component = entity.get_component(PositionComponent)
            hit_box_component = entity.get_component(HitBoxComponent)
            entity_x, entity_y = position_component.get_position()
            boundary = hit_box_component.get_hit_box()
            entity_is_rotated = hit_box_component.get_rotation_condition()
            point = Point(entity_x, entity_y, entity, boundary, entity_is_rotated)
            self.__quadtree.insert(point)

    def __render_background(self, camera_offset: (float, float)):
        current_top_left = self.__camera_top_left + camera_offset
        current_top_right = self.__camera_top_right + camera_offset
        current_bottom_right = self.__camera_bottom_right + camera_offset
        current_bottom_left = self.__camera_bottom_left + camera_offset
        collided_entities = self.__quadtree.get_entities([current_top_left, current_top_right, current_bottom_right, current_bottom_left])
        for entity in collided_entities:
            hit_box_component = entity.get_component(HitBoxComponent)
            background_image_component = entity.get_component(BackgroundImageComponent)
            entity_position = hit_box_component.get_top_left()
            current_position = pygame.math.Vector2(entity_position) - pygame.math.Vector2(camera_offset)
            image = background_image_component.get_image()
            self.__display.blit(image, current_position)

    def __render_weapon(self, camera_offset: (float, float), left_sight: bool, right_sight: bool, weapon_component: WeaponComponent, active_hand_component: ActiveHandComponent):
        weapon_image = weapon_component.get_image(left_sight, right_sight)
        weapon_angle = weapon_component.get_angle()
        hand_x_coord, hand_y_coord = active_hand_component.get_hand_coordinate(left_sight, right_sight)
        weapon_rect = weapon_image.get_rect()
        weapon_rect.center = (pygame.Vector2(hand_x_coord, hand_y_coord)+ pygame.Vector2(weapon_rect.width / 2, 0).rotate(weapon_angle))
        current_position = pygame.math.Vector2(weapon_rect.topleft) - pygame.math.Vector2(camera_offset)
        self.__display.blit(weapon_image, current_position)

    def __render_entities(self, camera_offset: (float, float), scaled_time: float):
        for entity in self.__main_entities:
            type_component = entity.get_component(TypeComponent)
            hit_box_component = entity.get_component(HitBoxComponent)
            entity_is_character, entity_is_bullet, entity_is_wall = type_component.get_type()
            entity_is_interactive_object = type_component.check_interactive_condition()
            entity_position = hit_box_component.get_top_left()
            current_entity_position = pygame.math.Vector2(entity_position) - pygame.math.Vector2(camera_offset)
            if entity_is_character:
                animation_component = entity.get_component(AnimationComponent)
                weapon_component = entity.get_component(WeaponComponent)
                sight_component = entity.get_component(SightComponent)
                left_sight, right_sight = sight_component.get_sights()
                if weapon_component:
                    active_hand_component = entity.get_component(ActiveHandComponent)
                    self.__render_weapon(camera_offset, left_sight, right_sight, weapon_component, active_hand_component)
                frame_duration = animation_component.get_frame_duration()
                time_accumulator = animation_component.get_time_accumulator()
                current_time = time_accumulator + scaled_time
                animation_component.set_time_accumulator(current_time)
                if current_time >= frame_duration:
                    animation_component.increase_image_index()
                    animation_component.set_time_accumulator(current_time - frame_duration)
                image = animation_component.get_image(left_sight, right_sight)
            elif entity_is_interactive_object:
                animation_condition_component = entity.get_component(AnimationConditionComponent)
                entity_has_animation = animation_condition_component.get_animation_condition()
                if entity_has_animation:
                    animation_component = entity.get_component(SingeAnimationComponent)
                    animation_duration = animation_component.get_animation_duration()
                    time_accumulator = animation_component.get_time_accumulator()
                    current_time = time_accumulator + scaled_time
                    animation_component.set_time_accumulator(current_time)
                    if current_time >= animation_duration:
                        animation_component.increase_image_index()
                        animation_component.set_time_accumulator(current_time - animation_duration)
                    image = animation_component.get_image()
                else:
                    image_component = entity.get_component(SingleImageComponent)
                    image = image_component.get_image()
            elif entity_is_bullet:
                bullet_image_component = entity.get_component(BulletImageComponent)
                image = bullet_image_component.get_image()
            self.__display.blit(image, current_entity_position)


    def render_menu(self, scaled_time: float):
        silver_color = (192, 192, 192)
        self.__display.fill(silver_color)
        for entity in self.__menu_entities:
            entity_hit_box_component = entity.get_component(HitBoxComponent)
            entity_type_component = entity.get_component(MenuEntityTypeComponent)
            top_left = entity_hit_box_component.get_top_left()
            entity_is_background, entity_is_button = entity_type_component.get_type()
            if entity_is_background:
                animation_condition_component = entity.get_component(AnimationConditionComponent)
                entity_has_animation = animation_condition_component.get_animation_condition()
                if entity_has_animation:
                    animation_component = entity.get_component(SingeAnimationComponent)
                    animation_duration = animation_component.get_animation_duration()
                    time_accumulator = animation_component.get_time_accumulator()
                    current_time = time_accumulator + scaled_time
                    animation_component.set_time_accumulator(current_time)
                    if current_time >= animation_duration:
                        animation_component.increase_image_index()
                        animation_component.set_time_accumulator(current_time - animation_duration)
                    image = animation_component.get_image()
                else:
                    image_component = entity.get_component(SingleImageComponent)
                    image = image_component.get_image()
            else:
                image_component = entity.get_component(SingleImageComponent)
                image = image_component.get_image()
            self.__display.blit(image, top_left)
        self.__display.blit(self.__cursor_image, self.__cursor_image.get_rect(center=pygame.mouse.get_pos()))
        pygame.display.flip()

    def render_game_world(self, player: Entity, scaled_time: float):
        camera_offset = CameraOffsetCalculation.calculate_camera_offset(player)
        self.__display.fill('black')
        self.__render_background(camera_offset)
        self.__render_entities(camera_offset, scaled_time)
        self.__render_interface(player, scaled_time)
        self.__display.blit(self.__crosshair_image, self.__crosshair_image.get_rect(center = pygame.mouse.get_pos()))
        pygame.display.flip()


class InputSystem(System):

    @staticmethod
    def __process_keyboard_input(animation_component: AnimationComponent, position_component: PositionComponent, hit_box_component: HitBoxComponent, moving_distance_component: MovingDistanceComponent, active_hand_component: ActiveHandComponent, scaled_time: float):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_d] or keys[pygame.K_a]:
            animation_component.activate_animation()
            moving_distance = moving_distance_component.get_moving_distance()
            delta_x, delta_y = 0, 0
            if keys[pygame.K_w]:
                delta_y -= moving_distance * scaled_time
            if keys[pygame.K_s]:
                delta_y += moving_distance * scaled_time
            if keys[pygame.K_d]:
                delta_x += moving_distance * scaled_time
            if keys[pygame.K_a]:
                delta_x -= moving_distance * scaled_time
            position_component.update_position(delta_x, delta_y)
            hit_box_component.update_coordinates(delta_x, delta_y)
            active_hand_component.update_coordinates(delta_x, delta_y)
        else:
            animation_component.deactivate_animation()

    @staticmethod
    def __process_sight(sight_component: SightComponent, position_component: PositionComponent, target_x_coord: float):
        left_sight, right_sight = sight_component.get_sights()
        entity_x_coord = position_component.get_position()[0]
        if target_x_coord >= entity_x_coord and not right_sight:
            sight_component.switch_sight()
        elif target_x_coord < entity_x_coord and not left_sight:
            sight_component.switch_sight()

    @staticmethod
    def __find_angle(entity_hand_x_coord: int, entity_hand_y_coord : int, target_x_coord: int, target_y_coord: int) -> float:
        delta_y = target_y_coord - entity_hand_y_coord
        delta_x = target_x_coord - entity_hand_x_coord
        angle = degrees(atan2(delta_y, delta_x))
        return angle

    @staticmethod
    def __process_angle(sight_component: SightComponent, active_hand_component: ActiveHandComponent, weapon_component: WeaponComponent, target_x_coord: int, target_y_coord: int, target_entity_condition: bool, enemy_is_angry: bool = False):
        left_sight, right_sight = sight_component.get_sights()
        hand_x_coord, hand_y_coord = active_hand_component.get_hand_coordinate(left_sight, right_sight)
        weapon_image_width = weapon_component.get_image_width()
        weapon_image_height = weapon_component.get_image_height()
        if not target_entity_condition:
            angle = InputSystem.__find_angle(hand_x_coord, hand_y_coord, target_x_coord, target_y_coord)
        else:
            if enemy_is_angry:
                angle = InputSystem.__find_angle(hand_x_coord, hand_y_coord, target_x_coord, target_y_coord)
            else:
                if left_sight:
                    angle = 180
                else:
                    angle = 0
        if right_sight:
            muzzle_offset = pygame.Vector2(weapon_image_width, -weapon_image_height / 2)
        else:
            muzzle_offset = pygame.Vector2(weapon_image_width, weapon_image_height / 2)
        rotated_muzzle_offset = muzzle_offset.rotate(angle)
        muzzle_position = pygame.Vector2(hand_x_coord, hand_y_coord) + rotated_muzzle_offset
        weapon_component.set_angle(angle)
        weapon_component.set_weapon_muzzle_coord(muzzle_position.x, muzzle_position.y)

    @staticmethod
    def __process_mouse_input(camera_offset: (float, float), sight_component: SightComponent, active_hand_component: ActiveHandComponent, weapon_component: WeaponComponent, position_component: PositionComponent, enemy_is_melee: bool, enemy_is_angry: bool, target_entity: Entity = None):
        if not target_entity:
            mouse_pos = pygame.mouse.get_pos()
            current_mouse_pos = pygame.math.Vector2(mouse_pos) + pygame.math.Vector2(camera_offset)
            target_x_coord, target_y_coord = current_mouse_pos
            target_entity_condition = False
        else:
            target_entity_position_component = target_entity.get_component(PositionComponent)
            target_x_coord, target_y_coord = target_entity_position_component.get_position()
            target_entity_condition = True
        InputSystem.__process_sight(sight_component, position_component, target_x_coord)
        if not enemy_is_melee:
            InputSystem.__process_angle(sight_component, active_hand_component, weapon_component, target_x_coord, target_y_coord, target_entity_condition, enemy_is_angry)

    @staticmethod
    def process_input(entity: Entity, scaled_time: float, target_entity: Entity = None):
        if not target_entity:
            camera_offset = CameraOffsetCalculation.calculate_camera_offset(entity)
            animation_component = entity.get_component(AnimationComponent)
            sight_component = entity.get_component(SightComponent)
            position_component = entity.get_component(PositionComponent)
            moving_distance_component = entity.get_component(MovingDistanceComponent)
            weapon_component = entity.get_component(WeaponComponent)
            hit_box_component = entity.get_component(HitBoxComponent)
            active_hand_component = entity.get_component(ActiveHandComponent)
            enemy_is_melee = False
            enemy_is_angry = False
        else:
            camera_offset = (0, 0)
            sight_component = entity.get_component(SightComponent)
            position_component = entity.get_component(PositionComponent)
            moving_distance_component = entity.get_component(MovingDistanceComponent)
            weapon_component = entity.get_component(WeaponComponent)
            hit_box_component = entity.get_component(HitBoxComponent)
            active_hand_component = entity.get_component(ActiveHandComponent)
            enemy_condition_component = entity.get_component(EnemyConditionComponent)
            enemy_is_melee = enemy_condition_component.get_melee_condition()
            enemy_is_angry = enemy_condition_component.get_status()
        if not target_entity:
            InputSystem.__process_keyboard_input(animation_component, position_component, hit_box_component, moving_distance_component, active_hand_component, scaled_time)
        InputSystem.__process_mouse_input(camera_offset, sight_component, active_hand_component, weapon_component, position_component, enemy_is_melee, enemy_is_angry, target_entity)


class BulletSystem(System):

    def __init__(self, list_of_bullets: list[Entity], main_entities: list[Entity], entities_with_collision: list[Entity]):
        self.__bullets = list_of_bullets
        self.__main_entities = main_entities
        self.__entities_with_collision = entities_with_collision

    @staticmethod
    def __get_rotated_rect_vertices(mid_left: (float, float), bullet_size: (int, int), angle: float) -> list[[float, float]]:

        def rotate_point(point: (float, float), center_x: float, center_y: float, angle: float) -> list[float, float]:
            point_x, point_y = point
            sinus = sin(angle)
            cosine = cos(angle)
            point_x -= center_x
            point_y -= center_y
            new_x = point_x * cosine - point_y * sinus
            new_y = point_x * sinus + point_y * cosine
            point_x = new_x + center_x
            point_y = new_y + center_y
            return [point_x, point_y]

        mid_left_x, mid_left_y = mid_left
        bullet_width, bullet_height = bullet_size
        center_x, center_y = mid_left_x - bullet_width / 2, mid_left_y
        top_left = [mid_left_x, mid_left_y - bullet_height / 2]
        top_right = [mid_left_x + bullet_width, mid_left_y - bullet_height / 2]
        bottom_left = [mid_left_x, mid_left_y + bullet_height / 2]
        bottom_right = [mid_left_x + bullet_width, mid_left_y + bullet_height / 2]
        rotated_top_left = rotate_point(top_left, center_x, center_y, angle)
        rotated_top_right = rotate_point(top_right, center_x, center_y, angle)
        rotated_bottom_left = rotate_point(bottom_left, center_x, center_y, angle)
        rotated_bottom_right = rotate_point(bottom_right, center_x, center_y, angle)
        center = [center_x, center_y]

        return [rotated_top_left, rotated_top_right, rotated_bottom_left, rotated_bottom_right, center]

    @staticmethod
    def __process_coordinates(camera_offset: (float, float), muzzle_x_coord: int, muzzle_y_coord: int, weapon_accuracy: int, multiple_bullet_condition: bool, bullet_size: (int, int), target_entity: Entity = None) -> list[(float, float, float)]:
        bullets = []
        if not target_entity:
            mouse_position = pygame.mouse.get_pos()
            current_mouse_position = pygame.math.Vector2(mouse_position) + pygame.math.Vector2(camera_offset)
            target_x_coord, target_y_coord = current_mouse_position
        else:
            target_entity_position_component = target_entity.get_component(PositionComponent)
            target_x_coord, target_y_coord = target_entity_position_component.get_position()
        delta_x = target_x_coord - muzzle_x_coord
        delta_y = target_y_coord - muzzle_y_coord
        angle = atan2(delta_y, delta_x)
        spread_angle = radians(gauss(0, weapon_accuracy))
        if multiple_bullet_condition:
            extra_angle = radians(5)
            first_bullet_final_angle = angle + spread_angle
            second_bullet_final_angle = angle + spread_angle + extra_angle
            third_bullet_final_angle = angle + spread_angle - extra_angle
            first_bullet_final_angle_degrees = degrees(first_bullet_final_angle)
            second_bullet_final_angle_degrees = degrees(second_bullet_final_angle)
            third_bullet_final_angle_degrees = degrees(third_bullet_final_angle)
            first_bullet_x_direction, first_bullet_y_direction = cos(first_bullet_final_angle), sin(first_bullet_final_angle)
            second_bullet_x_direction, second_bullet_y_direction = cos(second_bullet_final_angle), sin(second_bullet_final_angle)
            third_bullet_x_direction, third_bullet_y_direction = cos(third_bullet_final_angle), sin(third_bullet_final_angle)
            first_bullet_points = BulletSystem.__get_rotated_rect_vertices((muzzle_x_coord, muzzle_y_coord), bullet_size, first_bullet_final_angle)
            second_bullet_points = BulletSystem.__get_rotated_rect_vertices((muzzle_x_coord, muzzle_y_coord), bullet_size, second_bullet_final_angle)
            third_bullet_points = BulletSystem.__get_rotated_rect_vertices((muzzle_x_coord, muzzle_y_coord), bullet_size, third_bullet_final_angle)
            bullets.append((first_bullet_final_angle_degrees, first_bullet_x_direction, first_bullet_y_direction, first_bullet_points))
            bullets.append((second_bullet_final_angle_degrees, second_bullet_x_direction, second_bullet_y_direction, second_bullet_points))
            bullets.append((third_bullet_final_angle_degrees, third_bullet_x_direction, third_bullet_y_direction, third_bullet_points))
        else:
            final_angle = angle + spread_angle
            final_angle_degrees = degrees(final_angle)
            x_direction = cos(final_angle)
            y_direction = sin(final_angle)
            points = BulletSystem.__get_rotated_rect_vertices((muzzle_x_coord, muzzle_y_coord), bullet_size, final_angle)
            bullets.append((final_angle_degrees, x_direction, y_direction, points))
        return bullets

    @staticmethod
    def create_bullet(entity: Entity, new_bullets: list[Entity], target_entity: Entity = None) -> list[Entity]:
        type_component = entity.get_component(TypeComponent)
        entity_is_player, entity_is_enemy = type_component.get_character_type()
        if not target_entity:
            camera_offset = CameraOffsetCalculation.calculate_camera_offset(entity)
        else:
            camera_offset = (0, 0)
        weapon_component = entity.get_component(WeaponComponent)
        fire_condition = weapon_component.get_fire_condition()
        if fire_condition:
            damage = weapon_component.get_damage()
            multiple_bullet_condition = weapon_component.get_multiple_bullet_condition()
            weapon_muzzle_x_coord, weapon_muzzle_y_coord = weapon_component.get_weapon_muzzle_coord()
            weapon_accuracy = weapon_component.get_gauss_accuracy()
            bullet_image_path = weapon_component.get_bullet_image_path()
            bullet_speed = weapon_component.get_bullet_speed()
            bullet_size = weapon_component.get_bullet_size()
            bullets = BulletSystem.__process_coordinates(camera_offset, weapon_muzzle_x_coord, weapon_muzzle_y_coord, weapon_accuracy, multiple_bullet_condition, bullet_size, target_entity)
            for bullet_info in bullets:
                angle, x_direction, y_direction, points = bullet_info
                top_left, top_right, bottom_left, bottom_right, center = points
                is_player, is_character, is_bullet, is_wall, is_enemy = False, False, True, False, False
                if entity_is_player:
                    belong_to_player, belong_to_enemy = True, False
                else:
                    belong_to_player, belong_to_enemy = False, True
                is_rotated = True
                bullet = Entity()
                bullet.add_component(TypeComponent(is_player, is_character, is_bullet, is_wall, is_enemy))
                bullet.add_component(DamageComponent(damage))
                bullet.add_component(PositionComponent(center[0], center[1]))
                bullet.add_component(MovingDistanceComponent(bullet_speed))
                bullet.add_component(BulletImageComponent(bullet_image_path, -angle))
                bullet.add_component(BulletDirectionComponent(x_direction, y_direction))
                bullet.add_component(HitBoxComponent(top_left, top_right, bottom_left, bottom_right, is_rotated))
                bullet.add_component(CollisionComponent())
                bullet.add_component(BulletStatusComponent())
                bullet.add_component(BelongingComponent(belong_to_player, belong_to_enemy))
                new_bullets.append(bullet)

    def insert_bullets(self, new_bullets: list[Entity]):
        for bullet in new_bullets:
            self.__bullets.append(bullet)
            self.__main_entities.append(bullet)
            self.__entities_with_collision.append(bullet)

    def update_bullet(self, scaled_time: float):
        for bullet in self.__bullets:
            position_component = bullet.get_component(PositionComponent)
            hit_box_component = bullet.get_component(HitBoxComponent)
            moving_distance_component = bullet.get_component(MovingDistanceComponent)
            direction_component = bullet.get_component(BulletDirectionComponent)
            x_direction, y_direction = direction_component.get_direction()
            distance = moving_distance_component.get_moving_distance()
            delta_x = x_direction * distance * scaled_time
            delta_y = y_direction * distance * scaled_time
            position_component.update_position(delta_x, delta_y)
            hit_box_component.update_coordinates(delta_x, delta_y)


class WeaponSystem(System):

    def __init__(self):
        self.__player_weapon_component = None
        self.__reload_start_time = 0

    def save_weapon_component(self, player: Entity):
        self.__player_weapon_component = player.get_component(WeaponComponent)

    def reload(self):
        reload_condition = self.__player_weapon_component.get_reload_condition()
        magazine_size = self.__player_weapon_component.get_magazine_size()
        current_magazine_size = self.__player_weapon_component.get_current_magazine_size()
        if current_magazine_size < magazine_size and not reload_condition:
            self.__player_weapon_component.switch_reload_condition()
            self.__player_weapon_component.set_fire_condition(False)
            self.__reload_start_time = pygame.time.get_ticks()

    def shoot(self):
        fire_condition = self.__player_weapon_component.get_fire_condition()
        if fire_condition:
            current_magazine_size = self.__player_weapon_component.get_current_magazine_size()
            if current_magazine_size >= 1:
                self.__player_weapon_component.reduce_current_magazine_size()
            else:
                self.__player_weapon_component.set_fire_condition(False)

    def update(self):
        reload_condition = self.__player_weapon_component.get_reload_condition()
        if reload_condition:
            weapon_reload_duration = self.__player_weapon_component.get_reload_duration()
            current_time = pygame.time.get_ticks()
            if current_time - self.__reload_start_time >= weapon_reload_duration:
                self.__player_weapon_component.reload()
                self.__player_weapon_component.set_fire_condition(True)
                self.__player_weapon_component.switch_reload_condition()


class CollisionSystem(System):

    def __init__(self, entities_with_collision: list[Entity]):
        self.__entities_with_collision = entities_with_collision
        self.__player = None

    def save_player(self, player: Entity):
        self.__player = player

    def create_dungeon_collision(self):
        start_x, start_y = 0, 0
        world_size = WorldInfo.get_world_size()
        self.__boundary = Rectangle(start_x, start_y, world_size, world_size)

    def create_hub_collision(self):
        start_x, start_y = 0, 0
        hub_width = WorldInfo.get_hub_width()
        hub_height = WorldInfo.get_hub_height()
        self.__boundary = Rectangle(start_x, start_y, hub_width, hub_height)

    def __check_belonging(self, character: Entity, bullet: Entity) -> bool:
        type_component = character.get_component(TypeComponent)
        belonging_component = bullet.get_component(BelongingComponent)
        character_is_player, character_is_enemy = type_component.get_character_type()
        bullet_belong_to_player, bullet_belong_to_enemy = belonging_component.get_belonging()
        if (character_is_enemy and bullet_belong_to_player) or (character_is_player and bullet_belong_to_enemy):
            if character_is_enemy:
                self.__set_enemy_anger(character)
            return True
        return False

    def __set_enemy_anger(self, enemy: Entity):
        enemy_condition_component = enemy.get_component(EnemyConditionComponent)
        enemy_condition_component.set_anger()

    def __insert_entities(self, quadtree: QuadTree):
        for entity in self.__entities_with_collision:
            position_component = entity.get_component(PositionComponent)
            hit_box_component = entity.get_component(HitBoxComponent)
            entity_x, entity_y = position_component.get_position()
            boundary = hit_box_component.get_hit_box()
            entity_is_rotated = hit_box_component.get_rotation_condition()
            point = Point(entity_x, entity_y, entity, boundary, entity_is_rotated)
            quadtree.insert(point)

    def __calculate_bullet_damage(self, entity_is_character: Entity, entity_is_bullet: Entity):
        health_component = entity_is_character.get_component(HealthComponent)
        damage_component = entity_is_bullet.get_component(DamageComponent)
        bullet_status_component = entity_is_bullet.get_component(BulletStatusComponent)
        damage = damage_component.get_damage()
        health_component.update_health(damage)
        bullet_status_component.switch_bullet_status()

    def __calculate_minimum_translation_vector(self, first_entity: Entity, second_entity: Entity) -> (float, float):
        first_entity_hit_box_component = first_entity.get_component(HitBoxComponent)
        second_entity_hit_box_component = second_entity.get_component(HitBoxComponent)
        first_entity_top_left, first_entity_top_right, first_entity_bottom_right, first_entity_bottom_left = first_entity_hit_box_component.get_hit_box()
        second_entity_top_left, second_entity_top_right, second_entity_bottom_right, second_entity_bottom_left = second_entity_hit_box_component.get_hit_box()
        first_entity_max_x, first_entity_max_y = first_entity_bottom_right
        second_entity_max_x, second_entity_max_y = second_entity_bottom_right
        first_entity_min_x, first_entity_min_y = first_entity_top_left
        second_entity_min_x, second_entity_min_y = second_entity_top_left
        first_entity_position_component = first_entity.get_component(PositionComponent)
        second_entity_position_component = second_entity.get_component(PositionComponent)
        first_entity_center = first_entity_position_component.get_position()
        second_entity_center = second_entity_position_component.get_position()

        first_entity_center_x, first_entity_center_y = first_entity_center
        second_entity_center_x, second_entity_center_y = second_entity_center
        first_entity_width = first_entity_max_x - first_entity_min_x
        first_entity_height = first_entity_max_y - first_entity_min_y
        second_entity_width = second_entity_max_x - second_entity_min_x
        second_entity_height = second_entity_max_y - second_entity_min_y

        delta_x = first_entity_center_x - second_entity_center_x
        delta_y = first_entity_center_y - second_entity_center_y
        combined_half_widths = (first_entity_width / 2) + (second_entity_width / 2)
        combined_half_heights = (first_entity_height / 2) + (second_entity_height / 2)
        overlap_x = combined_half_widths - abs(delta_x)
        overlap_y = combined_half_heights - abs(delta_y)
        if overlap_x < overlap_y:
            if delta_x > 0:
                minimum_translation_vector = (overlap_x, 0)
            else:
                minimum_translation_vector = (-overlap_x, 0)
        else:
            if delta_y > 0:
                minimum_translation_vector = (0, overlap_y)
            else:
                minimum_translation_vector = (0, -overlap_y)
        return minimum_translation_vector

    def __calculate_distance(self, entity_is_character: Entity, entity_is_wall: Entity):
        minimum_translation_vector_x, minimum_translation_vector_y = self.__calculate_minimum_translation_vector(entity_is_character, entity_is_wall)
        position_component = entity_is_character.get_component(PositionComponent)
        hit_box_component = entity_is_character.get_component(HitBoxComponent)
        weapon_component = entity_is_character.get_component(WeaponComponent)
        active_hand_component = entity_is_character.get_component(ActiveHandComponent)
        position_component.update_position(minimum_translation_vector_x, minimum_translation_vector_y)
        hit_box_component.update_coordinates(minimum_translation_vector_x, minimum_translation_vector_y)
        if weapon_component:
            weapon_component.update_weapon_muzzle_coord(minimum_translation_vector_x, minimum_translation_vector_y)
        if active_hand_component:
            active_hand_component.update_coordinates(minimum_translation_vector_x, minimum_translation_vector_y)

    def __check_two_characters_collision(self, first_character: Entity, second_character: Entity) -> bool:
        first_character_type_component = first_character.get_component(TypeComponent)
        second_character_type_component = second_character.get_component(TypeComponent)
        first_character_is_player, first_character_is_enemy = first_character_type_component.get_character_type()
        second_character_is_player, second_character_is_enemy = second_character_type_component.get_character_type()
        if first_character_is_player and second_character_is_enemy:
            second_character_enemy_condition_component = second_character.get_component(EnemyConditionComponent)
            second_character_is_melee_enemy = second_character_enemy_condition_component.get_melee_condition()
            if second_character_is_melee_enemy:
                own_damage_component = second_character.get_component(OwnDamageComponent)
                melee_damage = own_damage_component.get_own_damage()
                own_damage_component.switch_explosion_condition()
                first_character_health_component = first_character.get_component(HealthComponent)
                first_character_health_component.update_health(melee_damage)
                return True
        elif first_character_is_enemy and second_character_is_player:
            first_character_enemy_condition_component = first_character.get_component(EnemyConditionComponent)
            first_character_is_melee_enemy = first_character_enemy_condition_component.get_melee_condition()
            if first_character_is_melee_enemy:
                own_damage_component = first_character.get_component(OwnDamageComponent)
                melee_damage = own_damage_component.get_own_damage()
                own_damage_component.switch_explosion_condition()
                second_character_health_component = second_character.get_component(HealthComponent)
                second_character_health_component.update_health(melee_damage)
                return True
        return False

    def __find_collision(self, quadtree: QuadTree):
        for main_entity in self.__entities_with_collision:
            main_entity_hit_box_component = main_entity.get_component(HitBoxComponent)
            main_entity_type_component = main_entity.get_component(TypeComponent)
            main_entity_is_character, main_entity_is_bullet, main_entity_is_wall = main_entity_type_component.get_type()
            region = main_entity_hit_box_component.get_hit_box()
            is_rotated = main_entity_hit_box_component.get_rotation_condition()
            collided_entities = quadtree.get_entities(region, is_rotated, main_entity)
            for entity in collided_entities:
                entities_is_collided = False
                entity_type_component = entity.get_component(TypeComponent)
                entity_is_character, entity_is_bullet, entity_is_wall = entity_type_component.get_type()
                if main_entity_is_wall and entity_is_character:
                    self.__calculate_distance(entity, main_entity)
                    entities_is_collided = True
                elif main_entity_is_character and entity_is_wall:
                    self.__calculate_distance(main_entity, entity)
                    entities_is_collided = True
                elif main_entity_is_character and entity_is_bullet:
                    if self.__check_belonging(main_entity, entity):
                        self.__calculate_bullet_damage(main_entity, entity)
                    entities_is_collided = True
                elif main_entity_is_bullet and entity_is_character:
                    if self.__check_belonging(entity, main_entity):
                        self.__calculate_bullet_damage(entity, main_entity)
                    entities_is_collided = True
                elif (main_entity_is_bullet and entity_is_wall) or (main_entity_is_wall and entity_is_bullet):
                    if main_entity_is_bullet:
                        bullet_status_component = main_entity.get_component(BulletStatusComponent)
                        bullet_status_component.switch_bullet_status()
                    else:
                        bullet_status_component = entity.get_component(BulletStatusComponent)
                        bullet_status_component.switch_bullet_status()
                    entities_is_collided = True
                elif main_entity_is_character and entity_is_character:
                    if self.__check_two_characters_collision(main_entity, entity):
                        entities_is_collided = True
                else:
                    main_entity_is_interactive_object = main_entity_type_component.check_interactive_condition()
                    entity_is_interactive_object = entity_type_component.check_interactive_condition()
                    main_entity_is_player, main_entity_is_enemy = main_entity_type_component.get_character_type()
                    entity_is_player, entity_is_enemy = entity_type_component.get_character_type()
                    if (main_entity_is_player and entity_is_interactive_object) or (main_entity_is_interactive_object and entity_is_player):
                        entities_is_collided = True
                if entities_is_collided:
                    entity_collision_component = entity.get_component(CollisionComponent)
                    entity_collision_component.switch_collision_condition()
                    main_entity_collision_component = main_entity.get_component(CollisionComponent)
                    main_entity_collision_component.switch_collision_condition()

    def process_collision(self):
        capacity = WorldInfo.get_collision_capacity()
        quadtree = QuadTree(self.__boundary, capacity)
        self.__insert_entities(quadtree)
        self.__find_collision(quadtree)

    def check_nearby_entities_collision(self):

        def calculate_distance(player_position: (float, float), entity_position: (float, float)) -> float:
            delta_x, delta_y = entity_position[0] - player_position[0], entity_position[1] - player_position[1]
            distance = sqrt(delta_x**2 + delta_y**2)
            return distance

        minimal_distance = 100
        player_position_component = self.__player.get_component(PositionComponent)
        player_position = player_position_component.get_position()
        for entity in self.__entities_with_collision:
            entity_type_component = entity.get_component(TypeComponent)
            if entity_type_component.check_interactive_condition() and entity != self.__player:
                entity_position_component = entity.get_component(PositionComponent)
                entity_position = entity_position_component.get_position()
                distance_to_player = calculate_distance(player_position, entity_position)
                if distance_to_player <= minimal_distance:
                    player_collision_component = self.__player.get_component(CollisionComponent)
                    entity_collision_component = entity.get_component(CollisionComponent)
                    player_collision_component.switch_collision_condition()
                    entity_collision_component.switch_collision_condition()
                    entity_action_component = entity.get_component(ActionComponent)
                    entity_action_component.set_action_readiness(True)


class EntitySystem(System):

    def __init__(self, entities_with_collision: list[Entity], bullets: list[Entity], main_entities: list[Entity], enemies: list[Entity]):
        self.__entities_with_collision = entities_with_collision
        self.__bullets = bullets
        self.__main_entities = main_entities
        self.__enemies = enemies
        self.__player = None

    def save_player(self, player: Entity):
        self.__player = player

    def __add_player_money(self):
        money_collection_component = self.__player.get_component(MoneyCollectionComponent)
        player_amount_of_money = money_collection_component.get_amount_of_money()
        coin = randint(10, 50)
        money_collection_component.set_amount_of_money(player_amount_of_money + coin)

    def __create_coin(self, enemy: Entity):
        enemy_position_component = enemy.get_component(PositionComponent)
        enemy_x_position, enemy_y_position = enemy_position_component.get_position()
        coin_animation = 'textures/interactive_objects/coin'
        coin_size = (32, 32)
        coin_width = coin_height = 64
        coin_top_left = (enemy_x_position - coin_width//2, enemy_y_position - coin_height//2)
        coin_top_right = (enemy_x_position + coin_width//2, enemy_y_position - coin_height//2)
        coin_bottom_right = (enemy_x_position + coin_width//2, enemy_y_position + coin_height//2)
        coin_bottom_left = (enemy_x_position - coin_width//2, enemy_y_position + coin_height//2)
        is_player, is_character, is_bullet, is_wall, is_enemy, is_interactive_object = False, False, False, False, False, True
        coin_has_animation = True
        coin = Entity()
        coin.add_component(TypeComponent(is_player, is_character, is_bullet, is_wall, is_enemy, is_interactive_object))
        coin.add_component(PositionComponent(enemy_x_position, enemy_y_position))
        coin.add_component(HitBoxComponent(coin_top_left, coin_top_right, coin_bottom_left, coin_bottom_right))
        coin.add_component(SingeAnimationComponent(coin_animation, coin_size))
        coin.add_component(CollisionComponent())
        coin.add_component(AnimationConditionComponent(coin_has_animation))
        coin.add_component(ActionComponent([self.__add_player_money]))
        coin.add_component(ExistenceConditionComponent(True))

        self.__main_entities.append(coin)
        self.__entities_with_collision.append(coin)

    def update_entities_condition(self):
        for entity in self.__entities_with_collision:
            type_component = entity.get_component(TypeComponent)
            collision_component = entity.get_component(CollisionComponent)
            entity_is_character, entity_is_bullet, entity_is_wall = type_component.get_type()
            entity_is_interactive_object = type_component.check_interactive_condition()
            entity_is_collided = collision_component.get_collision_condition()
            if entity_is_bullet and entity_is_collided:
                bullet_status_component = entity.get_component(BulletStatusComponent)
                bullet_is_exits = bullet_status_component.get_bullet_status()
                if not bullet_is_exits:
                    self.__entities_with_collision.remove(entity)
                    self.__bullets.remove(entity)
                    self.__main_entities.remove(entity)
                else:
                    collision_component.switch_collision_condition()
            elif entity_is_character and entity_is_collided:
                entity_is_player, entity_is_enemy = type_component.get_character_type()
                entity_is_exploded = False
                if entity_is_enemy:
                    enemy_condition_component = entity.get_component(EnemyConditionComponent)
                    enemy_is_melee = enemy_condition_component.get_melee_condition()
                    if enemy_is_melee:
                        own_damage_component = entity.get_component(OwnDamageComponent)
                        entity_is_exploded = own_damage_component.get_explosion_condition()
                health_component = entity.get_component(HealthComponent)
                entity_is_alive = health_component.get_living_condition()
                if not entity_is_alive or entity_is_exploded:
                    self.__entities_with_collision.remove(entity)
                    self.__main_entities.remove(entity)
                    if entity_is_enemy:
                        self.__enemies.remove(entity)
                        self.__create_coin(entity)
                else:
                    collision_component.switch_collision_condition()
            elif entity_is_wall and entity_is_collided:
                collision_component.switch_collision_condition()
            elif entity_is_interactive_object and entity_is_collided:
                action_component = entity.get_component(ActionComponent)
                action_is_ready = action_component.get_action_readiness()
                if action_is_ready:
                    action_component.action()
                    existence_condition_component = entity.get_component(ExistenceConditionComponent)
                    entity_disappear_after_interaction = existence_condition_component.get_existence_condition()
                    if entity_disappear_after_interaction:
                        self.__entities_with_collision.remove(entity)
                        self.__main_entities.remove(entity)
                    action_component.set_action_readiness(False)
                collision_component.switch_collision_condition()


class DungeonSystem(System):

    def __init__(self, entities_with_collision: list[Entity], background_entities: list[Entity], enemies: list[Entity], main_entities: list[Entity], portal_actions: list):
        self.__is_dungeon = False
        self.__is_dungeon_end = False
        self.__entities_with_collision = entities_with_collision
        self.__background_entities = background_entities
        self.__enemies = enemies
        self.__main_entities = main_entities
        self.__player_spawn_position = (0, 0)
        self.__rooms = []
        self.__player = None
        self.__portal_actions = portal_actions

    def save_player(self, player: Entity):
        self.__player = player

    def get_player_spawn_position(self) -> (int, int):
        return self.__player_spawn_position

    def __create_enemy_entity(self, top_left: (float, float), top_right: (float, float), bottom_right: (float, float), bottom_left: (float, float), center: (int, int), left_active_hand: list[int, int], right_active_hand: list[int, int], patrol_points: list[(int, int)], melee_enemy_condition: bool):
        enemy = Entity()
        is_player, is_character, is_bullet, is_wall, is_enemy = False, True, False, False, True
        if melee_enemy_condition:
            moving_right_images = 'textures/animations/grenade_enemy_R'
            moving_left_images = 'textures/animations/grenade_enemy_L'
            health = 100
            moving_distance = 380
            enemy.add_component(OwnDamageComponent())
        else:
            weapon = randint(1, 10)
            if weapon in range(1, 8):
                handgun, rifle, shotgun = True, False, False
            elif weapon in range(8, 10):
                handgun, rifle, shotgun = False, True, False
            else:
                handgun, rifle, shotgun = False, False, True
            moving_right_images = 'textures/animations/enemy_move_R'
            moving_left_images = 'textures/animations/enemy_move_L'
            health = 150
            moving_distance = 300
            enemy.add_component(ActiveHandComponent(left_active_hand, right_active_hand))
            enemy.add_component(WeaponComponent([handgun, rifle, shotgun]))
            enemy.add_component(EnemyActionQueueComponent())
        enemy.add_component(HealthComponent(health))
        enemy.add_component(PositionComponent(center[0], center[1]))
        enemy.add_component(HitBoxComponent(top_left, top_right, bottom_left, bottom_right))
        enemy.add_component(AnimationComponent(moving_right_images, moving_left_images))
        enemy.add_component(MovingDistanceComponent(moving_distance))
        enemy.add_component(TypeComponent(is_player, is_character, is_bullet, is_wall, is_enemy))
        enemy.add_component(CollisionComponent())
        enemy.add_component(SightComponent())
        enemy.add_component(EnemyConditionComponent(patrol_points, melee_enemy_condition))
        self.__enemies.append(enemy)
        self.__entities_with_collision.append(enemy)
        self.__main_entities.append(enemy)

    def __calculate_patrol_points(self, first_point_x: int, first_point_y: int, room_start_x: int, room_start_y: int, room_width: int, room_height: int, enemy_width: int, enemy_height: int, patrol_points: list[(int, int)]) -> (bool, bool, bool, bool):
        half_room_width = room_width // 2
        half_room_height = room_height // 2
        first_quarter = ((room_start_x, room_start_x + half_room_width), (room_start_y, room_start_y + half_room_height))
        second_quarter = ((room_start_x + half_room_width, room_start_x + room_width), (room_start_y, room_start_y + half_room_height))
        third_quarter = ((room_start_x, room_start_x + half_room_width), (room_start_y + half_room_height, room_start_y + room_height))
        fourth_quarter = ((room_start_x + half_room_width, room_start_x + room_width), (room_start_y + half_room_height, room_start_y + room_height))
        quarters = [first_quarter, second_quarter, third_quarter, fourth_quarter]
        for quarter in quarters:
            if (quarter[0][0] <= first_point_x <= quarter[0][1]) and (quarter[1][0] <= first_point_y <= quarter[1][1]):
                quarters.remove(quarter)
                break
        for chosen_quarter in quarters:
            if not ((chosen_quarter[0][0] + enemy_width >= chosen_quarter[0][1] - enemy_width) or (chosen_quarter[1][0] + enemy_height >= chosen_quarter[1][1] - enemy_height)):
                point_x = randint(chosen_quarter[0][0] + enemy_width, chosen_quarter[0][1] - enemy_width)
                point_y = randint(chosen_quarter[1][0] + enemy_height, chosen_quarter[1][1] - enemy_height)
                patrol_points.append((point_x, point_y))
                quarters.remove(chosen_quarter)

    def __create_enemies(self, room_start_x: int, room_start_y: int, room_width: int, room_height: int, block_size: int):
        real_room_start_x = room_start_x * block_size
        real_room_start_y = room_start_y * block_size
        real_room_width = room_width * block_size
        real_room_height = room_height * block_size
        room_square = real_room_height * real_room_width
        enemies_per_room_ratio = 150000
        possible_enemies_number = room_square // enemies_per_room_ratio
        for i in range(possible_enemies_number):
            melee_enemy_condition = choice([True, False])
            if melee_enemy_condition:
                enemy_width = 32
                enemy_height = 53
            else:
                enemy_width = 64
                enemy_height = 100
            enemy_center_x = randint(real_room_start_x + enemy_width, real_room_start_x + real_room_width - enemy_width)
            enemy_center_y = randint(real_room_start_y + enemy_height, real_room_start_y + real_room_height - enemy_height)
            top_left = [enemy_center_x - enemy_width // 2, enemy_center_y - enemy_height // 2]
            bottom_left = [enemy_center_x - enemy_width // 2, enemy_center_y + enemy_height // 2]
            top_right = [enemy_center_x + enemy_width // 2, enemy_center_y - enemy_height // 2]
            bottom_right = [enemy_center_x + enemy_width // 2, enemy_center_y + enemy_height // 2]
            center = [enemy_center_x, enemy_center_y]
            right_active_hand = [top_left[0] + 60, top_left[1] + 58]
            left_active_hand = [top_left[0] + 4, top_left[1] + 58]
            patrol_points = [center]
            self.__calculate_patrol_points(enemy_center_x, enemy_center_y, real_room_start_x,
                    real_room_start_y, real_room_width, real_room_height, enemy_width, enemy_height, patrol_points)
            self.__create_enemy_entity(top_left, top_right, bottom_right, bottom_left, center, left_active_hand, right_active_hand, patrol_points, melee_enemy_condition)

    def __process_rooms(self):
        block_size = WorldInfo.get_block_size()

        self.__rooms.sort(key=lambda room: room.get_room_info()[2] * room.get_room_info()[3]) # sort by square

        player_room_center_x, player_room_center_y = self.__rooms[0].get_room_center()
        player_room_center_x *= block_size
        player_room_center_y *= block_size
        self.__player_spawn_position = (player_room_center_x, player_room_center_y)

        for i in range(1, len(self.__rooms)):
            room_start_x, room_start_y, room_width, room_height = self.__rooms[i].get_room_info()
            self.__create_enemies(room_start_x, room_start_y, room_width, room_height, block_size)

    def update_dungeon(self):

        def create_portal(point: (int, int)):
            block_size = WorldInfo.get_block_size()
            x_coord, y_coord = point[0]*block_size, point[1]*block_size
            portal_width = portal_height = 200
            portal_animation_path = 'textures/interactive_objects/portal'
            portal_top_left = (x_coord - portal_width//2, y_coord - portal_height//2)
            portal_top_right = (x_coord + portal_width//2, y_coord - portal_height//2)
            portal_bottom_right = (x_coord + portal_width//2, y_coord + portal_height//2)
            portal_bottom_left = (x_coord - portal_width//2, y_coord + portal_height//2)
            is_player, is_character, is_bullet, is_wall, is_enemy, is_interactive_object = False, False, False, False, False, True
            portal_has_animation = True
            portal_actions = []
            for action in self.__portal_actions:
                portal_actions.append(action)
            portal = Entity()
            portal.add_component(TypeComponent(is_player, is_character, is_bullet, is_wall, is_enemy, is_interactive_object))
            portal.add_component(PositionComponent(x_coord, y_coord))
            portal.add_component(HitBoxComponent(portal_top_left, portal_top_right, portal_bottom_left, portal_bottom_right))
            portal.add_component(SingeAnimationComponent(portal_animation_path, (portal_width, portal_height)))
            portal.add_component(ActionComponent(portal_actions))
            portal.add_component(CollisionComponent())
            portal.add_component(AnimationConditionComponent(portal_has_animation))
            portal.add_component(ExistenceConditionComponent())

            self.__entities_with_collision.append(portal)
            self.__main_entities.append(portal)

        def calculate_distance(player_point: (float, float), room_point: (float, float)) -> float:
            block_size = WorldInfo.get_block_size()
            player_x, player_y = player_point
            room_x, room_y = room_point[0]*block_size, room_point[1]*block_size
            delta_x, delta_y = room_x - player_x, room_y - player_y
            distance = sqrt(delta_x**2 + delta_y**2)
            return distance

        if not self.__enemies and not self.__is_dungeon_end:
            player_position_component = self.__player.get_component(PositionComponent)
            player_position = player_position_component.get_position()
            nearest_room_center = self.__rooms[0].get_room_center()
            shortest_distance_to_player = calculate_distance(player_position, nearest_room_center)
            for i in range(1, len(self.__rooms)):
                room_center = self.__rooms[i].get_room_center()
                distance_to_player = calculate_distance(player_position, room_center)
                if distance_to_player < shortest_distance_to_player:
                    shortest_distance_to_player = distance_to_player
                    nearest_room_center = room_center
            create_portal(nearest_room_center)
            self.__is_dungeon_end = True

    def create_dungeon(self) -> (int, int):
        self.__rooms = []
        minimal_room_size = WorldInfo.get_minimal_room_size()
        world_map_size = WorldInfo.get_world_map_size()
        world_map = [[0 for i in range(world_map_size)] for j in range(world_map_size)]
        tree = BinaryTree(0, 0, world_map_size, world_map_size)
        tree.create_dungeon(self.__entities_with_collision, self.__background_entities, world_map, minimal_room_size, self.__rooms)
        self.__process_rooms()
        self.__is_dungeon = True

    def create_hub(self):
        self.__is_dungeon = False
        hud_width, hub_height = WorldInfo.get_hub_map_size()
        hub_map = [[0 for i in range(hud_width)] for j in range(hub_height)]
        tree = BinaryTree(0, 0, hud_width, hub_height)
        tree.create_hub(self.__entities_with_collision, self.__background_entities, hub_map)
        self.__player_spawn_position = (600, 500)
        self.__is_dungeon = False

    def check_dungeon_condition(self) -> bool:
        return self.__is_dungeon


class EnemyManagementSystem(System):

    def __init__(self, enemies: list[Entity]):
        self.__enemies = enemies
        self.__player = None

    def save_player(self, player: Entity):
        self.__player = player

    def __calculate_distance_and_vector_to_target(self, first_point: (float, float), second_point: (float, float), return_difference: bool = False) -> (float, float, float):
        delta_x = second_point[0] - first_point[0]
        delta_y = second_point[1] - first_point[1]
        distance = sqrt(delta_x**2 + delta_y**2)
        vector_x, vector_y = 0, 0
        if distance != 0:
            vector_x = delta_x / distance
            vector_y = delta_y / distance
        if return_difference:
            return delta_x, delta_y
        else:
            return distance, vector_x, vector_y

    def __patrol(self, enemy: Entity, scaled_time: float):
        enemy_position_component = enemy.get_component(PositionComponent)
        enemy_hit_box_component = enemy.get_component(HitBoxComponent)
        enemy_moving_distance_component = enemy.get_component(MovingDistanceComponent)
        enemy_animation_component = enemy.get_component(AnimationComponent)
        enemy_active_hand_component = enemy.get_component(ActiveHandComponent)
        enemy_condition_component = enemy.get_component(EnemyConditionComponent)
        enemy_weapon_component = enemy.get_component(WeaponComponent)
        enemy_sight_component = enemy.get_component(SightComponent)
        left, right = enemy_sight_component.get_sights()
        enemy_position = enemy_position_component.get_position()
        moving_distance = enemy_moving_distance_component.get_moving_distance()
        target_point = enemy_condition_component.get_patrol_point()
        distance, vector_x, vector_y = self.__calculate_distance_and_vector_to_target(enemy_position, target_point)
        if vector_x > 0 and not right:
            enemy_sight_component.switch_sight()
        elif vector_x < 0 and not left:
            enemy_sight_component.switch_sight()
        delta_x = vector_x * moving_distance * scaled_time
        delta_y = vector_y * moving_distance * scaled_time
        enemy_position_component.update_position(delta_x, delta_y)
        enemy_hit_box_component.update_coordinates(delta_x, delta_y)
        if enemy_active_hand_component:
            enemy_active_hand_component.update_coordinates(delta_x, delta_y)
        if distance <= 10:
            enemy_condition_component.switch_to_next_point()
        if enemy_weapon_component:
            if right:
                enemy_weapon_component.set_angle(0)
            else:
                enemy_weapon_component.set_angle(180)
        enemy_animation_component.activate_animation()

    def __alert_nearby_enemies(self, enemy: Entity):
        enemy_condition_component = enemy.get_component(EnemyConditionComponent)
        alert_range = enemy_condition_component.get_alert_range()
        for nearby_enemy in self.__enemies:
            if nearby_enemy != self:
                nearby_enemy_condition_component = nearby_enemy.get_component(EnemyConditionComponent)
                nearby_enemy_is_angry = nearby_enemy_condition_component.get_status()
                if not nearby_enemy_is_angry:
                    enemy_position_component = enemy.get_component(PositionComponent)
                    nearby_enemy_position_component = nearby_enemy.get_component(PositionComponent)
                    enemy_position = enemy_position_component.get_position()
                    nearby_enemy_position = nearby_enemy_position_component.get_position()
                    distance, vector_x, vector_y = self.__calculate_distance_and_vector_to_target(enemy_position, nearby_enemy_position)
                    if distance <= alert_range:
                        nearby_enemy_condition_component.set_anger()

    def __move_towards_player(self, enemy: Entity, vector_x: float, vector_y: float, scaled_time: float):
        enemy_position_component = enemy.get_component(PositionComponent)
        enemy_hit_box_component = enemy.get_component(HitBoxComponent)
        enemy_moving_distance_component = enemy.get_component(MovingDistanceComponent)
        enemy_animation_component = enemy.get_component(AnimationComponent)
        enemy_active_hand_component = enemy.get_component(ActiveHandComponent)
        moving_distance = enemy_moving_distance_component.get_moving_distance()
        delta_x = vector_x * moving_distance * scaled_time
        delta_y = vector_y * moving_distance * scaled_time
        enemy_position_component.update_position(delta_x, delta_y)
        enemy_hit_box_component.update_coordinates(delta_x, delta_y)
        if enemy_active_hand_component:
            enemy_active_hand_component.update_coordinates(delta_x, delta_y)
        enemy_animation_component.activate_animation()

    def __make_new_actions(self, enemy: Entity, enemy_action_queue_component: EnemyActionQueueComponent):
        enemy_position_component = enemy.get_component(PositionComponent)
        player_position_component = self.__player.get_component(PositionComponent)
        enemy_position = enemy_position_component.get_position()
        player_position = player_position_component.get_position()
        delta_x, delta_y = self.__calculate_distance_and_vector_to_target(enemy_position, player_position, True)
        if abs(delta_x) > abs(delta_y):
            first_y_direction = choice([-1, 1])
            second_y_direction = - first_y_direction
            first_x_direction = 0
            second_x_direction = 0
        else:
            first_x_direction = choice([-1, 1])
            second_x_direction = - first_x_direction
            first_y_direction = 0
            second_y_direction = 0
        actions = [WaitAction(), ShootAction(), MoveAction(first_x_direction, first_y_direction), WaitAction(),
                                ShootAction(), MoveAction(second_x_direction, second_y_direction)]
        for action in actions:
            enemy_action_queue_component.insert_action(action)

    def __make_decision(self, enemy: Entity, new_bullets: list[Entity], scaled_time: float):
        enemy_action_queue_component = enemy.get_component(EnemyActionQueueComponent)
        current_action = enemy_action_queue_component.get_current_action()
        if current_action:
            animation_component = enemy.get_component(AnimationComponent)
            action_is_move_action, action_is_shoot_action, action_is_wait_action = current_action.get_type()
            if action_is_shoot_action:
                animation_component.deactivate_animation()
                BulletSystem.create_bullet(enemy, new_bullets, self.__player)
                enemy_action_queue_component.remove_current_action()
            elif action_is_wait_action:
                animation_component.deactivate_animation()
                wait_time = current_action.get_wait_time()
                time_accumulator = current_action.get_time_accumulator()
                if time_accumulator + scaled_time < wait_time:
                    current_action.update_time_accumulator(scaled_time)
                else:
                    enemy_action_queue_component.remove_current_action()
            elif action_is_move_action:
                animation_component.activate_animation()
                moving_distance_component = enemy.get_component(MovingDistanceComponent)
                position_component = enemy.get_component(PositionComponent)
                hit_box_component = enemy.get_component(HitBoxComponent)
                active_hand_component = enemy.get_component(ActiveHandComponent)
                weapon_component = enemy.get_component(WeaponComponent)
                move_distance = current_action.get_move_distance()
                move_accumulator = current_action.get_move_accumulator()
                x_direction, y_direction = current_action.get_direction()
                enemy_moving_distance = moving_distance_component.get_moving_distance()
                x_direction *= enemy_moving_distance * scaled_time
                y_direction *= enemy_moving_distance * scaled_time
                position_component.update_position(x_direction, y_direction)
                hit_box_component.update_coordinates(x_direction, y_direction)
                weapon_component.update_weapon_muzzle_coord(x_direction, y_direction)
                active_hand_component.update_coordinates(x_direction, y_direction)
                if x_direction != 0:
                    main_direction = abs(x_direction)
                else:
                    main_direction = abs(y_direction)
                if move_accumulator + main_direction < move_distance:
                    current_action.update_move_accumulator(main_direction)
                else:
                    enemy_action_queue_component.remove_current_action()
        else:
            self.__make_new_actions(enemy, enemy_action_queue_component)

    def __process_angry_behavior(self, enemy: Entity, vector_x: float, vector_y: float, distance_to_player: float, new_bullets: list[Entity], scaled_time: float):
        enemy_condition_component = enemy.get_component(EnemyConditionComponent)
        enemy_is_melee = enemy_condition_component.get_melee_condition()
        if not enemy_is_melee:
            minimal_distance_to_target = enemy_condition_component.get_anger_range()
            if distance_to_player > minimal_distance_to_target:
                self.__move_towards_player(enemy, vector_x, vector_y, scaled_time)
            else:
                self.__make_decision(enemy, new_bullets, scaled_time)
        else:
            self.__move_towards_player(enemy, vector_x, vector_y, scaled_time)

    def update_enemy_condition(self, new_bullets: list[Entity], scaled_time: float) -> list[Entity]:
        for enemy in self.__enemies:
            enemy_position = enemy.get_component(PositionComponent).get_position()
            player_position = self.__player.get_component(PositionComponent).get_position()
            enemy_condition_component = enemy.get_component(EnemyConditionComponent)
            enemy_is_angry = enemy_condition_component.get_status()
            enemy_anger_range = enemy_condition_component.get_anger_range()
            distance_to_player, vector_x, vector_y = self.__calculate_distance_and_vector_to_target(enemy_position, player_position)
            if distance_to_player <= enemy_anger_range or enemy_is_angry:
                InputSystem.process_input(enemy, scaled_time, self.__player)
                enemy_condition_component.set_anger()
                self.__process_angry_behavior(enemy, vector_x, vector_y, distance_to_player, new_bullets, scaled_time)
                self.__alert_nearby_enemies(enemy)
            else:
                self.__patrol(enemy, scaled_time)
