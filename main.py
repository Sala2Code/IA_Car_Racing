import pygame
from math import * 
import neat
import sys
import os
import random
import numpy as np

pygame.init()

pygame.font.init() 
FONT = pygame.font.SysFont('Comic Sans MS', 20)


width = 900
height = 900
width_car = width/60
height_car = height/30

fps = 60
nb_line_view = 5
fov = 90
coef_v = 0.5
acc_or_dec = 0.1*coef_v 

w_view = 7 # Odd # If you modify this, you must modify the map manually 
mid_view = floor(w_view/2)
w_2_v = width/(2*(w_view-2))

def gauche(map,map_co):
    for i in range(w_view):
        map[i] = map[i][-1:]+map[i][:-1]
    map_co[0]-=1

    for i in range(w_view):
        path = 0
        for e,co in enumerate(coord):
            if co[0]==map_co[0]-mid_view and co[1]==map_co[1]+mid_view+i :
                path = type_road[e]
                break
        map[i][0]=path
    generate_road(map,map_co)
    return map,map_co

def droite(map,map_co):
    for i in range(w_view):
        map[i] = map[i][1:]+map[i][:1]
    map_co[0]+=1

    for i in range(w_view):
        path = 0
        for e,co in enumerate(coord):
            if co[0]==map_co[0]+mid_view and co[1]==map_co[1]+mid_view+i :
                path = type_road[e]
                break
        map[i][-1]=path
    generate_road(map,map_co)
    return map,map_co

def haut(map,map_co):
    map = np.array(map).T.tolist()
    for i in range(w_view):
        map[i] = map[i][-1:]+map[i][:-1]
    map = np.array(map).T.tolist()
    map_co[1]+=1
    for i in range(w_view):
        path = 0
        for e,co in enumerate(coord):
            if co[0]==map_co[0]-mid_view+i and co[1]==map_co[1]+mid_view :
                path = type_road[e]
                break
        map[0][i]=path
    generate_road(map,map_co)
    return map,map_co

def bas(map,map_co):
    map = np.array(map).T.tolist()
    for i in range(w_view):
        map[i] = map[i][1:]+map[i][:1]
    map = np.array(map).T.tolist()
    map_co[1]-=1
    for i in range(w_view):
        path = 0
        for e,co in enumerate(coord):
            if co[0]==map_co[0]-mid_view+i and co[1]==map_co[1]-mid_view :
                path = type_road[e]
                break
        map[-1][i]=path
    generate_road(map,map_co)
    return map,map_co

def generate_road(map,map_co):
    a_co = type_road[-1]

    if a_co==1 or a_co==7 or a_co==8:
        return choice_path(map,[1,3,4], (0,1),map_co)

    if a_co==-1 or a_co==9 or a_co==10:
        return choice_path(map,[-1,5,6], (0,-1),map_co)

    if a_co==-2 or a_co==4 or a_co==6:
        return choice_path(map,[-2,8,10], (-1,0),map_co)

    if a_co==2 or a_co==3 or a_co==5:
        return choice_path(map, [2,7,9], (1,0),map_co)

def choice_path(map, possible_move, move, map_co):
    global dist_min
    # Gauche : Left / Droite : Right / Haut : Up / Bas : Down (long live the French :) )
    # -2 gauche
    # -1 bas
    # 1 haut
    # 2 droite
    # 3 turn haut-droite
    # 4 turn haut-gauche
    # 5 turn bas-droite
    # 6 turn bas-gauche
    # 7 turn droite-haut
    # 8 turn gauche-haut
    # 9 turn droite-bas
    # 10 turn gauche-bas
    next_move = {
        -2 : (-1,0),
        -1 : (0,-1),
        1 : (0,1),
        2 : (1,0),
        3 : (1,0),
        4 : (-1,0),
        5 : (1,0),
        6 : (-1,0),
        7 : (0,1),
        8 : (0,1),
        9 : (0,-1),
        10 : (0,-1)
    }
    while True:
        chemin = random.choice(possible_move)
        next_co = sum(sum(coord[-1],next_move[chemin]),move)
        dist = next_co[0]**2 + next_co[1]**2
        if dist_min**2 <= dist:
            coord.append((coord[-1][0]+move[0],coord[-1][1]+move[1]))
            map[ abs(coord[-1][1]-map_co[1]-mid_view) ][ coord[-1][0]-map_co[0] + mid_view]=chemin
            type_road.append(chemin)
            if dist>=(dist_min+1)**2:
                dist_min = floor(sqrt(dist))
            return map

def sum(a,b):
    return (a[0]+b[0],a[1]+b[1])

def generate_map(map):
    for i,row in enumerate(map):
        for j,col in enumerate(row):
            taille = (width/(w_view-2),height/(w_view-2))
            pos = (
                (j-1)*width/(w_view-2)-decalage[0], 
                (i-1)*height/(w_view-2)+decalage[1]
                )
            window.blit(pygame.transform.scale(tile[map[i][j]][0], taille), pos)

