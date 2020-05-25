import pygame
import sys
import os
import pygame.freetype

# import pygame_cffi

'''
Objects
'''


class Platform(pygame.sprite.Sprite):
    # x location, y location, img width, img height, img file
    def __init__(self, xloc, yloc, imgw, imgh, img):
        ALPHA = (0, 0, 0)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images', img)).convert()
        self.image.convert_alpha()
        self.image.set_colorkey(ALPHA)
        self.rect = self.image.get_rect()
        self.rect.y = yloc
        self.rect.x = xloc


class Player(pygame.sprite.Sprite):
    # Spawn a player
    def __init__(self):
        ALPHA = (0, 255, 0)
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0  # move along X
        self.movey = 0  # move along Y
        self.frame = 0  # count frames
        self.collide_delta = 0
        self.jump_delta = 6
        self.health = 10
        self.score = 0
        self.damage = 0
        self.images = []
        for i in range(1, 9):
            img = pygame.image.load(os.path.join('images', 'firzen' + str(i) + '.png')).convert()
            img.convert_alpha()  # optimise alpha
            img.set_colorkey(ALPHA)  # set alpha
            self.images.append(img)
            self.image = self.images[0]
            self.rect = self.image.get_rect()

    def jump(self, platform_list):
        self.jump_delta = 0

    def gravity(self):
        global grav
        if grav:
            self.movey += 2  # how fast player falls
        if self.rect.y > worldy and self.movey >= 0:
            self.movey = 0
            self.rect.y = worldy - ty * 2

    def control(self, x, y):

        # control player movement

        self.movex += x
        self.movey += y

    def update(self):
        global grav
        global cooldown
        grav = 1

        # Update sprite position
        if cooldown == 0:
            self.rect.x = self.rect.x + self.movex

        else:
            self.rect.x -= steps
            cooldown -= 1

        self.rect.y = self.rect.y + self.movey

        # moving left
        if self.movex < 0:
            self.frame += 1
            if self.frame > (3 * ani - 1):
                self.frame = 0
            self.image = self.images[(self.frame // 3) + 4]

        # moving right
        if self.movex > 0:
            self.frame += 1
            if self.frame > (3 * ani - 1):
                self.frame = 0
            self.image = self.images[self.frame // 3]

        enemy_hit_list = pygame.sprite.spritecollide(self, enemy_list, False)
        # for enemy in hit_list:
        #     self.health -= 1
        #     if self.rect.x <= enemy.rect.x:
        #         cooldown = 20
        #     elif self.rect.x > enemy.rect.x:
        #         cooldown = 20
        if self.damage == 0:
            for enemy in enemy_hit_list:
                if not self.rect.contains(enemy):
                    self.damage = self.rect.colliderect(enemy)
                    cooldown = 20
        if self.damage == 1:
            idx = self.rect.collidelist(enemy_hit_list)
            if idx == -1:
                self.damage = 0  # set damage back to 0
                self.health -= 1  # subtract 1 hp

        loot_hit_list = pygame.sprite.spritecollide(self, loot_list, False)
        for loot in loot_hit_list:
            loot_list.remove(loot)
            self.score += 1
        print(self.score)

        ground_hit_list = pygame.sprite.spritecollide(self, ground_list, False)
        for g in ground_hit_list:
            self.movey = 0
            self.rect.y = worldy - ty * 2 - 25
            self.collide_delta = 0  # stop jumping
            grav = 0

        plat_hit_list = pygame.sprite.spritecollide(self, plat_list, False)
        for p in plat_hit_list:
            if self.rect.y > p.rect.y:
                self.rect.y = p.rect.y + ty + 20
                self.collide_delta = 0
                self.movey = 0
                grav = 1  # gravity on
            else:
                self.rect.y = p.rect.y - ty - 25
                self.collide_delta = 0  # stop jumping
                self.movey = 0
                grav = 0  # gravity off

        # prevent exiting screen right side.
        if self.rect.x < 0:
            self.rect.x = 0
        # prevent exiting screen left side / end lvl condition will be added later.
        if self.rect.x >= 1030:
            self.rect.x = 1030
        # print(self.rect.x)

        # jump mechanic
        if self.collide_delta < 6 and self.jump_delta < 6:
            # self.jump_delta = 6*2
            self.movey -= 33  # how high to jump
            self.collide_delta += 6
            self.jump_delta += 6
            grav = 1


class Enemy(pygame.sprite.Sprite):
    # Spawn a enemy
    def __init__(self, x, y, ename):
        ALPHA = (0, 0, 0)
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0  # move along X
        self.movey = 0  # move along Y
        self.frame = 0  # count frames
        self.images = []
        for i in range(1, 11):
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
        speed = 1

        if self.counter >= 0 and self.counter <= distance:
            self.rect.x -= speed
            self.frame += 1
            if self.frame > (3 * ani - 1):
                self.frame = 0
            self.image = self.images[self.frame // 3]
        elif self.counter >= distance and self.counter <= distance * 2:
            self.rect.x += speed
            self.frame += 1
            if self.frame > (3 * ani - 1):
                self.frame = 0
            self.image = self.images[(self.frame // 3) + 5]
        else:
            self.counter = 0

        self.counter += 1
    # def gravity(self):
    #     self.movey += 2 # how fast player falls
    #     if self.rect.y > worldy and self.movey >= 0:
    #         self.movey = 0
    #         self.rect.y = worldy-ty*2


class Level():
    def bad(lvl, eloc, ename):
        if lvl == 1:
            enemy = Enemy(eloc[0], eloc[1], ename)  # spawn enemy
            enemy_list = pygame.sprite.Group()  # create enemy group
            enemy_list.add(enemy)  # add enemy to group
        if lvl == 2:
            enemy = Enemy(eloc[0], eloc[1], ename)  # spawn enemy
            enemy_list = pygame.sprite.Group()  # create enemy group
            enemy_list.add(enemy)  # add enemy to group

        return enemy_list

    def ground(lvl, x, y, w, h):
        ground_list = pygame.sprite.Group()
        # if lvl == 1:
        ground = Platform(x, y, w, h, 'ground.png')
        ground_list.add(ground)

        # if lvl == 2:
        #     print("Level " + str(lvl))

        return ground_list

    def platform(lvl, first_plat_loc):
        plat_list = pygame.sprite.Group()
        if lvl == 1:
            plat = Platform(first_plat_loc, worldy - 100 - 128, 285, 67, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(500, worldy - 100 - 320, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(800, worldy - 100 - 200, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1100, worldy - 100 - 128, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1400, worldy - 100 - 128, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1700, worldy - 100 - 200, 197, 54, 'plat1.png')
            plat_list.add(plat)
        if lvl == 2:
            plat = Platform(first_plat_loc, worldy - 100 - 128, 285, 67, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(500, worldy - 100 - 128, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(800, worldy - 100 - 200, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1100, worldy - 100 - 320, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1400, worldy - 100 - 200, 197, 54, 'plat1.png')
            plat_list.add(plat)


        return plat_list

    def loot(lvl):
        if lvl == 1:
            loot_list = pygame.sprite.Group()
            loot = Platform(280, worldy - 300, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(600, worldy - 480, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(850, worldy - 400, tx, ty, 'gogo.png')
            loot_list.add(loot)
            loot = Platform(1300, worldy - 100, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(1800, worldy - 100, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(1850, worldy - 360, tx, ty, 'gogo.png')
            loot_list.add(loot)
        if lvl == 2:
            loot_list = pygame.sprite.Group()
            loot = Platform(280, worldy - 300, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(600, worldy - 480, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(850, worldy - 400, tx, ty, 'gogo.png')
            loot_list.add(loot)
            loot = Platform(1300, worldy - 100, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(950, worldy - 100, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(1300, worldy - 360, tx, ty, 'gogo.png')
            loot_list.add(loot)

        return loot_list


def stats(score, health, lvl):
    myfont.render_to(world, (4, 4), "Score:" + str(score), WHITE, None, size=64)
    myfont.render_to(world, (4, 72), "Health:" + str(health), WHITE, None, size=64)
    myfont.render_to(world, (4, 140), "level:" + str(lvl), WHITE, None, size=64)

def setup_lvl(lvl_num):
    backdrop = pygame.image.load(os.path.join('images', 'stage' + str(lvl_num) + '.png')).convert()
    player.rect.x = 0  # go to x
    player.rect.y = 200
    enemy_list = Level.bad(lvl_num, [900, 480], 'john')
    plat_list = Level.platform(lvl_num, first_plat_x)
    loot_list = Level.loot(lvl_num)
    return backdrop,enemy_list,plat_list,loot_list

'''
Setup
'''
worldx = 1080
worldy = 600
tx = 50
ty = 50
world = pygame.display.set_mode([worldx, worldy])
backdrop = pygame.image.load(os.path.join('images', 'stage1.png')).convert()
backdropbox = world.get_rect()

player = Player()  # spawn player
player.rect.x = 0  # go to x
player.rect.y = 200  # go to y
player_list = pygame.sprite.Group()
player_list.add(player)
steps = 5  # how many pixels to move
# jump = -24
grav = 1
forwardx = 800
backwardx = 230
first_plat_x = 200
scroll_token = 0
end_token = 1
cooldown = 0
lvl = 1
lvl_start = 0

enemy_list = Level.bad(1, [900, 480], 'john')
ground_list = Level.ground(1, 0, worldy - ty, 1080, 100)
plat_list = Level.platform(1, first_plat_x)
loot_list = Level.loot(1)

BLUE = (25, 25, 200)
BLACK = (23, 23, 23)
WHITE = (254, 254, 254)

fps = 40  # frame rate
ani = 4  # animation cycles
clock = pygame.time.Clock()
pygame.init()

font_path = os.path.join('fonts', 'PixelOperator.ttf')
font_size = tx
myfont = pygame.freetype.Font(font_path, font_size)

main = True

'''
Main Loop
'''
if __name__ == "__main__":
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
                    player.jump(plat_list)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    player.control(steps, 0)
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    player.control(-steps, 0)

                if event.key == ord('q'):
                    pygame.quit()
                    sys.exit()
                    main = False

        # scroll the world forward
        if player.rect.x >= forwardx and end_token:
            i = 0
            scroll_token = 1
            scroll = player.rect.x - forwardx
            player.rect.x = forwardx
            for p in plat_list:
                i += 1
                if p.rect.x <= -700 and i == 1:
                    end_token = 0
                else:
                    p.rect.x -= scroll
            for e in enemy_list:
                e.rect.x -= scroll
            for l in loot_list:
                l.rect.x -= scroll

        # scroll the world backward
        if player.rect.x <= backwardx and scroll_token:
            j = 0
            scroll = backwardx - player.rect.x
            player.rect.x = backwardx

            for p in plat_list:
                j += 1
                if p.rect.x >= first_plat_x and j == 1:
                    scroll_token = 0
                else:
                    p.rect.x += scroll
                    end_token = 1
            for e in enemy_list:
                e.rect.x += scroll
            for l in loot_list:
                l.rect.x += scroll


        world.blit(backdrop, backdropbox)
        loot_list.draw(world)
        player.gravity()  # check gravity
        player.update()  # update player position
        player_list.draw(world)  # draw player
        enemy_list.draw(world)  # refresh enemies
        for e in enemy_list:
            e.move()

        # ground_list.draw(world)  # refresh ground
        plat_list.draw(world)  # refresh platforms
        stats(player.score, player.health, lvl)  # draw text

        if player.score == 6:
            lvl +=1
            player.score = 0
            backdrop,enemy_list,plat_list,loot_list = setup_lvl(lvl)
            if lvl == 6:
                lvl = 1
                player.score = 0
                backdrop,enemy_list,plat_list,loot_list = setup_lvl(lvl)

        pygame.display.flip()
        clock.tick(fps)

