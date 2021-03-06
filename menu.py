'''
LEVY JUMPER 2D side scrolling game
Created by Gilai Levy
2020
'''

import pygame
import sys
import os
import pygame.freetype
from High_Score_Module import highscore, show_top10

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


class button(pygame.sprite.Sprite):

    def __init__(self, xloc, yloc, img):
        # ALPHA = (0, 0, 0)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images', img)).convert_alpha()
        # self.image.convert_alpha()
        # self.image.set_colorkey(ALPHA)
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
        self.fire_frame = 0
        self.collide_delta = 0
        self.jump_delta = 6
        self.health = 3
        self.score = 0
        self.damage = 0
        self.shot = 0
        self.images = []
        for i in range(1, 15):
            img = pygame.image.load(os.path.join('images', 'firzen' + str(i) + '.png')).convert()
            img.convert_alpha()  # optimise alpha
            img.set_colorkey(ALPHA)  # set alpha
            self.images.append(img)
            self.image = self.images[0]
            self.rect = self.image.get_rect()

    def jump(self, platform_list):
        self.jump_delta = 0

    def fire(self):
        self.shot = 1
        self.fire_frame = 11

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
        global direction
        # Update sprite position
        if cooldown == 0:
            self.rect.x = self.rect.x + self.movex
        elif direction == 'left':
            self.rect.x -= steps
            cooldown -= 1
        elif direction == 'right':
            self.rect.x += steps
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
        if self.damage == 0:
            for enemy in enemy_hit_list:
                if not self.rect.contains(enemy):
                    self.damage = self.rect.colliderect(enemy)
                    cooldown = 20
                    hit_sound.play()
                    if self.rect.x <= enemy.rect.x:
                        direction = 'left'
                    else:
                        direction = 'right'
        if self.damage == 1:
            idx = self.rect.collidelist(enemy_hit_list)
            if idx == -1:
                self.damage = 0  # set damage back to 0
                self.health -= 1  # subtract 1 hp

        loot_hit_list = pygame.sprite.spritecollide(self, loot_list, False)
        for loot in loot_hit_list:
            loot_list.remove(loot)
            coin_sound.play()
            self.score += 1

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

        # jump mechanic
        if self.collide_delta < 6 and self.jump_delta < 6:
            self.movey -= 33  # how high to jump
            jump_sound.play()
            self.collide_delta += 6
            self.jump_delta += 6
            grav = 1

        # shooting fireball mechanics
        for f in fireball_list:
            plat_fire_list = pygame.sprite.spritecollide(f, plat_list, False)
            for pf in plat_fire_list:
                fireball_list.remove(f)
            bad_fire_list = pygame.sprite.spritecollide(f, enemy_list, False)
            for bf in bad_fire_list:
                fire_hit.play()
                fireball_list.remove(f)
                enemy_list.remove(bf)
                self.score += 1
            distance = 50
            global shot_speed
            if self.shot == 1:
                if self.image in self.images[0:4]:
                    f.image = f.images[0]
                    shot_speed = 8
                    self.shot = 0
                else:
                    f.image = f.images[1]
                    shot_speed = -8
                    self.shot = 0
            f.rect.x += shot_speed
            f.counter += 1
            if f.counter == distance:
                self.shot = 0
                f.counter = 0
                shot_speed = 0
                fireball_list.remove(f)

        if self.fire_frame > 0:
            if shot_speed >= 0:
                self.image = self.images[self.fire_frame // 4 + 8]
                self.fire_frame -= 1
                if self.fire_frame == 0:
                    self.image = self.images[0]
            else:
                self.image = self.images[self.fire_frame // 4 + 11]
                self.fire_frame -= 1
                if self.fire_frame == 0:
                    self.image = self.images[4]


class Fireball(pygame.sprite.Sprite):
    # x location, y location
    def __init__(self, xloc, yloc):
        ALPHA = (0, 0, 0)
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for i in range(1, 3):
            img = pygame.image.load(os.path.join('images', 'fireball' + str(i) + '.png')).convert()
            img.convert_alpha()  # optimise alpha
            img.set_colorkey(ALPHA)  # set alpha
            self.images.append(img)
            self.image = self.images[0]
            self.rect = self.image.get_rect()
            self.rect.x = xloc
            self.rect.y = yloc + 15
            self.counter = 0  # counter variable


class Enemy(pygame.sprite.Sprite):
    # Spawn a enemy
    def __init__(self, x, y, ename):
        ALPHA = (0, 0, 0)
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0  # move along X
        self.movey = 0  # move along Y
        self.frame = 0  # count frames
        self.hit_frame = 0
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
            if self.frame > (3 * 5 - 1):
                self.frame = 0
            self.image = self.images[self.frame // 3]
        elif self.counter >= distance and self.counter <= distance * 2:
            self.rect.x += speed
            self.frame += 1
            if self.frame > (3 * 5 - 1):
                self.frame = 0
            self.image = self.images[(self.frame // 3) + 5]
        else:
            self.counter = 0

        self.counter += 1


class Level():
    def bad(lvl, eloc, ename):
        if lvl == 1:
            enemy = Enemy(eloc[0], eloc[1], ename)  # spawn enemy
            enemy_list = pygame.sprite.Group()  # create enemy group
            enemy_list.add(enemy)  # add enemy to group
        if lvl == 2:
            enemy_list = pygame.sprite.Group()  # create enemy group
            enemy = Enemy(eloc[0], eloc[1], ename)  # spawn enemy
            enemy_list.add(enemy)  # add enemy to group
            enemy = Enemy(eloc[0] - 400, eloc[1], ename)  # spawn enemy
            enemy_list.add(enemy)  # add enemy to group
        if lvl == 3:
            enemy_list = pygame.sprite.Group()  # create enemy group
            enemy = Enemy(eloc[0], eloc[1], ename)  # spawn enemy
            enemy_list.add(enemy)  # add enemy to group
            enemy = Enemy(eloc[0] + 250, eloc[1], ename)  # spawn enemy
            enemy_list.add(enemy)  # add enemy to group
        if lvl == 4:
            enemy_list = pygame.sprite.Group()  # create enemy group
            enemy = Enemy(eloc[0], eloc[1], ename)  # spawn enemy
            enemy_list.add(enemy)  # add enemy to group
            enemy = Enemy(eloc[0] + 250, eloc[1], ename)  # spawn enemy
            enemy_list.add(enemy)  # add enemy to group
            enemy = Enemy(eloc[0] - 250, eloc[1], ename)  # spawn enemy
            enemy_list.add(enemy)  # add enemy to group
        if lvl == 5:
            enemy_list = pygame.sprite.Group()  # create enemy group
            enemy = Enemy(eloc[0], eloc[1], ename)  # spawn enemy
            enemy_list.add(enemy)  # add enemy to group
            enemy = Enemy(500, 225, ename)  # spawn enemy
            enemy_list.add(enemy)  # add enemy to group
        if lvl == 6:
            enemy_list = pygame.sprite.Group()  # create enemy group
            enemy = Enemy(eloc[0], eloc[1], ename)  # spawn enemy
            enemy_list.add(enemy)  # add enemy to group
            enemy = Enemy(1500, eloc[1], ename)  # spawn enemy
            enemy_list.add(enemy)  # add enemy to group
            enemy = Enemy(1200, eloc[1], ename)  # spawn enemy
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
        if lvl == 3:
            plat = Platform(first_plat_loc, worldy - 100 - 128, 285, 67, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(300, worldy - 100 - 200, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(500, worldy - 100 - 128, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(800, worldy - 100 - 320, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1000, worldy - 100 - 200, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1300, worldy - 100 - 128, 197, 54, 'plat1.png')
            plat_list.add(plat)
        if lvl == 4:
            plat = Platform(first_plat_loc, worldy - 100 - 200, 285, 67, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(500, worldy - 100 - 320, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(800, worldy - 100 - 400, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1100, worldy - 100 - 200, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1400, worldy - 100 - 300, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1100, worldy - 100 - 450, 197, 54, 'plat1.png')
            plat_list.add(plat)
        if lvl == 5:
            plat = Platform(first_plat_loc, worldy - 100 - 128, 285, 67, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(300, worldy - 100 - 200, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(200, worldy - 100 - 350, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(550, worldy - 100 - 350, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(750, worldy - 100 - 128, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1100, worldy - 100 - 220, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1400, worldy - 100 - 350, 197, 54, 'plat1.png')
            plat_list.add(plat)
        if lvl == 6:
            plat = Platform(first_plat_loc, worldy - 100 - 300, 285, 67, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(300, worldy - 100 - 150, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(500, worldy - 100 - 220, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(700, worldy - 100 - 300, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(900, worldy - 100 - 400, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1100, worldy - 100 - 320, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1400, worldy - 100 - 200, 197, 54, 'plat1.png')
            plat_list.add(plat)
            plat = Platform(1000, worldy - 100 - 128, 197, 54, 'plat1.png')
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
        if lvl == 3:
            loot_list = pygame.sprite.Group()
            loot = Platform(330, worldy - 400, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(600, worldy - 480, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(870, worldy - 500, tx, ty, 'gogo.png')
            loot_list.add(loot)
            loot = Platform(1300, worldy - 100, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(950, worldy - 100, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(1100, worldy - 450, tx, ty, 'gogo.png')
            loot_list.add(loot)
        if lvl == 4:
            loot_list = pygame.sprite.Group()
            loot = Platform(280, worldy - 400, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(600, worldy - 480, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(850, worldy - 400, tx, ty, 'gogo.png')
            loot_list.add(loot)
            loot = Platform(1500, worldy - 100, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(950, worldy - 100, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(1250, worldy - 360, tx, ty, 'gogo.png')
            loot_list.add(loot)
        if lvl == 5:
            loot_list = pygame.sprite.Group()
            loot = Platform(280, 80, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(600, 80, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(850, worldy - 400, tx, ty, 'gogo.png')
            loot_list.add(loot)
            loot = Platform(1500, 50, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(850, worldy - 300, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(1200, worldy - 400, tx, ty, 'gogo.png')
            loot_list.add(loot)
        if lvl == 6:
            loot_list = pygame.sprite.Group()
            loot = Platform(330, worldy - 320, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(600, worldy - 480, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(950, worldy - 570, tx, ty, 'gogo.png')
            loot_list.add(loot)
            loot = Platform(1300, worldy - 100, tx, ty, 'yuval.png')
            loot_list.add(loot)
            loot = Platform(1050, worldy - 300, tx, ty, 'inbal.png')
            loot_list.add(loot)
            loot = Platform(1500, worldy - 360, tx, ty, 'gogo.png')
            loot_list.add(loot)
        return loot_list


def stats(score, health, lvl):
    myfont.render_to(world, (600, 4), "Score:" + str(score), WHITE, None, size=44)
    myfont.render_to(world, (4, 4), "Health:" + str(health), WHITE, None, size=44)
    myfont.render_to(world, (300, 4), "level:" + str(lvl), WHITE, None, size=44)


def lvl_cutscene(lvl):
    backdropbox = world.get_rect()
    backdrop = pygame.image.load(os.path.join('images', 'stage' + str(lvl) + '.png')).convert()
    world.blit(backdrop, backdropbox)
    myfont.render_to(world, (200, 200), "level:" + str(lvl), WHITE, None, size=200)
    pygame.display.update()
    clock.tick(fps)
    pygame.time.wait(2000)
    return


def setup_lvl(lvl_num, first_plat):
    backdrop = pygame.image.load(os.path.join('images', 'stage' + str(lvl_num) + '.png')).convert()
    player.rect.x = 0  # go to x
    player.rect.y = 0
    enemy_list = Level.bad(lvl_num, [900, 480], 'john')
    plat_list = Level.platform(lvl_num, first_plat)
    loot_list = Level.loot(lvl_num)
    return backdrop, enemy_list, plat_list, loot_list


def main_menu():
    global click
    backdropbox = world.get_rect()
    backdrop = pygame.image.load(os.path.join('images', 'levy jumper.png')).convert()

    button_list = pygame.sprite.Group()
    button1_mouseover = pygame.image.load(os.path.join('images', 'new game hover.png')).convert_alpha()
    button1_mouseclick = pygame.image.load(os.path.join('images', 'new game click.png')).convert_alpha()
    button1 = button(200, 200, 'new game 1.png')
    button_list.add(button1)
    button2_mouseover = pygame.image.load(os.path.join('images', 'settings hover.png')).convert_alpha()
    button2_mouseclick = pygame.image.load(os.path.join('images', 'settings click.png')).convert_alpha()
    button2 = button(200, 350, 'settings normal.png')
    button_list.add(button2)
    button3_mouseover = pygame.image.load(os.path.join('images', 'continue hover.png')).convert_alpha()
    button3_mouseclick = pygame.image.load(os.path.join('images', 'continue click.png')).convert_alpha()
    button3_blocked = pygame.image.load(os.path.join('images', 'continue locked.png')).convert_alpha()
    button3 = button(600, 200, 'continue normal.png')
    button_list.add(button3)
    button4_mouseover = pygame.image.load(os.path.join('images', 'high scores hover.png')).convert_alpha()
    button4_mouseclick = pygame.image.load(os.path.join('images', 'high scores click.png')).convert_alpha()
    button4 = button(600, 350, 'high scores normal.png')
    button_list.add(button4)

    global cont

    while True:
        world.blit(backdrop, backdropbox)
        button_list.draw(world)
        b = 0
        if not cont:
            world.blit(button3_blocked, (600, 200))

        for r in button_list:
            b += 1
            if r.rect.collidepoint(pygame.mouse.get_pos()) and b == 1:
                world.blit(button1_mouseover, (200, 200))
                if click:
                    world.blit(button1_mouseclick, (200, 200))
                    cont = 0
                    game()
            if r.rect.collidepoint(pygame.mouse.get_pos()) and b == 2:
                world.blit(button2_mouseover, (200, 350))
                if click:
                    world.blit(button2_mouseclick, (200, 350))
                    settings(world)
            if r.rect.collidepoint(pygame.mouse.get_pos()) and b == 3 and cont:
                world.blit(button3_mouseover, (600, 200))
                if click:
                    world.blit(button3_mouseclick, (600, 200))
                    game()
            if r.rect.collidepoint(pygame.mouse.get_pos()) and b == 4:
                world.blit(button4_mouseover, (600, 350))
                if click:
                    world.blit(button4_mouseclick, (600, 350))
                    show_top10(world, 'score_file.txt')

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        clock.tick(fps)


def game():
    main = True

    global steps
    global grav
    global forwardx
    global backwardx
    global first_plat_x
    global scroll_token
    global end_token
    global cooldown
    global lvl
    global direction
    global cont
    global enemy_list
    global ground_list
    global plat_list
    global loot_list
    global player
    global player_list
    global fireball_list

    backdropbox = world.get_rect()

    if not cont:
        player = Player()  # spawn player
        player.rect.x = 0  # go to x
        player.rect.y = 0  # go to y
        player_list = pygame.sprite.Group()
        player_list.add(player)
        grav = 1
        scroll_token = 0
        end_token = 1
        cooldown = 0
        lvl = 1
        direction = 'left'
        enemy_list = Level.bad(1, [900, 480], 'john')
        ground_list = Level.ground(1, 0, worldy - ty, 1080, 100)
        plat_list = Level.platform(1, first_plat_x)
        loot_list = Level.loot(1)

    backdrop = pygame.image.load(os.path.join('images', 'stage' + str(lvl) + '.png')).convert()

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
                if event.key == pygame.K_SPACE:
                    if not fireball_list:
                        fireball = Fireball(player.rect.x, player.rect.y)
                        fireball_list.add(fireball)
                        fire.play()
                        player.fire()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    player.control(steps, 0)
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    player.control(-steps, 0)

                if event.key == pygame.K_ESCAPE:
                    cont = 1
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
        fireball_list.draw(world)
        plat_list.draw(world)  # refresh platforms
        stats(player.score, player.health, lvl)  # draw text

        if not loot_list:
            if lvl == 6:
                lvl = 0
            lvl += 1
            lvl_cutscene(lvl)
            scroll_token = 0
            end_token = 1
            backdrop, enemy_list, plat_list, loot_list = setup_lvl(lvl, first_plat_x)

        if player.health == 0:
            highscore(world, 'score_file.txt', player.score)
            cont = 0
            main = False

        pygame.display.flip()
        clock.tick(fps)


def settings(world):
    global music
    global effects
    running = True
    backdropbox = world.get_rect()
    backdrop = pygame.image.load(os.path.join('images', 'settings background.png')).convert()

    sound_button_list = pygame.sprite.Group()
    music_button_off = pygame.image.load(os.path.join('images', 'off.png')).convert_alpha()
    music_button_on = button(600, 160, 'on.png')
    sound_button_list.add(music_button_on)
    effects_button_off = pygame.image.load(os.path.join('images', 'off.png')).convert_alpha()
    effects_button_on = button(600, 230, 'on.png')
    sound_button_list.add(effects_button_on)

    while running:
        world.blit(backdrop, backdropbox)
        sound_button_list.draw(world)
        b = 0
        if not music:
            world.blit(music_button_off, (600, 160))

        if not effects:
            world.blit(effects_button_off, (600, 230))

        for l in sound_button_list:
            b += 1
            if l.rect.collidepoint(pygame.mouse.get_pos()) and b == 1:
                if click and music:
                    pygame.mixer.music.set_volume(0)
                    music = 0
                elif click and not music:
                    pygame.mixer.music.set_volume(0.1)
                    music = 1
            if l.rect.collidepoint(pygame.mouse.get_pos()) and b == 2:
                if click and effects:
                    hit_sound.set_volume(0)
                    coin_sound.set_volume(0)
                    jump_sound.set_volume(0)
                    fire_hit.set_volume(0)
                    fire.set_volume(0)
                    effects = 0
                elif click and not effects:
                    hit_sound.set_volume(0.3)
                    coin_sound.set_volume(0.1)
                    jump_sound.set_volume(0.1)
                    fire_hit.set_volume(0.3)
                    fire.set_volume(0.3)
                    effects = 1

        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        clock.tick(fps)


'''
Setup
'''

click = False

worldx = 1080
worldy = 600
tx = 50
ty = 50

world = pygame.display.set_mode([worldx, worldy])

player = Player()  # spawn player
player.rect.x = 0  # go to x
player.rect.y = 0  # go to y
player_list = pygame.sprite.Group()
player_list.add(player)
steps = 5  # how many pixels to move
grav = 1
forwardx = 800
backwardx = 230
first_plat_x = 200
scroll_token = 0
end_token = 1
cooldown = 0
lvl = 1
direction = 'left'
cont = 0
shot_speed = 0

enemy_list = Level.bad(1, [900, 480], 'john')
ground_list = Level.ground(1, 0, worldy - ty, 1080, 100)
plat_list = Level.platform(1, first_plat_x)
loot_list = Level.loot(1)
fireball_list = pygame.sprite.Group()
BLUE = (25, 25, 200)
BLACK = (23, 23, 23)
WHITE = (254, 254, 254)

fps = 40  # frame rate
ani = 4  # animation cycles
clock = pygame.time.Clock()
pygame.init()

# getting font for the score
font_path = os.path.join('fonts', 'anomalia-regular.otf')
font_size = tx
myfont = pygame.freetype.Font(font_path, font_size)

# importing music and sounds
pygame.mixer.music.load(os.path.join('sound', 'Theme.mp3'))
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)
hit_sound = pygame.mixer.Sound(os.path.join('sound', 'attack.wav'))
hit_sound.set_volume(0.3)
coin_sound = pygame.mixer.Sound(os.path.join('sound', 'coin.wav'))
coin_sound.set_volume(0.1)
jump_sound = pygame.mixer.Sound(os.path.join('sound', 'jump.wav'))
jump_sound.set_volume(0.1)
fire_hit = pygame.mixer.Sound(os.path.join('sound', 'fire hit.wav'))
fire_hit.set_volume(0.3)
fire = pygame.mixer.Sound(os.path.join('sound', 'Fire.aif'))
fire.set_volume(0.3)

music = 1
effects = 1
'''
Main Loop
'''
if __name__ == "__main__":
    main_menu()
