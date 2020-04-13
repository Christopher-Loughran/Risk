import pygame
from pygame.locals import *
import random
import os
import math
import cmath
import time
import ctypes


WIDTH = 1400 #user32.GetSystemMetrics(0)
HEIGHT = 700 #user32.GetSystemMetrics(1)
MAX_FPS = 60
Click = False



BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (126, 168, 0)
YELLOW = (255, 255, 0)
DARK_ORANGE = (255, 102, 0)
RED = (255, 0, 0,)


game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")
snd_folder = os.path.join(game_folder, "snd")


os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,100)
pygame.init()
pygame.mixer.init()
pygame.display.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))#, pygame.FULLSCREEN)
fullscreen = False
pygame.display.set_caption("Rpg tests")


clock = pygame.time.Clock()


PAUSE_TICKS = 0
REAL_TICKS = pygame.time.get_ticks() - PAUSE_TICKS

font_name = pygame.font.match_font("courier", bold = True)

def draw_text(surf, text, size, x, y, colour):
	font = pygame.font.Font(font_name, size)
	text_surface = font.render(text, False, colour)
	text_rect = text_surface.get_rect()
	text_rect.midtop = (x, y)
	surf.blit(text_surface, text_rect)



class Player:
	
	PLAYER_COUNT = 0
	player_colours = [(34, 177, 76), (255, 140, 64), (237, 28, 36), (163, 73, 164), (89, 172, 255), (255, 174, 201)]
	
	starting_armies = [0, 0, 40, 35, 30, 25, 20]
	#number of starting armies for i players. ex: number of starting armies for 3 players = 35. for 0 and 1 player : 0 armies
	
	def __init__(self):
		Player.PLAYER_COUNT += 1
		self.number = Player.PLAYER_COUNT
		self.colour = Player.player_colours[self.number]
		self.num_regions = 0
		self.armies_left = 0 #number of armies left to be deployed



class Cursor(pygame.sprite.Sprite):
	
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(os.path.join(img_folder, "cursor.png")).convert_alpha()
		self.rect = self.image.get_rect()
		self.mask = pygame.mask.from_surface(self.image)
		self.rect.center = pygame.mouse.get_pos()
		
		
	def update(self, window):
		self.rect.center = pygame.mouse.get_pos()
	
	
	
	def select(self, regions):
		global Click
		
		for reg in regions:
			if(pygame.sprite.collide_mask(self, reg)):
				if Click:
					return reg


#todo
#combine whitemap and bridges/names
#game start
#menu
#cards/bonuses
#continent bonuses
#randomize region distribution
#region name colour
#deploy function


def dice(attackers, defenders): #number of attacking dice 1-3, defending dice 1-2 returns True if attack is succesful
	att_dice = []
	def_dice = []
	
	for i in range(attackers):
		att_dice.append(random.randint(1, 6))
	att_dice.sort(reverse=True)
	
	#print("attackers: ", att_dice)
	
	for i in range(defenders):
		def_dice.append(random.randint(1, 6))
	def_dice.sort(reverse=True)
	
	#print("defenders: ",def_dice)
	
	while(def_dice != [] and att_dice != []):
		if(att_dice[0] > def_dice[0]):
			return True
		elif(att_dice[0] < def_dice[0]):
			return False
		else:
			att_dice.pop(0)
			def_dice.pop(0)
	
	return False






