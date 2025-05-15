import pygame
import random
import sys
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
TARGET_RADIUS = 40
TARGET_SPEED = 1.2  # Slower than before
SPAWN_RATE = 60  # More forgiving spawn rate
INITIAL_TIME = 30  # Starting time (seconds)
TIME_PER_HIT = 2  # Seconds added per hit
TIME_PENALTY = 1  # Seconds lost per missed target
BG_COLOR = (10, 10, 30)

# Colors
WHITE = (255, 255, 255)
GREEN = (50, 255, 50)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
BLUE = (100, 100, 255)

# Fonts
font_large = pygame.font.SysFont("Arial", 36)
font_medium = pygame.font.SysFont("Arial", 26)

class Target:
    def __init__(self, word):
        self.word = word
        self.radius = TARGET_RADIUS
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT // 2)
        self.speed_x = random.choice([-TARGET_SPEED, TARGET_SPEED])
        self.speed_y = 0
        self.typed_so_far = ""
        self.is_alive = True

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Bounce off edges
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.speed_x *= -1
        if self.y <= self.radius or self.y >= HEIGHT - self.radius:
            self.speed_y *= -1

    def draw(self, screen):
        # Draw target
        pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, RED)
        pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, WHITE)
        
        # Draw word
        text = font_medium.render(self.word, True, WHITE)
        screen.blit(text, (self.x - text.get_width() // 2, self.y - text.get_height() // 2))
        
        # Draw typed progress
        progress = font_medium.render(self.typed_so_far, True, GREEN)
        screen.blit(progress, (self.x - progress.get_width() // 2, self.y + self.radius + 5))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Target Shooting Typing Game")

    word_list = ["pygame", "target", "shoot", "code", "type", "hit", "key", "fun"]
    active_targets = []
    current_input = ""
    score = 0
    timer = INITIAL_TIME * 60  # Convert to frames
    clock = pygame.time.Clock()
    spawn_timer = 0
    explosions = []

    running = True
    while running:
        screen.fill(BG_COLOR)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    current_input = current_input[:-1]
                else:
                    current_input += event.unicode.lower()

        # Check for hits
        for target in active_targets[:]:
            if current_input.lower() == target.word:
                score += len(target.word) * 10
                timer += TIME_PER_HIT * 60  # Add time
                active_targets.remove(target)
                current_input = ""
                explosions.extend([(target.x, target.y, random.randint(10, 20)) for _ in range(10)])
                break

        # Update targets and track typing progress
        for target in active_targets:
            target.update()
            target.typed_so_far = ""
            for i in range(min(len(current_input), len(target.word))):
                if current_input[i] == target.word[i]:
                    target.typed_so_far += current_input[i]

        # Spawn new targets
        spawn_timer += 1
        if spawn_timer >= SPAWN_RATE:
            active_targets.append(Target(random.choice(word_list)))
            spawn_timer = 0

        # Update timer and check for misses
        timer -= 1
        for target in active_targets[:]:
            if target.y > HEIGHT + target.radius:  # Fell off screen
                active_targets.remove(target)
                timer -= TIME_PENALTY * 60  # Reduce time
                explosions.extend([(target.x, HEIGHT, random.randint(5, 10)) for _ in range(5)])  # Bottom explosion

        # Draw explosions
        for particle in explosions[:]:
            x, y, life = particle
            pygame.gfxdraw.filled_circle(screen, int(x), int(y), life // 2, YELLOW)
            explosions.remove(particle)
            if life > 1:
                explosions.append((x + random.randint(-3, 3), y + random.randint(-3, 3), life - 1))

        # Draw targets
        for target in active_targets:
            target.draw(screen)

        # Draw UI
        time_left = max(0, timer // 60)
        ui_text = f"Time: {time_left}s | Score: {score} | Next: {SPAWN_RATE - spawn_timer}"
        ui_surface = font_medium.render(ui_text, True, BLUE)
        screen.blit(ui_surface, (20, 20))

        input_surface = font_medium.render(f"Typing: {current_input}", True, GREEN)
        screen.blit(input_surface, (20, HEIGHT - 50))

        # Game over check
        if timer <= 0:
            game_over_text = font_large.render(f"GAME OVER! Score: {score}", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()