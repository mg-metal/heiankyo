import pyxel
import stage as stg


PLAYER_IMG = [(8,0), (16,0), (24,0), (32,0), (40,0), (48,0), (128,0)]
ALIEN_IMG = [(64,8), (72,8), (80,8), (88,8), (96,8), (104,8),]
HOLE_IMG = [(0, 128), (8, 128), (0, 136), (8, 136), (16, 128), (16, 136), 
            (24, 128), (24, 136), (32, 128), (32, 136), (40, 128),]
IMG_BNK = 0


class GameObjectManager:
    def __init__(self, num, Obj) -> None:
        self.pool = []
        for i in range(num):
            self.pool.append(Obj())
    
    def add(self):
        for obj in self.pool:
            if obj.exists == False:
                obj.exists = True
                return obj
        return None
    
    def update(self):
        for obj in self.pool:
            if obj.exists:
                obj.update()

    def draw(self):
        for obj in self.pool:
            if obj.exists:
                obj.draw()

    def vanish(self):
        pass


class Hole:
    mgr = None
    @classmethod
    def add(cls, x, y):
        obj = cls.mgr.add()
        if obj != None:
            obj.init(x, y)

    def __init__(self) -> None:
        self.exists = False
        self.x = 0
        self.y = 0
        self.state = 0
        self.u, self.v = HOLE_IMG[0]
        self.num_digs = 0
        self.INTVAL_NUM_DIGS = 7
        self.INTVAL_ANIM = 16
        self.loopcnt = 0
        self.hold_time = 0

    def init(self, x, y):
        self.x = x
        self.y = y
        self.num_digs = 1
        self.state = 1
        self.loopcnt = 0
        self.hold_time = 0
        # self.exists = True

    def update(self):
        self.state = self.evaluate_digs()
        if self.state >= 6:
            self.hold_time += 1

        if self.state == 0 or self.state == 12:
            self.exists = False
            return
        self.u, self.v = self.set_uv()
        self.loopcnt += 1
        self.do_anim()

    def dig(self):
        if self.num_digs <= self.INTVAL_NUM_DIGS * 12:
            self.num_digs += 1

    def fill(self):
        if self.num_digs > 0:
            self.num_digs -= 1

    def delete(self):
        self.state = 0
        self.num_digs = 0

    def got_alien(self):
        if self.state == 5:
            self.state = 6
            return True
        if self.state < 5:
            self.delete()
        return False
    
    def get_hold_time(self):
        return self.hold_time

    def do_anim(self):
        if (self.state == 6 or self.state == 7) and self.loopcnt % self.INTVAL_ANIM == 0:
            self.state = 6 + 6 // self.state

    def set_uv(self):
        if self.state == 0:
            return (0, 0)
        return HOLE_IMG[self.state-1]
        
    def evaluate_digs(self):
        if self.state <= 5: # 穴掘り中なら
            if self.num_digs <= 0:
                return 0
            elif self.num_digs == self.INTVAL_NUM_DIGS * 1:            
                pyxel.play(3, 5)
                return 1
            elif self.num_digs == self.INTVAL_NUM_DIGS * 3:
                pyxel.play(3, 5)
                return 2
            elif self.num_digs == self.INTVAL_NUM_DIGS * 6:
                pyxel.play(3, 5)
                return 3
            elif self.num_digs == self.INTVAL_NUM_DIGS * 9:
                pyxel.play(3, 5)
                return 4
            elif self.num_digs == self.INTVAL_NUM_DIGS * 12:
                pyxel.play(3, 5)
                return 5

        if self.state >= 6: # 確保アニメ中なら
            if self.num_digs == self.INTVAL_NUM_DIGS * 12:
                pyxel.play(3, 6)
                return 8
            elif self.num_digs == self.INTVAL_NUM_DIGS * 9:
                self.hold_time = 20
                pyxel.play(3, 6)
                return 9
            elif self.num_digs == self.INTVAL_NUM_DIGS * 6:
                self.hold_time = 20
                pyxel.play(3, 6)
                return 10
            elif self.num_digs == self.INTVAL_NUM_DIGS * 3:
                self.hold_time = 20
                pyxel.play(3, 6)
                return 11
            elif self.num_digs == self.INTVAL_NUM_DIGS * 1:
                pyxel.play(3, 6)
                return 12   # 消滅
        return self.state

    def draw(self):
        pyxel.blt(self.x, self.y, IMG_BNK, self.u, self.v, 8, 8, 0)


