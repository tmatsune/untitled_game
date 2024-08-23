import pygame as pg, os, json
import src.settings as s
import src.utils as utils 

hitable_tilesets = {'tileset_0', 'tileset_1', 'tileset_2'}

# ------- AUTOTILE ------- #
top_left = 0
top_center = 1
top_right = 2
mid_left = 3
mid_center = 4
mid_right = 5
bottom_left = 6
bottom_center = 7
bottom_right = 8
auto_tile_config: dict = {
    ((0, 1), (1, 0)): top_left,
    ((-1, 0), (0, 1), (1, 0)): top_center,
    ((-1, 0), (0, 1)): top_right,
    ((0, -1), (0, 1), (1, 0)): mid_left,
    ((-1, 0), (0, -1), (0, 1), (1, 0)): mid_center,
    ((-1, 0), (0, -1), (0, 1)): mid_right,
    ((0, -1), (1, 0)): bottom_left,
    ((-1, 0), (0, -1), (1, 0)): bottom_center,
    ((-1, 0), (0, -1)): bottom_right,
}

# ------- OFFSETS ------- #
tile_offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
NEARBY_OFFSET = [[-1, 0], [0, 0], [1, 0], [-1, -1],
                 [0, -1], [1, -1], [-1, 1], [0, 1], [1, 1]]
for p in [[[x - 2, y - 2] for x in range(5)] for y in range(5)]:
    NEARBY_OFFSET += p

HIT_TILE_PATH = 'src/images/tiles/tileset/'
OBJ_TILE_PATH = 'src/images/tiles/objects/'

'''
    Tile Map:
        - hash table
            - pos (x,y)
                - layers (-1,0,1)
                    - tiles
                        [tile_type, tile_name, tile_id, tile_img_path, tile_image] 
                        ['bg_tiles', 'bg_tiles_0', '2', 'src/tiles/bg_tiles/bg_tiles_0/1.png', <Surface(16x16x32 SW)>]
'''


def tuple_to_str(tuple):
    key = f'{tuple[0]},{tuple[1]}'
    return key

def str_to_tuple(str):
    key = str.split(',')
    return (int(key[0]), int(key[1]))

