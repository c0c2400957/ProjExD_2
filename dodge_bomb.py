import os
import random
import sys
import time
import math
import pygame as pg

WIDTH, HEIGHT = 1100, 650
# 仕様に合わせて、ベクトルのノルム（大きさ）をsqrt(50)に設定
BOMB_NORM = math.sqrt(50)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    blackout = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(blackout, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    blackout.set_alpha(200)
    screen.blit(blackout, [0, 0])
    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect(center=(WIDTH/2, HEIGHT/2))
    screen.blit(txt, txt_rct)
    cry_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 2.0)
    cry_kk_rct = cry_kk_img.get_rect(center=(WIDTH/2, HEIGHT/2 + 100))
    screen.blit(cry_kk_img, cry_kk_rct)
    pg.display.update()
    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    kk_base_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    orientations = {
        (0, -5): (90, True), (5, -5): (45, True), (5, 0): (0, True),
        (5, 5): (-45, True), (0, 5): (-90, True), (-5, 5): (-45, False),
        (-5, 0): (0, False), (-5, -5): (45, False)
    }
    kk_imgs = {(0, 0): kk_base_img}
    for move, (angle, flip) in orientations.items():
        img = pg.transform.flip(kk_base_img, flip, False)
        kk_imgs[move] = pg.transform.rotozoom(img, angle, 1.0)
    return kk_imgs

# --- ここから関数定義を修正 ---
def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    爆弾から見たこうかとんの方向ベクトルを計算する
    ただし、距離が300未満の場合は慣性を優先する
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    distance = math.sqrt(dx**2 + dy**2)

    # 距離が300未満なら、現在の進行方向を維持する
    if distance < 300:
        return current_xy
    
    # 距離が300以上なら、新しく方向を計算する
    if distance == 0:
        return 0, 0 # ゼロ除算を避ける

    # ノルムがsqrt(50)になるように正規化
    vx = dx / distance * BOMB_NORM
    vy = dy / distance * BOMB_NORM
    return vx, vy
# --- ここまで関数定義を修正 ---

def main() -> None:
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    
    # --- ここから変更 ---
    # 爆弾の速度ベクトルをループの外で初期化し、保持する
    vx, vy = +5, +5 
    # --- ここまで変更 ---

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        delta = {
            pg.K_UP: (0, -5), pg.K_DOWN: (0, 5),
            pg.K_LEFT: (-5, 0), pg.K_RIGHT: (5, 0),
        }
        for key, mv in delta.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_img = kk_imgs[tuple(sum_mv)] if tuple(sum_mv) in kk_imgs else kk_imgs[(0, 0)]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        bb_rct.width = bb_img.get_width()
        bb_rct.height = bb_img.get_height()
        acc = bb_accs[idx]

        # --- ここから変更 ---
        # 現在の進行方向(vx, vy)を引数として渡す
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        bb_rct.move_ip(vx * acc, vy * acc)
        # --- ここまで変更 ---

        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()