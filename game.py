import pygame
import sys
import random

# 初期設定
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("T-Rex Game")
clock = pygame.time.Clock()

# 色定義
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
DARK_GRAY = (169, 169, 169)
SKY_BLUE = (135, 206, 235)

# プレイヤー（恐竜）設定
player = pygame.Rect(100, 300, 40, 40)  # 恐竜の大きさ
player_color = (0, 200, 0)
player_velocity_y = 0
is_jumping = False
jump_power = -15
gravity = 0.8

# 障害物（サボテン）設定
cactus_color = (0, 128, 0)
cacti = []
cactus_speed = 5
min_cactus_frequency = 1500  # サボテンの最小出現間隔（ミリ秒）
max_cactus_frequency = 2500  # サボテンの最大出現間隔（ミリ秒）
last_cactus_spawn_time = 0  # 最後にサボテンが出現した時間（ミリ秒）

# ゲームのフラグ
score = 0
game_over = False

# サボテン生成
def generate_cactus():
    cactus_height = random.randint(30, 70)
    cactus_x = WIDTH
    cactus = pygame.Rect(cactus_x, HEIGHT - cactus_height - 50, 20, cactus_height)
    cacti.append(cactus)

# サボテンの速度をスコアに応じて増加
def update_cactus_speed():
    global cactus_speed
    if score > 300:
        cactus_speed = 10
    elif score > 200:
        cactus_speed = 8
    elif score > 100:
        cactus_speed = 7
    else:
        cactus_speed = 5

# ゲームループ
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # 入力処理
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not is_jumping:
        player_velocity_y = jump_power
        is_jumping = True

    # 重力処理
    player_velocity_y += gravity
    player.y += player_velocity_y

    # 地面判定
    if player.colliderect(pygame.Rect(0, HEIGHT - 50, WIDTH, 50)):
        player.y = HEIGHT - 90
        player_velocity_y = 0
        is_jumping = False

    # サボテンの移動
    for cactus in cacti:
        cactus.x -= cactus_speed
        if cactus.x < -20:  # サボテンが画面外に出たら削除
            cacti.remove(cactus)
            score += 1

    # 新しいサボテンの生成
    current_time = pygame.time.get_ticks()
    if current_time - last_cactus_spawn_time > random.randint(min_cactus_frequency, max_cactus_frequency):
        generate_cactus()
        last_cactus_spawn_time = current_time  # サボテンの最後の出現時間を更新

    # サボテンの速度更新
    update_cactus_speed()

    # 衝突判定（サボテンと恐竜）
    for cactus in cacti:
        if player.colliderect(cactus):
            game_over = True

    # 描画処理
    screen.fill(SKY_BLUE)  # 背景を空の色に設定
    pygame.draw.rect(screen, BROWN, (0, HEIGHT - 50, WIDTH, 50))  # 地面

    # プレイヤー（恐竜）を描画
    pygame.draw.rect(screen, player_color, player)

    # サボテンを描画
    for cactus in cacti:
        pygame.draw.rect(screen, cactus_color, cactus)

    # スコアを表示
    font = pygame.font.SysFont("Arial", 30)
    score_text = font.render(f"Score: {score}", True, DARK_GRAY)
    screen.blit(score_text, (10, 10))

    # ゲームオーバー画面
    if game_over:
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
sys.exit()
