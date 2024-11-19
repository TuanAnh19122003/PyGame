import pygame
import random

pygame.init()

# Thiết lập hiển thị
screen_width = 500
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Plane Fighting Game')

clock = pygame.time.Clock()
player_image = pygame.image.load('image/player.png')
enemy_image = pygame.image.load('image/enemy.png')

# Tải hình nền
background_image = pygame.image.load('image/background.png')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

bullet_image = pygame.Surface((10, 20))
bullet_image.fill((255, 0, 0))

# Thiết lập âm thanh
pygame.mixer.music.load('nhac/background.wav')
pygame.mixer.music.play(-1)  # Phát âm thanh nền lặp lại vô hạn
explosion_sound = pygame.mixer.Sound('nhac/explosion.wav')
laser_sound = pygame.mixer.Sound('nhac/laser.wav')
game_over_music = pygame.mixer.Sound('nhac/game_over.wav')

# Thiết lập font chữ cho Game Over
pygame.font.init()
font = pygame.font.Font(None, 74)
game_over_text = font.render('Game Over', True, (255, 0, 0))
restart_text = font.render('Press R to Restart', True, (255, 255, 255))

difficulty_increase = 0  # Tăng độ khó ban đầu

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.centerx = screen_width // 2
        self.rect.bottom = screen_height - 20
        self.speed = 5
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.defeated = False

    def update(self):
        if self.defeated:
            return 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(self.rect.x, screen_width - self.rect.width))
        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            laser_sound.play()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, max(0, screen_width - self.rect.width))
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(1, 3)

    def update(self):
        if player.defeated:
            return
        self.rect.y += self.speed + difficulty_increase  # Tăng tốc độ theo độ khó
        if self.rect.top > screen_height:
            self.reset()
        if self.rect.colliderect(player.rect):
            player.defeated = True
    
    def reset(self):
        self.rect.x = random.randint(0, max(0, screen_width - self.rect.width))
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(1, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 255, 0))  # Màu xanh cho power-up
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            self.kill()  # Xóa power-up khi vượt quá màn hình

def increase_difficulty():
    global difficulty_increase
    difficulty_increase += 0.01  # Tăng độ khó từ từ theo thời gian

def reset_game():
    global player, all_sprites, enemies, bullets, powerups, game_over
    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    for _ in range(7):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    for _ in range(3):  # Số lượng power-up
        powerup = PowerUp()
        all_sprites.add(powerup)
        powerups.add(powerup)

    game_over = False
    global difficulty_increase
    difficulty_increase = 0  # Đặt lại độ khó khi khởi động lại

player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
enemies = pygame.sprite.Group()

for _ in range(7):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

running = True
game_over = False
score = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        all_sprites.update()

        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit_enemy in hits:
            explosion_sound.play()  # Phát âm thanh nổ khi tiêu diệt kẻ thù
            score += 100
            enemy = Enemy()  # Thêm kẻ thù mới sau khi tiêu diệt
            all_sprites.add(enemy)
            enemies.add(enemy)

        powerup_hits = pygame.sprite.spritecollide(player, powerups, True)  # Kiểm tra nhặt power-up
        for hit_powerup in powerup_hits:
            player.shoot_delay = 100  # Tăng tốc độ bắn khi nhặt power-up

        increase_difficulty()  # Tăng độ khó theo thời gian

        screen.blit(background_image, (0, 0))
        all_sprites.draw(screen)
        
        score_text = font.render(f'Score: {score}', True, (255, 255, 255))  # Vẽ điểm số
        screen.blit(score_text, (10, 10))

        if pygame.sprite.spritecollideany(player, enemies):  # Kiểm tra va chạm giữa player và enemies
            player.defeated = True
            game_over = True
            game_over_music.play() 
    else:
        screen.blit(background_image, (0, 0))
        screen.blit(game_over_text, (screen_width // 4, screen_height // 4))
        screen.blit(restart_text, (screen_width // 10, screen_height // 2.5))
        
        game_over_score_text = font.render(f'Final Score: {score}', True, (255, 255, 255))
        game_over_score_rect = game_over_score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        screen.blit(game_over_score_text, game_over_score_rect)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_game()
            score = 0

    pygame.display.flip()
    clock.tick(60)
