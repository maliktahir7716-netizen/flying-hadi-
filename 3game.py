import pygame
import random
import sys
import os

# Initialize Pygame and Mixer (for sound)
pygame.init()
pygame.mixer.init()

# Game Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
FPS = 60

# Colors - Aesthetic Gradient Theme
SKY_TOP = (255, 183, 197)  # Soft pink
SKY_BOTTOM = (255, 218, 185)  # Peach
CLOUD_COLOR = (255, 255, 255, 180)  # Semi-transparent white
GROUND_TOP = (186, 220, 88)  # Light green
GROUND_BOTTOM = (123, 179, 91)  # Darker green
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PIPE_COLOR = (255, 182, 193)  # Light pink
PIPE_OUTLINE = (255, 105, 180)  # Hot pink
RED = (220, 20, 60)
GOLD = (255, 215, 0)
PARTICLE_COLORS = [(255, 182, 193), (173, 216, 230), (221, 160, 221), (255, 218, 185)]

# Game Settings
GRAVITY = 0.5
JUMP_STRENGTH = -10
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 90

class Cloud:
    """Decorative cloud."""
    
    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(50, 250)
        self.speed = random.uniform(0.3, 0.8)
        self.size = random.randint(30, 60)
    
    def update(self):
        """Move cloud."""
        self.x -= self.speed
        if self.x < -100:
            self.x = WINDOW_WIDTH + 50
            self.y = random.randint(50, 250)
    
    def draw(self, screen):
        """Draw cloud."""
        # Create cloud shape with multiple circles
        surface = pygame.Surface((self.size * 3, self.size), pygame.SRCALPHA)
        pygame.draw.circle(surface, CLOUD_COLOR, (self.size, self.size//2), self.size//2)
        pygame.draw.circle(surface, CLOUD_COLOR, (self.size * 2, self.size//2), self.size//2)
        pygame.draw.circle(surface, CLOUD_COLOR, (int(self.size * 1.5), 0), self.size//2)
        screen.blit(surface, (int(self.x), int(self.y)))


class Star:
    """Twinkling star particle."""
    
    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(0, WINDOW_HEIGHT - 100)
        self.size = random.randint(1, 3)
        self.twinkle = random.randint(0, 60)
        self.color_index = random.randint(0, len(PARTICLE_COLORS) - 1)
    
    def update(self):
        """Update twinkle effect."""
        self.twinkle = (self.twinkle + 1) % 120
    
    def draw(self, screen):
        """Draw star with twinkle effect."""
        alpha = abs(60 - self.twinkle) * 4
        if alpha > 0:
            color = PARTICLE_COLORS[self.color_index] + (min(alpha, 255),)
            surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (self.size * 2, self.size * 2), self.size)
            screen.blit(surface, (int(self.x - self.size * 2), int(self.y - self.size * 2)))


class Particle:
    """Jump particle effect."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = random.uniform(-2, 2)
        self.velocity_y = random.uniform(-3, -1)
        self.life = 30
        self.size = random.randint(2, 5)
        self.color = random.choice(PARTICLE_COLORS)
    
    def update(self):
        """Update particle position."""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.2
        self.life -= 1
    
    def draw(self, screen):
        """Draw particle."""
        if self.life > 0:
            alpha = int((self.life / 30) * 255)
            color = self.color + (alpha,)
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (self.size, self.size), self.size)
            screen.blit(surface, (int(self.x - self.size), int(self.y - self.size)))
    
    def is_dead(self):
        """Check if particle is dead."""
        return self.life <= 0


class SoundManager:
    """Manages all game sounds."""
    
    def __init__(self):
        self.jump_sound = None
        self.hit_sound = None
        self.point_sound = None
        
        # Try to load default sounds (you can replace these paths)
        self.load_default_sounds()
    
    def load_default_sounds(self):
        """Create simple beep sounds if no files are provided."""
        try:
            # You can replace these with actual sound file paths
            # Example: self.jump_sound = pygame.mixer.Sound('jump.wav')
            pass
        except:
            print("No sound files found. Game will run without sound.")
    
    def load_jump_sound(self, filepath):
        """Load custom jump sound."""
        try:
            self.jump_sound = pygame.mixer.Sound(filepath)
            print(f"✓ Jump sound loaded: {filepath}")
        except Exception as e:
            print(f"✗ Failed to load jump sound: {e}")
    
    def load_hit_sound(self, filepath):
        """Load custom hit/crash sound."""
        try:
            self.hit_sound = pygame.mixer.Sound(filepath)
            print(f"✓ Hit sound loaded: {filepath}")
        except Exception as e:
            print(f"✗ Failed to load hit sound: {e}")
    
    def play_jump(self):
        """Play jump sound."""
        if self.jump_sound:
            self.jump_sound.play()
    
    def play_hit(self):
        """Play hit/crash sound."""
        if self.hit_sound:
            self.hit_sound.play()
    
    def play_point(self):
        """Play point scored sound."""
        if self.point_sound:
            self.point_sound.play()


class Bird:
    """Player character."""
    
    def __init__(self, sound_manager):
        self.x = 80
        self.y = 250
        self.width = 40
        self.height = 40
        self.velocity = 0
        self.rotation = 0
        self.image = None
        self.sound_manager = sound_manager
        self.trail = []  # Trail effect
    
    def load_image(self, filepath):
        """Load custom character image."""
        try:
            self.image = pygame.image.load(filepath)
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            print(f"✓ Character image loaded: {filepath}")
        except Exception as e:
            print(f"✗ Failed to load character image: {e}")
            self.image = None
    
    def jump(self):
        """Make the character jump."""
        self.velocity = JUMP_STRENGTH
        self.sound_manager.play_jump()  # Play jump sound
        return [(self.x + self.width//2, self.y + self.height//2) for _ in range(5)]  # Return particle positions
    
    def update(self):
        """Update character physics."""
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Update rotation
        self.rotation = min(max(self.velocity * 3, -30), 90)
        
        # Add to trail
        self.trail.append((self.x + self.width//2, self.y + self.height//2, 10))
        if len(self.trail) > 8:
            self.trail.pop(0)
        
        # Update trail alpha
        for i in range(len(self.trail)):
            x, y, alpha = self.trail[i]
            self.trail[i] = (x, y, alpha - 1)
        
        # Ground collision
        if self.y > WINDOW_HEIGHT - 100 - self.height:
            self.y = WINDOW_HEIGHT - 100 - self.height
            self.velocity = 0
    
    def draw(self, screen):
        """Draw the character with trail."""
        # Draw trail
        for i, (x, y, alpha) in enumerate(self.trail):
            if alpha > 0:
                size = int(self.width * 0.3 * (i / len(self.trail)))
                color = PARTICLE_COLORS[i % len(PARTICLE_COLORS)] + (alpha * 25,)
                surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surface, color, (size, size), size)
                screen.blit(surface, (int(x - size), int(y - size)))
        
        if self.image:
            # Rotate and draw image with glow
            rotated_image = pygame.transform.rotate(self.image, -self.rotation)
            rect = rotated_image.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            
            # Draw glow effect
            glow_surface = pygame.Surface((self.width * 2, self.height * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 255, 30), (self.width, self.height), self.width)
            screen.blit(glow_surface, (int(self.x - self.width//2), int(self.y - self.height//2)))
            
            screen.blit(rotated_image, rect)
        else:
            # Draw default circle with glow
            glow_surface = pygame.Surface((self.width * 2, self.height * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 215, 0, 50), (self.width, self.height), self.width)
            screen.blit(glow_surface, (int(self.x - self.width//2), int(self.y - self.height//2)))
            
            pygame.draw.circle(screen, GOLD, 
                             (int(self.x + self.width//2), int(self.y + self.height//2)), 
                             self.width//2)
    
    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Pipe:
    """Obstacle pipe."""
    
    def __init__(self, x, obstacle_image=None):
        self.x = x
        self.width = 60
        
        # Random height for top pipe
        self.top_height = random.randint(50, WINDOW_HEIGHT - 200 - PIPE_GAP)
        self.bottom_y = self.top_height + PIPE_GAP
        self.bottom_height = WINDOW_HEIGHT - 100 - self.bottom_y
        
        self.passed = False
        self.obstacle_image = obstacle_image
    
    def update(self):
        """Move pipe left."""
        self.x -= PIPE_SPEED
    
    def draw(self, screen):
        """Draw pipes with aesthetic design."""
        if self.obstacle_image:
            # Draw custom obstacle images with shadow
            shadow_surface = pygame.Surface((self.width + 10, max(self.top_height, self.bottom_height) + 10), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 30), (5, 5, self.width, max(self.top_height, self.bottom_height)))
            
            top_img = pygame.transform.scale(self.obstacle_image, (self.width, self.top_height))
            bottom_img = pygame.transform.scale(self.obstacle_image, (self.width, self.bottom_height))
            
            # Flip top image
            top_img = pygame.transform.flip(top_img, False, True)
            
            screen.blit(top_img, (self.x, 0))
            screen.blit(bottom_img, (self.x, self.bottom_y))
        else:
            # Draw aesthetic gradient pipes
            # Top pipe
            for i in range(self.top_height):
                gradient_factor = i / max(self.top_height, 1)
                color = tuple(int(PIPE_COLOR[j] * (1 - gradient_factor * 0.3)) for j in range(3))
                pygame.draw.line(screen, color, (self.x, i), (self.x + self.width, i))
            
            # Pipe outline and cap
            pygame.draw.rect(screen, PIPE_OUTLINE, (self.x, 0, self.width, self.top_height), 3)
            pygame.draw.rect(screen, PIPE_OUTLINE, (self.x - 5, self.top_height - 20, self.width + 10, 20))
            pygame.draw.rect(screen, PIPE_COLOR, (self.x - 5, self.top_height - 20, self.width + 10, 20), 3)
            
            # Bottom pipe
            for i in range(self.bottom_height):
                gradient_factor = i / max(self.bottom_height, 1)
                color = tuple(int(PIPE_COLOR[j] * (1 - gradient_factor * 0.3)) for j in range(3))
                pygame.draw.line(screen, color, (self.x, self.bottom_y + i), (self.x + self.width, self.bottom_y + i))
            
            pygame.draw.rect(screen, PIPE_OUTLINE, (self.x, self.bottom_y, self.width, self.bottom_height), 3)
            pygame.draw.rect(screen, PIPE_OUTLINE, (self.x - 5, self.bottom_y, self.width + 10, 20))
            pygame.draw.rect(screen, PIPE_COLOR, (self.x - 5, self.bottom_y, self.width + 10, 20), 3)
    
    def is_off_screen(self):
        """Check if pipe is off screen."""
        return self.x + self.width < 0
    
    def get_rects(self):
        """Get collision rectangles."""
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width, self.bottom_height)
        return [top_rect, bottom_rect]


def check_collision(bird, pipes):
    """Check if bird collides with pipes."""
    bird_rect = bird.get_rect()
    
    for pipe in pipes:
        for pipe_rect in pipe.get_rects():
            if bird_rect.colliderect(pipe_rect):
                return True
    
    # Check ground collision
    if bird.y + bird.height >= WINDOW_HEIGHT - 100:
        return True
    
    return False


def draw_text(screen, text, size, x, y, color=WHITE, shadow=True):
    """Draw text with shadow."""
    font = pygame.font.Font(None, size)
    if shadow:
        shadow_surface = font.render(text, True, (0, 0, 0, 100))
        shadow_rect = shadow_surface.get_rect(center=(x + 3, y + 3))
        screen.blit(shadow_surface, shadow_rect)
    
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)


def main():
    """Main game function."""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Flappy Game with Sound")
    clock = pygame.time.Clock()
    
    # Initialize sound manager
    sound_manager = SoundManager()
    
    # Print instructions
    print("\n" + "="*50)
    print("FLAPPY GAME - Sound Setup Instructions")
    print("="*50)
    print("\nTo add custom sounds and images:")
    print("1. Place files in the same folder as this script")
    print("2. Name them as follows:")
    print("   - character.png (character image)")
    print("   - obstacle.png (obstacle image)")
    print("   - jump.wav or jump.mp3 (jump sound)")
    print("   - hit.wav or hit.mp3 (crash sound)")
    print("\n" + "="*50)
    print("\nControls:")
    print("- SPACE or MOUSE CLICK: Jump")
    print("- R: Restart after game over")
    print("- ESC: Quit")
    print("="*50 + "\n")
    
    # Try to load custom files
    bird = Bird(sound_manager)
    obstacle_image = None
    
    # Load character image
    if os.path.exists('character.png'):
        bird.load_image('character.png')
    
    # Load obstacle image
    if os.path.exists('obstacle.png'):
        try:
            obstacle_image = pygame.image.load('obstacle.png')
            print("✓ Obstacle image loaded: obstacle.png")
        except:
            print("✗ Failed to load obstacle.png")
    
    # Load sounds
    for jump_file in ['jump.wav', 'jump.mp3', 'jump.ogg']:
        if os.path.exists(jump_file):
            sound_manager.load_jump_sound(jump_file)
            break
    
    for hit_file in ['hit.wav', 'hit.mp3', 'crash.wav', 'crash.mp3']:
        if os.path.exists(hit_file):
            sound_manager.load_hit_sound(hit_file)
            break
    
    # Game variables
    pipes = []
    particles = []
    clouds = [Cloud() for _ in range(5)]
    stars = [Star() for _ in range(20)]
    score = 0
    best_score = 0
    frame_count = 0
    game_active = False
    game_over = False
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                if event.key == pygame.K_SPACE:
                    if not game_active and not game_over:
                        game_active = True
                    if game_active and not game_over:
                        particle_positions = bird.jump()
                        # Create jump particles
                        for pos in particle_positions:
                            particles.append(Particle(pos[0], pos[1]))
                    
                if event.key == pygame.K_r and game_over:
                    # Restart
                    bird = Bird(sound_manager)
                    if os.path.exists('character.png'):
                        bird.load_image('character.png')
                    pipes = []
                    particles = []
                    score = 0
                    frame_count = 0
                    game_active = False
                    game_over = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game_active and not game_over:
                    game_active = True
                if game_active and not game_over:
                    particle_positions = bird.jump()
                    # Create jump particles
                    for pos in particle_positions:
                        particles.append(Particle(pos[0], pos[1]))
        
        # Update game
        if game_active and not game_over:
            frame_count += 1
            
            # Update bird
            bird.update()
            
            # Update particles
            for particle in particles[:]:
                particle.update()
                if particle.is_dead():
                    particles.remove(particle)
            
            # Spawn pipes
            if frame_count % PIPE_FREQUENCY == 0:
                pipes.append(Pipe(WINDOW_WIDTH, obstacle_image))
            
            # Update pipes
            for pipe in pipes[:]:
                pipe.update()
                
                # Check if passed
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1
                    sound_manager.play_point()
                
                # Remove off-screen pipes
                if pipe.is_off_screen():
                    pipes.remove(pipe)
            
            # Check collision
            if check_collision(bird, pipes):
                game_over = True
                sound_manager.play_hit()  # Play hit sound
                if score > best_score:
                    best_score = score
        
        # Update background elements
        for cloud in clouds:
            cloud.update()
        for star in stars:
            star.update()
        
        # Draw everything - Gradient sky background
        for y in range(WINDOW_HEIGHT - 100):
            gradient_factor = y / (WINDOW_HEIGHT - 100)
            color = tuple(int(SKY_TOP[i] + (SKY_BOTTOM[i] - SKY_TOP[i]) * gradient_factor) for i in range(3))
            pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))
        
        # Draw stars
        for star in stars:
            star.draw(screen)
        
        # Draw clouds
        for cloud in clouds:
            cloud.draw(screen)
        
        # Draw ground with gradient
        for y in range(100):
            gradient_factor = y / 100
            color = tuple(int(GROUND_TOP[i] + (GROUND_BOTTOM[i] - GROUND_TOP[i]) * gradient_factor) for i in range(3))
            pygame.draw.line(screen, color, (0, WINDOW_HEIGHT - 100 + y), (WINDOW_WIDTH, WINDOW_HEIGHT - 100 + y))
        
        # Ground decoration - grass blades
        for x in range(0, WINDOW_WIDTH, 15):
            offset = (frame_count % 30) - 15
            grass_x = x + offset
            if 0 <= grass_x < WINDOW_WIDTH:
                pygame.draw.line(screen, (100, 150, 50), (grass_x, WINDOW_HEIGHT - 100), 
                               (grass_x + 2, WINDOW_HEIGHT - 110), 3)
        
        pygame.draw.line(screen, (80, 140, 60), (0, WINDOW_HEIGHT - 100), (WINDOW_WIDTH, WINDOW_HEIGHT - 100), 4)
        
        # Draw pipes
        for pipe in pipes:
            pipe.draw(screen)
        
        # Draw bird
        bird.draw(screen)
        
        # Draw score
        draw_text(screen, str(score), 64, WINDOW_WIDTH // 2, 50)
        
        # Draw start message
        if not game_active and not game_over:
            draw_text(screen, "Flappy Game with Sound", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60)
            draw_text(screen, "Press SPACE or CLICK to start", 28, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            draw_text(screen, f"Best Score: {best_score}", 32, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)
        
        # Draw game over
        if game_over:
            draw_text(screen, "GAME OVER!", 64, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60, RED)
            draw_text(screen, f"Score: {score}", 40, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            draw_text(screen, f"Best: {best_score}", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)
            draw_text(screen, "Press R to restart", 28, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000