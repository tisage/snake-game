#!/usr/bin/env python3
"""
Snake Game - Backup Demo Version
Simple, reliable implementation for workshop demos
"""

import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PINK = (255, 20, 147)
PURPLE = (148, 0, 211)
CYAN = (0, 255, 255)

# Food Types
FOOD_TYPE_NORMAL = "normal"
FOOD_TYPE_2X = "2x"
FOOD_TYPE_SLOW = "slow"
FOOD_TYPE_WRAP = "wrap"

FOOD_CONFIG = [
    (RED, FOOD_TYPE_NORMAL, 0.7),    # 70% chance
    (YELLOW, FOOD_TYPE_2X, 0.1),    # 10% chance
    (CYAN, FOOD_TYPE_SLOW, 0.1),    # 10% chance
    (PURPLE, FOOD_TYPE_WRAP, 0.1)   # 10% chance
]

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - LLM Workshop Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.base_fps = 10  # Lowered speed
        self.reset_game()
    
    def reset_game(self):
        # Snake starts in the middle
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # Moving right
        self.score = 0
        self.game_over = False
        
        # Power-up states
        self.slow_timer = 0
        self.wrap_timer = 0
        
        # Create multiple food items
        self.foods = []
        self.spawn_food()
        self.spawn_food()
        self.spawn_food()
    
    def spawn_food(self):
        """Spawn a food item at a random location not occupied by snake or other food"""
        max_attempts = 100
        for _ in range(max_attempts):
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            
            # Check if position is free
            if (x, y) not in self.snake and not any((x, y) == food[:2] for food in self.foods):
                # Pick food type based on weights
                r = random.random()
                cumulative = 0
                for color, f_type, weight in FOOD_CONFIG:
                    cumulative += weight
                    if r <= cumulative:
                        self.foods.append((x, y, color, f_type))
                        break
                break
    
    def handle_input(self):
        """Handle WASD key input"""
        keys = pygame.key.get_pressed()
        
        # WASD controls
        if keys[pygame.K_w] and self.direction != (0, 1):  # W - up
            self.direction = (0, -1)
        elif keys[pygame.K_s] and self.direction != (0, -1):  # S - down
            self.direction = (0, 1)
        elif keys[pygame.K_a] and self.direction != (1, 0):  # A - left
            self.direction = (-1, 0)
        elif keys[pygame.K_d] and self.direction != (-1, 0):  # D - right
            self.direction = (1, 0)
    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
        
        # Update timers
        if self.slow_timer > 0:
            self.slow_timer -= 1
        if self.wrap_timer > 0:
            self.wrap_timer -= 1
            
        # Move snake
        head_x, head_y = self.snake[0]
        new_head_x = head_x + self.direction[0]
        new_head_y = head_y + self.direction[1]
        
        # Check wall collision or wrap around
        if self.wrap_timer > 0:
            # Wrap around logic
            new_head_x %= GRID_WIDTH
            new_head_y %= GRID_HEIGHT
        else:
            # Normal wall collision
            if (new_head_x < 0 or new_head_x >= GRID_WIDTH or 
                new_head_y < 0 or new_head_y >= GRID_HEIGHT):
                self.game_over = True
                return
        
        new_head = (new_head_x, new_head_y)
        
        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check food collision
        food_eaten = False
        for i, food in enumerate(self.foods):
            fx, fy, color, f_type = food
            if new_head[0] == fx and new_head[1] == fy:
                # Apply food effects
                if f_type == FOOD_TYPE_2X:
                    self.score += 20
                else:
                    self.score += 10
                    
                if f_type == FOOD_TYPE_SLOW:
                    self.slow_timer = 50  # ~5 seconds at 10 FPS
                elif f_type == FOOD_TYPE_WRAP:
                    self.wrap_timer = 50  # ~5 seconds at 10 FPS
                    
                self.foods.pop(i)
                self.spawn_food()  # Spawn new food
                food_eaten = True
                break
        
        # Remove tail if no food eaten
        if not food_eaten:
            self.snake.pop()
    
    def draw_3d_food(self, x, y, color):
        """Draw food with 3D effect"""
        pixel_x = x * GRID_SIZE
        pixel_y = y * GRID_SIZE
        
        # Create shadow
        shadow_color = tuple(max(0, c - 100) for c in color)
        pygame.draw.circle(self.screen, shadow_color, 
                         (pixel_x + GRID_SIZE//2 + 2, pixel_y + GRID_SIZE//2 + 2), 
                         GRID_SIZE//2 - 2)
        
        # Main food circle
        pygame.draw.circle(self.screen, color, 
                         (pixel_x + GRID_SIZE//2, pixel_y + GRID_SIZE//2), 
                         GRID_SIZE//2 - 2)
        
        # Highlight
        highlight_color = tuple(min(255, c + 100) for c in color)
        pygame.draw.circle(self.screen, highlight_color, 
                         (pixel_x + GRID_SIZE//2 - 3, pixel_y + GRID_SIZE//2 - 3), 
                         GRID_SIZE//4)
    
    def render(self):
        """Render the game"""
        self.screen.fill(BLACK)
        
        # Draw snake
        for i, segment in enumerate(self.snake):
            x, y = segment
            pixel_x = x * GRID_SIZE
            pixel_y = y * GRID_SIZE
            
            # Snake head is brighter
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(self.screen, color, 
                           (pixel_x, pixel_y, GRID_SIZE-1, GRID_SIZE-1))
        
        # Draw food items with 3D effect
        for food in self.foods:
            x, y, color, f_type = food
            self.draw_3d_food(x, y, color)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw active power-ups
        y_offset = 50
        if self.slow_timer > 0:
            slow_text = self.font.render(f"SLOW MO: {self.slow_timer//10 + 1}s", True, CYAN)
            self.screen.blit(slow_text, (10, y_offset))
            y_offset += 40
        if self.wrap_timer > 0:
            wrap_text = self.font.render(f"GHOST MODE: {self.wrap_timer//10 + 1}s", True, PURPLE)
            self.screen.blit(wrap_text, (10, y_offset))
            y_offset += 40
        
        # Draw game over
        if self.game_over:
            game_over_text = self.font.render("GAME OVER! Press R to restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        print("Snake Game Controls: W/A/S/D to move, R to restart, ESC to quit")
        print("Food Powers: Yellow=2x Score, Cyan=Slow Down, Purple=Ghost Mode")
        
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:  # Quit
                        running = False
            
            # Handle continuous input
            self.handle_input()
            
            # Update game
            self.update()
            
            # Render
            self.render()
            
            # Control game speed
            current_fps = self.base_fps
            if self.slow_timer > 0:
                current_fps = self.base_fps // 2
                
            self.clock.tick(current_fps)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()