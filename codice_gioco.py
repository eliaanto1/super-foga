import pygame
import sys
import math

# Inizializzazione Pygame
pygame.init()

# Costanti di Gioco
WIDTH, HEIGHT = 1000, 600
FPS = 60
GRAVITY = 0.6
FRICTION = 0.99  

# Colori
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
BLUE = (30, 144, 255)
RED = (220, 20, 60)
BALL_COLOR = (245, 245, 245) 
BLACK = (20, 20, 20)          
GOAL_COLOR = (200, 200, 200)
GOLD = (255, 215, 0)
GRAY = (180, 180, 180)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Head Ball 2 - Rematch & Head Bounce Edition")
clock = pygame.time.Clock()

class Player:
    def __init__(self, x, y, color, is_player_one):
        self.x = x
        self.y = y
        self.radius = 40
        self.color = color
        self.is_player_one = is_player_one
        self.speed = 7
        self.jump_power = -18  
        self.vel_y = 0
        self.is_grounded = False
        
    def move(self, keys):
        old_y = self.y

        # Input Movimento P1 (WASD)
        if self.is_player_one:
            if keys[pygame.K_a] and self.x - self.radius > 0:
                self.x -= self.speed
            if keys[pygame.K_d] and self.x + self.radius < WIDTH:
                self.x += self.speed
            if keys[pygame.K_w] and self.is_grounded:
                self.vel_y = self.jump_power
                self.is_grounded = False
        # Input Movimento P2 (Frecce)
        else:
            if (keys[pygame.K_LEFT] or keys[276]) and self.x - self.radius > 0:
                self.x -= self.speed
            if (keys[pygame.K_RIGHT] or keys[275]) and self.x + self.radius < WIDTH:
                self.x += self.speed
            if (keys[pygame.K_UP] or keys[273]) and self.is_grounded:
                self.vel_y = self.jump_power
                self.is_grounded = False

        # Fisica Salto Modificata (Moltiplicatore 2.0)
        PLAYER_GRAVITY = 0.95
        if self.vel_y > 0:
            self.vel_y += PLAYER_GRAVITY * 2.0  
        else:
            self.vel_y += PLAYER_GRAVITY
        self.y += self.vel_y

        # Soffitto Invisibile
        if self.y - self.radius <= 100:
            self.y = 100 + self.radius
            self.vel_y = 0

        # Collisione Traverse
        on_left_crossbar = (self.x - self.radius <= 80)
        on_right_crossbar = (self.x + self.radius >= 920)
        if on_left_crossbar or on_right_crossbar:
            if self.y + self.radius >= 320 and self.y - self.radius <= 330:
                if old_y + self.radius <= 325:
                    self.y = 320 - self.radius
                    self.vel_y = 0
                    self.is_grounded = True
                elif old_y - self.radius >= 325:
                    self.y = 330 + self.radius
                    self.vel_y = 0
                else:
                    if on_left_crossbar: self.x = 80 + self.radius
                    if on_right_crossbar: self.x = 920 - self.radius

        # Terreno
        if self.y + self.radius >= 500:
            self.y = 500 - self.radius
            self.vel_y = 0
            self.is_grounded = True

    def kick(self, keys, ball):
        dx = ball.x - self.x
        dy = ball.y - self.y
        distance = math.hypot(dx, dy)
        
        if distance < self.radius + ball.radius + 25:
            if self.is_player_one:
                if keys[pygame.K_f]: # Tiro teso
                    ball.vel_x = 24  
                    ball.vel_y = -1.5
                elif keys[pygame.K_g]: # Pallonetto teso
                    ball.vel_x = 19  
                    ball.vel_y = -12 
            else:
                if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS] or keys[45]: # Tiro teso
                    ball.vel_x = -24 
                    ball.vel_y = -1.5
                elif keys[pygame.K_PERIOD] or keys[pygame.K_KP_PERIOD] or keys[46]: # Pallonetto teso
                    ball.vel_x = -19 
                    ball.vel_y = -12 

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        eye_offset = 20 if self.is_player_one else -20
        pygame.draw.circle(surface, WHITE, (int(self.x + eye_offset), int(self.y - 10)), 8)
        pygame.draw.circle(surface, (0,0,0), (int(self.x + eye_offset + (3 if self.is_player_one else -3)), int(self.y - 10)), 4)


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.vel_x = 0
        self.vel_y = 0
        self.elasticity = 0.75
        self.is_grounded = False
        self.trail = [] 

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 12: 
            self.trail.pop(0)

        self.vel_y += GRAVITY
        self.vel_x *= FRICTION
        self.x += self.vel_x
        self.y += self.vel_y

        # Terreno
        if self.y + self.radius >= 500:
            self.y = 500 - self.radius
            self.vel_y = -self.vel_y * self.elasticity
            self.vel_x *= 0.95
            self.is_grounded = True
        else:
            self.is_grounded = True if abs((self.y + self.radius) - 500) < 5 else False

        # Soffitto e pareti
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vel_y = -self.vel_y * self.elasticity
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vel_x = -self.vel_x * self.elasticity
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.vel_x = -self.vel_x * self.elasticity

    def check_collision_player(self, player):
        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.hypot(dx, dy)
        min_dist = self.radius + player.radius

        if distance < min_dist:
            # Rimbalzo elastico sulla TESTA (metà superiore del giocatore)
            if self.y < player.y + 5: 
                angle = math.atan2(dy, dx)
                self.x = player.x + min_dist * math.cos(angle)
                self.y = player.y + min_dist * math.sin(angle)
                
                # --- AUMENTATO IL RIMBALZO SULLA TESTA ---
                # Moltiplichiamo l'energia del rimbalzo per renderla reattiva quasi come il pavimento
                speed = math.hypot(self.vel_x, self.vel_y)
                bounce_power = max(speed * 0.95, 10) # Rimbalzo minimo alzato a 10 e conservazione velocità al 95%
                
                self.vel_x = math.cos(angle) * bounce_power
                self.vel_y = math.sin(angle) * bounce_power
            else:
                # Spinta laterale raso terra camminando
                if self.x > player.x:
                    self.x = player.x + min_dist
                    if self.vel_x < player.speed: self.vel_x = player.speed
                else:
                    self.x = player.x - min_dist
                    if self.vel_x > -player.speed: self.vel_x = -player.speed

    def check_sandwich(self, p1, p2):
        if p1.is_grounded and p2.is_grounded and self.is_grounded:
            dist_p1 = math.hypot(self.x - p1.x, self.y - p1.y)
            dist_p2 = math.hypot(self.x - p2.x, self.y - p2.y)
            if dist_p1 < (self.radius + p1.radius + 8) and dist_p2 < (self.radius + p2.radius + 8):
                self.vel_y = -14  
                self.vel_x = (self.x - (p1.x + p2.x) / 2) * 0.4 
                self.y = 500 - p1.radius * 2 - self.radius
                self.is_grounded = False

    def check_goal_collision(self):
        if 0 <= self.x <= 80 and abs(self.y - 320) <= self.radius:
            self.vel_y = -self.vel_y * self.elasticity
            self.y = 320 - self.radius if self.vel_y < 0 else 320 + self.radius
        if 920 <= self.x <= WIDTH and abs(self.y - 320) <= self.radius:
            self.vel_y = -self.vel_y * self.elasticity
            self.y = 320 - self.radius if self.vel_y < 0 else 320 + self.radius

    def draw(self, surface):
        speed = math.hypot(self.vel_x, self.vel_y)
        if speed > 2: 
            for i, pos in enumerate(self.trail):
                alpha = int((i / len(self.trail)) * 200)
                radius = int(self.radius * (0.3 + 0.7 * (i / len(self.trail)))) 
                if radius > 0:
                    trail_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surf, (174, 219, 243, alpha), (radius, radius), radius)
                    surface.blit(trail_surf, (int(pos[0] - radius), int(pos[1] - radius)))

        pygame.draw.circle(surface, BALL_COLOR, (int(self.x), int(self.y)), self.radius)

        # Sagome da calcio
        cx, cy = int(self.x), int(self.y)
        p_radius = self.radius * 0.32
        pentagon_points = []
        for i in range(5):
            angle = math.radians(i * 72 - 18)
            px = cx + p_radius * math.cos(angle)
            py = cy + p_radius * math.sin(angle)
            pentagon_points.append((px, py))
        
        pygame.draw.polygon(surface, BLACK, pentagon_points)

        for i in range(5):
            angle = math.radians(i * 72 - 18)
            start_x = cx + p_radius * math.cos(angle)
            start_y = cy + p_radius * math.sin(angle)
            end_x = cx + (self.radius * 0.75) * math.cos(angle)
            end_y = cy + (self.radius * 0.75) * math.sin(angle)
            pygame.draw.line(surface, BLACK, (start_x, start_y), (end_x, end_y), 2)

            edge_angle = angle + math.radians(36)
            b_in_x = cx + (self.radius * 0.78) * math.cos(edge_angle)
            b_in_y = cy + (self.radius * 0.78) * math.sin(edge_angle)
            pygame.draw.circle(surface, BLACK, (int(b_in_x), int(b_in_y)), 3)

        pygame.draw.circle(surface, BLACK, (cx, cy), self.radius, 2)


