import pyxel

tile_dict = {
    "floor": (0, 0),
    "footprint": (0, 4),
    "tree1": (1, 12),
    "tree2": (3, 12),
    "wall": (1, 13),
    "up_st": (14, 14),
    "down_st": (15, 14),
}

level = [
    # u, v, w, h  値はマス数で。
    [0, 0, 8, 8],
    [8, 0, 8, 8],
    [16, 0, 8, 8],
]

class Stage:
    def __init__(self) -> None:
        # Memo: w,h固定
        self.num = 2     # tilemap No.
        self.num_u = 0       # tilemap 始点xマス数 
        self.num_v = 0       # tilemap 始点yマス数
        self.u = 0       # tilemap 始点x
        self.v = 0       # tilemap 始点y
        self.t_len = 8   # tile 長さ(固定)
        self.num_w = 8   # tilemap 幅マス数
        self.num_h = 8   # tilemap 高さマス数
        self.w = self.num_w * self.t_len   # tilemap 幅
        self.h = self.num_h * self.t_len   # tilemap 高さ
        self.ofs_x = 0   # tilemap 画面描画オフセット x
        self.ofs_y = 0   # tilemap 画面描画オフセット y
        self.mc_visible = False

    def update(self):
        pass

    def draw(self):
        pyxel.bltm(self.ofs_x, self.ofs_y, 
                   self.num, self.u, self.v, self.w, self.h)
        if self.mc_visible:
            mx = pyxel.mouse_x
            my = pyxel.mouse_y
            tile_name = self.get_tile_name(mx, my)
            pyxel.text(mx+6, my-2, tile_name, 6)

    def change_level(self, num):
        pass
    
    def get_tile_name(self, x, y):
        if self.is_outside(x, y):
            return "OUTSIDE"
        x = x - self.ofs_x
        y = y - self.ofs_y
        img_pos = pyxel.tilemap(self.num).pget(
            int(x/self.num_w) + self.num_u, 
            int(y/self.num_h) + self.num_v)
        tile_name = "NONE"
        for k, v  in tile_dict.items():
            if img_pos == v:
                tile_name = k
                break
        return tile_name
    
    def get_tile_poslist(self, name):
        tile_poslist = []
        find = False
        for k in tile_dict.keys():
            if name == k:
                find = True
                break
        if not find:
            return tile_poslist.append((-999, -999))
            
        img_pos1 = tile_dict[name]
        for i in range(self.num_h):
            for j in range(self.num_w):
                img_pos2 = pyxel.tilemap(self.num).pget(j + self.num_u, i + self.num_v)
                if img_pos1 == img_pos2:
                    tile_poslist.append((j, i))
        return tile_poslist

    def replace_all_tile(self, name1, name2):
        find = 0
        for k, v in tile_dict.items():
            if name1 == k or name2 == k:
                find += 1
        if find != 2:
            return False
        img_pos1 = tile_dict[name1]
        img_pos2 = tile_dict[name2]
        for i in range(self.num_h):
            for j in range(self.num_w):
                img_pos_tmp = pyxel.tilemap(self.num).pget(j + self.num_u, i + self.num_v)
                if img_pos_tmp == img_pos1:
                    pyxel.tilemap(self.num).pset(j + self.num_u, i + self.num_v, img_pos2)
        return True

    def replace_tile(self, x, y, name):
        for k, v in tile_dict.items():
            if name == k:
                pyxel.tilemap(self.num).pset(
                    int(x/self.num_w) + self.num_u, 
                    int(y/self.num_h) + self.num_v, 
                    v)
                return True
        return False
        
    def is_outside(self, x, y):
        x = x - self.ofs_x
        y = y - self.ofs_y
        if (0 <= x < self.w) and (0 <= y < self.h):
            return False
        return True

