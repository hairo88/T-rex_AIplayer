import random
import numpy as np
import pygame
import sys

# ゲーム初期設定
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
player = pygame.Rect(100, 300, 40, 40)
player_color = (0, 200, 0)
player_velocity_y = 0
is_jumping = False
jump_power = -15
gravity = 0.8

# 障害物（サボテン）設定
cactus_color = (0, 128, 0)
cacti = []
cactus_speed = 5
min_cactus_frequency = 1500
max_cactus_frequency = 2500
last_cactus_spawn_time = 0

# ゲームフラグ
score = 0
game_over = False

# Q学習のパラメータ設定
gamma = 0.9  # 割引率
alpha = 0.1  # 学習率
epsilon = 0.1  # 探索率

# Qテーブルの初期化（簡略化のため状態空間を縮小）
q_table = np.zeros((41, 81, 2))  # Y位置: 0〜40, サボテンとの距離: 0〜80, アクション: 2種類

# サボテンを生成
def generate_cactus():
    cactus = pygame.Rect(800, 310, 20, 40)
    cacti.append(cactus)

# ゲーム状態の取得（離散化）
def get_state():
    if cacti:
        cactus = cacti[0]
        y_pos = min(max(player.y // 10, 0), 40)  # Y位置を0〜40の範囲に正規化
        distance = min(max((cactus.x - player.x) // 10, 0), 80)  # サボテンとの距離を0〜80の範囲に正規化
        return [y_pos, distance]
    return [0, 80]

# アクションの選択（ε-greedy法）
def select_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, 1)  # 探索（ランダム）
    return np.argmax(q_table[state[0], state[1]])  # 利用（最大Q値のアクションを選択）

# Q値の更新
def update_q_value(state, action, reward, next_state):
    old_q_value = q_table[state[0], state[1], action]
    future_q_value = np.max(q_table[next_state[0], next_state[1]])
    q_table[state[0], state[1], action] = old_q_value + alpha * (reward + gamma * future_q_value - old_q_value)

# ゲームのリセット
def reset_game():
    global player, cacti, player_velocity_y, is_jumping, score, game_over
    player = pygame.Rect(100, 300, 40, 40)
    cacti = []
    player_velocity_y = 0
    is_jumping = False
    score = 0
    game_over = False

# ゲームループ
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 状態の取得
    state = get_state()

    # アクションの選択
    action = select_action(state)

    if action == 1 and not is_jumping:
        player_velocity_y = jump_power
        is_jumping = True

    # 重力処理
    player_velocity_y += gravity
    player.y += player_velocity_y

    # 地面判定
    if player.y >= 300:
        player.y = 300
        player_velocity_y = 0
        is_jumping = False

    # サボテンの移動
    for cactus in cacti:
        cactus.x -= cactus_speed
        if cactus.x < -20:
            cacti.remove(cactus)
            score += 1

    # 新しいサボテンの生成
    current_time = pygame.time.get_ticks()
    if current_time - last_cactus_spawn_time > random.randint(min_cactus_frequency, max_cactus_frequency):
        generate_cactus()
        last_cactus_spawn_time = current_time

    # 衝突判定
    reward = 0
    for cactus in cacti:
        if player.colliderect(cactus):
            reward = -1  # 衝突した場合、負の報酬
            game_over = True

    # 次の状態を取得
    next_state = get_state()

    # Q値の更新
    update_q_value(state, action, reward, next_state)

    # ゲームオーバー処理
    if game_over:
        reset_game()
        continue

    # 描画処理
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, BROWN, (0, HEIGHT - 50, WIDTH, 50))
    pygame.draw.rect(screen, player_color, player)
    for cactus in cacti:
        pygame.draw.rect(screen, cactus_color, cactus)

    # スコアを表示
    font = pygame.font.SysFont("Arial", 30)
    score_text = font.render(f"Score: {score}", True, DARK_GRAY)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)
