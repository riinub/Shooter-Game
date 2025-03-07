import pygame
import sys
from os.path  import join
from random import randint, uniform
import pygame.freetype

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 600
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(("Space shooter"))

running = True
score = 0
clock = pygame.time.Clock()

# import sounds
game_music = pygame.mixer.Sound(join( 'audio', 'game_music.wav'))
game_music.set_volume(0.1)
game_music.play()
laser_sound = pygame.mixer.Sound(join( 'audio', 'laser-shot.mp3'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join( 'audio', 'explosion.wav'))
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'playerimg.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH /2, WINDOW_HEIGHT/2))
        self.direction = pygame.math.Vector2()
        self.speed = 300
        #coldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 300
        
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >=self.cooldown_duration:
                self.can_shoot = True
                
    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        #normalization
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed *dt
        
        recent_keys = pygame.key.get_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        self.laser_timer()
        
        #boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT      
            
class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0,WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))
        
class Laser(pygame.sprite.Sprite):
    def __init__(self,surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        
    def update(self, dt):
        self.rect.centery -= 300*dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self,surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 2000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(200, 300)
        
    def update(self, dt):
        self.rect.center += self.direction* self.speed* dt 
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
           
class Explosives(pygame.sprite.Sprite):
    def __init__(self,frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frames_index = 0
        self.image = self.frames[self.frames_index]
        self.rect = self.image.get_frect(center = pos)

    def update(self, dt):
        self.frames_index += 20* dt
        if self.frames_index < len(self.frames):
            self.image = self.frames[int(self.frames_index)]
        else:
            self.kill()
        
def collisions():
    global running
    global score 
    collision_sprites =pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False
        
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            score += 1
            laser.kill()
            Explosives(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
            
#Font Displays
font_time = pygame.font.Font(join('images', 'Funkie Retro.otf'), 30)

def display_score():
    current_time = pygame.time.get_ticks() //1000
    text_surf2 = font_time.render(f"Time: {str(current_time)}", True, (240, 240, 240))
    kill_surf = font_time.render(f"Score: {str(score)}", True,(240, 240, 240))
    text_rect2 = text_surf2.get_frect(midleft = (15, 30))
    kill_rect = kill_surf.get_frect(midleft = (15, 60))
    display_surface.blit(text_surf2, text_rect2)
    display_surface.blit(kill_surf, kill_rect)
    

# Sprtie groups
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# Imports
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()

for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)

# custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500) #the event you want to loop and iteration in milisecs

# Main event loop
while running: 
    dt= clock.tick() / 500
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x,y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x,y), (all_sprites, meteor_sprites))

    all_sprites.update(dt)
    collisions()
    display_surface.fill('#302438')
    all_sprites.draw(display_surface)  
    display_score()
    pygame.display.update()

pygame.quit()   