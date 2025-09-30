# ステップ2のコード
import os
import random
import sys
import time
import math  # mathモジュールを追加
import pygame as pg

WIDTH, HEIGHT = 1100, 650
BOMB_BASE_SPEED = 2  # 爆弾の基本速度を定数として定義
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface):
    # (ステップ1から変更なし)
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

# --- ここから追加 ---
def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    拡大率と加速度の異なる爆弾Surfaceリストと加速度リストを生成する
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs
# --- ここまで追加 ---
def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルに対応するこうかとんSurfaceを値とした辞書を返す
    """
    kk_base_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_imgs = {
        (0, 0): kk_base_img,
        (0, -5): pg.transform.rotozoom(pg.transform.flip(kk_base_img, True, False), 90, 1.0),
        (5, -5): pg.transform.rotozoom(pg.transform.flip(kk_base_img, True, False), 45, 1.0),
        (5, 0): pg.transform.flip(kk_base_img, True, False),
        (5, 5): pg.transform.rotozoom(pg.transform.flip(kk_base_img, True, False), -45, 1.0),
        (0, 5): pg.transform.rotozoom(pg.transform.flip(kk_base_img, True, False), -90, 1.0),
        (-5, 5): pg.transform.rotozoom(kk_base_img, -45, 1.0),
        (-5, 0): kk_base_img,
        (-5, -5): pg.transform.rotozoom(kk_base_img, 45, 1.0),
    }
    return kk_imgs

# --- ここから追加 ---
def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    爆弾から見たこうかとんの方向ベクトルを計算する
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    distance = math.sqrt(dx**2 + dy**2)
    if distance == 0:
        return 0, 0
    vx = dx / distance * BOMB_BASE_SPEED
    vy = dy / distance * BOMB_BASE_SPEED
    return vx, vy
# --- ここまで追加 ---

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_imgs = get_kk_imgs() # こうかとん画像辞書を初期化
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # --- ここから変更 ---
    bb_imgs, bb_accs = init_bb_imgs() # 爆弾リストを初期化
    bb_img = bb_imgs[0]
    # --- ここまで変更 ---
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5

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

        # --- ここから変更/追加 ---
        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        bb_rct.width = bb_img.get_width()
        bb_rct.height = bb_img.get_height()
        acc = bb_accs[idx]
        vx, vy = calc_orientation(bb_rct, kk_rct)
        bb_rct.move_ip(vx * acc, vy * acc)
        # --- ここまで変更/追加 ---

        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()