class Region(pygame.sprite.Sprite):
	
	font = pygame.font.Font(font_name, 15)
	REG_COUNT = 0 #region id
	width_ratio = WIDTH/1200
	height_ratio = HEIGHT/614
	contient_colours = [("Asia", (51, 153, 102), (95, 201, 148)), ("Europe", (0, 56, 225), (66, 114, 255)), ("North America", (213, 213, 0), (255, 255, 0)), ("Africa", (174, 87, 0), (230, 115, 0)), ("Australia", (153, 51, 102), (200, 91, 146)), ("South America", (128, 0, 64), (204, 0, 102))]
	#Contient, normal colour, colour when selected
	
	#continent bonuses
	
	
	def __init__(self, filename, name, xratio, yratio, xoffset, yoffset, continent):
		pygame.sprite.Sprite.__init__(self)

		(self.unselected_colour, self.selected_colour) = self.get_colours(continent) #obtaining the colours of the region when selected and when not
		
		self.orig_image = pygame.image.load(os.path.join(img_folder, filename)).convert_alpha()
		self.unselected_image = pygame.transform.scale(self.orig_image, (int(self.orig_image.get_width()*Region.width_ratio), int(self.orig_image.get_height()*Region.height_ratio)))
		
		#making the image that will be the region when selected
		pixels = pygame.PixelArray(self.unselected_image)
		pixels.replace(self.unselected_colour, self.selected_colour)
		self.selected_image = pixels.make_surface()
		
		#making the rectangle that contains the image
		self.unselected_image = pygame.transform.scale(self.orig_image, (int(self.orig_image.get_width()*Region.width_ratio), int(self.orig_image.get_height()*Region.height_ratio)))
		self.image = self.unselected_image
		self.rect = self.image.get_rect()
		self.mask = pygame.mask.from_surface(self.image)
		self.rect.center = (WIDTH*xratio, HEIGHT*yratio)
		
		
		self.xoffset = xoffset
		self.yoffset = yoffset
		self.selected = False
		
		self.name = name
		Region.REG_COUNT += 1
		self.number = Region.REG_COUNT
		
		self.player = 0
		self.armies = 0
		self.adjacent = []
		
	
	def check_hover(self, cursor):
		hit = pygame.sprite.collide_mask(self, cursor)
		if hit:
			if(self.selected == False): #collision and region was previously unselected
				self.image = self.selected_image
				self.selected = True
				#print(self.name)
		else:
			if (self.selected == True): #no collision and region was previously selected
				self.image = self.unselected_image
				self.selected = False
		
	
	def get_colours(self, continent):
		for con in Region.contient_colours:
			if (con[0] == continent):
				return (con[1], con[2])
	
	def draw_armies(self): #draws the number of armies currently in this region
		text_surface = Region.font.render(str(self.armies), False, self.player.colour)
		text_rect = text_surface.get_rect()
		text_rect.midtop = (self.rect.centerx+self.xoffset, self.rect.centery+self.yoffset)
		window.blit(text_surface, text_rect)
	
	def update(self, window):
		self.draw_armies()
		

def add_to_groupes(region, Regions):
	Regions.add(region)



