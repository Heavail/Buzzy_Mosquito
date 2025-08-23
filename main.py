import pygame as pm
from pygame.locals import *
import os
import random
import time
import asyncio
pm.init()
screen_info = pm.display.Info()
height = screen_info.current_h
width = screen_info.current_w

screen = pm.display.set_mode((width,height- 50))

class assets:
    def __init__(self,frame_folder,pos,size):
        self.frame_folder = frame_folder
        self._pos = pos
        self._size = size
        self.for_once = True
        self.frame_count = 0
        self.rate_count = 0
        self.frame = {}
        self.frames = os.listdir(self.frame_folder)
        for count,frame in enumerate(self.frames):
            self.frame[f'{count}'] = pm.image.load(f'{self.frame_folder}\\{frame}').convert_alpha()
        print(self.frame)

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self,value):
        if self._pos != value:
            self._pos = value
            # self.animate()
    @property
    def size(self):
        return self._size
    @size.setter
    def size(self,value):
        if self._size != value:
            self._size = value
            # self.animate()

    def animate(self,pos = None,size = None,rotate = 0,flipx = False,flipy = False,rate = None):
        if pos == None:
            pos = self.pos
        else:
            self.pos = pos
        if size == None:
            size = self.size
        else:
            self.size = size
        if self.frame_count == len(self.frames):
            self.frame_count = 0
        if self.rate_count == rate or self.for_once == True:
            self.rate_count = 0
            self.image = pm.transform.rotate(pm.transform.scale(self.frame[f'{self.frame_count}'],(size[0],size[1])),rotate)
            self.image = pm.transform.flip(self.image,flipx,flipy)
            self.frame_count += 1
            self.for_once = False
        screen.blit(self.image,(pos[0],pos[1]))
        if rate != None:
            self.rate_count += 1

class multiple_asset:
    def __init__(self):
        self.ys = []
    def repeatperscreen(self,screenwidth,asset,frame_folder,size,pos,count,y_list = None,biasx = 5,biasy = 0,randomyrange = (0,0),moveby = 0,rotate = 0,rate = None,score = None):
        # print(asset)
        gap = screenwidth/(count - 1)
        # if len(asset) > count:
        #     asset.pop(0)
        
        
        # print(score)
        while len(asset) < count:
            if y_list == None:
                asset.append(assets(frame_folder,[pos[0] + len(asset) * gap,random.randint(randomyrange[0],randomyrange[1])],size))
            else:
                asset.append(assets(frame_folder,[pos[0] + len(asset) * gap,y_list[len(asset)] + biasy],size))
            self.ys.append(asset[-1].pos[1])
        self.a = asset
        for object in asset:
            object.pos = [object.pos[0] + moveby,object.pos[1]]
            if object.pos[0] + object.size[0] < 0:
                if score != None:
                    score += 1
                if y_list == None:
                    object.pos = [gap * count - (object.size[0] + biasx),random.randint(randomyrange[0],randomyrange[1])]
                else:
                    object.pos = [gap * count - (object.size[0] + biasx),y_list[-1] + biasy]
                self.ys.pop(0)
                self.ys.append(object.pos[1])
                pos = [pos[0] + gap,pos[1]]
            object.animate(rotate = rotate,rate = rate)
        if score != None:
            return asset,score
        else:
            return asset,self.ys
    def collision(self,object,x_bias = 0,width_bias = 0,y_bias = 0,height_bias = 0):
        collision = False
        for asset in self.a:
            if object.pos[0] + object.size[0] + width_bias > asset.pos[0] and asset.pos[0] + asset.size[0] > object.pos[0] + x_bias and object.pos[1] + object.size[1] + height_bias > asset.pos[1] and asset.pos[1] + asset.size[1] > object.pos[1] + y_bias:
                collision = True
                break
        return collision
