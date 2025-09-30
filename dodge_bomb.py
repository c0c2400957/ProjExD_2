# ステップ1のコード
import os
import random
import sys
import time  # timeモジュールを追加
import pygame as pg

WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate

# --- ここから追加 ---
def gameover(screen: pg.Surface):
    """
    ゲームオーバー画面を表示し、5秒後にゲームを終了する
    """
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
# --- ここまで追加 ---

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
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

        # --- ここから変更 ---
        if kk_rct.colliderect(bb_rct):
            gameover(screen)  # ゲームオーバー関数を呼び出す
            return
        # --- ここまで変更 ---

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

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        bb_rct.move_ip(vx, vy)
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