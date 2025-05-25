import pygame
import sys
from sprites import *
from platforms import *
from coins import *
from safezone import *
import random
import time
import os

WIDTH, HEIGHT = 800, 600

WHITE = (255, 255, 255)
RED = (255, 0, 0)
SKY_BLUE = (135, 206, 235)
FPS = 60


class Game():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sidescrolling Platformer")
        self.clock = pygame.time.Clock()
        self.running = True

        # pygame.mixer.music.load('images/Jungle musique.wav')
        # # pygame.mixer.music.set_volume(1.0)
        # pygame.mixer.music.play(-1)

        self.background = pygame.image.load(join('images', 'Sui run jungle.png'))
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        self.all_sprites = pygame.sprite.Group()
        self.player_frames = [pygame.image.load('images/moving1.png'), pygame.image.load('images/moving2.png')]
        self.player = Player(100, HEIGHT - 150, self.player_frames)
        self.all_sprites.add(self.player)

        self.platforms = pygame.sprite.Group()
        ground = Platform(0, HEIGHT - 40, 3000, 40)
        ground.image = pygame.image.load(join('images', 'Sui run jungle.png'))
        ground.image = pygame.transform.scale(ground.image, (3000, 40))
        self.platforms.add(ground)
        self.all_sprites.add(ground)

        self.safe_zones = pygame.sprite.Group()

        self.left_safe = SafeZone(0, HEIGHT - 40, 300, 40)

        self.right_safe = SafeZone(3000 - 300, HEIGHT - 40, 300, 40)

        self.safe_zones.add(self.left_safe, self.right_safe)

        self.username = None
        self.start_time = None
        self.final_time = None

        # platform_positions = [
        #     (300, 450, 200, 30),
        #     (600, 400, 180, 30),
        #     (900, 350, 150, 30),
        #     (1200, 300, 200, 30),
        #     (1500, 350, 180, 30),
        #     (1800, 400, 200, 30),
        #     (2100, 450, 150, 30),
        #     (2400, 420, 100, 30),
        #     (2700, 380, 120, 30),
        # ]

        # for pos in platform_positions:
        #     plat = Platform(*pos)
        #     self.platforms.add(plat)
        #     self.all_sprites.add(plat)
        platform_x = 50  # starting X after ground
        platform_count = 10
        min_gap = 200  # minimum horizontal gap between platforms
        max_gap = 350  # maximum horizontal gap
        min_width = 100
        max_width = 250
        min_y = 250  # highest platform
        max_y = HEIGHT - 155  # lowest platform (above ground)
        max_vertical_diff = 80  # max vertical jump height

        last_y = 450  # start height

        for i in range(platform_count):
            width = random.randint(min_width, max_width)
            # ensure next x is reachable
            platform_x += random.randint(min_gap, max_gap)
            # vary y but keep within jumpable range
            new_y = last_y + random.randint(-max_vertical_diff, max_vertical_diff)
            new_y = max(min_y, min(new_y, max_y))  # clamp to screen limits
            plat = Platform(platform_x, new_y, width, 30)
            plat.id = f"plat_{i}"  # optional: assign unique id
            self.platforms.add(plat)
            self.all_sprites.add(plat)
            last_y = new_y  # update for next platform
        # plat1 = Platform(250, 450, 200, 20)
        # plat2 = Platform(500, 350, 200, 20)
        # plat3 = Platform(750, 300, 200, 20)
        # plat4 = Platform(1000, 400, 200, 20)
        # self.platforms.add(ground, plat1, plat2, plat3, plat4)
        # self.all_sprites.add(ground, plat1, plat2, plat3, plat4)

        self.coins = pygame.sprite.Group()
        coin_spacing = 500
        for platform in self.platforms:
            if platform.rect.top == HEIGHT - 40:
                continue
            x1 = platform.rect.left + platform.rect.width // 3
            x2 = platform.rect.left + 2 * platform.rect.width // 3
            y = platform.rect.top - 15
            if(x1 < 2900):
                coin1 = Coin(x1, y)
                self.coins.add(coin1)
                self.all_sprites.add(coin1)
            if x2 < 2900:
                coin2 = Coin(x2, y)
                self.coins.add(coin2)
                self.all_sprites.add(coin2)
        
        # ground = [p for p in self.platforms if p.rect.top == HEIGHT - 40][0]
        # num_coins = ground.rect.width // coin_spacing

        # for i in range(num_coins):
        #     x = ground.rect.left + i * coin_spacing + coin_spacing // 2
        #     y = ground.rect.top - 15
        #     if (y < 20):
        #         coin = Coin(x, y)
        #         self.coins.add(coin)
        #         self.all_sprites.add(coin)


        self.scroll = 0
        self.score = 0

        self.level = 1
        self.font = pygame.font.SysFont(None, 36)
        self.level_complete = False
        self.level_complete_time = 0
        self.time_file = "user_times.txt"
        self.game_finished = False

    def get_username(self):
        input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 40)
        enter_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 40, 100, 40)
        font = pygame.font.SysFont(None, 36)
        active = True
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        button_color = pygame.Color('green')
        button_text_color = pygame.Color('white')
        color = color_active
        text = ''
        cursor_visible = True
        cursor_timer = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN and text.strip():
                            self.username = text.strip()
                            return
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if enter_button.collidepoint(event.pos) and text.strip():
                        self.username = text.strip()
                        return

            cursor_timer += 1
            if cursor_timer % 300 == 0:
                cursor_visible = not cursor_visible

            self.screen.fill(SKY_BLUE)
            prompt_text = font.render("Enter your username:", True, (0, 0, 0))
            self.screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 80))

            txt_surface = font.render(text, True, (0, 0, 0))
            self.screen.blit(txt_surface, (input_box.x + 10, input_box.y + 5))
            if cursor_visible:
                cursor_x = input_box.x + 10 + txt_surface.get_width()
                pygame.draw.line(self.screen, (0, 0, 0), (cursor_x, input_box.y + 5), (cursor_x, input_box.y + 35), 2)

            pygame.draw.rect(self.screen, color, input_box, 2)

            pygame.draw.rect(self.screen, button_color, enter_button)
            button_text = font.render("Enter", True, button_text_color)
            self.screen.blit(button_text, (enter_button.x + (enter_button.width - button_text.get_width()) // 2,
                                           enter_button.y + (enter_button.height - button_text.get_height()) // 2))

            pygame.display.flip()

    def run(self):
        self.get_username() 
        self.start_time = time.time()
        pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/Jungle musique.wav'))
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        self.all_sprites.update(keys)
        self.player.on_ground = False

        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        for platform in hits:
            if self.player.vel_y > 0 and self.player.rect.bottom <= platform.rect.bottom:
                self.player.rect.bottom = platform.rect.top
                self.player.vel_y = 0
                self.player.on_ground = True
            elif self.player.vel_y < 0 and self.player.rect.top >= platform.rect.top:
                self.player.rect.top = platform.rect.bottom
                self.player.vel_y = 0
        
        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        for platform in hits:
            if self.player.rect.right > platform.rect.left and self.player.rect.left < platform.rect.left:
                self.player.rect.right = platform.rect.left
            elif self.player.rect.left < platform.rect.right and self.player.rect.right > platform.rect.right:
                self.player.rect.left = platform.rect.right
        
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        if coin_hits:
            # pygame.mixer.music.load('images/coinsound.wav')
            # pygame.mixer.music.play()
            pygame.mixer.Channel(1).set_volume(0.5)
            pygame.mixer.Channel(1).play(pygame.mixer.Sound('music/coinsound.wav'))
            self.score += len(coin_hits)
            for coin in coin_hits:
                self.all_sprites.remove(coin)
        
        # if self.player.rect.bottom >= HEIGHT - 40:
        #     in_safe_zone = False
        #     for safe_zone in self.safe_zones:
        #         if self.player.rect.colliderect(self.left_safe.rect):
        #             in_safe_zone = True
        #             break
        #     if not in_safe_zone:
        #         print("Player touched dangerous ground — exiting game.")
        #         pygame.quit()
        #         sys.exit()

        
        if self.player.rect.centerx - self.scroll > WIDTH * 0.6:
            self.scroll = self.player.rect.centerx - WIDTH * 0.6
        if self.player.rect.centerx - self.scroll < WIDTH * 0.4:
            self.scroll = self.player.rect.centerx - WIDTH * 0.4
        
        if self.scroll < 0:
            self.scroll = 0
        
        LEVEL_WIDTH = 3000
        max_scroll = LEVEL_WIDTH - WIDTH
        if self.scroll > max_scroll:
            self.scroll = max_scroll

        all_coins_collected = len(self.coins) == 0
        at_level_end = self.player.rect.right >= LEVEL_WIDTH

        if all_coins_collected and at_level_end and not self.level_complete:
            pygame.mixer.Channel(2).play(pygame.mixer.Sound('music/lvlcomplete.wav'))
            self.level_complete = True
            self.level_complete_time = pygame.time.get_ticks()
        
        if self.level_complete:
            if self.level == 4 and not self.game_finished:
                self.final_time = time.time() - self.start_time
                with open(self.time_file, "a") as file:
                    file.write(f"{self.username}: {self.final_time:.2f} seconds\n")
                print(f"User {self.username} completed the game in {self.final_time:.2f} seconds.")
                self.game_finished = True
            elif pygame.time.get_ticks() - self.level_complete_time > 5000:
                self.level += 1
                self.nextLevel()
                if self.level == 2:
                    pygame.mixer.music.stop()
                    pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/Wind.wav'))
                elif self.level == 3:
                    pygame.mixer.music.stop()
                    pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/underthesea.wav'))
                elif self.level == 4:
                    pygame.mixer.music.stop()
                    pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/finalboss.wav'))
                else:
                    pygame.quit()
                    sys.exit()


    def draw(self):
        # self.screen.fill(SKY_BLUE)
        self.screen.blit(self.background, (0, 0))
        # self.all_sprites.draw(self.screen)
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, (sprite.rect.x - self.scroll, sprite.rect.y))
        for safe_zone in self.safe_zones:
            self.screen.blit(safe_zone.image, safe_zone.rect.move(-self.scroll, 0))
        if self.level != 4:
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
            self.screen.blit(score_text, (10, 10))

            level_text = self.font.render(f"Level {self.level}", True, (0, 0, 0))
            self.screen.blit(level_text, (10, 40))
        else:
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))

            level_text = self.font.render(f"Level {self.level}", True, (255, 255, 255))
            self.screen.blit(level_text, (10, 40))

        if self.final_time is not None:
            timer_text = self.font.render(f"Time: {self.final_time:.2f}s", True, (255, 255, 255) if self.level == 4 else (0, 0, 0))
        else:
            elapsed_time = time.time() - self.start_time
            timer_text = self.font.render(f"Time: {elapsed_time:.2f}s", True, (255, 255, 255) if self.level == 4 else (0, 0, 0))
        self.screen.blit(timer_text, (WIDTH - 150, 10))

        if self.level_complete:
            if self.level != 4:
                complete_text = self.font.render("Level Complete!", True, (255, 0, 0))
                text_rect = complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
                self.screen.blit(complete_text, text_rect)
            else:
                complete_text = self.font.render("You Win!", True, (255, 0, 0))
                text_rect = complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
                self.screen.blit(complete_text, text_rect)

        pygame.display.flip()
    
    def nextLevel(self):
        self.score = 0
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))

        self.level_complete = False
        self.coins.empty()
        self.platforms.empty()
        self.all_sprites.empty()

        global LEVEL_WIDTH
        LEVEL_WIDTH = 3000

        if self.level == 2:
            self.background = pygame.image.load(join('images', 'clouds.png'))
            self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        elif self.level == 3:
            self.background = pygame.image.load(join('images', 'sea.png'))
            self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        elif self.level == 4:
            self.background = pygame.image.load(join('images', 'boss.png'))
            self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        self.player = Player(100, HEIGHT - 150, self.player_frames)
        self.all_sprites.add(self.player)

        self.ground = Platform(0, HEIGHT - 40, LEVEL_WIDTH, 40)
        if self.level == 2:
            self.ground.image = pygame.image.load(join('images', 'clouds.png'))
            self.ground.image = pygame.transform.scale(self.ground.image, (LEVEL_WIDTH, 40))
        elif self.level == 3:
            self.ground.image = pygame.image.load(join('images', 'sea.png'))
            self.ground.image = pygame.transform.scale(self.ground.image, (LEVEL_WIDTH, 40))
        elif self.level == 4:
            self.ground.image = pygame.image.load(join('images', 'boss.png'))
            self.ground.image = pygame.transform.scale(self.ground.image, (LEVEL_WIDTH, 40))
        self.platforms.add(self.ground)
        self.all_sprites.add(self.ground)

        self.safe_zones = pygame.sprite.Group()

        left_safe = SafeZone(0, HEIGHT - 40, 300, 40)

        right_safe = SafeZone(3000 - 300, HEIGHT - 40, 300, 40)

        self.safe_zones.add(left_safe, right_safe)


        # platform_positions = [
        #     (300, 450, 200, 20),
        #     (600, 400, 180, 20),
        #     (900, 350, 150, 20),
        #     (1200, 300, 200, 20),
        #     (1500, 350, 180, 20),
        #     (1800, 400, 200, 20),
        #     (2100, 450, 150, 20),
        #     (2400, 420, 100, 20),
        #     (2700, 380, 120, 20),
        # ]

        # for pos in platform_positions:
        #     plat = Platform(*pos)
        #     if self.level == 2:
        #         plat.image = pygame.image.load(join('images', 'p2.png'))
        #         plat.image = pygame.transform.scale(plat.image, (pos[2], 30))
        #     elif self.level == 3:
        #         plat.image = pygame.image.load(join('images', 'p3.png'))
        #         plat.image = pygame.transform.scale(plat.image, (pos[2], 30))
        #     elif self.level == 4:
        #         plat.image = pygame.image.load(join('images', 'p4.png'))
        #         plat.image = pygame.transform.scale(plat.image, (pos[2], 30))
        #     self.platforms.add(plat)
        #     self.all_sprites.add(plat)

        platform_x = 100  # starting X after ground
        platform_count = 10
        min_gap = 200  # minimum horizontal gap between platforms
        max_gap = 350  # maximum horizontal gap
        min_width = 100
        max_width = 250
        min_y = 250  # highest platform
        max_y = HEIGHT - 200  # lowest platform (above ground)
        max_vertical_diff = 80  # max vertical jump height

        last_y = 450  # start height

        for i in range(platform_count):
            width = random.randint(min_width, max_width)
            # ensure next x is reachable
            platform_x += random.randint(min_gap, max_gap)
            # vary y but keep within jumpable range
            new_y = last_y + random.randint(-max_vertical_diff, max_vertical_diff)
            new_y = max(min_y, min(new_y, max_y))  # clamp to screen limits
            plat = Platform(platform_x, new_y, width, 30)
            plat.id = f"plat_{i}"  # optional: assign unique id
            if self.level == 2:
                plat.image = pygame.image.load(join('images', 'p2.png'))
                plat.image = pygame.transform.scale(plat.image, (width, 30))
            elif self.level == 3:
                plat.image = pygame.image.load(join('images', 'p3.png'))
                plat.image = pygame.transform.scale(plat.image, (width, 30))
            elif self.level == 4:
                plat.image = pygame.image.load(join('images', 'p4.png'))
                plat.image = pygame.transform.scale(plat.image, (width, 30))
            self.platforms.add(plat)
            self.all_sprites.add(plat)
            last_y = new_y  # update for next platform

        coin_spacing = 500
        for platform in self.platforms:
            if platform.rect.top == HEIGHT - 40:
                continue
            x1 = platform.rect.left + platform.rect.width // 3
            x2 = platform.rect.left + 2 * platform.rect.width // 3
            y = platform.rect.top - 15
            if(x1 < 2900):
                coin1 = Coin(x1, y)
                self.coins.add(coin1)
                self.all_sprites.add(coin1)
            if x2 < 2900:
                coin2 = Coin(x2, y)
                self.coins.add(coin2)
                self.all_sprites.add(coin2)

        # num_coins = self.ground.rect.width // coin_spacing
        # for i in range(num_coins):
        #     x = self.ground.rect.left + i * coin_spacing + coin_spacing // 2
        #     y = self.ground.rect.top - 15
        #     coin = Coin(x, y)
        #     self.coins.add(coin)
        #     self.all_sprites.add(coin)

    def run(self):
        self.get_username() 
        self.start_time = time.time()
        pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/Jungle musique.wav'))
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()
