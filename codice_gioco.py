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
PURPLE = (148, 0, 211) 
BALL_COLOR = (245, 245, 245) 
BLACK = (20, 20, 20)          
GOAL_COLOR = (200, 200, 200)
NET_COLOR = (160, 160, 160) 
GOLD = (255, 215, 0)
GRAY = (180, 180, 180)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Head Ball 2 - Enhanced UI & Stun Stars")
clock = pygame.time.Clock()

class Player:
    def __init__(self, x, y, color, is_player_one):
        self.x = x
        self.y = y
        self.radius = 40
        self.base_color = color
        self.color = color
        self.is_player_one = is_player_one
        self.speed = 9         
        self.jump_power = -18  
        self.vel_y = 0
        self.is_grounded = False
        
        # Meccanica di Stun
        self.hit_count = 0
        self.last_hit_time = 0
        self.stun_timer = 0
        self.star_angle = 0 
        self.hits_landed = 0 

    def move(self, keys):
        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.star_angle += 0.1 
            self.vel_y += 0.95 
            self.y += self.vel_y
            if self.y + self.radius >= 500:
                self.y = 500 - self.radius
                self.vel_y = 0
                self.is_grounded = True
            return

        if self.hit_count > 0 and pygame.time.get_ticks() - self.last_hit_time > 3000:
            self.hit_count = 0

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

        # Fisica Salto
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
        on_left_crossbar = (self.x - self.radius <= 60)
        on_right_crossbar = (self.x + self.radius >= 940)
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
                    if on_left_crossbar: self.x = 60 + self.radius
                    if on_right_crossbar: self.x = 940 - self.radius

        # Terreno
        if self.y + self.radius >= 500:
            self.y = 500 - self.radius
            self.vel_y = 0
            self.is_grounded = True

    def kick(self, keys, ball, opponent):
        if self.stun_timer > 0:
            return

        if opponent.hit_count == 0:
            self.hits_landed = 0

        kick_pressed = False
        if self.is_player_one:
            if keys[pygame.K_f] or keys[pygame.K_g]:
                kick_pressed = True
        else:
            if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS] or keys[45] or keys[pygame.K_PERIOD] or keys[pygame.K_KP_PERIOD] or keys[46]:
                kick_pressed = True

        if kick_pressed:
            dist_to_opponent = math.hypot(opponent.x - self.x, opponent.y - self.y)
            if dist_to_opponent < (self.radius + opponent.radius + 35) and opponent.stun_timer == 0:
                current_time = pygame.time.get_ticks()
                if current_time - opponent.last_hit_time > 200:
                    opponent.hit_count += 1
                    opponent.last_hit_time = current_time
                    self.hits_landed = opponent.hit_count 
                    
                    if opponent.hit_count >= 5:
                        opponent.stun_timer = 120 
                        opponent.hit_count = 0
                        self.hits_landed = 0

        # Fisica del tiro sulla palla
        dx = ball.x - self.x
        dy = ball.y - self.y
        distance = math.hypot(dx, dy)
        
        if distance < self.radius + ball.radius + 25:
            ball.is_kickoff = False 
            
            if self.is_player_one:
                if keys[pygame.K_f]: 
                    ball.vel_x = 19  
                    if ball.y < self.y:
                        ball.vel_y = 12  
                    else:
                        ball.vel_y = -1.5 
                elif keys[pygame.K_g]: 
                    ball.vel_x = 19  
                    ball.vel_y = -12 
            else:
                if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS] or keys[45]: 
                    ball.vel_x = -19 
                    if ball.y < self.y:
                        ball.vel_y = 12  
                    else:
                        ball.vel_y = -1.5 
                elif keys[pygame.K_PERIOD] or keys[pygame.K_KP_PERIOD] or keys[46]: 
                    ball.vel_x = -19 
                    ball.vel_y = -12 

    def update_color(self):
        if self.stun_timer > 0:
            self.color = PURPLE
        else:
            ratio = self.hit_count / 5.0
            r = int(self.base_color[0] + (PURPLE[0] - self.base_color[0]) * ratio)
            g = int(self.base_color[1] + (PURPLE[1] - self.base_color[1]) * ratio)
            b = int(self.base_color[2] + (PURPLE[2] - self.base_color[2]) * ratio)
            self.color = (r, g, b)

    def draw_stars(self, surface):
        if self.stun_timer > 0:
            num_stars = 3
            center_x = int(self.x)
            center_y = int(self.y - self.radius - 25) # Alzate leggermente per far spazio alle stelle più grandi
            radius_orbit = 28 # Raggio dell'orbita aumentato (prima era 20)
            
            for i in range(num_stars):
                angle = self.star_angle + (i * (2 * math.pi / num_stars))
                star_x = center_x + int(radius_orbit * math.cos(angle))
                star_y = center_y + int(radius_orbit * math.sin(angle) * 0.4)
                
                # Disegno geometrico della singola stella (Ingrandita)
                points = []
                for p in range(10):
                    # Raggi aumentati per rendere le stelle visibilmente più grandi
                    r = 10 if p % 2 == 0 else 5 # Prima era 6 e 3
                    a = angle * 2 + p * (math.pi / 5)
                    px = star_x + int(r * math.cos(a))
                    py = star_y + int(r * math.sin(a))
                    points.append((px, py))
                pygame.draw.polygon(surface, GOLD, points)

    def draw(self, surface):
        self.update_color()
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        eye_offset = 20 if self.is_player_one else -20
        pygame.draw.circle(surface, WHITE, (int(self.x + eye_offset), int(self.y - 10)), 8)
        pygame.draw.circle(surface, (0,0,0), (int(self.x + eye_offset + (3 if self.is_player_one else -3)), int(self.y - 10)), 4)
        
        self.draw_stars(surface)


