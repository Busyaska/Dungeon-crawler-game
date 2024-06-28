import math


class AxisAlignedBoundingBox:

    @staticmethod
    def check_collision(first_region: list[(float, float)], second_region: list[(float, float)]) -> bool:
        first_top_left, first_top_right, first_bottom_right, first_bottom_left = first_region
        second_top_left, second_top_right, second_bottom_right, second_bottom_left = second_region
        first_region_min_x, first_region_min_y = first_top_left
        first_region_max_x, first_region_max_y = first_bottom_right
        second_region_min_x, second_region_min_y = second_top_left
        second_region_max_x, second_region_max_y = second_bottom_right
        condition = (first_region_min_x <= second_region_max_x and first_region_max_x >= second_region_min_x) and \
                    (first_region_min_y <= second_region_max_y and first_region_max_y >= second_region_min_y)
        return condition


class SeparatingAxisTheorem:

    @staticmethod
    def __calculate_edge_vector(first_point, second_point) -> (float, float):
        edge_vector = (second_point[0] - first_point[0], second_point[1] - first_point[1])
        perpendicular_vector = (-edge_vector[1], edge_vector[0])
        perpendicular_vector_length = math.sqrt(perpendicular_vector[0]**2 + perpendicular_vector[1]**2)
        normal_edge_vector = (perpendicular_vector[0]/perpendicular_vector_length, perpendicular_vector[1]/perpendicular_vector_length)
        return normal_edge_vector

    @staticmethod
    def __calculate_scalar_product(first_vector: (float, float), second_vector: (float, float)) -> float:
        product = first_vector[0] * second_vector[0] + first_vector[1] * second_vector[1]
        return product

    @staticmethod
    def __project_polygon(vertices: list[(float, float)], axis: (float, float)) -> (float, float):
        min_projection_point = max_projection_point = SeparatingAxisTheorem.__calculate_scalar_product(vertices[0], axis)
        for vertex in vertices[1:]:
            projection = SeparatingAxisTheorem.__calculate_scalar_product(vertex, axis)
            if projection < min_projection_point:
                min_projection_point = projection
            if projection > max_projection_point:
                max_projection_point = projection
        return min_projection_point, max_projection_point

    @staticmethod
    def check_collision(first_region_vertices: list[(float, float)], second_region_vertices: list[(float, float)]) -> bool:
        axes = []
        for i in range(len(first_region_vertices)):
            point_1 = first_region_vertices[i]
            point_2 = first_region_vertices[(i + 1) % len(first_region_vertices)]
            edge = SeparatingAxisTheorem.__calculate_edge_vector(point_1, point_2)
            axes.append(edge)
        for i in range(len(second_region_vertices)):
            point_1 = second_region_vertices[i]
            point_2 = second_region_vertices[(i + 1) % len(second_region_vertices)]
            edge = SeparatingAxisTheorem.__calculate_edge_vector(point_1, point_2)
            axes.append(edge)
        for axis in axes:
            min1, max1 = SeparatingAxisTheorem.__project_polygon(first_region_vertices, axis)
            min2, max2 = SeparatingAxisTheorem.__project_polygon(second_region_vertices, axis)
            if max1 < min2 or max2 < min1:
                return False
        return True