def set_regions():
	Regions = pygame.sprite.Group()
	
	alaska = Region("alaska.png", "Alaska", 0.06, 0.13428571428571429, 0, -10, "North America")
	add_to_groupes(alaska, Regions)
		
	alberta = Region("alberta.png", "Alberta", 0.13, 0.19, 0, 0, "North America")
	add_to_groupes( alberta, Regions)
	
	argentina = Region("argentina.png", "Argentina", 0.25, 0.84, 0, 0, "South America")
	add_to_groupes( argentina, Regions)
	
	brazil = Region("brazil.png", "Brazil", 0.2742857142857143, 0.6771428571428572, 0, 0, "South America")
	add_to_groupes( brazil, Regions)
	
	central_america = Region("central_america.png", "Central America", 0.15428571428571428, 0.4342857142857143, 0, 0, "North America")
	add_to_groupes( central_america, Regions)
	
	china = Region("china.png", "China", 0.77, 0.3357142857142857, 0, 0, "Asia")
	add_to_groupes( china, Regions)
	
	congo = Region("congo.png", "Congo", 0.5257142857142857, 0.5857142857142857, 0, 0, "Africa")
	add_to_groupes( congo, Regions)
	
	E_africa = Region("E_africa.png", "East Africa", 0.5757142857142857, 0.5557142857142857, 0, -20, "Africa")
	add_to_groupes( E_africa, Regions)
	
	E_australia = Region("E_australia.png", "Eastern Australia", 0.9164285714285715, 0.7757142857142857, 0, 20, "Australia")
	add_to_groupes( E_australia, Regions)
	
	eastern_US = Region("eastern_US.png", "Eastern United States", 0.17685714285714287, 0.31142857142857144, 0, 10, "North America")
	add_to_groupes( eastern_US, Regions)
	
	egypt = Region("egypt.png", "Egypt", 0.5278571428571428, 0.39, 0, 0, "Africa")
	add_to_groupes( egypt, Regions)
	
	GB = Region("GB.png", "Great Britain", 0.445, 0.19142857142857142, -35, 0, "Europe")
	add_to_groupes( GB, Regions)
	
	greenland = Region("greenland.png", "Greenland", 0.37142857142857144, 0.08428571428571428, 0, 0, "North America")
	add_to_groupes( greenland, Regions)
	
	iceland = Region("iceland.png", "Iceland", 0.4135714285714286, 0.12142857142857143, 0, 10, "Europe")
	add_to_groupes( iceland, Regions)
	
	india = Region("india.png", "India", 0.7092857142857143, 0.41714285714285715, 0, 0, "Asia")
	add_to_groupes( india, Regions)
	
	indonesia = Region("indonesia.png", "Indonesia", 0.8285714285714286, 0.5485714285714286, 0, 10, "Australia")
	add_to_groupes( indonesia, Regions)
	
	irkutsk = Region("irkutsk.png", "Irkutsk", 0.7807142857142857, 0.17857142857142858, 0, 10, "Asia")
	add_to_groupes( irkutsk, Regions)
	
	japan = Region("japan.png", "Japan", 0.8878571428571429, 0.30428571428571427, 0, 0, "Asia")
	add_to_groupes( japan, Regions)
	
	kamchatka = Region("kamchatka.png", "Kamchatka", 0.8828571428571429, 0.18, 0, -20, "Asia")
	add_to_groupes( kamchatka, Regions)
	
	kazakhstan = Region("kazakhstan.png", "Kazakhstan", 0.6492857142857142, 0.25285714285714284, 0, 0, "Asia")
	add_to_groupes( kazakhstan, Regions)
	
	madagascar = Region("madagascar.png", "Madagascar", 0.6078571428571429, 0.7157142857142857, 0, 0, "Africa")
	add_to_groupes( madagascar, Regions)
	
	middle_east = Region("middle_east.png", "Middle East", 0.5978571428571429, 0.38, 0, 0, "Asia")
	add_to_groupes( middle_east, Regions)
	
	mongolia = Region("mongolia.png", "Mongolia", 0.7914285714285715, 0.26142857142857145, 0, 0, "Asia")
	add_to_groupes( mongolia, Regions)
	
	N_africa = Region("N_africa.png", "North Africa", 0.4642857142857143, 0.4342857142857143, 0, 0, "Africa")
	add_to_groupes( N_africa, Regions)
	
	N_europe = Region("N_europe.png", "Northern Europe", 0.4957142857142857, 0.20857142857142857, 25, 5, "Europe")
	add_to_groupes( N_europe, Regions)
	
	nw_territories = Region("nw_territories.png", "NorthWest Territories", 0.17, 0.10714285714285714, 0, 0, "North America")
	add_to_groupes( nw_territories, Regions)
	
	ontario = Region("ontario.png", "Ontario", 0.19142857142857142, 0.21285714285714286, 0, -10, "North America")
	add_to_groupes( ontario, Regions)
	
	papua_NG = Region("papua_NG.png", "Papua New Guinea", 0.94, 0.61, 0, 0, "Australia")
	add_to_groupes( papua_NG, Regions)
	
	peru = Region("peru.png", "Peru", 0.22642857142857142, 0.6714285714285714, 0, 10, "South America")
	add_to_groupes( peru, Regions)
	
	quebec = Region("quebec.png", "Quebec", 0.2571428571428571, 0.2, 0, 0, "North America")
	add_to_groupes( quebec, Regions)
	
	S_africa = Region("S_africa.png", "South Africa", 0.5414285714285715, 0.7242857142857143, 0, 10, "Africa")
	add_to_groupes( S_africa, Regions)
	
	S_europe = Region("S_europe.png", "Southern Europe", 0.5092857142857142, 0.2714285714285714, 25, -15, "Europe")
	add_to_groupes( S_europe, Regions)
	
	scandinavia = Region("scandinavia.png", "Scandinavia", 0.5064285714285715, 0.13142857142857142, 0, 0, "Europe")
	add_to_groupes( scandinavia, Regions)
	
	siam = Region("siam.png", "Siam", 0.7892857142857143, 0.4685714285714286, 0, 0, "Asia")
	add_to_groupes( siam, Regions)
	
	siberia = Region("siberia.png", "Siberia", 0.6985714285714286, 0.13857142857142857, 0, -20, "Asia")
	add_to_groupes( siberia, Regions)
	
	ukraine = Region("ukraine.png", "Ukraine", 0.576428571428514, 0.19428571428571428, 0, 0, "Europe")
	add_to_groupes( ukraine, Regions)
	
	ural = Region("ural.png", "Ural", 0.6611428571428571, 0.15757142857142856, 0, 0, "Asia")
	add_to_groupes( ural, Regions)
	
	venezuela = Region("venezuela.png", "Venezuela", 0.23, 0.5485714285714286, -10, -10, "South America")
	add_to_groupes( venezuela, Regions)
	
	W_australia = Region("W_australia.png", "Western Australia", 0.8692857142857143, 0.7657142857142857, 0, 10, "Australia")
	add_to_groupes( W_australia, Regions)
	
	W_europe = Region("W_europe.png", "Western Europe", 0.45285714285714285, 0.2642857142857143, -10, 10, "Europe")
	add_to_groupes( W_europe, Regions)
	
	western_US = Region("western_US.png", "Western United States", 0.11357142857142857, 0.29, 0, 0, "North America")
	add_to_groupes( western_US, Regions)
	
	yakutsk = Region("yakutsk.png", "Yakutsk", 0.7921428571428571, 0.12285714285714286, 0, 0, "Asia")
	add_to_groupes( yakutsk, Regions)
	
	alaska.adjacent = [alberta, nw_territories, kamchatka]
	alberta.adjacent = [alaska, nw_territories, ontario, western_US]
	argentina.adjacent = [peru, brazil]
	brazil.adjacent = [argentina, peru, venezuela, N_africa]
	central_america.adjacent = [western_US, eastern_US, venezuela]
	china.adjacent = [siam, india, kazakhstan, ural, siberia, mongolia]
	congo.adjacent = [N_africa, E_africa, S_africa]
	E_africa.adjacent = [egypt, N_africa, congo, S_africa, madagascar, middle_east]
	E_australia.adjacent = [W_australia, papua_NG]
	eastern_US.adjacent = [central_america, western_US, ontario, quebec]
	egypt.adjacent = [N_africa, E_africa, middle_east, S_europe]
	GB.adjacent = [iceland, W_europe, N_europe, scandinavia]
	greenland.adjacent = [iceland, quebec, ontario, nw_territories]
	iceland.adjacent = [greenland, GB, scandinavia]
	india.adjacent = [middle_east, kazakhstan, china, siam]
	indonesia.adjacent = [W_australia, papua_NG, siam]
	irkutsk.adjacent = [mongolia, siberia, yakutsk, kamchatka]
	japan.adjacent = [mongolia, kamchatka]
	kamchatka.adjacent = [alaska, japan, mongolia, irkutsk, yakutsk]
	kazakhstan.adjacent = [ukraine, ural, china, india, middle_east]
	madagascar.adjacent = [S_africa, E_africa]
	middle_east.adjacent = [S_europe, ukraine, kazakhstan, india, E_africa, egypt]
	mongolia.adjacent = [japan, china, siberia, irkutsk, kamchatka]
	N_africa.adjacent = [W_europe, egypt, E_africa, congo, brazil, S_europe]
	N_europe.adjacent = [W_europe, GB, scandinavia, ukraine, S_europe]
	nw_territories.adjacent = [alaska, greenland, ontario, alberta]
	ontario.adjacent = [alberta, nw_territories, greenland, quebec, western_US, eastern_US]
	papua_NG.adjacent = [indonesia, W_australia, E_australia]
	peru.adjacent = [venezuela, brazil, argentina]
	quebec.adjacent = [eastern_US, ontario, greenland]
	S_africa.adjacent = [madagascar, congo, E_africa]
	S_europe.adjacent = [W_europe, N_europe, ukraine, middle_east, egypt, N_africa]
	scandinavia.adjacent = [iceland, ukraine, N_europe, GB]
	siam.adjacent = [indonesia, india, china]
	siberia.adjacent = [ural, yakutsk, irkutsk, mongolia, china]
	ukraine.adjacent = [S_europe, N_europe, scandinavia, ural, kazakhstan, middle_east, ]
	ural.adjacent = [ukraine, siberia, china, kazakhstan]
	venezuela.adjacent = [central_america, peru, brazil]
	W_australia.adjacent = [E_australia, indonesia, papua_NG]
	W_europe.adjacent = [GB, N_europe, S_europe, N_africa]
	western_US.adjacent = [alberta, ontario, eastern_US, central_america]
	yakutsk.adjacent = [siberia, kamchatka, irkutsk]
	
	
	return Regions