class Ball:
    def __init__(self, x, y, is_kickoff=False):
        self.x = x
        self.y = y
        self.radius = 20
        self.vel_x = 0
        self.vel_y = 0
        self.elasticity = 0.75
        self.is_grounded = False
        self.is_kickoff = is_kickoff 
        self.trail = [] 
        self.rotation_angle = 0.0

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 12: 
            self.trail.pop(0)

        current_gravity = 0.22 if self.is_kickoff else GRAVITY
        
        self.vel_y += current_gravity
        self.vel_x *= FRICTION
        self.x += self.vel_x
        self.y += self.vel_y

        self.rotation_angle += self.vel_x / self.radius

        # Terreno
        if self.y + self.radius >= 500:
            self.y = 500 - self.radius
            self.vel_y = -self.vel_y * self.elasticity
            self.vel_x *= 0.95
            self.is_grounded = True
            self.is_kickoff = False 
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
            self.is_kickoff = False 
            
            if self.y < player.y + 5: 
                angle = math.atan2(dy, dx)
                self.x = player.x + min_dist * math.cos(angle)
                self.y = player.y + min_dist * math.sin(angle)
                
                speed = math.hypot(self.vel_x, self.vel_y)
                bounce_power = max(speed * 0.95, 10) 
                
                self.vel_x = math.cos(angle) * bounce_power
                self.vel_y = math.sin(angle) * bounce_power
            else:
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
                self.is_kickoff = False
                self.vel_y = -14  
                self.vel_x = (self.x - (p1.x + p2.x) / 2) * 0.4 
                self.y = 500 - p1.radius * 2 - self.radius
                self.is_grounded = False

    def check_goal_collision(self):
        if 0 <= self.x <= 60 + self.radius:
            if abs((self.y + self.radius) - 320) <= 6 and self.vel_y > 0:
                self.y = 320 - self.radius
                self.vel_y = -self.vel_y * self.elasticity
                self.is_kickoff = False
            elif abs((self.y - self.radius) - 330) <= 6 and self.vel_y < 0:
                self.y = 330 + self.radius
                self.vel_y = -self.vel_y * self.elasticity
            elif abs(self.x - 60) <= self.radius and 320 <= self.y <= 330:
                if self.vel_x < 0:
                    self.x = 60 + self.radius
                    self.vel_x = -self.vel_x * self.elasticity

        if 940 - self.radius <= self.x <= WIDTH:
            if abs((self.y + self.radius) - 320) <= 6 and self.vel_y > 0:
                self.y = 320 - self.radius
                self.vel_y = -self.vel_y * self.elasticity
                self.is_kickoff = False
            elif abs((self.y - self.radius) - 330) <= 6 and self.vel_y < 0:
                self.y = 330 + self.radius
                self.vel_y = -self.vel_y * self.elasticity
            elif abs(self.x - 940) <= self.radius and 320 <= self.y <= 330:
                if self.vel_x > 0:
                    self.x = 940 - self.radius
                    self.vel_x = -self.vel_x * self.elasticity

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

        cx, cy = int(self.x), int(self.y)
        p_radius = self.radius * 0.32
        
        pentagon_points = []
        for i in range(5):
            angle = math.radians(i * 72 - 18) + self.rotation_angle
            px = cx + p_radius * math.cos(angle)
            py = cy + p_radius * math.sin(angle)
            pentagon_points.append((px, py))
        
        pygame.draw.polygon(surface, BLACK, pentagon_points)

        for i in range(5):
            angle = math.radians(i * 72 - 18) + self.rotation_angle
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
    
    pygame.draw.line(screen, WHITE, (0, 500), (WIDTH, 500), 3)
    pygame.draw.line(screen, WHITE, (WIDTH // 2, 500), (WIDTH // 2, 600), 3)
    pygame.draw.circle(screen, WHITE, (WIDTH // 2, 550), 35, 3)
    pygame.draw.circle(screen, WHITE, (WIDTH // 2, 550), 4) 
    pygame.draw.rect(screen, WHITE, (60, 500, 140, 75), 3) 
    pygame.draw.rect(screen, WHITE, (WIDTH - 60 - 140, 500, 140, 75), 3)

    # Porte di Sinistra
    for x in range(0, 61, 15): 
        pygame.draw.line(screen, NET_COLOR, (x, 320), (x, 500), 1)
    for y in range(320, 501, 15): 
        pygame.draw.line(screen, NET_COLOR, (0, y), (60, y), 1)

    # Porte di Destra
    for x in range(940, 1001, 15): 
        pygame.draw.line(screen, NET_COLOR, (x, 320), (x, 500), 1)
    for y in range(320, 501, 15): 
        pygame.draw.line(screen, NET_COLOR, (940, y), (1000, y), 1)
        
    pygame.draw.rect(screen, GOAL_COLOR, (0, 320, 60, 180), 5)
    pygame.draw.rect(screen, GOAL_COLOR, (940, 320, 60, 180), 5)

def main():
    player1 = Player(200, 400, BLUE, is_player_one=True)
    player2 = Player(800, 400, RED, is_player_one=False)
    ball = Ball(WIDTH // 2, 200)

    score_p1 = 0
    score_p2 = 0
    font = pygame.font.SysFont("Arial", 40, bold=True)
    stats_font = pygame.font.SysFont("Arial", 25, bold=True) 
    goal_font = pygame.font.SysFont("Arial", 100, bold=True)
    winner_font = pygame.font.SysFont("Arial", 65, bold=True) 
    rematch_font = pygame.font.SysFont("Arial", 30, bold=True) 

    match_duration = 90 
    start_ticks = pygame.time.get_ticks()
    frozen_ticks_total = 0 
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
            seconds_passed = (pygame.time.get_ticks() - start_ticks - frozen_ticks_total) // 1000
            time_left = max(0, match_duration - seconds_passed)
            if time_left == 0:
                game_over = True

            if goal_flash_timer == 0:
                player1.move(keys)
                player2.move(keys)
                handle_player_collision(player1, player2)
                
                player1.kick(keys, ball, player2)
                player2.kick(keys, ball, player1)

                ball.update()
                ball.check_collision_player(player1)
                ball.check_collision_player(player2)
                ball.check_sandwich(player1, player2)
                ball.check_goal_collision()

                if ball.y > 325:
                    is_goal = False
                    kickoff_direction = 0 

                    if ball.x < 60:
                        score_p2 += 1
                        is_goal = True
                        kickoff_direction = -8.5 
                    elif ball.x > 940:
                        score_p1 += 1
                        is_goal = True
                        kickoff_direction = 8.5
                    
                    if is_goal:
                        goal_flash_timer = 70 
                        ball = Ball(WIDTH // 2, 300, is_kickoff=True)
                        ball.vel_x = kickoff_direction
                        ball.vel_y = -2 
                        
                        player1.x, player1.y = 200, 400
                        player2.x, player2.y = 800, 400
                        player1.hit_count, player1.stun_timer, player1.hits_landed = 0, 0, 0
                        player2.hit_count, player2.stun_timer, player2.hits_landed = 0, 0, 0
            else:
                frozen_ticks_total += clock.get_time()
                goal_flash_timer -= 1
        else:
            if keys[pygame.K_r]:
                score_p1 = 0
                score_p2 = 0
                start_ticks = pygame.time.get_ticks()
                frozen_ticks_total = 0
                game_over = False
                ball = Ball(WIDTH // 2, 200)
                player1.x, player1.y = 200, 400
                player2.x, player2.y = 800, 400
                player1.hit_count, player1.stun_timer, player1.hits_landed = 0, 0, 0
                player2.hit_count, player2.stun_timer, player2.hits_landed = 0, 0, 0

        draw_scenery()
        player1.draw(screen)
        player2.draw(screen)
        ball.draw(screen)

        if goal_flash_timer > 0:
            if goal_flash_timer % 4 < 2:
                flash_surf = pygame.Surface((WIDTH, HEIGHT))
                flash_surf.fill((255, 255, 255))
                flash_surf.set_alpha(100)
                screen.blit(flash_surf, (0,0))
            goal_text = goal_font.render("GOAL!", True, GOLD)
            screen.blit(goal_text, (WIDTH//2 - goal_text.get_width()//2, HEIGHT//2 - goal_text.get_height()//2))

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
            
            rematch_text = rematch_font.render("Premi R per Rivincita", True, GRAY)
            screen.blit(rematch_text, (WIDTH//2 - rematch_text.get_width()//2, HEIGHT//2 - rematch_text.get_height()//2 + 50))

        # --- INTERFACCIA GRAFICA SUPERIORE (UI) ---
        # Centro: Tabellone principale e Timer
        score_text = font.render(f"{score_p1} - {score_p2}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
        
        timer_text = font.render(f"Tempo: {time_left if not game_over else 0}s", True, WHITE)
        screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 70))

        # Estremo Sinistro: Contatore colpi sferrati Giocatore 1 (X=40)
        p1_hits_text = stats_font.render(f"Colpi P1: {player1.hits_landed}/5", True, BLUE)
        screen.blit(p1_hits_text, (40, 35))

        # Estremo Destro: Contatore colpi sferrati Giocatore 2 (WIDTH - larghezza - 40)
        p2_hits_text = stats_font.render(f"Colpi P2: {player2.hits_landed}/5", True, RED)
        screen.blit(p2_hits_text, (WIDTH - p2_hits_text.get_width() - 40, 35))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()