import pygame
import sys
import math

# Inizializzazione Pygame
pygame.init()

# Costanti di Gioco
WIDTH, HEIGHT = 1000, 600
FPS = 60
GRAVITY = 0.6
FRICTION = 0.99  # Attrito dell'aria per la palla

# Colori
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
BLUE = (30, 144, 255)
RED = (220, 20, 60)
BALL_COLOR = (240, 240, 240)
GOAL_COLOR = (200, 200, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Head Ball 2 Clone - Fixed Arrow Keys")
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
        old_x = self.x
        old_y = self.y

        # --- GESTIONE INPUT MOVIMENTO ---
        if self.is_player_one:
            # P1: WASD
            if keys[pygame.K_a] and self.x - self.radius > 0:
                self.x -= self.speed
            if keys[pygame.K_d] and self.x + self.radius < WIDTH:
                self.x += self.speed
            if keys[pygame.K_w] and self.is_grounded:
                self.vel_y = self.jump_power
                self.is_grounded = False
        else:
            # P2: FRECCE DIREZIONALI (Sincronizzazione forzata)
            if (keys[pygame.K_LEFT] or keys[276]) and self.x - self.radius > 0:
                self.x -= self.speed
            if (keys[pygame.K_RIGHT] or keys[275]) and self.x + self.radius < WIDTH:
                self.x += self.speed
            if (keys[pygame.K_UP] or keys[273]) and self.is_grounded:
                self.vel_y = self.jump_power
                self.is_grounded = False

        # --- FISICA DEL SALTO CON LE TUE MODIFICHE ---
        PLAYER_GRAVITY = 0.95
        
        if self.vel_y > 0:
            self.vel_y += PLAYER_GRAVITY * 2.0  # La tua modifica fissa
        else:
            self.vel_y += PLAYER_GRAVITY
            
        self.y += self.vel_y

        # --- COLLISIONE SOFFITTO INVISIBILE ---
        if self.y - self.radius <= 100:
            self.y = 100 + self.radius
            self.vel_y = 0

        # --- COLLISIONE CON LE TRAVERSE DELLE PORTE ---
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
                    if on_left_crossbar:
                        self.x = 80 + self.radius
                    if on_right_crossbar:
                        self.x = 920 - self.radius

        # --- COLLISIONE CON IL TERRENO ---
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
                # P1: F = Raso terra, G = Pallonetto
                if keys[pygame.K_f]:   
                    ball.vel_x = 15
                    ball.vel_y = -2
                elif keys[pygame.K_g]: 
                    ball.vel_x = 10
                    ball.vel_y = -13
            else:
                # P2: - (Trattino) = Raso terra, . (Punto) = Pallonetto
                # Aggiunti controlli numerici alternativi per evitare conflitti di layout
                if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS] or keys[45]: 
                    ball.vel_x = -15
                    ball.vel_y = -2
                elif keys[pygame.K_PERIOD] or keys[pygame.K_KP_PERIOD] or keys[46]: 
                    ball.vel_x = -10
                    ball.vel_y = -13

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

    def update(self):
        self.vel_y += GRAVITY
        self.vel_x *= FRICTION
        
        self.x += self.vel_x
        self.y += self.vel_y

        # Collisione Terreno
        if self.y + self.radius >= 500:
            self.y = 500 - self.radius
            self.vel_y = -self.vel_y * self.elasticity
            self.vel_x *= 0.95
            self.is_grounded = True
        else:
            if abs((self.y + self.radius) - 500) < 5:
                self.is_grounded = True
            else:
                self.is_grounded = False

        # Collisione Soffitto
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vel_y = -self.vel_y * self.elasticity

        # Collisioni Pareti Laterali
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
            angle = math.atan2(dy, dx)
            self.x = player.x + min_dist * math.cos(angle)
            self.y = player.y + min_dist * math.sin(angle)
            
            speed = math.hypot(self.vel_x, self.vel_y)
            actual_speed = max(speed * self.elasticity, 5) 
            
            self.vel_x = math.cos(angle) * actual_speed
            self.vel_y = math.sin(angle) * actual_speed

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
        pygame.draw.circle(surface, BALL_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0,0,0), (int(self.x), int(self.y)), self.radius, 2)


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

    running = True
    while running:
        clock.tick(FPS)
        
        # Gestione interna degli eventi necessaria per aggiornare lo stato di pygame.key.get_pressed()
        pygame.event.pump()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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
            if ball.x + ball.radius < 80:
                score_p2 += 1
                ball = Ball(WIDTH // 2, 200)
                player1.x, player1.y = 200, 400
                player2.x, player2.y = 800, 400
            elif ball.x - ball.radius > 920:
                score_p1 += 1
                ball = Ball(WIDTH // 2, 200)
                player1.x, player1.y = 200, 400
                player2.x, player2.y = 800, 400

        draw_scenery()
        player1.draw(screen)
        player2.draw(screen)
        ball.draw(screen)

        score_text = font.render(f"{score_p1} - {score_p2}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()