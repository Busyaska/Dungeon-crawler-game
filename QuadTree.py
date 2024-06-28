from Entities import Entity
from Components import CollisionComponent
from CheckCollisionMethods import AxisAlignedBoundingBox, SeparatingAxisTheorem


class Point:

    def __init__(self, x: int, y: int, entity: Entity, boundary: list[(float, float)], is_rotated: bool = False):
        self.__x_coord = x
        self.__y_coord = y
        self.__entity = entity
        self.__entity_boundary = boundary
        self.__is_rotated = is_rotated

    def get_coordinates(self) -> (int, int):
        return self.__x_coord, self.__y_coord

    def get_entity_boundary(self) -> list[(float, float)]:
        return self.__entity_boundary

    def get_entity(self) -> Entity:
        return self.__entity

    def get_rotation_condition(self) -> bool:
        return self.__is_rotated


class Rectangle:

    def __init__(self, x: int, y: int, width: int, height: int):
        self.__x_coord = x
        self.__y_coord = y
        self.__width = width
        self.__height = height

    def get_boundary(self) -> (int, int, int, int):
        return self.__x_coord, self.__y_coord, self.__width, self.__height

    def check_contain(self, point: Point) -> bool:
        point_x_coord, point_y_coord = point.get_coordinates()
        condition = self.__x_coord <= point_x_coord and self.__x_coord + self.__width >= point_x_coord and \
                    self.__y_coord <= point_y_coord and self.__y_coord + self.__height >= point_y_coord
        return condition


class QuadTree:

    def __init__(self, boundary: Rectangle, capacity: int):
        self.__boundary = boundary
        self.__capacity = capacity
        self.__points = []
        self.__is_divided = False
        self.__top_right = None
        self.__top_left = None
        self.__bottom_right = None
        self.__bottom_left = None

    def __subdivide(self):
        boundary_x, boundary_y, boundary_width, boundary_height = self.__boundary.get_boundary()
        top_left_boundary = Rectangle(boundary_x, boundary_y, boundary_width / 2, boundary_height / 2)
        self.__top_left = QuadTree(top_left_boundary, self.__capacity)
        top_right_boundary = Rectangle(boundary_x + boundary_width / 2, boundary_y, boundary_width / 2, boundary_height / 2)
        self.__top_right = QuadTree(top_right_boundary, self.__capacity)
        bottom_left_boundary = Rectangle(boundary_x, boundary_y + boundary_height / 2, boundary_width / 2, boundary_height / 2)
        self.__bottom_left = QuadTree(bottom_left_boundary, self.__capacity)
        bottom_right_boundary = Rectangle(boundary_x + boundary_width / 2, boundary_y + boundary_height / 2, boundary_width / 2, boundary_height / 2)
        self.__bottom_right = QuadTree(bottom_right_boundary, self.__capacity)
        self.__is_divided = True

    def __transform_boundary(self) -> list[(float, float)]:
        top_left_x, top_left_y, width, height = self.__boundary.get_boundary()
        top_left = (top_left_x, top_left_y)
        bottom_left = (top_left_x, top_left_y + height)
        top_right = (top_left_x + width, top_left_y)
        bottom_right = (top_left_x + width, top_left_y + height)
        return [top_left, top_right, bottom_right, bottom_left]

    def __check_intersection(self, first_region: list[(float, float)], second_region: list[(float, float)], rotation_condition: bool) -> bool:
        if not rotation_condition:
            collided = AxisAlignedBoundingBox.check_collision(first_region, second_region)
        else:
            collided = SeparatingAxisTheorem.check_collision(first_region, second_region)
        return collided

    def insert(self, point: Point) -> bool:
        if not self.__boundary.check_contain(point):
            return False
        if (len(self.__points) + 1) <= self.__capacity:
            self.__points.append(point)
            return True
        else:
            if not self.__is_divided:
                self.__subdivide()
            if self.__top_left.insert(point):
                return True
            elif self.__top_right.insert(point):
                return True
            elif self.__bottom_left.insert(point):
                return True
            elif self.__bottom_right.insert(point):
                return True
        return False

    def get_entities(self, region: list[[int, int]], entity_is_rotated: bool = False, entity: Entity = None) -> list[Entity]:
        entities = []
        current_quadtree_region = self.__transform_boundary()
        if not self.__check_intersection(region, current_quadtree_region, entity_is_rotated):
            return entities
        for point in self.__points:
            point_entity = point.get_entity()
            if not entity:
                point_is_collided = False
            else:
                collision_component = entity.get_component(CollisionComponent)
                point_is_collided = collision_component.get_collision_condition()
            if not point_is_collided and entity != point_entity:
                entity_boundary = point.get_entity_boundary()
                point_entity_is_rotated = point.get_rotation_condition()
                rotation_condition = (entity_is_rotated or point_entity_is_rotated)
                if self.__check_intersection(region, entity_boundary, rotation_condition):
                    entities.append(point_entity)
        if self.__is_divided:
            entities += self.__top_right.get_entities(region, entity_is_rotated, entity)
            entities += self.__top_left.get_entities(region, entity_is_rotated, entity)
            entities += self.__bottom_right.get_entities(region, entity_is_rotated, entity)
            entities += self.__bottom_left.get_entities(region, entity_is_rotated, entity)
        return entities
