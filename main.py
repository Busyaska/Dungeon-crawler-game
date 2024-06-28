import pygame
import sys

from Systems import (RenderSystem, InputSystem, BulletSystem, MenuSystem, WeaponSystem, EntitySystem,
                          CollisionSystem, DungeonSystem, EnemyManagementSystem, UpgradeSystem, SavingSystem)
from Components import (PositionComponent, AnimationComponent, HealthComponent, TypeComponent, CollisionComponent,
                        MovingDistanceComponent, WeaponComponent, SightComponent, HitBoxComponent, ActiveHandComponent,
                        SingleImageComponent, SingeAnimationComponent, ActionComponent, AnimationConditionComponent,
                        MoneyCollectionComponent, ExistenceConditionComponent)
from Entities import Entity


class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Game')
        pygame.mouse.set_visible(False)
        self.__new_game = True
        self.__clock = pygame.time.Clock()
        self.__main_entities: list[Entity] = []
        self.__entities_with_collision: list[Entity] = []
        self.__bullets: list[Entity] = []
        self.__background_entities: list[Entity] = []
        self.__enemies: list[Entity] = []
        self.__menu_entities: list[Entity] = []
        self.__game_speed: float = 1.0
        self.__delta_time: float = 0
        self.__upgrade_system = UpgradeSystem()
        self.__saving_system = SavingSystem()
        self.__render_system: RenderSystem = RenderSystem(self.__main_entities, self.__background_entities, self.__enemies, self.__menu_entities)
        self.__input_system: InputSystem = InputSystem()
        self.__weapon_system: WeaponSystem = WeaponSystem()
        self.__bullet_system: BulletSystem = BulletSystem(self.__bullets, self.__main_entities, self.__entities_with_collision)
        self.__entity_system: EntitySystem = EntitySystem(self.__entities_with_collision, self.__bullets, self.__main_entities, self.__enemies)
        self.__collision_system: CollisionSystem = CollisionSystem(self.__entities_with_collision)
        self.__dungeon_system: DungeonSystem = DungeonSystem(self.__entities_with_collision, self.__background_entities, self.__enemies, self.__main_entities, [self.__create_hub])
        self.__enemy_management_system: EnemyManagementSystem = EnemyManagementSystem(self.__enemies)

        save_action = self.__saving_system.save_data
        new_game_button_actions = [self.__render_system.draw_loading_screen, self.__set_new_game_true, self.__initialize_player, self.__create_hub]
        load_game_button_actions = [self.__render_system.draw_loading_screen, self.__set_new_game_false, self.__initialize_player, self.__create_hub]
        main_menu_button_actions = [self.__render_system.draw_loading_screen]
        upgrade_health_button_action = [self.__upgrade_system.upgrade_health]
        self.__menu_system = MenuSystem(self.__menu_entities, new_game_button_actions, load_game_button_actions, main_menu_button_actions, upgrade_health_button_action, save_action)

    def __set_new_game_false(self):
        self.__new_game = False

    def __set_new_game_true(self):
        self.__new_game = True

    def __clear_game_entities(self):
        self.__enemies.clear()
        self.__main_entities.clear()
        self.__background_entities.clear()
        self.__entities_with_collision.clear()
        self.__bullets.clear()

    def __clear_menu_entities(self):
        self.__menu_entities.clear()

    def __create_player(self):
        if self.__new_game:
            player_health = 100
            handgun, rifle, shotgun = True, False, False
            amount_of_money = 0
        else:
            player_health, current_weapon, amount_of_money = self.__saving_system.load_data()
            handgun, rifle, shotgun = current_weapon
        player_width = 53
        player_height = 100
        center_x, center_y = (0, 0)
        top_left = [center_x - player_width / 2, center_y - player_height / 2]
        bottom_left = [center_x - player_width / 2, center_y + player_height / 2]
        top_right = [center_x + player_width / 2, center_y - player_height / 2]
        bottom_right = [center_x + player_width / 2, center_y + player_height / 2]
        center = [center_x, center_y]
        player_right_active_hand = [top_left[0] + 50, top_left[1] + 50]
        player_left_active_hand = [top_left[0] + 5, top_left[1] + 50]
        moving_distance = 500
        moving_right_images = 'textures/animations/player_move_R'
        moving_left_images = 'textures/animations/player_move_L'
        is_player, is_character, is_bullet, is_wall, is_enemy = True, True, False, False, False
        self.__player = Entity()
        self.__player.add_component(TypeComponent(is_player, is_character, is_bullet, is_wall, is_enemy))
        self.__player.add_component(PositionComponent(center[0], center[1]))
        self.__player.add_component(HitBoxComponent(top_left, top_right, bottom_left, bottom_right))
        self.__player.add_component(ActiveHandComponent(player_left_active_hand, player_right_active_hand))
        self.__player.add_component(WeaponComponent([handgun, rifle, shotgun]))
        self.__player.add_component(AnimationComponent(moving_right_images, moving_left_images))
        self.__player.add_component(HealthComponent(player_health))
        self.__player.add_component(MovingDistanceComponent(moving_distance))
        self.__player.add_component(SightComponent())
        self.__player.add_component(CollisionComponent())
        self.__player.add_component(MoneyCollectionComponent(amount_of_money))

    def __update_player(self):
        health_component = self.__player.get_component(HealthComponent)

        if not health_component.get_living_condition():
            money_collection_component = self.__player.get_component(MoneyCollectionComponent)
            current_money = money_collection_component.get_amount_of_money()
            money_collection_component.set_amount_of_money(current_money//2)

        health_component.resurrect()

        position_component = self.__player.get_component(PositionComponent)
        hit_box_component = self.__player.get_component(HitBoxComponent)
        active_hand_component = self.__player.get_component(ActiveHandComponent)
        weapon_component = self.__player.get_component(WeaponComponent)
        current_x, current_y = position_component.get_position()
        spawn_x, spawn_y = self.__dungeon_system.get_player_spawn_position()
        delta_x, delta_y = spawn_x - current_x, spawn_y - current_y
        position_component.update_position(delta_x, delta_y)
        hit_box_component.update_coordinates(delta_x, delta_y)
        active_hand_component.update_coordinates(delta_x, delta_y)
        weapon_component.update_weapon_muzzle_coord(delta_x, delta_y)

        self.__weapon_system.reload()

    def __create_hub_entities(self):
        portal_size = (200, 200)
        portal_animation_path = 'textures/interactive_objects/portal'
        portal_position = (600, 50)
        portal_top_left = (500, -50)
        portal_top_right = (700, -50)
        portal_bottom_right = (700, 150)
        portal_bottom_left = (500, 150)
        is_player, is_character, is_bullet, is_wall, is_enemy, is_interactive_object = False, False, False, False, False, True
        portal_has_animation = True
        portal = Entity()
        portal.add_component(TypeComponent(is_player, is_character, is_bullet, is_wall, is_enemy, is_interactive_object))
        portal.add_component(PositionComponent(portal_position[0], portal_position[1]))
        portal.add_component(HitBoxComponent(portal_top_left, portal_top_right, portal_bottom_left, portal_bottom_right))
        portal.add_component(SingeAnimationComponent(portal_animation_path, portal_size))
        portal.add_component(ActionComponent([self.__render_system.draw_loading_screen, self.__create_dungeon]))
        portal.add_component(CollisionComponent())
        portal.add_component(AnimationConditionComponent(portal_has_animation))
        portal.add_component(ExistenceConditionComponent())

        weapon_column_size = (164, 98)
        weapon_column_position = (602, 630)
        weapon_column_top_left = (520, 592)
        weapon_column_top_right = (684, 592)
        weapon_column_bottom_left = (520, 690)
        weapon_column_bottom_right = (684, 690)
        weapon_column_path = 'textures/interactive_objects/objects/weapon_column.png'
        is_player, is_character, is_bullet, is_wall, is_enemy, is_interactive_object = False, False, False, False, False, True
        column_has_animation = False
        action_is_ready = False
        weapon_column = Entity()
        weapon_column.add_component(PositionComponent(weapon_column_position[0], weapon_column_position[1]))
        weapon_column.add_component(HitBoxComponent(weapon_column_top_left, weapon_column_top_right, weapon_column_bottom_left, weapon_column_bottom_right))
        weapon_column.add_component(TypeComponent(is_player, is_character, is_bullet, is_wall, is_enemy, is_interactive_object))
        weapon_column.add_component(SingleImageComponent(weapon_column_path, weapon_column_size))
        weapon_column.add_component(CollisionComponent())
        weapon_column.add_component(ActionComponent([self.__menu_system.create_upgrade_menu], action_is_ready))
        weapon_column.add_component(AnimationConditionComponent(column_has_animation))
        weapon_column.add_component(ExistenceConditionComponent())

        self.__entities_with_collision.append(portal)
        self.__main_entities.append(portal)
        self.__main_entities.append(weapon_column)
        self.__entities_with_collision.append(weapon_column)

    def __create_dungeon(self):
        self.__menu_system.set_menu_condition(False)
        self.__menu_system.set_main_menu_condition(False)
        self.__clear_menu_entities()
        self.__clear_game_entities()
        self.__menu_system.create_in_game_menu()
        self.__dungeon_system.create_dungeon()
        self.__render_system.create_dungeon_render()
        self.__render_system.insert_background_entities()
        self.__collision_system.create_dungeon_collision()
        self.__update_player()
        self.__main_entities.append(self.__player)
        self.__entities_with_collision.append(self.__player)

    def __create_hub(self):
        self.__menu_system.set_menu_condition(False)
        self.__menu_system.set_main_menu_condition(False)
        self.__clear_menu_entities()
        self.__clear_game_entities()
        self.__create_hub_entities()
        self.__menu_system.create_in_game_menu()
        self.__dungeon_system.create_hub()
        self.__render_system.create_hub_render()
        self.__render_system.insert_background_entities()
        self.__collision_system.create_hub_collision()
        self.__update_player()
        self.__main_entities.append(self.__player)
        self.__entities_with_collision.append(self.__player)

    def __check_players_life(self):
        player_health_component = self.__player.get_component(HealthComponent)
        player_is_alive = player_health_component.get_living_condition()
        if not player_is_alive:
            self.__render_system.draw_loading_screen()
            self.__create_hub()

    def __update_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not self.__menu_system.is_main_menu_active():
                if event.key == pygame.K_ESCAPE:
                    self.__menu_system.resume_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.__menu_system.check_buttons()

    def __update_game_world(self):
        self.__check_players_life()
        new_bullets = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.__weapon_system.reload()
                if event.key == pygame.K_ESCAPE:
                    self.__menu_system.set_menu_condition(True)
                if event.key == pygame.K_e and not self.__dungeon_system.check_dungeon_condition():
                    self.__collision_system.check_nearby_entities_collision()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.__weapon_system.shoot()
                    self.__bullet_system.create_bullet(self.__player, new_bullets)

        scaled_time = self.__delta_time * self.__game_speed
        self.__input_system.process_input(self.__player, scaled_time)
        self.__enemy_management_system.update_enemy_condition(new_bullets, scaled_time)
        self.__bullet_system.insert_bullets(new_bullets)
        self.__bullet_system.update_bullet(scaled_time)
        self.__weapon_system.update()
        self.__collision_system.process_collision()
        self.__entity_system.update_entities_condition()
        if self.__dungeon_system.check_dungeon_condition():
            self.__dungeon_system.update_dungeon()

    def __update(self):
        if self.__menu_system.is_menu_active():
            self.__update_menu()
        else:
            self.__update_game_world()

    def __render(self):
        scaled_time = self.__delta_time * self.__game_speed
        if self.__menu_system.is_menu_active():
            self.__render_system.render_menu(scaled_time)
        else:
            self.__render_system.render_game_world(self.__player, scaled_time)

    def __turn_on_main_cycle(self):
        while True:
            self.__update()
            self.__render()
            self.__delta_time = self.__clock.tick(60)/1000

    def __initialize_player(self):
        self.__create_player()
        self.__weapon_system.save_weapon_component(self.__player)
        self.__entity_system.save_player(self.__player)
        self.__enemy_management_system.save_player(self.__player)
        self.__dungeon_system.save_player(self.__player)
        self.__collision_system.save_player(self.__player)
        self.__menu_system.save_player(self.__player)
        self.__upgrade_system.save_player(self.__player)
        self.__saving_system.save_player(self.__player)

    def run(self):
        self.__menu_system.create_main_menu()
        self.__turn_on_main_cycle()


if __name__ == '__main__':
    game = Game()
    game.run()
