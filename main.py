import pgzrun
from pygame import Rect
import random

# Window
WIDTH = 1440
HEIGHT = 400
floor = Rect((0, HEIGHT - 10), (WIDTH, 10)) # the platform to make the character and enemy seem more believable standing on ground

#  Game States
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"
game_state = MENU

# #Music
music_on = True
music.set_volume(0.5)
music.play("backgroundmusic")

def toggle_music():
    global music_on
    if music_on:
        music.stop()
        music_on = False
    else:
        music.play("backgroundmusic")
        music_on = True

# Sounds
sounds_on = True

#Player
class Player:
    def __init__(self):
        self.actor = Actor("swatidle")
        self.actor.pos = (WIDTH // 2, HEIGHT - 40)
        self.actor.scale = 0.125
        self.speed = 5
        self.jumping = False
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.facing_left = False
        self.shooting_timer = 0
        self.current_frame = 0
        self.frame_counter = 0

        self.run_frames_right = ["swatrun1", "swatrun2"]
        self.run_frames_left = ["swatrun1-left", "swatrun2-left"]
        self.idle_right = "swatidle"
        self.idle_left = "swatidle-left"
        self.jump_right = "swatjump"
        self.jump_left = "swatjump-left"
        self.shoot_right = "swatshoot"
        self.shoot_left = "swatshoot-left"

    def update(self):
        moving = False
        if keyboard.left:
            self.actor.x -= self.speed
            moving = True
            self.facing_left = True
        elif keyboard.right:
            self.actor.x += self.speed
            moving = True
            self.facing_left = False

        if self.jumping:
            self.velocity_y += self.gravity
            self.actor.y += self.velocity_y
            self.actor.image = self.jump_left if self.facing_left else self.jump_right

        # to check if player is in jump position on on ground to determine the idle or moving position
        player_bottom = self.actor.y + self.actor.height / 2
        if player_bottom >= floor.top:
            self.actor.y = floor.top - self.actor.height / 2
            if self.jumping:
                self.jumping = False
                self.velocity_y = 0
                if self.shooting_timer == 0:
                    self.actor.image = self.idle_left if self.facing_left else self.idle_right


        if self.shooting_timer > 0:
            self.shooting_timer -= 1
        elif moving and not self.jumping:
            self.frame_counter += 1
            if self.frame_counter >= 10:
                self.frame_counter = 0
                self.current_frame = (self.current_frame + 1) % 2
            self.actor.image = self.run_frames_left[self.current_frame] if self.facing_left else self.run_frames_right[self.current_frame]
        elif not moving and not self.jumping:
            self.actor.image = self.idle_left if self.facing_left else self.idle_right

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.velocity_y = self.jump_strength
            if sounds_on:
                sounds.playerjump.play()

    def shoot(self):
        self.shooting_timer = 5
        self.actor.image = self.shoot_left if self.facing_left else self.shoot_right
        if sounds_on:
            sounds.shoot.play()
        return Bullet(self.actor.x, self.actor.y, self.facing_left)

    def hitbox(self):
        scale = 0.5
        return Rect(
            (self.actor.x - self.actor.width / 2 * scale,
             self.actor.y - self.actor.height / 2 * scale),
            (self.actor.width * scale, self.actor.height * scale)
        )

# Bullet - simple usage of bullet png picture that moves either left or right depending on the player position
class Bullet:
    def __init__(self, x, y, left):
        self.actor = Actor("bullet")
        self.actor.pos = (x, y)
        self.speed = -10 if left else 10

    def update(self):
        self.actor.x += self.speed

    def hitbox(self):
        return Rect(
            (self.actor.x - self.actor.width/2,
             self.actor.y - self.actor.height/2),
            (self.actor.width, self.actor.height)
        )

# Enemy - 2 enemies determined by their location (left and right) and their movement speed as well as different skins/pictures
class Enemy:
    def __init__(self):
        self.actor = Actor("banditrun1")
        self.actor.pos = (-50, floor.top - self.actor.height/2)
        self.actor.scale = 0.125
        self.speed = 3
        self.frames = ["banditrun1", "banditrun2"]
        self.frame_index = 0
        self.frame_counter = 0

    def update(self):
        self.actor.x += self.speed
        self.frame_counter += 1
        if self.frame_counter >= 10:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.actor.image = self.frames[self.frame_index]

    def hitbox(self):
        scale = 0.5
        return Rect(
            (self.actor.x - self.actor.width/2*scale,
             self.actor.y - self.actor.height/2*scale),
            (self.actor.width*scale, self.actor.height*scale)
        )

class Bandit2(Enemy):
    def __init__(self):
        super().__init__()
        self.actor = Actor("bandit2run1")
        self.actor.pos = (WIDTH + 50, floor.top - self.actor.height/2)
        self.speed = -4.5
        self.frames = ["bandit2run1", "bandit2run2"]
        self.frame_index = 0
        self.frame_counter = 0

# Menu - as explained in the DST file, there needs to be start button, music toggle, sound toggle and exit button which are defined as function later on
menu_buttons = {
    "start": Rect((WIDTH//2 - 100, 150), (200, 50)),
    "music": Rect((WIDTH//2 - 100, 220), (200, 50)),
    "sounds": Rect((WIDTH//2 - 100, 290), (200, 50)),
    "exit": Rect((WIDTH//2 - 100, 360), (200, 50))
}

game_over_buttons = {
    "restart": Rect((WIDTH//2 - 200, 280), (150, 50)),
    "exit": Rect((WIDTH//2 + 50, 280), (150, 50))
}

# Game - Initital values when starting
player = Player()
bullets = []
enemies = []
enemy_spawn_timer = 0
ENEMY_SPAWN_INTERVAL = 120
score = 0

# Draw
def draw_buttons():
    for name, rect in menu_buttons.items():
        screen.draw.filled_rect(rect, "gray")
        if name == "music":
            label = f"Music: {'ON' if music_on else 'OFF'}"
        elif name == "sounds":
            label = f"Sounds: {'ON' if sounds_on else 'OFF'}"
        else:
            label = name.replace("_", " ").title()
        screen.draw.text(label, center=rect.center, fontsize=40, color="white")

def draw_game_over_buttons():
    for name, rect in game_over_buttons.items():
        screen.draw.filled_rect(rect, "gray")
        label = name.replace("_", " ").title()
        screen.draw.text(label, center=rect.center, fontsize=40, color="white")

def draw():
    screen.fill("black")
    if game_state == MENU:
        screen.draw.text("Urban Shooter", center=(WIDTH//2, HEIGHT//2 - 100), fontsize=60, color="white")
        draw_buttons()
    elif game_state == PLAYING:
        screen.blit("background", (0,0))
        player.actor.draw()
        for b in bullets:
            b.actor.draw()
        for e in enemies:
            e.actor.draw()
        screen.draw.text(f"Score: {score}", (WIDTH - 200, 20), fontsize=40, color="white")
    elif game_state == PAUSED:
        screen.blit("background", (0,0))
        player.actor.draw()
        for b in bullets:
            b.actor.draw()
        for e in enemies:
            e.actor.draw()
        screen.draw.text(f"Score: {score}", (WIDTH - 200, 20), fontsize=40, color="white")
        screen.draw.text("PAUSED", center=(WIDTH//2, HEIGHT//2), fontsize=80, color="red")
    elif game_state == GAME_OVER:
        screen.blit("background", (0, 0))
        screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=80, color="red")
        screen.draw.text(f"Score: {score}", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=50, color="white")
        draw_game_over_buttons()

# Update - checking the enemies in game, the score status as well as game status if playing or lost
def update():
    global enemy_spawn_timer, score, game_state
    if game_state != PLAYING:
        return

    player.update()

    for b in bullets[:]:
        b.update()
        if b.actor.x < 0 or b.actor.x > WIDTH:
            bullets.remove(b)

    enemy_spawn_timer += 1
    if enemy_spawn_timer >= ENEMY_SPAWN_INTERVAL:
        enemy_spawn_timer = 0
        if random.random() < 0.5:
            enemies.append(Enemy())
        else:
            enemies.append(Bandit2())

    player_hitbox = player.hitbox()

    for e in enemies[:]:
        e.update()
        enemy_hitbox = e.hitbox()
        for b in bullets[:]:
            if enemy_hitbox.colliderect(b.hitbox()):
                bullets.remove(b)
                enemies.remove(e)
                score += 2 if isinstance(e, Bandit2) else 1
                break

        player_on_floor = abs(player.actor.y + player.actor.height/2 - floor.top) < 1
        if enemy_hitbox.colliderect(player_hitbox) and player_on_floor:
            game_state = GAME_OVER

        if isinstance(e, Enemy) and e.actor.left > WIDTH+50:
            enemies.remove(e)
        elif isinstance(e, Bandit2) and e.actor.right < -50:
            enemies.remove(e)

# Key functions - there are 4 used buttons total - arrow left, right and up as well as space, mouse clicks for start and end game too
def on_key_down(key):
    global game_state
    if game_state == PLAYING:
        if key == keys.UP:
            player.jump()
        elif key == keys.SPACE:
            bullets.append(player.shoot())
        elif key == keys.P:
            game_state = PAUSED
    elif game_state == PAUSED and key == keys.P:
        game_state = PLAYING

#Mouse
def on_mouse_down(pos):
    global game_state, score, bullets, enemies, player, sounds_on
    if game_state == MENU:
        if menu_buttons["start"].collidepoint(pos):
            game_state = PLAYING
            score = 0
            bullets.clear()
            enemies.clear()
        elif menu_buttons["music"].collidepoint(pos):
            toggle_music()
        elif menu_buttons["sounds"].collidepoint(pos):
            sounds_on = not sounds_on
        elif menu_buttons["exit"].collidepoint(pos):
            exit()
    elif game_state == GAME_OVER:
        if game_over_buttons["restart"].collidepoint(pos):
            game_state = PLAYING
            score = 0
            bullets.clear()
            enemies.clear()
            player.actor.pos = (WIDTH // 2, HEIGHT - 40)
            player.jumping = False
            player.velocity_y = 0
        elif game_over_buttons["exit"].collidepoint(pos):
            exit()
pgzrun.go()
