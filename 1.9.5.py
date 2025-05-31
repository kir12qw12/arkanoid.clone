import json
import os
import random
import pygame
import math

pygame.init()
             #Значения бонусов
                                #1 bonus1 Увеличение платформы
                                #2 bonus2 Двойной шар
                                #3 bonus3 Умножение каждого шара на 3
                                #4 bonus4 Пол снизу

   #Иконка бонусов
# Загрузка иконок бонусов
bonus_icons = {
    1: pygame.transform.scale(pygame.image.load("bonus1.png"), (64, 64)),
    2: pygame.transform.scale(pygame.image.load("bonus2.png"), (64, 64)),
    3: pygame.transform.scale(pygame.image.load("bonus3.png"), (64, 64)),
    4: pygame.transform.scale(pygame.image.load("bonus4.png"), (64, 64)),
}

      #Музыка
pygame.mixer.music.load("background.mp3")  # или .ogg
pygame.mixer.music.set_volume(0.3)  # громкость от 0.0 до 1.0
pygame.mixer.music.play(-1)  # -1 — бесконечный цикл

WIDTH, HEIGHT = 1920, 1080
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLOCK_COLORS = [
    (255, 100, 100),
    (100, 255, 100),
    (100, 100, 255),
    (255, 255, 100),
    (255, 100, 255)
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arkanoid Clone")

# Звуки (укажи свои пути)
bounce_sound = pygame.mixer.Sound("bounce.wav")
bonus_sound = pygame.mixer.Sound("bonus.wav")
pygame.mixer.music.set_volume(0.3)


SAVE_FILE = "save_data.json"
if not os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "w") as f:
        json.dump({"unlocked_levels": 1, "high_scores": [0]*15}, f)

with open(SAVE_FILE) as f:
    save_data = json.load(f)

unlocked_levels = save_data["unlocked_levels"]
high_scores = save_data["high_scores"]