class TileMap:
    def __init__(self, app) -> None:
        self.app = app
        self.tiles = {}
        self.objects = {}
        self.markers = {}
        self.all_layers = []

    def get_visible_tiles(self, offset=[0,0]):
        layers = {l: [] for l in self.all_layers}
        for c in range(int(0 + offset[0] // s.CELL_SIZE) - 1, int((s.COLS * s.CELL_SIZE + offset[0]) // s.CELL_SIZE) + 2):
            for r in range(int(0 + offset[1] // s.CELL_SIZE) - 1, int((s.ROWS * s.CELL_SIZE + offset[1]) // s.CELL_SIZE) + 2):
                pos = (c, r)
                if pos in self.tiles:
                    for layer, data in self.tiles[pos].items():
                        tile_data = [pos] + data
                        layers[int(layer)].append(tile_data)
        return layers

    def get_nearby_tiles(self, pos):
        p = [int(pos[0] // s.CELL_SIZE), int(pos[1] // s.CELL_SIZE)]
        tiles = []
        for offset in NEARBY_OFFSET:
            key = (p[0] + offset[0], p[1] + offset[1])
            if key in self.tiles:
                for layer in self.tiles[key]:
                    if self.tiles[key][layer][2] in {'tileset_0', 'tileset_1'}:
                        tiles.append(pg.Rect(key[0] * s.CELL_SIZE, key[1] * s.CELL_SIZE, s.CELL_SIZE, s.CELL_SIZE))
        return tiles

    def load_map(self, map_name):
        self.reset_map()
        new_tiles = {}
        new_markers = {}

        path = f'{s.MAP_PATH}{map_name}.json'
        fl = open(path, 'r')
        map_data = json.load(fl)
        fl.close()

        for k, layers in map_data['tiles'].items():
            key = str_to_tuple(k)
            new_tiles[key] = {}

            for layer, tile in layers.items():
                tile.append(utils.get_image(tile[3], tile[4]['size']))
                tile.insert(0, (key[0]*s.CELL_SIZE, key[1]*s.CELL_SIZE))
                new_tiles[key][layer] = tile

        if 'markers' in map_data:
            for k, marker in map_data['markers'].items():
                key = str_to_tuple(k)
                new_markers[key] = marker

        self.tiles = new_tiles
        self.all_layers = map_data['all_layers']
        self.all_layers.sort()

        return new_markers

    def reset_map(self):
        self.tiles = {}
        self.objects = {}
        self.markers = {}
        self.all_layers = []

# tile: (0,0): ['tileset', 'tileset_1', '0', 'src/tiles/tileset/tileset_1/0.png', <Surface(16x16x32 SW)>]
class Tile_Editor:
    def __init__(self, app) -> None:
        self.app = app
        self.tile_data = []
        self.tile_map = TileMap(self)
        self.layers = set()
        self.tiles = {}
        self.markers = {}
        self.get_tile_data()

    def add_tile(self, pos, tile_data, layer):
        key = (int(pos[0]), int(pos[1]))
        if tile_data[0] == 'markers':
            self.markers[key] = tile_data
            return 
        if layer not in self.layers:
            self.layers.add(layer)
        if key not in self.tile_map.tiles:
            self.tile_map.tiles[key] = {}
            self.tile_map.tiles[key][layer] = tile_data
        self.tile_map.tiles[key][layer] = tile_data

    def remove_tile(self, pos, layer):
        key = (int(pos[0]), int(pos[1]))
        if key in self.tile_map.tiles:
            if layer in self.tile_map.tiles[key]:
                del self.tile_map.tiles[key][layer]
                if len(self.tile_map.tiles[key]) == 0:
                    del self.tile_map.tiles[key]

    def auto_tile(self, starting_pos, tileset_imgs, layer):
        v = set()
        key = tuple(starting_pos)
        if key not in self.tile_map.tiles:
            print('pos not in tile map')
            return
        if layer not in self.tile_map.tiles[key]:
            print('pos in tile map, but incorrect layer')
            return
        
        # ['tileset', 'tileset_1', '0', 'src/tiles/tileset/tileset_1/0.png', <Surface(16x16x32 SW)>]
        def dfs(pos, v: set):
            if pos in v:
                return
            v.add(pos)
            nearby_tiles = []
            neighbors = []
            for offset in tile_offsets:
                search_pos = (pos[0] + offset[0], pos[1] + offset[1])
                if search_pos in self.tile_map.tiles and layer in self.tile_map.tiles[search_pos]:
                    nearby_tiles.append(offset)
                    neighbors.append(search_pos)
            auto_tile_key = tuple(sorted(nearby_tiles))
            if auto_tile_key in auto_tile_config:
                tile_imgs = sorted(tileset_imgs)
                self.tile_map.tiles[pos][layer][-1] = utils.get_image(tile_imgs[auto_tile_config[auto_tile_key]], [s.CELL_SIZE,s.CELL_SIZE])
                self.tile_map.tiles[pos][layer][2] = str(auto_tile_config[auto_tile_key])

                # NOTE might have to change it auto tile gets more complex, but fine for now NOTE
                self.tile_map.tiles[pos][layer][3] = self.auto_tile_new_tile_path(self.tile_map.tiles[pos][layer], auto_tile_config[auto_tile_key])

            for n in neighbors:
                dfs(n, v)
        dfs(key, v)

    def auto_tile_new_tile_path(self, tile, new_id): return f'{s.TILES_PATH}{tile[0]}/{tile[1]}/{new_id}.png'

    def flood_fill(self, starting_pos, layer):
        pass

    def test_render(self, surf, offset=[0, 0]):
        for c in range(int(0 + offset[0] // s.CELL_SIZE) - 1, int((s.COLS * s.CELL_SIZE + offset[0]) // s.CELL_SIZE) + 2):
            for r in range(int(0 + offset[1] // s.CELL_SIZE) - 1, int((s.ROWS * s.CELL_SIZE + offset[1]) // s.CELL_SIZE) + 2):
                pos = (c, r)
                if pos in self.tile_map.tiles:
                    for layer, data in self.tile_map.tiles[pos].items():
                        surf.blit(data[-1], ( (pos[0] * s.CELL_SIZE) - offset[0], (pos[1] * s.CELL_SIZE) - offset[1]) )
                if pos in self.markers:
                    surf.blit(self.markers[pos][-1], ( (pos[0] * s.CELL_SIZE) - offset[0], (pos[1] * s.CELL_SIZE) - offset[1]) )

    def get_visible_tiles(self, offset=[0,0]):
        layers = {l: [] for l in self.all_layers}
        objects = []
        for c in range(int(0 + offset[0] // s.CELL_SIZE) - 1, int((s.COLS * s.CELL_SIZE + offset[0]) // s.CELL_SIZE) + 2):
            for r in range(int(0 + offset[1] // s.CELL_SIZE) - 1, int((s.ROWS * s.CELL_SIZE + offset[1]) // s.CELL_SIZE) + 2):
                pos = (c, r)
                if pos in self.tile_map:
                    for layer, data in self.tile_map[pos].items():
                        tile_data = [pos] + data
                        layers[layer].append(tile_data)
                if pos in self.objects:
                    data = self.objects[pos]
                    tile = [pos] + data
                    objects.append(tile)
        return layers
    
    def save_map(self, map_name):
        saved_tiles = {} 
        saved_markers = {}
        layers_found = set()

        for key, layer in self.tile_map.tiles.items():
            layers_copy = {}
            for l_num, tile in layer.items():
                layers_copy[str(l_num)] = [tile[0], tile[1], tile[2], tile[3], tile[4]]
            saved_tiles[tuple_to_str(key)] = layers_copy
            for layer in layer:
                layers_found.add(l_num)

        for key, marker in self.markers.items():
            saved_markers[tuple_to_str(key)] = [marker[0], marker[1], marker[3]]

        layers = []
        for l in layers_found:
            layers.append(l)

        path = f'{s.MAP_PATH}/{map_name}.json'
        fl = open(path, 'w')
        json.dump({
            'all_layers': layers,
            'tiles': saved_tiles,
            'markers': saved_markers
        }, fl)
        fl.close()

    def reset_map(self):
        self.map.tiles = {}
        self.layers = set()

    def load_map(self, map_name):
        new_tiles = {}
        new_markers = {}
        all_layers = set()

        path = f'{s.MAP_PATH}{map_name}'
        fl = open(path, 'r')
        map_data = json.load(fl)
        fl.close()

        for k, layers in map_data['tiles'].items():
            key = str_to_tuple(k)
            new_tiles[key] = {}

            for layer, tile in layers.items():
                tile.append(utils.get_image(tile[3], tile[4]['size']))
                new_tiles[key][layer] = tile

        for k, marker in map_data['markers'].items():
            key = str_to_tuple(k)
            marker.append(utils.get_image(marker[2], [s.CELL_SIZE, s.CELL_SIZE]))
            new_markers[key] = marker

        self.tile_map.tiles = new_tiles
        self.markers = new_markers
        self.tile_map.all_layers = map_data['all_layers']

    def get_tile_data(self):
        # TILE_TYPES: tileset, bg_tiles, objects, markers
        # tileset are main tiles in game that entities cant get passed
        # bg_tiles are background tiles that arent meant to be interracted with NOTE: might be worth to cache it depending on size of bg
        # objects can have mutiple types with their own attributes
        # markere are spawn points for player, enemies, weapons, etc
        tileset_names = os.listdir(s.TILESET_PATH)
        bg_tile_names = os.listdir(s.BG_TILES_PATH)
        obj_names = os.listdir(s.OBJECTS_PATH)
        marker_names = os.listdir(s.MARKERS_PATH)
        decor_names = os.listdir(s.DECOR_PATH)

        # [tile_type:str, tile_name:str, images:list, config:dict]
        tilesets = []
        for tile_name in tileset_names:
            tile_ids = os.listdir(s.TILESET_PATH + f'{tile_name}')
            tile_ids.sort()
            tileset_images_paths = []
            config = None
            for tile_id in tile_ids:
                if tile_id[-3:] == 'png':
                    full_tileset_path = f'{s.TILESET_PATH}{tile_name}/{tile_id}'
                    tileset_images_paths.append(full_tileset_path)
                else:
                    f = open(f'{s.TILESET_PATH}{tile_name}/{tile_id}', 'r')
                    config = json.loads(f.read())
            tilesets.append(
                ['tileset', tile_name, tileset_images_paths, config])
        self.tile_data.append(tilesets)

        bg_tiles = []
        for bg_tile_name in bg_tile_names:
            bg_tile_ids = os.listdir(s.BG_TILES_PATH + f'{bg_tile_name}')
            bg_tile_ids.sort()
            bg_tiles_images_paths = []
            config = None
            for tile_id in bg_tile_ids:
                if tile_id[-3:] == 'png':
                    full_tileset_path = f'{s.BG_TILES_PATH}{bg_tile_name}/{tile_id}'
                    bg_tiles_images_paths.append(full_tileset_path)
                else:
                    f = open(f'{s.BG_TILES_PATH}{bg_tile_name}/{tile_id}', 'r')
                    config = json.loads(f.read())
            bg_tiles.append(['bg_tiles', bg_tile_name, bg_tiles_images_paths, config])
        self.tile_data.append(bg_tiles)

        decors = []
        for decor_name in decor_names:
            decor_ids = os.listdir(s.DECOR_PATH + f'{decor_name}')
            decor_ids.sort()
            decor_images_paths = []
            config = None
            for decor_id in decor_ids:
                if decor_id[-3:] == 'png':
                    full_decor_path = f'{s.DECOR_PATH}{decor_name}/{decor_id}'
                    decor_images_paths.append(full_decor_path)
                else:
                    f = open(f'{s.DECOR_PATH}{decor_name}/{decor_id}', 'r')
                    config = json.loads(f.read())
            decors.append(['decor', decor_name, decor_images_paths, config])
        self.tile_data.append(decors)

        markers = []
        for marker_name in marker_names:
            marker_path = f'{s.MARKERS_PATH}{marker_name}'
            markers.append(['markers', marker_name, marker_path])
        self.tile_data.append(markers)

        '''
            [
                [
                    [tile_type:str, tile_name:str, images:list, config:dict],
                    [tile_type:str, tile_name:str, images:list, config:dict],
                ]
            ]
        '''
        