async def main():
    back_pos = [0,0]
    for_once = True
    backgrounds = []
    pipe_pos1 = [2 * width,0]
    pipes1 = []
    pipe_pos2 = [2 * width,0]
    pipes2 = []
    clock = pm.time.Clock()
    pipe_gap = 250
    backs = multiple_asset()
    pipes_1 = multiple_asset()
    pipes_2 = multiple_asset()
    player = assets('mosquito',[100,500],[200,200])
    Font = pm.font.SysFont("Kristen ITC",30)
    game_over = False
    over_width,over_height = (700,125)
    gameover = pm.transform.scale(Font.render("YOU GOT ELECTROCUTED",True,(255,255,0)),(over_width,over_height))
    taptoplay = pm.transform.scale(Font.render("Tap to restart",True,(122,122,122)),(over_width/3,over_height/3))
    Loading = pm.transform.scale(Font.render("Loading....",True,(255,255,255)),(over_width/2,over_height/2))
    background_velocity = -1
    pipes_velocity = -10
    player_rate = 2
    collided1,collided2 = False,False
    score = 0
    high_score = int(open('highscore.txt','r').read())
    acceleration = -0.009
    print(high_score)
    while True:
        for event in pm.event.get():
            if event.type == pm.QUIT:
                pm.quit()
            if game_over and event.type == MOUSEBUTTONDOWN:
                screen.blit(Loading,((width/2 - Loading.get_width()/2,height/2 + Loading.get_height()/2)))
                pm.display.update()
                await main()
        screen.fill((0,0,0))
        if not collided1 and not collided2:
            playery = pm.mouse.get_pos()[1]
            background_velocity += acceleration
            pipes_velocity += acceleration
        backgrounds,back_pos = backs.repeatperscreen(2 * width,backgrounds,'background',[width,height],back_pos,4,moveby= background_velocity,rate = None)
        player.animate(pos=[player.pos[0],playery],flipx = True,rate = player_rate)
        pipes1,pipe1y = pipes_1.repeatperscreen(width,pipes1,'obstacle',[100,height],pipe_pos1,4,randomyrange=(-int(height),-pipe_gap),moveby=pipes_velocity ,rotate=180)
        collided1 = pipes_1.collision(player,width_bias = -100,y_bias= 100,height_bias = -70,x_bias = 70)
        pipes2,score = pipes_2.repeatperscreen(width,pipes2,'obstacle',[100,height],pipe_pos2,4,moveby=pipes_velocity,y_list=pipe1y,biasy = height + pipe_gap,score = score)
        collided2 = pipes_2.collision(player,width_bias = -100,y_bias= 100,height_bias = -70,x_bias = 70)
        score_image = Font.render(f'SCORE = {score}',True,(255,0,0))
        High_score_image = Font.render(f'HIGHSCORE = {high_score}',True,(255,0,0))
        screen.blit(score_image,(0,0))
        screen.blit(High_score_image,(0,40))
        if score > high_score:
            open('highscore.txt','w').write(f'{score}')
        if collided1 == True or collided2 == True:
            background_velocity = 0
            pipes_velocity = 0
            player_rate = None
            game_over = True
            screen.blit(gameover,(width/2 - over_width/2,height/2.5 - over_height/2))
            screen.blit(taptoplay,(width/2 - taptoplay.get_width()/2,height/2 - taptoplay.get_height()/2))

        pm.display.update()
        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main())

''' just writing some damn shitty stuff to test whether my hackclub is working well or not may be 
    I will be writing this for about 1 to 2 minutes to check my summer of making in hackclub accound
    so let's just have a look after the given minutes if my summer of making is responding or not
    anyways what if it works am I sure it will be ok for the rest of the further times or will it 
    start bugging like it did before ?? whatever happens my simple goal is to keep learning and  in 
    the meanwhile whatever I will learn and whatever the project I will create for the next 30 days 
    I will keep uploading them on the github and summer of making including hackatime to record 
    my progress and actively participate in the event with this it says I am done with 7 minutes of work
    so let's see my hackatime and summer of making website whether they are working perfectly or not
    '''

""" let's start again for about a minute to track my coding time in the hackclub because this
    shitty thing falied again and let's have a look if it works this time or not anyways this timem 
    I won't be taking too long just about a minute or two and then I will be done with woaaa it suddenly says 
    4 minute how in the world is that possible like seriously it jumperd from 0 to 4 directly how 
    the hell this plugin or api whatever we can say actually works ?? I know for sure it's may
    be not recobnizing that I am commenting rather than coding to track my coding time anyways I guess 
    even if the wakatime is wrong I would have still passed the time of about more than a minute so 
    let's check if I come back again or not it's very possible I won't be coming back because I won't be 
    wasting my too much time for this anyways"""