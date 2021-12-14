from typing_extensions import ParamSpecArgs
import pygame
from pygame.locals import *
import sys
import random
import time

pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional
 
HEIGHT = 450
WIDTH = 400
#create realistic movement and implement gravity
ACC = 0.5
FRIC = -0.12
FPS = 60
 
FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

#Creating surface objects in each class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.surf = pygame.Surface((30, 30))
        self.surf.fill((128,255,40))
        self.rect = self.surf.get_rect()

        #vec is simply used to create variables with two dimensions.
        self.pos = vec((10, 385)) #first parameters represents acceleration/velocity along the X axis and the second is for the Y axis
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.jumping = False
        self.score = 0

    #for player to move it
    def move(self):
        self.acc = vec(0,0.5) #constant force of gravity/ makes the object fall
        
        pressed_keys = pygame.key.get_pressed()
        #If the left key has been pressed, it will update the acceleration with a negative value (acceleration in the opposite direction) 
        #If the right key has been pressed, acceleration will have a positive value
        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC  

        #use friction to to decrease the value of the velocity. Without friction, our player would not de-accelerate
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc    

        #AKA “screen warping” allows you to “go through” the left side of the screen, and pop up on the right side. 
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
     
        self.rect.midbottom = self.pos #updates to current position
 
    #Ensures the player cannot jump again until he is in contact with the floor again.
    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
           self.jumping = True
           self.vel.y = -15

    def cancel_jump(self): #to decrease the velocity of the player.
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3
    
    def update(self):
        hits = pygame.sprite.spritecollide(P1 ,platforms, False)
        if self.vel.y > 0:        
            if hits:
                if self.pos.y < hits[0].rect.bottom:  
                    self.vel.y = 0
                    self.pos.y = hits[0].rect.top + 1 #makes sure velocity is not set to zero unless there is already some initial velocity
                    self.vel.y = 0
                    self.jumping = False

class platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((random.randint(50,100), 12))
        self.surf.fill((0,255,0))
        self.rect = self.surf.get_rect(center = (random.randint(0,WIDTH-10),
                                                 random.randint(0, HEIGHT-30)))

        self.speed = random.randint(-1, 1)
        
        self.point = True   
        self.moving = True

    def move(self):
        if self.moving == True:  
            self.rect.move_ip(self.speed,0)
            if self.speed > 0 and self.rect.left > WIDTH:
                self.rect.right = 0
            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = WIDTH


def check(platform, groupies):
    if pygame.sprite.spritecollideany(platform,groupies):
        return True
    else:
        for entity in groupies:
            if entity == platform:
                continue
            if (abs(platform.rect.top - entity.rect.bottom) < 40) and (abs(platform.rect.bottom - entity.rect.top) < 40):
                return True
        C = False

#Creating platforms
def plat_gen():
    while len(platforms) < 7 : #we only initialized 5 – 6 platforms. Yet, here we have 7. This code is supposed to run only when there are less than 7 platforms on screen.
        width = random.randrange(50,100) #Assigns a random width which we’ve use to create new platforms. Added for a degree of variety in our platforms.
        p  = platform()             
        p.rect.center = (random.randrange(0, WIDTH - width), #Creates and places the platform right above the visible part of the screen. The position is randomly generated using the random library.
                             random.randrange(-50, 0))
        platforms.add(p) #the platform is added to both sprite groups.
        all_sprites.add(p)

 
PT1 = platform()
P1 = Player()

PT1.surf = pygame.Surface((WIDTH, 20))
PT1.surf.fill((255,0,0))
PT1.rect = PT1.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))

all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)

platforms = pygame.sprite.Group()
platforms.add(PT1)

PT1.moving = False
PT1.point = False

#The code will run either 5 or 6 time
for x in range(random.randint(5, 6)):
    C = True
    pl = platform()
    while C:
        pl = platform()
        C = check(pl, platforms)
    platforms.add(pl)
    all_sprites.add(pl)

while True:
    P1.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit() #If the person keeps pressing space bar, the player will jump again in mid air.
        if event.type == pygame.KEYDOWN:    
            if event.key == pygame.K_SPACE:
                P1.jump()
        if event.type == pygame.KEYUP:    
            if event.key == pygame.K_SPACE:
                P1.cancel_jump() 

    if P1.rect.top > HEIGHT:
        for entity in all_sprites:
            entity.kill()
            time.sleep(1)
            displaysurface.fill((255,0,0))
            pygame.display.update()
            time.sleep(1)
            pygame.quit()
            sys.exit()

    if P1.rect.top <= HEIGHT / 3: #checks to see the position of the player with respect to the screen. basically the deciding point for when to move the screen up. 
        #After some testing with our screen size, player speed etc, we decided on setting that point for HEIGHT / 3.
        P1.pos.y += abs(P1.vel.y) #keep updating the position of the player as the screen moves. use the abs() function to remove the negative sign from the velocity value.
        for plat in platforms:
            plat.rect.y += abs(P1.vel.y) #updating positions for all sprites
            if plat.rect.top >= HEIGHT: #destroys any platforms that go off the screen from the bottom.
                plat.kill()
    plat_gen()
    displaysurface.fill((0,0,0))
    f = pygame.font.SysFont("Verdana", 20)     
    g  = f.render(str(P1.score), True, (123,255,0))   
    displaysurface.blit(g, (WIDTH/2, 10))   

    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
        entity.move()
 
    pygame.display.update()
    FramePerSec.tick(FPS)