class Cars:
    def __init__(self):
        self.x = width/2
        self.y = height/2
        self.angle = 90
        self.touch = [False,False,True] # The thirth elements it's useless for this code but I keep it to modify sometimes the code
        self.alive = True
        self.vitesse = 8*coef_v
        self.travel = 0
        self.first = False

        self.car = pygame.image.load("img/car.png").convert_alpha()
        self.carf = pygame.image.load("img/carf.png").convert_alpha() # To see which car is first (or at least, in the firsts)
        self.car_die = pygame.image.load("img/car_die.png").convert_alpha()

        self.car = pygame.transform.scale(self.car, (height_car,width_car))
        self.carf = pygame.transform.scale(self.carf, (height_car,width_car))
        self.car_die = pygame.transform.scale(self.car_die, (height_car, width_car))
        
    
    def update(self, stadium):
        if self.touch[0]:
            self.angle +=5*coef_v
        if self.touch[1]:
            self.angle -=5*coef_v
        if self.touch[2]: 
            d_x = cos((self.angle)*pi/180)*self.vitesse
            d_y =  sin((self.angle)*pi/180)*self.vitesse
            self.travel+= sqrt(d_x**2+d_y**2)
            self.x += d_x - prec_dec[0]
            self.y -= d_y - prec_dec[1]
        
        car_update = pygame.transform.rotate(self.carf, self.angle) if self.first else pygame.transform.rotate(self.car, self.angle)

        self.point_rotate = (int( (self.x - car_update.get_width()/2)),int((self.y - car_update.get_height()/2)))
        self.centre = (self.x,self.y)
        # detect if it's out of screen
        if (self.x - all_cars[i_car_far].x)**2 + (self.y - all_cars[i_car_far].y)**2 > (width**2/4):
            self.alive = False

        # view
        self.view = [0]*nb_line_view
        self.dist_view = [0]*nb_line_view
        for i in range(nb_line_view):
            angle_temp = -(self.angle - fov/2 + i*fov/nb_line_view)*pi/180
            pos_test = (int(self.x),int(self.y))
            iter = 0
            length = 0

            # ? To avoid knowing the color of a pixel out of the window (as impossible)
            # ? I think it can be optimized
            if pos_test[0]>width or pos_test[0]<0 or pos_test[1]>height or pos_test[1]<0:
                self.alive=False
                self.view[i] = pos_test
                self.dist_view[i] = length # = 0
            else:
                while pygame.Surface.get_at(stadium,pos_test)!=(0,210,0,255) and length < 200:
                    pos_test = (int(self.x + cos(angle_temp)*iter),int(self.y + sin(angle_temp)*iter))

                    if pos_test[0]>=width or pos_test[0]<=0 or pos_test[1]>=height or pos_test[1]<=0:
                        self.alive = False
                        self.view[i] = pos_test
                        self.dist_view[i] =  length 
                        break
                    iter+=1
                    length = sqrt( (cos(angle_temp)*iter)**2 + (sin(angle_temp)*iter)**2)     
                self.view[i] = pos_test
                self.dist_view[i] =  length
        return car_update


window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Car Racing")

# Each image is in a list because later I will put others image to complicate the road (to instance with hole in the middle of the road)
tile = {
    -2 : [pygame.image.load("img/tile_2.png").convert_alpha()],
    -1 : [pygame.image.load("img/tile_1.png").convert_alpha()],
    0 : [pygame.image.load("img/tile_0.png").convert_alpha()],
    1 : [pygame.image.load("img/tile_1.png").convert_alpha()],
    2 : [pygame.image.load("img/tile_2.png").convert_alpha()],
    3 : [pygame.image.load("img/tile_3.png").convert_alpha()],
    4 : [pygame.image.load("img/tile_4.png").convert_alpha()],
    5 : [pygame.image.load("img/tile_5.png").convert_alpha()],
    6 : [pygame.image.load("img/tile_6.png").convert_alpha()],
    7 : [pygame.image.load("img/tile_6.png").convert_alpha()],
    8 : [pygame.image.load("img/tile_5.png").convert_alpha()],
    9 : [pygame.image.load("img/tile_4.png").convert_alpha()],
    10 : [pygame.image.load("img/tile_3.png").convert_alpha()],
}