def handle_player_collision(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    distance = math.hypot(dx, dy)
    min_dist = p1.radius + p2.radius
    if distance < min_dist:
        angle = math.atan2(dy, dx)
        overlap = min_dist - distance
        p1.x -= (overlap / 2) * math.cos(angle)
        p1.y -= (overlap / 2) * math.sin(angle)
        p2.x += (overlap / 2) * math.cos(angle)
        p2.y += (overlap / 2) * math.sin(angle)

def draw_scenery():
    screen.fill((135, 206, 235))
    pygame.draw.rect(screen, GREEN, (0, 500, WIDTH, 100))
    pygame.draw.rect(screen, DARK_GREEN, (0, 500, WIDTH, 10))
    pygame.draw.rect(screen, GOAL_COLOR, (0, 320, 80, 180), 5)
    pygame.draw.rect(screen, GOAL_COLOR, (920, 320, 80, 180), 5)

def main():
    player1 = Player(200, 400, BLUE, is_player_one=True)
    player2 = Player(800, 400, RED, is_player_one=False)
    ball = Ball(WIDTH // 2, 200)

    score_p1 = 0
    score_p2 = 0
    font = pygame.font.SysFont("Arial", 40, bold=True)
    goal_font = pygame.font.SysFont("Arial", 100, bold=True)
    winner_font = pygame.font.SysFont("Arial", 65, bold=True) 
    rematch_font = pygame.font.SysFont("Arial", 30, bold=True) # Font per l'avviso di rivincita

    match_duration = 90 
    start_ticks = pygame.time.get_ticks()
    game_over = False
    goal_flash_timer = 0

    running = True
    while running:
        clock.tick(FPS)
        pygame.event.pump()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
            time_left = max(0, match_duration - seconds_passed)
            if time_left == 0:
                game_over = True

            player1.move(keys)
            player2.move(keys)
            handle_player_collision(player1, player2)
            player1.kick(keys, ball)
            player2.kick(keys, ball)

            ball.update()
            ball.check_collision_player(player1)
            ball.check_collision_player(player2)
            ball.check_sandwich(player1, player2)
            ball.check_goal_collision()

            if ball.y > 320:
                is_goal = False
                if ball.x + ball.radius < 80:
                    score_p2 += 1
                    is_goal = True
                elif ball.x - ball.radius > 920:
                    score_p1 += 1
                    is_goal = True
                
                if is_goal:
                    goal_flash_timer = 30 
                    ball = Ball(WIDTH // 2, 200)
                    player1.x, player1.y = 200, 400
                    player2.x, player2.y = 800, 400
        else:
            # --- GESTIONE RIVINCITA (Tasto R) ---
            if keys[pygame.K_r]:
                score_p1 = 0
                score_p2 = 0
                start_ticks = pygame.time.get_ticks()
                game_over = False
                ball = Ball(WIDTH // 2, 200)
                player1.x, player1.y = 200, 400
                player2.x, player2.y = 800, 400

        draw_scenery()
        player1.draw(screen)
        player2.draw(screen)
        ball.draw(screen)

        if goal_flash_timer > 0:
            goal_flash_timer -= 1
            if goal_flash_timer % 4 < 2:
                flash_surf = pygame.Surface((WIDTH, HEIGHT))
                flash_surf.fill((255, 255, 255))
                flash_surf.set_alpha(100)
                screen.blit(flash_surf, (0,0))
            goal_text = goal_font.render("GOAL!", True, GOLD)
            screen.blit(goal_text, (WIDTH//2 - goal_text.get_width()//2, HEIGHT//2 - goal_text.get_height()//2))

        # Schermata Finale con Scritta Rivincita
        if game_over:
            end_surf = pygame.Surface((WIDTH, HEIGHT))
            end_surf.fill((0, 0, 0))
            end_surf.set_alpha(180)
            screen.blit(end_surf, (0, 0))
            
            if score_p1 > score_p2:
                winner_text = "IL GIOCATORE 1 VINCE!"
                color = BLUE
            elif score_p2 > score_p1:
                winner_text = "IL GIOCATORE 2 VINCE!"
                color = RED
            else:
                winner_text = "PAREGGIO!"
                color = WHITE
                
            res_text = winner_font.render(winner_text, True, color)
            screen.blit(res_text, (WIDTH//2 - res_text.get_width()//2, HEIGHT//2 - res_text.get_height()//2 - 30))
            
            # Testo aggiuntivo per la rivincita
            rematch_text = rematch_font.render("Premi R per Rivincita", True, GRAY)
            screen.blit(rematch_text, (WIDTH//2 - rematch_text.get_width()//2, HEIGHT//2 - rematch_text.get_height()//2 + 50))

        score_text = font.render(f"{score_p1} - {score_p2}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
        
        timer_text = font.render(f"Tempo: {time_left if not game_over else 0}s", True, WHITE)
        screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 70))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()