def testlevel():
	global REAL_TICKS
	global PAUSE_TICKS
	global Click
	
	
	Sprites = pygame.sprite.Group()
	Regions = set_regions(Sprites)
	Regs = []
	
	reg_names = ["alaska", "alberta", "argentina", "brazil", "central_america", "china", "congo", "E_africa", "E_australia", "eastern_US", "egypt", "GB", "greenland", "iceland", "india", "indonesia", "irkutsk", "japan", "kamchatka", "kasakhstan", "madagascar", "middle_east", "mongolia", "N_africa", "N_europe", "nw_territories", "ontario", "papua_NG", "peru", "quebec", "S_africa", "S_europe", "scandinavia", "siam", "siberia", "ukraine", "ural", "venezuela", "W_australia", "W_europe", "western_US", "yakutsk"]

	
	for reg in reg_names:
		regfile = reg + ".png"
		r = Region(regfile, reg, 0.5, 0.5)
		# Sprites.add(r)
		# Regions.add(r)
		# Regs.append(r)
	
	name_bridges = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, "name_bridge.png")).convert_alpha(), (WIDTH, HEIGHT))
	white_map = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, "white_map.png")).convert_alpha(), (WIDTH, HEIGHT))
	
	x = 0
	y = 0
	selected = 0
	# selected_reg = Regs[0]
	
	cursor = Cursor()
	Sprites.add(cursor)
	
	
	running = True

	while(running):
		clock.tick(MAX_FPS)
		REAL_TICKS = pygame.time.get_ticks() - PAUSE_TICKS
		window.fill((50, 128, 230))
		
		
		
		window.blit(white_map, (0, 0)) #map with just the borders of each region makes the map looks cleaner
		
		Sprites.draw(window)
		
		window.blit(name_bridges, (0, 0))
		
		draw_text(window, str(clock.get_fps()//1), 30, WIDTH-40, 20, BLACK)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				running = False
				
			elif event.type == pygame.MOUSEBUTTONDOWN:
				click = True
			elif event.type == pygame.MOUSEBUTTONUP:
				click = False
			
			if event.type == pygame.KEYUP and event.key == pygame.K_d:
				selected += 1
				if(selected >= len(Regs)):
					selected = 0
				print(len(Regs))
				print(selected)
				# selected_reg = Regs[selected]
				# pygame.mouse.set_pos((selected_reg.rect.centerx, selected_reg.rect.centery))
			if event.type == pygame.KEYUP and event.key == pygame.K_a:
				selected -= 1
				if(selected < 0):
					selected = len(Regs)-1
				print(len(Regs))
				print(selected)
				# selected_reg = Regs[selected]
				# pygame.mouse.set_pos((selected_reg.rect.centerx, selected_reg.rect.centery))
		
		key_state = pygame.key.get_pressed()
		if key_state[pygame.K_UP]: 
			selected_reg.rect.centery -= 1
		if key_state[pygame.K_DOWN]:
			selected_reg.rect.centery += 1
		if key_state[pygame.K_LEFT]:
			selected_reg.rect.centerx -= 1
		if key_state[pygame.K_RIGHT]:
			selected_reg.rect.centerx += 1
			
		
		
		
		
		
		# print(selected_reg.rect.centerx/WIDTH, selected_reg.rect.centery/HEIGHT, selected_reg.name)
		# 
		# 
		# pos = pygame.mouse.get_pos()
		# selected_reg.rect.centerx = pos[0]
		# selected_reg.rect.centery = pos[1]
		
		pygame.display.flip()
		
		Sprites.update()



def distribute(players, Regions):
	
	regs = []
	for r in Regions:
		regs.append(r)
	
	random.shuffle(regs)
	
	
	i = 0
	for r in regs:
		r.player = players[i % len(players)]
		players[i % len(players)].num_regions += 1
		i+=1

	

def start(num_players): #, num_bots, num_neutrals): #players are human, bots are AI, neutral don't get turns
	
	players = []
	
	for i in range(num_players):
		player = Player()
		player.armies_left = Player.starting_armies[num_players]
		players.append(player)
		
	
	Regions = set_regions()
	distribute(players, Regions)
	
	for r in Regions:
		r.armies = 1
	
	for p in players:
		p.armies_left -= p.num_regions

	return players, Regions



def deploy(player, Sprites, Regions, cursor, window):
	global REAL_TICKS
	global PAUSE_TICKS
	global Click
	
	LEFT = 1
	RIGHT = 3 #mouse buttons

	background = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, "name_bridge.png")).convert_alpha(), (WIDTH, HEIGHT))
	
	
	running = True
	

	while(running):
		clock.tick(MAX_FPS)
		REAL_TICKS = pygame.time.get_ticks() - PAUSE_TICKS
		window.fill((146, 216, 228))
		
		
		
		window.blit(background, (0, 0)) #map with just the borders of each region makes the map looks cleaner + names and bridges
		
		# x = iter(Regions)
		# for i in range(len(Regions)):
		# 	next(x).check_hover(cursor)
		
		for r in Regions:
			r.check_hover(cursor)
		
		
		
		Sprites.draw(window)
		
		Regions.update(window)
		
		
		draw_text(window, str(clock.get_fps()//1), 30, WIDTH-20, 20, BLACK)
		
		message = "Player " + str(player.number) + " you have " + str(player.armies_left) + " armies left to deploy"
		draw_text(window, message, 20, WIDTH/2, HEIGHT-50, player.colour)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				running = False
			elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
				for r in Regions:
					if(r.selected and r.player == player):
						r.armies += 1
						player.armies_left -= 1
						
			elif event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT:
				for r in Regions:
					if(r.selected and r.player == player and r.armies > 1):
						r.armies -= 1
						player.armies_left += 1
		
		if(player.armies_left <= 0):
			running = False
		
		
		pygame.display.flip()
		
		Sprites.update(window)
	
	
	

def testlevel2():
	global REAL_TICKS
	global PAUSE_TICKS
	global Click
	
	players, Regions = start(3)
	
	Sprites = Regions.copy()
	
	background = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, "name_bridge.png")).convert_alpha(), (WIDTH, HEIGHT))
	

	cursor = Cursor()
	Sprites.add(cursor)
	
	
	distribute(players, Regions)
	
	# x = iter(Regions)
	# for i in range(len(Regions)):
	# 	current = next(x)
	# 	print(current.name, current.player.number)
	
	for p in players:
		deploy(p, Sprites, Regions, cursor, window)
	
	
	running = True

	while(running):
		clock.tick(MAX_FPS)
		REAL_TICKS = pygame.time.get_ticks() - PAUSE_TICKS
		window.fill((146, 216, 228))
		
		
		
		window.blit(background, (0, 0)) #map with just the borders of each region makes the map looks cleaner + names and bridges
		
		x = iter(Regions)
		for i in range(len(Regions)):
			next(x).check_hover(cursor)
		
		
		
		
		Sprites.draw(window)
		
		Regions.update(window)
		
		
		draw_text(window, str(clock.get_fps()//1), 30, WIDTH-40, 20, BLACK)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				running = False
			
			
		
		pygame.display.flip()
		
		Sprites.update(window)
	
	
testlevel2()

# while(True):
# 	nxt = ""
# 	
# 	att = random.randint(1, 3)
# 	defe = random.randint(1, 2)
# 	
# 	if (dice(att, defe)):
# 		print("attackers win")
# 	else:
# 		print("defenders win")
# 
# 	nxt = input()