def eval_genomes(genomes,config):
    global l_cars, ge, nets, all_cars, decalage, map_co, map, prec_dec, coord, dist_min, type_road, i_car_far
    clock = pygame.time.Clock()
    l_cars = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        l_cars.append(Cars())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    all_cars = l_cars.copy()

    def statistics():
        global l_cars, ge
        text_1 = FONT.render(f'Cars Alive:  {str(len(l_cars))}', True, (255, 255, 255))
        text_2 = FONT.render(f'Generation:  {popu.generation+1}', True, (255, 255, 255))
        text_3 = FONT.render(f'Traveled:  {int(d_travel)}', True, (255, 255, 255))

        window.blit(text_1, (50, 50))
        window.blit(text_2, (50, 100))
        window.blit(text_3, (50, 150))

    map = [
        [0,0,0,0,0,0,0],
        [0,0,0,3,2,0,0],
        [0,0,0,1,0,0,0],
        [0,0,0,1,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0]
    ]
    coord = [(0,0),(0,1),(0,2),(1,2)]
    map_co = [0,0] # Coordinates of the map's center
    type_road = [1,1,3,2] 

    dist_min = 2
    decalage = [0,0] # To create a fluid view
    prec_dec = [0,0]
    i_car_far = 0 # index of farthest car (or at least one of the farthest)

    isOpen = True
    while isOpen:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit() 
                sys.exit()

        window.fill((0,0,0))
        generate_map(map)
        stadium = window.copy()
        # ? Update cars
        for i in all_cars:
            if i.alive:
                car_upd = i.update(stadium)
                window.blit(car_upd,i.point_rotate)
                for j in range(nb_line_view):
                    pygame.draw.line(window, (255,0,0), i.centre, i.view[j])
            else:
                i.x-=prec_dec[0]
                i.y+=prec_dec[1]
                car_die_upd = pygame.transform.rotate(i.car, i.angle)
                i.point_rotate = (int( (i.x - car_die_upd.get_width()/2)),int((i.y - car_die_upd.get_height()/2)))
                window.blit(i.car_die,i.point_rotate)

        # ? d_travel && center
        d_travel=0
        for i, car in enumerate(all_cars):
            if car.travel > d_travel and car.alive:
                if i!=i_car_far:
                    x_to_center = all_cars[i_car_far].x - all_cars[i].x
                    y_to_center = all_cars[i_car_far].y - all_cars[i].y
                    for all_v in all_cars:
                        all_v.x+= x_to_center
                        all_v.y+= y_to_center
                    
                    decalage = [decalage[0]-x_to_center,decalage[1]+y_to_center]
                    all_cars[i_car_far].first = False
                    i_car_far = i
                d_travel = car.travel
                car.first = True

        # ? To get out of the loop
        if len(l_cars)==0:
            break
        
        # ? To center the window with the "first" car
        prec_dec[0] = cos((all_cars[i_car_far].angle)*pi/180)*all_cars[i_car_far].vitesse
        prec_dec[1] = sin((all_cars[i_car_far].angle)*pi/180)*all_cars[i_car_far].vitesse
        decalage[0] += prec_dec[0]
        decalage[1] += prec_dec[1]

        # ? Death -> substract (remove)
        l_cars_die = [False]*len(l_cars)
        for e,car in enumerate(l_cars):
            for i in car.dist_view:
                if i==0 or not car.alive:
                    car.alive=False 
                    l_cars_die[e] = True
        l_cars = [l_cars[i] for i in range(len(l_cars_die)) if not l_cars_die[i]]  
        ge = [ge[i] for i in range(len(l_cars_die)) if not l_cars_die[i]]  
        nets = [nets[i] for i in range(len(l_cars_die)) if not l_cars_die[i]]  


        # ? Output
        for i, car in enumerate(l_cars):
            output = nets[i].activate((car.dist_view[0],car.dist_view[1],car.dist_view[2],car.dist_view[3],car.dist_view[4]))
            # ? Turn
            if output[0] >= 0.5:
                car.touch[0] = True
                car.touch[1] = False
            else:
                car.touch[0] = False
                car.touch[1] = True

            # ? Velocity is progressive
            if output[1] >= 0.5 :
                car.vitesse-=acc_or_dec if car.vitesse>4*coef_v else -acc_or_dec
            else:
                car.vitesse+=acc_or_dec if car.vitesse<8*coef_v else -acc_or_dec

        for e, car in enumerate(l_cars):
            ge[e].fitness=car.travel

        if decalage[1] > w_2_v and coord[-3][1]>coord[-4][1]:
            map, map_co = haut(map, map_co)
            decalage[1] = -width/(w_view-2) + decalage[1] 

        if decalage[1] < - w_2_v and coord[-3][1]<coord[-4][1]:
            map, map_co = bas(map,map_co)
            decalage[1] = width/(w_view-2) + decalage[1] 

        if decalage[0] > w_2_v and coord[-3][0]>coord[-4][0]:
            map, map_co = droite(map, map_co)
            decalage[0] =  - width/(w_view-2) + decalage[0] 

        if decalage[0] < - w_2_v and coord[-3][0]<coord[-4][0]:
            map, map_co = gauche(map,map_co)
            decalage[0] = width/(w_view-2) - decalage[0] 

        statistics()
        pygame.draw.circle(window,(255,255,255),(width/2,height/2),1) # Window's center
        pygame.display.flip()
        clock.tick(fps)



def run(config_path):
    global popu
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    popu = neat.Population(config)
    popu.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)