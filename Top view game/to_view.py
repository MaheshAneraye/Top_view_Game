from typing import *
import pygame
from sys import exit
import math

from pygame.sprite import Group
from settings import *

pygame.init()

win=pygame.display.set_mode((width,height))
pygame.display.set_caption("TOP_VIEW")
clock=pygame.time.Clock()

score=0



bg=pygame.image.load("background.png")
font=pygame.font.Font('Pixellettersfull-Bnj5.ttf',35)
text=font.render('Score:'+str(score),True,'white')
 

last_spawn_time = pygame.time.get_ticks()  

class player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(player_group, all_sprites_group)
        self.image=pygame.transform.rotozoom(pygame.image.load('player_1.png').convert_alpha(),0,player_size)
        self.base_player_image=self.image                                         #copy the base player image
        self.pos=pygame.math.Vector2(player_start_x,player_start_y)
        
        self.hitbox_rect=self.base_player_image.get_rect(center=self.pos)          #hitbox rect
        self.rect=self.hitbox_rect.copy()                                          #rotating rect 
        
        self.speed=player_speed
        self.shoot=False
        self.shoot_cooldown = 0
        self.gun_barrel_offset= pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y)
        
    def player_rotation(self):
        self.mouse_coord=pygame.mouse.get_pos()
        self.x_change_mouse_player= (self.mouse_coord[0]) - (self.hitbox_rect.centerx)
        self.y_change_mouse_player= (self.mouse_coord[1]) - (self.hitbox_rect.centery)
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player))
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect= self.image.get_rect(center= self.hitbox_rect.center)
        
        
    def user_input(self):
        self.velocity_x=0
        self.velocity_y=0
        
        keys=pygame.key.get_pressed()
        
        if keys [pygame.K_w]:
            self.velocity_y -= player_speed
            
        if keys [pygame.K_s] :
            self.velocity_y += player_speed
        
        if keys [pygame.K_a]:
            self.velocity_x -= player_speed
            
        if keys [pygame.K_d]:
            self.velocity_x += player_speed
            
        if self.velocity_x !=0 and self.velocity_y !=0: 
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)
        
        if pygame.mouse.get_pressed() == (1,0,0) or keys[pygame.K_SPACE]:
            self.shoot=True
            self.is_shooting()
        else:
            self.shoot=False
        
    
    def is_shooting(self):
        if self.shoot_cooldown ==0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            spawn_bullet_pos= self.pos + self.gun_barrel_offset.rotate(self.angle)
            self.bullet=Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            bullet_group.add(self.bullet)
            all_sprites_group.add(self.bullet)
                
        
    
    def move(self):
        self.pos +=pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox_rect.center = self.pos
        self.rect.center =self.hitbox_rect.center 
        

    def enemy_collision(self):
        hits = pygame.sprite.spritecollide(self, enemy_group, False)
        for hit in hits:
            hit.kill()
            pygame.display.flip()           
                    
       
       
        
    def update(self):
        self.user_input()
        self.move() 
        self.player_rotation()
        #self.enemy_collision()
        
        
        if self.shoot_cooldown >0:
            self.shoot_cooldown -= 1
            
class enemy(pygame.sprite.Sprite):
    def __init__(self,position):
        super().__init__(enemy_group, all_sprites_group)
        self.image = pygame.image.load('slime_vU.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image,0,NECRO_SIZE)
        self.position=position
        
        self.hitbox_rect=self.image.get_rect()
        
        
        
        self.rect=self.image.get_rect()
        self.rect.center = position
        
        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.speed = enemy_speed
        
    def chase_player(self):
        player_vector = pygame.math.Vector2( man.hitbox_rect.center)
        enemy_vector = pygame.math.Vector2(self.rect.center)
        distance = self.get_vector_distance(player_vector, enemy_vector)
        
        if distance >20:
            self.direction = (player_vector - enemy_vector).normalize()
        else:
            self.direction = pygame.math.Vector2()
            self.kill()
        
        self.velocity = self.direction * self.speed
        self.position += self.velocity
        
        self.rect.centerx = self.position.x
        self.rect.centery = self.position.y
    
    def get_vector_distance(self, vector_1, vector_2):
        return (vector_1 - vector_2).magnitude()
    
    def bullet_enemy_collision(self):
        hits = pygame.sprite.spritecollide(self, bullet_group,False) # collision detection for enemy groups and bullet groups
        for hit in hits:
            hit.kill()
            self.kill()
           
            pygame.display.flip()
  
    def player_collision(self):
        hits = pygame.sprite.spritecollide(self, player_group, False)
        for hit in hits:
            print("Player")
            self.kill()
            hit.kill()
            pygame.quit()
        
    def update(self):
        self.chase_player()
        self.bullet_enemy_collision()
        self.player_collision()
        
        
        
    
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,angle):
        super().__init__()
        self.image=pygame.image.load("bullet.png").convert_alpha()
        self.image= pygame.transform.rotozoom(self.image,0,bullet_size)
        
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)  
        self.x=x
        self.y=y
        self.angel=angle
        self.speed= bullet_speed
        self.x_vel= math.cos(self.angel * (2 * math.pi/360)) * self.speed
        self.y_vel= math.sin(self.angel * (2 * math.pi/360)) * self.speed  
        
        self.bullet_lifetime=BULLET_LIFETIME
        self.spawn_time=pygame.time.get_ticks()  
        
        
    def bullet_movement(self):
        self.x += self.x_vel 
        self.y += self.y_vel
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()
        
    def update(self):
        self.bullet_movement()                       



def drawGrid():
        blockSize = 35 
        for x in range(0, width, blockSize):
            for y in range(0, height, blockSize):
                rect = pygame.Rect(x, y, blockSize, blockSize)
                pygame.draw.rect(win,'white', rect, 1)
                        
                        
    
all_sprites_group=pygame.sprite.Group()
bullet_group=pygame.sprite.Group()
enemy_group=pygame.sprite.Group()
player_group=pygame.sprite.Group()
    
man=player()

#slime=enemy((320,90))

new_enemy = enemy((300,70))
            
new_enemy_1=enemy((70,300))

new_enemy_2=enemy((550,300))
new_enemy_3=enemy((300,550))




while True:
    
    keys=pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
        
        
    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time > spawn_time:
            new_enemy = enemy((300,70))
            enemy_group.add(new_enemy)
            
            new_enemy_1=enemy((70,300))
            enemy_group.add(new_enemy_1)
            
            new_enemy_2=enemy((550,300))
            enemy_group.add(new_enemy_2)
            
            new_enemy_3=enemy((300,550))
            enemy_group.add(new_enemy_3)
            last_spawn_time = current_time
            


        
    win.blit(bg,(5,5))
    #win.blit(text,(470,40))
        
    all_sprites_group.draw(win)
    all_sprites_group.update()
        
    pygame.draw.rect(win,'red',man.hitbox_rect,width=1)
    pygame.draw.rect(win,'green',man.rect,width=1)
              
    
    pygame.display.update()
    clock.tick(fps)
        
        
        
        