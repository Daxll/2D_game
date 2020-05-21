import pygame
import sys
import os

# import pygame_cffi

'''
Objects
'''
class Platform(pygame.sprite.Sprite):
# x location, y location, img width, img height, img file
    def __init__(self,xloc,yloc,imgw,imgh,img):
        ALPHA = (0, 0, 0)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images',img)).convert()
        self.image.convert_alpha()
        self.image.set_colorkey(ALPHA)
        self.rect = self.image.get_rect()
        self.rect.y = yloc
        self.rect.x = xloc

class Player(pygame.sprite.Sprite):
    # Spawn a player
    def __init__(self):
        ALPHA = (0,255,0)
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0  # move along X
        self.movey = 0  # move along Y
        self.frame = 0  # count frames
        self.health = 10
        self.images = []
        for i in range(1, 5):
            img = pygame.image.load(os.path.join('images', 'firzen' + str(i) + '.png')).convert()
            img.convert_alpha()  # optimise alpha
            img.set_colorkey(ALPHA)  # set alpha
            self.images.append(img)
            self.image = self.images[0]
            self.rect = self.image.get_rect()

    def control(self, x, y):

        # control player movement

        self.movex += x
        if self.rect.y == 500:
            self.movey += y
        else:
            self.movey = 0

    def update(self):

        # Update sprite position

        self.rect.x = self.rect.x + self.movex
        if self.rect.y == (500 - steps*3):
            self.rect.y = 500
        else:
            self.rect.y = self.rect.y + self.movey

        # moving left
        if self.movex < 0:
            self.frame += 1
            if self.frame > (3*ani-1):
                self.frame = 0
            self.image = self.images[self.frame // 3]

        # moving right
        if self.movex > 0:
            self.frame += 1
            if self.frame > (3*ani-1):
                self.frame = 0
            self.image = self.images[self.frame // 3]


        hit_list = pygame.sprite.spritecollide(self, enemy_list, False)
        for enemy in hit_list:
            self.health -= 1
            print(self.health)

class Enemy(pygame.sprite.Sprite):
    # Spawn a enemy
    def __init__(self, x, y, ename):
        ALPHA = (0,0,0)
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0  # move along X
        self.movey = 0  # move along Y
        self.frame = 0  # count frames
        self.images = []
        for i in range(1, 6):
            img = pygame.image.load(os.path.join('images', ename + str(i) + '.png')).convert()
            img.convert_alpha()  # optimise alpha
            img.set_colorkey(ALPHA)  # set alpha
            self.images.append(img)
            self.image = self.images[0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.counter = 0  # counter variable

    def move(self):
        '''
        enemy movement
        '''
        distance = 300
        speed = 2

        if self.counter >= 0 and self.counter <= distance:
            self.rect.x -= speed
            self.frame += 1
            if self.frame > (3 * ani - 1):
                self.frame = 0
            self.image = self.images[self.frame // 3]
        elif self.counter >= distance and self.counter <= distance*2:
            self.rect.x += speed
            self.frame += 1
            if self.frame > (3 * ani - 1):
                self.frame = 0
            self.image = self.images[self.frame // 3]
        else:
            self.counter = 0

        self.counter += 1

class Level():
    def bad(lvl, eloc, ename):
        if lvl == 1:
            enemy = Enemy(eloc[0],eloc[1],ename) # spawn enemy
            enemy_list = pygame.sprite.Group() # create enemy group
            enemy_list.add(enemy)              # add enemy to group
        if lvl == 2:
            print("Level " + str(lvl) )

        return enemy_list

    # def ground(lvl, x, y, w, h):
    #     ground_list = pygame.sprite.Group()
    #     if lvl == 1:
    #         ground = Platform(x, y, w, h, 'block-ground.png')
    #         ground_list.add(ground)
    #
    #     if lvl == 2:
    #         print("Level " + str(lvl))
    #
    #     return ground_list

    def platform(lvl):
        plat_list = pygame.sprite.Group()
        if lvl == 1:
            plat = Platform(200, worldy - 97 - 128, 285, 67, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(500, worldy - 97 - 320, 197, 54, 'plat1.png')
            plat_list.add(plat)
        if lvl == 2:
            print("Level " + str(lvl))

        return plat_list
'''
Setup
'''
worldx = 1080
worldy = 600

world = pygame.display.set_mode([worldx, worldy])
backdrop = pygame.image.load(os.path.join('images', 'stage.png')).convert()
backdropbox = world.get_rect()

player = Player()  # spawn player
player.rect.x = 0  # go to x
player.rect.y = 500  # go to y
player_list = pygame.sprite.Group()
player_list.add(player)
steps = 6  # how many pixels to move

# enemy   = Enemy(900,500,'john') # spawn enemy
# enemy_list = pygame.sprite.Group()   # create enemy group
# enemy_list.add(enemy)                # add enemy to group

enemy_list = Level.bad(1, [900,500], 'john')
# ground_list = Level.ground( 1,0,worldy-97,1080,97 )
plat_list   = Level.platform( 1 )

BLUE = (25, 25, 200)
BLACK = (23, 23, 23)
WHITE = (254, 254, 254)


fps = 30 # frame rate
ani = 4  # animation cycles
clock = pygame.time.Clock()
pygame.init()

main = True

'''
Main Loop
'''

while main:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit()
            main = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player.control(-steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(steps, 0)
            if event.key == pygame.K_UP or event.key == ord('w'):
                player.control(0, -steps*3)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player.control(steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(-steps, 0)
            if event.key == ord('q'):
                pygame.quit()
                sys.exit()
                main = False

    world.blit(backdrop, backdropbox)
    player.update()  # update player position
    player_list.draw(world)  # draw player
    enemy_list.draw(world)  # refresh enemies
    for e in enemy_list:
        e.move()
    # ground_list.draw(world)  # refresh ground
    plat_list.draw(world)  # refresh platforms
    pygame.display.flip()
    clock.tick(fps)
