class WorldInfo:

    __BLOCK_SIZE = 30
    __WORLD_MAP_SIZE = 100
    __HUB_WIDTH = 40
    __HUB_HEIGHT = 25
    __MINIMAL_ROOM_SIZE = 25
    __RENDER_CAPACITY = 40
    __COLLISION_CAPACITY = 6

    @staticmethod
    def get_hub_map_size() -> (int, int):
        return WorldInfo.__HUB_WIDTH, WorldInfo.__HUB_HEIGHT

    @staticmethod
    def get_hub_width() -> int:
        return WorldInfo.__HUB_WIDTH * WorldInfo.__BLOCK_SIZE

    @staticmethod
    def get_hub_height() -> int:
        return WorldInfo.__HUB_HEIGHT * WorldInfo.__BLOCK_SIZE

    @staticmethod
    def get_world_size() -> int:
        return WorldInfo.__WORLD_MAP_SIZE * WorldInfo.__BLOCK_SIZE

    @staticmethod
    def get_render_capacity() -> int:
        return WorldInfo.__RENDER_CAPACITY

    @staticmethod
    def get_collision_capacity() -> int:
        return WorldInfo.__COLLISION_CAPACITY

    @staticmethod
    def get_world_map_size() -> int:
        return WorldInfo.__WORLD_MAP_SIZE

    @staticmethod
    def get_minimal_room_size() -> int:
        return WorldInfo.__MINIMAL_ROOM_SIZE

    @staticmethod
    def get_block_size() -> int:
        return WorldInfo.__BLOCK_SIZE