class AliensManager(GameObjectManager):
    def update(self, stg:stg.Stage, holes:Hole):
        for obj in self.pool:
            if obj.exists:
                obj.update(stg, holes)

    def get_num_exists(self):
        num = 0
        for obj in self.pool:
            if obj.exists:
                num += 1
        return num


class Alien:
    mgr = None
    @classmethod
    def add(cls, tx, ty):
        obj = cls.mgr.add()
        if obj != None:
            obj.init(tx, ty)

    def __init__(self) -> None:
        self.exists = False
        self.tx = 0
        self.ty = 0
        self.speed = 1
        self.x = 0
        self.y = 0
        self.img_num = 2
        self.u, self.v = ALIEN_IMG[self.img_num]
        self.dirc = [0, 1]
        self.is_hold = False
        self.fallen_hole = None
        self.loopcnt = 0
        self.movecnt = 1

    def init(self, tx, ty):
        self.exists = True
        self.tx = tx
        self.ty = ty
        self.x = tx * 8
        self.y = ty * 8
        self.u, self.v = ALIEN_IMG[0]
        self.dirc = [0, -1]
        self.is_hold = False
        self.fallen_hole = None
        self.loopcnt = 0

    def update(self, stg:stg.Stage, holes:Hole):
        x = self.x
        y = self.y
        sp = self.speed

        for h in holes:
            if self.is_hold:
                break
            if h.exists and h.x+1 <= (x+4) <= h.x+7 and h.y+1 <= (y+4) <= h.y+7:
                self.is_hold = h.got_alien()
                if self.is_hold:
                    self.fallen_hole = h
                    self.x = self.tx * 8
                    self.y = self.ty * 8

        if self.is_hold:
            if self.fallen_hole.get_hold_time() > 100:
                self.fallen_hole.delete()
                self.is_hold = False
            if self.fallen_hole.exists == False:
                self.exists = False
            return

        if pyxel.btn(pyxel.KEY_UP) or self.dirc == [0, -1]:
            if stg.get_tile_name(x+1, y-sp) == "floor" and stg.get_tile_name(x+6, y-sp) == "floor":
                self.y -= self.speed
                self.movecnt += 1
        if pyxel.btn(pyxel.KEY_DOWN) or self.dirc == [0, 1]:
            if stg.get_tile_name(x+1, y+7+sp) == "floor" and stg.get_tile_name(x+6, y+7+sp) == "floor":
                self.y += self.speed
                self.movecnt += 1
        if pyxel.btn(pyxel.KEY_LEFT) or self.dirc == [-1, 0]:
            if stg.get_tile_name(x-sp, y+1) == "floor" and stg.get_tile_name(x-sp, y+6) == "floor":
                self.x -= self.speed
                self.movecnt += 1
        if pyxel.btn(pyxel.KEY_RIGHT) or self.dirc == [1, 0]:
            if stg.get_tile_name(x+7+sp, y+1) == "floor" and stg.get_tile_name(x+7+sp, y+6) == "floor":
                self.x += self.speed
                self.movecnt += 1

        self.loopcnt += 1
        if self.loopcnt % 24 == 0:
            self.movecnt = 1
            road_options = [-1, -1, -1, -1]
            road_options = self.detect_turn(stg, holes)
            dir = 0
            num = -1
            while num == -1:    # 壁以外を検知するまで
                dir = pyxel.rndi(0, 3)
                num = road_options[dir]
            if dir == 0:
                self.dirc = [0, -1]
                self.img_num = 2
            elif dir == 1:
                self.dirc = [0, 1]
                self.img_num = 0
            elif dir == 2:
                self.dirc = [-1, 0]
                self.img_num = 4
            elif dir == 3:
                self.dirc = [1, 0]
                self.img_num = 4

        self.update_tile_coodinate()

    def update_tile_coodinate(self):
        self.tx = (self.x + 4) // 8
        self.ty = (self.y + 4) // 8

    def detect_turn(self, stg:stg.Stage, holes:Hole):
        x = self.x
        y = self.y
        result = [-1, -1, -1, -1]   # up, dpwn, left, right
        def detect_hole(x, y):
            for h in holes:
                if h.exists and h.state >= 6 and h.x+1 <= x <= h.x+7 and h.y+1 <= y <= h.y+7:
                    return True
            return False
        if stg.get_tile_name(x+4, y-4) == "floor" and detect_hole(x+4, y-4) == False:
            result[0] = 1
        if stg.get_tile_name(x+4, y+7+3) == "floor" and detect_hole(x+4, y+7+3) == False:
            result[1] = 1
        if stg.get_tile_name(x-4, y+4) == "floor" and detect_hole(x-4, y+4) == False:
            result[2] = 1
        if stg.get_tile_name(x+7+3, y+4) == "floor" and detect_hole(x+7+3, y+4) == False:
            result[3] = 1
        return result
    
    def stop(self):
        self.speed = 0

    def draw(self):
        if self.is_hold:
            return
        flip = 1
        base_num = 0
        if self.dirc == [0, -1]:
            base_num = 2
        elif self.dirc == [0, 1]:
            base_num = 0
        elif self.dirc == [-1, 0]:
            base_num = 4
            flip = -1
        elif self.dirc == [1, 0]:
            base_num = 4

        if self.movecnt % 4 == 0:
            self.img_num = base_num + (base_num + 1 - self.img_num)
        self.u, self.v = ALIEN_IMG[self.img_num]
        pyxel.blt(self.x, self.y, IMG_BNK, self.u, self.v, 8 * flip, 8, 0)


