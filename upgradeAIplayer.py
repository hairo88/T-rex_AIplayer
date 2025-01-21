import pygame
import sys
import random
import numpy as np
import os

# pygameの初期化
pygame.init()

# ウィンドウの設定
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("T-Rex Game AI")
clock = pygame.time.Clock()

# 色の定義
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
player_color = (0, 200, 0)
cactus_color = (0, 128, 0)

# プレイヤーの設定
player = pygame.Rect(100, 300, 40, 40)
player_velocity_y = 0
is_jumping = False
jump_power = -15
gravity = 0.8

# サボテンの設定
cacti = []
cactus_speed = 5
min_cactus_frequency = 1500
max_cactus_frequency = 2500
last_cactus_spawn_time = 0

# ゲームフラグ
score = 0
game_over = False

# Q学習のパラメータ
gamma = 0.9  # 割引率
alpha = 0.1  # 学習率
epsilon = 0.1  # 探索率

# Qテーブルの初期化
Q_TABLE_PATH = "q_table.npy"

def initialize_q_table(path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        try:
            q_table = np.load(path)
            print("Qテーブルを読み込みました。")
            return q_table
        except Exception as e:
            print(f"Qテーブルの読み込みに失敗しました: {e}")
    print("新しいQテーブルを作成しました。")
    return np.zeros((401, 801, 2))

q_table = initialize_q_table(Q_TABLE_PATH)

# サボテンを生成
def generate_cactus():
    cactus = pygame.Rect(800, 310, 20, 40)
    cacti.append(cactus)

# ゲーム状態の取得
def get_state():
    if cacti:
        cactus = cacti[0]
        return [min(player.y, 400), max(cactus.x, 0)]
    return [min(player.y, 400), 0]

# アクションの選択（ε-greedy法）
def select_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, 1)
    return np.argmax(q_table[state[0], state[1]])

# Q値の更新
def update_q_value(state, action, reward, next_state):
    old_q_value = q_table[state[0], state[1], action]
    future_q_value = np.max(q_table[next_state[0], next_state[1]])
    q_table[state[0], state[1], action] = old_q_value + alpha * (reward + gamma * future_q_value - old_q_value)

# ゲームループ
previous_score = 0  # 前回のスコアを保持する変数
while True:
    reward = 0  # rewardを初期化
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            np.save(Q_TABLE_PATH, q_table)
            print("Qテーブルを保存しました。")
            pygame.quit()
            sys.exit()

    if game_over:
        cacti.clear()
        player.y = 300
        player_velocity_y = 0
        is_jumping = False
        score = 0
        previous_score = 0
        game_over = False

    # 状態の取得
    state = get_state()

    # アクションの選択
    action = select_action(state)

    # ジャンプアクションの実行
    if action == 1 and not is_jumping:
        player_velocity_y = jump_power
        is_jumping = True

        # ジャンプしたときにスコアが増えていない場合に罰を与える
        if score == previous_score:
            reward = -0.015  # 罰を与える
        else:
            reward = 0  # スコアが増えている場合は罰を与えない

    # 重力処理
    player_velocity_y += gravity
    player.y += player_velocity_y

    # 地面判定
    if player.y >= HEIGHT - 90:
        player.y = HEIGHT - 90
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
    for cactus in cacti:
        if player.colliderect(cactus):
            reward = -1
            game_over = True

    # 次の状態を取得
    next_state = get_state()

    # Q値の更新
    update_q_value(state, action, reward, next_state)

    # 前回のスコアを更新
    previous_score = score

    # 描画処理
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, BROWN, (0, HEIGHT - 50, WIDTH, 50))
    pygame.draw.rect(screen, player_color, player)

    for cactus in cacti:
        pygame.draw.rect(screen, cactus_color, cactus)

    # スコア表示
    font = pygame.font.SysFont("Arial", 30)
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)