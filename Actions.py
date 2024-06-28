from abc import ABC


class Action(ABC):
    pass


class MoveAction(Action):

    def __init__(self, x_direction: float, y_direction: float):
        self.__is_move_action = True
        self.__is_shoot_action = False
        self.__is_wait_action = False
        self.__x_direction = x_direction
        self.__y_direction = y_direction
        self.__move_distance = 180
        self.__move_accumulator = 0

    def get_type(self) -> (bool, bool, bool):
        return self.__is_move_action, self.__is_shoot_action, self.__is_wait_action

    def get_move_distance(self) -> int:
        return self.__move_distance

    def get_move_accumulator(self) -> float:
        return self.__move_accumulator

    def update_move_accumulator(self, move: float):
        self.__move_accumulator += move

    def get_direction(self) -> (int, int):
        return self.__x_direction, self.__y_direction


class ShootAction(Action):

    def __init__(self):
        self.__is_move_action = False
        self.__is_shoot_action = True
        self.__is_wait_action = False

    def get_type(self) -> (bool, bool, bool):
        return self.__is_move_action, self.__is_shoot_action, self.__is_wait_action


class WaitAction(Action):

    def __init__(self):
        self.__is_move_action = False
        self.__is_shoot_action = False
        self.__is_wait_action = True
        self.__wait_time = 0.500
        self.__time_accumulator = 0

    def get_type(self) -> (bool, bool, bool):
        return self.__is_move_action, self.__is_shoot_action, self.__is_wait_action

    def get_wait_time(self) -> int:
        return self.__wait_time

    def get_time_accumulator(self) -> float:
        return self.__time_accumulator

    def update_time_accumulator(self, delta_time: float):
        self.__time_accumulator += delta_time