class Player:
    def __init__(self, tx, ty) -> None:
        self.tx = tx
        self.ty = ty
        self.speed = 1
        self.x = tx * 8
        self.y = ty * 8
        self.dirc = [-1, 0]
        self.img_num = 4
        self.u, self.v = PLAYER_IMG[self.img_num]
        self.is_dig = False
        self.is_dead = False
        self.movecnt = 1

    def update(self, stg:stg.Stage, holes:Hole, aliens:Alien):
        if self.is_dead:
            self.y -= 0.5
            return
        x = self.x
        y = self.y
        sp = self.speed
        anykey_pressed = False
        self.is_dig = False
        def collision_holes(x, y):
            for h in holes:
                if h.exists and h.x <= x <= h.x+8 and h.y <= y <= h.y+8:
                    return True
            return False 
        if pyxel.btn(pyxel.KEY_W):
            anykey_pressed = True
            if self.dirc != [0, -1]:
                self.img_num = 2
            self.dirc = [0, -1]
            if stg.get_tile_name(x+1, y-sp) == "floor" and stg.get_tile_name(x+6, y-sp) == "floor" \
                and not collision_holes(x+3, y+2-sp):
                self.y -= self.speed
                self.movecnt += 1

        if pyxel.btn(pyxel.KEY_S):
            anykey_pressed = True
            if self.dirc != [0, 1]:
                self.img_num = 0
            self.dirc = [0, 1]
            if stg.get_tile_name(x+1, y+7+sp) == "floor" and stg.get_tile_name(x+6, y+7+sp) == "floor" \
                and not collision_holes(x+3, y+7-2+sp):
                self.y += self.speed
                self.movecnt += 1

        if pyxel.btn(pyxel.KEY_A):
            anykey_pressed = True
            if self.dirc != [-1, 0]:
                self.img_num = 4
            self.dirc = [-1, 0]
            if stg.get_tile_name(x-sp, y+1) == "floor" and stg.get_tile_name(x-sp, y+6) == "floor" \
                and not collision_holes(x-sp, y+3):
                self.x -= self.speed
                self.movecnt += 1

        if pyxel.btn(pyxel.KEY_D):
            anykey_pressed = True
            if self.dirc != [1, 0]:
                self.img_num = 4
            self.dirc = [1, 0]
            if stg.get_tile_name(x+7+sp, y+1) == "floor" and stg.get_tile_name(x+7+sp, y+6) == "floor" \
                and not collision_holes(x+7+sp, y+3):
                self.x += self.speed
                self.movecnt += 1

        if pyxel.btn(pyxel.KEY_J):
            anykey_pressed = True
            self.is_dig = False
            gx = ((x+4+self.dirc[0]*6) // 8 ) * 8 
            gy = ((y+4+self.dirc[1]*6) // 8 ) * 8 
            for h in holes:
                if h.exists == False:
                    continue
                if h.x == gx and h.y == gy:
                    h.dig()
                    self.is_dig = True
                    break
            if (not self.is_dig) and stg.get_tile_name(gx, gy) == "floor":
                Hole.add(gx, gy) 
                self.is_dig = True
            self.movecnt += 1
            

        if pyxel.btn(pyxel.KEY_K):
            anykey_pressed = True
            for h in holes:
                if h.x <= (x+4+self.dirc[0]*6) <= h.x+8 and h.y <= (y+4+self.dirc[1]*6) <= h.y+8:
                    h.fill()
                    break
            self.movecnt += 1

        if anykey_pressed == False:
            self.movecnt = 1

        for alien in aliens:
            if alien.exists and (alien.x+1) <= (x+3) and (x+5) <= (alien.x+6) and (alien.y+1) <= (y+3) and (y+5) <= (alien.y+6):
                self.is_dead = True
                self.img_num = 6
                self.u, self.v = PLAYER_IMG[self.img_num]
                alien.stop()
                pyxel.play(3, 7)
                break

        self.update_tile_coodinate()

    def update_tile_coodinate(self):
        self.tx = (self.x + 4) // 8
        self.ty = (self.y + 4) // 8

    def draw(self):
        flip = 1
        if self.img_num != 6:
            base_num = 0
            if self.dirc == [0, -1]:
                base_num = 2
            elif self.dirc == [0, 1]:
                base_num = 0
            elif self.dirc == [-1, 0]:
                base_num = 4
                flip = -1
            elif self.dirc == [1, 0]:
                base_num = 4

            anim_span = 4
            if self.is_dig:
                anim_span = 2
            if self.movecnt % anim_span == 0:
                self.img_num = base_num + (base_num + 1 - self.img_num)
        self.u, self.v = PLAYER_IMG[self.img_num]
        pyxel.blt(self.x, self.y, IMG_BNK, self.u, self.v, 8 * flip, 8, 0)


class App():
    def __init__(self) -> None:
        pyxel.init(80, 80)
        pyxel.load("sample.pyxres")
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self):
        self.player = Player(5, 5)
        self.stg = stg.Stage()
        Hole.mgr = GameObjectManager(10, Hole)
        Alien.mgr = AliensManager(3, Alien)
        Alien.add(5, 1)
        Alien.add(4, 3)

        self.level = 0
        self.gamestart = False
        self.stageclear = False
        self.stageclear_waittime = 30
        self.gameclear = False
        self.failure = False
        self.loopcnt = 0    # 経過時間用のフレームカウンタ      Memo: pyxel.frame_countは止められないので別途用意
        self.highscore = 0.0

    def update(self):
        if self.failure and pyxel.btnp(pyxel.KEY_SPACE):
            self.init()
            self.failure = False
        self.stg.update()
        self.player.update(self.stg, Hole.mgr.pool, Alien.mgr.pool)
        Hole.mgr.update()
        Alien.mgr.update(self.stg, Hole.mgr.pool)
        if Alien.mgr.get_num_exists() == 0:
            self.gameclear = True

    def draw(self):
        pyxel.cls(0)
        self.stg.draw()
        self.player.draw()
        Hole.mgr.draw()
        Alien.mgr.draw()
        if self.gameclear:
            pyxel.text(20, 35, "GAME CLEAR!", 14)
            pyxel.text(11, 47, "Press SPACE KEY", 7)
        if self.player.y < -10:
            self.failure = True
            pyxel.text(20, 35, "GAME OVER", 13)
            pyxel.text(11, 47, "Press SPACE KEY", 7)
App()