class Paddle(pygame.Rect):
    def __init__(self):
        super().__init__(WIDTH // 2 - 100, HEIGHT - 50, 200, 20)
        self.speed = 15

    def move(self, direction):
        if direction == "left" and self.left > 0:
            self.left -= self.speed
        if direction == "right" and self.right < WIDTH:
            self.left += self.speed

class Ball:
    def __init__(self):
        self.radius = 10
        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed_x = 7 * random.choice([-1, 1])
        self.speed_y = -7

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            self.speed_x *= -1
            bounce_sound.play()
        if self.y - self.radius <= 0:
            self.speed_y *= -1
            bounce_sound.play()

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

class Block(pygame.Rect):
    def __init__(self, x, y, color, bonus_type=0, unbreakable=False):
        super().__init__(x, y, 100, 40)
        self.color = color
        self.bonus_type = bonus_type
        self.unbreakable = unbreakable

    def draw(self):
        col = self.color if not self.unbreakable else (80, 80, 80)  # серый цвет для неразбиваемых
        pygame.draw.rect(screen, col, self)

class Bonus:
    def __init__(self, x, y, bonus_type):
        self.rect = pygame.Rect(x, y, 64, 64)  # размер 64x64
        self.speed = 5
        self.type = bonus_type

    def move(self):
        self.rect.y += self.speed

    def draw(self):
        icon = bonus_icons.get(self.type)
        if icon:
            screen.blit(icon, self.rect)
        else:
            # fallback, если иконки нет
            color_map = {
                1: (0, 255, 0),
                2: (255, 0, 0),
                3: (0, 0, 255),
                4: (255, 255, 0)
            }
            pygame.draw.rect(screen, color_map.get(self.type, (0, 255, 255)), self.rect)

def create_blocks_for_level(level_num):
    blocks = []

    block_w, block_h = 100, 40
    margin_x = 10
    margin_y = 60
    cols = 16
    rows = 10

    def add_block(col, row, bonus_type=0, unbreakable=False):
        x = col * (block_w + 5) + margin_x
        y = row * (block_h + 10) + margin_y
        color = BLOCK_COLORS[(row + col) % len(BLOCK_COLORS)]
        blocks.append(Block(x, y, color, bonus_type, unbreakable))

    if level_num == 0:
        # Простой ровный ряд блоков
        for r in range(5):
            for c in range(cols):
                bonus = random.randint(1,4) if random.random() < 0.2 else 0
                add_block(c, r, bonus)
    elif level_num == 1:
        # Крест
        for r in range(7):
            for c in range(cols):
                if c == r or c == cols - 1 - r:
                    bonus = random.randint(1,4) if random.random() < 0.25 else 0
                    add_block(c, r, bonus)
    elif level_num == 2:
        # Трапеция
        for r in range(7):
            start = r
            end = cols - r - 1
            for c in range(start, end + 1):
                bonus = random.randint(1,4) if random.random() < 0.2 else 0
                add_block(c, r, bonus)
    elif level_num == 3:
        # Круг/овал
        mid = cols // 2
        for r in range(7):
            for c in range(cols):
                if abs(c - mid) + abs(r - 3) <= 3:
                    bonus = random.randint(1,4) if random.random() < 0.15 else 0
                    add_block(c, r, bonus)
    elif level_num == 4:
        # Волна
        for r in range(6):
            for c in range(cols):
                wave = int(3 * (1 + math.sin(c / 2.0)))
                if r == wave or r == wave + 1:
                    bonus = random.randint(1,4) if random.random() < 0.2 else 0
                    add_block(c, r, bonus)

    else:
        # С 5 по 14 уровни: добавляем неразбиваемые блоки + бонусы
        for r in range(3):
            for c in range(cols):
                bonus = random.randint(1,4) if random.random() < 0.15 else 0
                add_block(c, r, bonus)

        # Неразбиваемые блоки на разных позициях для разных уровней
        unbreak_positions = {
            5: [(4,4),(5,4),(6,4),(9,4),(10,4),(11,4)],
            6: [(2,5),(3,5),(12,5),(13,5)],
            7: [(0,6),(1,6),(14,6),(15,6)],
            8: [(7,4),(8,4),(7,5),(8,5)],
            9: [(6,7),(7,7),(8,7),(9,7)],
            10: [(5,5),(6,5),(9,5),(10,5)],
            11: [(3,8),(4,8),(11,8),(12,8)],
            12: [(1,3),(2,3),(13,3),(14,3)],
            13: [(5,6),(6,6),(7,6),(8,6)],
            14: [(0,9),(1,9),(14,9),(15,9)]
        }
        positions = unbreak_positions.get(level_num, [])
        for pos in positions:
            c, r = pos
            add_block(c, r, bonus_type=0, unbreakable=True)

    return blocks

def draw_text(text, size, x, y, center=True):
    font = pygame.font.SysFont("comic sans ms", size)
    render = font.render(text, True, WHITE)
    rect = render.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(render, rect)

def save_progress():
    with open(SAVE_FILE, "w") as f:
        json.dump({
            "unlocked_levels": unlocked_levels,
            "high_scores": high_scores
        }, f)

def level_menu():
    global unlocked_levels  # Убедитесь, что вы можете изменять переменную
    current_level = 0  # Начальный уровень
    running = True
    while running:
        screen.fill(BLACK)
        draw_text("Выберите уровень (1-15):", 60, WIDTH // 2, 200)
        for i in range(15):
            color = WHITE if i < unlocked_levels else (100, 100, 100)
            draw_text(f"{i + 1} (Рекорд: {high_scores[i]})", 40, WIDTH // 2, 300 + i * 40)

        # Подсветка текущего уровня
        draw_text(">", 40, WIDTH // 2 - 200, 300 + current_level * 40)

        # Добавьте текст в углу экрана
        draw_text("Все права защищенны \nkirya.g.2023@mail.ru \npatch 1.9.4", 20, 10, 10, center=False)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_9:
                    level = event.key - pygame.K_1
                    if level < unlocked_levels:
                        return level
                elif event.key == pygame.K_0 and unlocked_levels >= 10:
                    return 9
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левый клик
                    if current_level < unlocked_levels:
                        return current_level
            if event.type == pygame.MOUSEWHEEL:  # Обработка прокрутки колесика мыши
                if event.y > 0:  # Прокрутка вверх
                    current_level = max(0, current_level - 1)
                elif event.y < 0:  # Прокрутка вниз
                    current_level = min(unlocked_levels - 1, current_level + 1)






def game_loop(level_num):
    global unlocked_levels
    paddle = Paddle()
    balls = [Ball()]
    blocks = create_blocks_for_level(level_num)
    lives = 3
    score = 0
    bonuses = []

    platform_extended_timer = 0
    floor_active_timer = 0

    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move("left")
        if keys[pygame.K_RIGHT]:
            paddle.move("right")

        for ball in balls[:]:
            ball.move()

            # Столкновение с платформой
            if paddle.collidepoint(ball.x, ball.y + ball.radius) and ball.speed_y > 0:
                ball.speed_y *= -1
                bounce_sound.play()

            # Столкновение с блоками
            for block in blocks[:]:
                if block.collidepoint(ball.x, ball.y):
                    if not block.unbreakable:
                        blocks.remove(block)
                        score += 10
                        if block.bonus_type != 0:
                            bonuses.append(Bonus(block.centerx, block.centery, block.bonus_type))
                            bonus_sound.play()
                    ball.speed_y *= -1
                    bounce_sound.play()
                    break

            # Если шар вышел вниз
            if ball.y - ball.radius > HEIGHT:
                balls.remove(ball)

        if len(balls) == 0:
            lives -= 1
            balls.append(Ball())
            if lives == 0:
                # Игра окончена
                if score > high_scores[level_num]:
                    high_scores[level_num] = score
                save_progress()
                return

        # Обработка бонусов
        for bonus in bonuses[:]:
            bonus.move()
            if paddle.colliderect(bonus.rect):
                if bonus.type == 1:
                    paddle.width = min(paddle.width + 100, WIDTH)
                    if paddle.right > WIDTH:
                        paddle.right = WIDTH
                    platform_extended_timer = FPS * 10
                elif bonus.type == 2:
                    new_balls = []
                    for ball in balls:
                        for _ in range(2):
                            new_ball = Ball()
                            new_ball.x = ball.x
                            new_ball.y = ball.y
                            new_ball.speed_x = ball.speed_x * random.choice([-1,1])
                            new_ball.speed_y = -ball.speed_y
                            new_balls.append(new_ball)
                    balls.extend(new_balls)
                elif bonus.type == 3:
                    for _ in range(3):
                        new_ball = Ball()
                        new_ball.x = paddle.centerx
                        new_ball.y = paddle.top - 15
                        new_ball.speed_x = random.choice([-7,7])
                        new_ball.speed_y = -7
                        balls.append(new_ball)
                elif bonus.type == 4:
                    floor_active_timer = FPS * 5
                bonuses.remove(bonus)
                bonus_sound.play()

            elif bonus.rect.top > HEIGHT:
                bonuses.remove(bonus)

        # Таймеры эффектов
        if platform_extended_timer > 0:
            platform_extended_timer -=1
        else:
            paddle.width = 200

        if floor_active_timer > 0:
            floor_active_timer -= 1
            pygame.draw.rect(screen, (100, 100, 255), (0, HEIGHT - 10, WIDTH, 10))
            # Пол снизу отскакивает шар
            for ball in balls:
                if ball.y + ball.radius >= HEIGHT - 10 and ball.speed_y > 0:
                    ball.speed_y *= -1
                    bounce_sound.play()

        # Отрисовка
        paddle_rect = pygame.Rect(paddle.left, paddle.top, paddle.width, paddle.height)
        pygame.draw.rect(screen, WHITE, paddle_rect)

        for ball in balls:
            ball.draw()

        for block in blocks:
            block.draw()

        for bonus in bonuses:
            bonus.draw()

        draw_text(f"Жизни: {lives}  Очки: {score}", 40, 150, 20, center=False)

        pygame.display.flip()

        # Проверка выигрыша (если блоков нет, кроме неразбиваемых)
        if all(block.unbreakable for block in blocks):
            if score > high_scores[level_num]:
                high_scores[level_num] = score
            if level_num == unlocked_levels - 1 and unlocked_levels < 15:
                unlocked_levels += 1
            save_progress()
            return

def main():
    global unlocked_levels
    while True:
        level = level_menu()
        game_loop(level)

if __name__ == "__main__":
    main()