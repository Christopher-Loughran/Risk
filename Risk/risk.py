import pygame
from pygame.locals import *
import random
import os
import time
import sys


WIDTH = 1400
HEIGHT = 700
MAX_FPS = 60


#todo
#menu
#losing/winning
#class continents maybe
#sound
#alter background
#redo +/- buttons


#bugs
#amry count drawn in front of dice
#end turn button needs too say redeploy
#move button needs to say move/end turn


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (126, 168, 0)
YELLOW = (255, 255, 0)
DARK_ORANGE = (255, 102, 0)
RED = (255, 0, 0,)
SEA_COLOUR = (146, 216, 228)


game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")
snd_folder = os.path.join(game_folder, "snd")


os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,100)
pygame.init()
pygame.mixer.init()
pygame.display.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Risk")


clock = pygame.time.Clock()

font_name = pygame.font.match_font("courier", bold = True)

background = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, "name_bridge.png")).convert_alpha(), (WIDTH, HEIGHT))


def draw_text(surf, text, size, x, y, colour, center=False):
	font = pygame.font.Font(font_name, size)
	text_surface = font.render(text, False, colour)
	text_rect = text_surface.get_rect()
	if(center):
		text_rect.center = (x, y)
	else:
		text_rect.topleft = (x, y)
	surf.blit(text_surface, text_rect)



_circle_cache = {}
def _circlepoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


def draw_text_outlined(text, size, x, y, innercolor, outercolor=(0, 0, 0), opx=2):
	global window
	font = pygame.font.Font(font_name, size)
	textsurface = font.render(text, True, innercolor).convert_alpha()
	w = textsurface.get_width() + 2 * opx
	h = font.get_height()

	osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
	osurf.fill((0, 0, 0, 0))

	surf = osurf.copy()

	osurf.blit(font.render(text, True, outercolor).convert_alpha(), (0, 0))

	for dx, dy in _circlepoints(opx):
		surf.blit(osurf, (dx + opx, dy + opx))

	surf.blit(textsurface, (opx, opx))
	window.blit(surf, (x, y))



class Player:
	
	PLAYER_COUNT = 0
	player_colours = [(237, 28, 36), (34, 177, 76), (255, 140, 64), (163, 73, 164), (89, 172, 255), (255, 174, 201)]
	random.shuffle(player_colours)
	
	starting_armies = [0, 0, 40, 35, 30, 25, 20]
	#number of starting armies for i players. ex: number of starting armies for 3 players = 35. for 0 and 1 player : 0 armies
	
	canon1 = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, "canon.png")).convert_alpha(), (int(WIDTH/2), int(HEIGHT/2)))
	canon3 = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, "canon3.png")).convert_alpha(), (int(WIDTH/3), int(HEIGHT/3)))
	canon2 = pygame.transform.flip(canon3, True, False)
	
	def __init__(self):
		Player.PLAYER_COUNT += 1
		self.number = Player.PLAYER_COUNT
		self.colour = Player.player_colours[self.number-1]
		self.num_regions = 0
		self.armies_left = 0 #number of armies left to be deployed
		self.cards = []
		
		# for i in range(4):
		# 	c = Card()
		# 	self.cards.append(c)
	
	def redeemable(self): #see if the cards that the player holds are redeemable or not
		
		if(len(self.cards) < 3):
			return 0
		
		inf = 0
		cav = 0
		art = 0
		
		for c in self.cards:
			if(c.type == "infantry"):
				inf += 1
			elif(c.type == "cavalry"):
				cav += 1
			else:
				art += 1
		
		if(inf >= 1 and cav >= 1 and art >= 1):
			return 10
		elif(cav >= 3):
			return 8
		elif(inf >= 3):
			return 6
		elif(art >= 3):
			return 4
		else:
			return 0
	
	def redeem_cards(self, armies):
		
		if(armies == 10):
			cav = False
			art = False
			inf = False
			i = 0
			while(not(cav and art and inf)):
				if(self.cards[i].type == "cavalry" and not cav):
					self.cards.pop(i)
					cav = True
				elif(self.cards[i].type == "infantry" and not inf):
					self.cards.pop(i)
					inf = True
				elif(self.cards[i].type == "artillery" and not art):
					self.cards.pop(i)
					art = True
				else:
					i+=1
		else:
			card_type = ""
			
			if(armies == 8):
				card_type = "cavalry"
			elif(armies == 6):
				card_type = "infantry"
			elif(armies == 4):
				card_type = "artillery"				

			cards_removed = 0
			i = 0
			while(cards_removed < 3 and i < len(self.cards)):
				if(self.cards[i].type == card_type):
					self.cards.pop(i)
					cards_removed+=1
				else:
					i+=1
	
	def lose(self, cursor):
		global window
		
		
		Buttons = pygame.sprite.Group()
		next = Button("Next", 300, HEIGHT-50)
		Buttons.add(next)
		
		
		CLICK = False
		
		running = True
		while(running):
			clock.tick(MAX_FPS)
		
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT: 
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					CLICK = True
				elif event.type == pygame.MOUSEBUTTONUP:
					CLICK = False
			
			if(next.check_clicked(cursor, CLICK)):
				return
			
			Buttons.update()
			cursor.update()
			
			window.fill(SEA_COLOUR)
			Buttons.draw(window)
			
			window.blit(Player.canon1, (int(WIDTH/4), HEIGHT-500))
			draw_text_outlined(("Player " + str(self.number) + " has been defeated!"), 50, 300, 100, self.colour)
			
			
			for b in Buttons:
				b.draw_button_text(window)
			
			
			pygame.display.flip()
	
	
	def win(self, cursor):
		global window
		
		Buttons = pygame.sprite.Group()
		next = Button("Exit", 300, HEIGHT-50)
		Buttons.add(next)
		
		CLICK = False
		
		running = True
		while(running):
			clock.tick(MAX_FPS)
			
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT: 
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					CLICK = True
				elif event.type == pygame.MOUSEBUTTONUP:
					CLICK = False
			
			if(next.check_clicked(cursor, CLICK)):
				sys.exit()
			
			Buttons.update()
			cursor.update()
			
			window.fill(SEA_COLOUR)
			Buttons.draw(window)
			
			window.blit(Player.canon3, (WIDTH/4 - 200, HEIGHT-400))
			window.blit(Player.canon2, (WIDTH/4*3 -250, HEIGHT-400))
			draw_text_outlined(("Player " + str(self.number) + " is Victorious!"), 50, 350, 100, self.colour)
			
			
			for b in Buttons:
				b.draw_button_text(window)
			
			
			pygame.display.flip()


class Cursor(pygame.sprite.Sprite):
	
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(os.path.join(img_folder, "cursor.png")).convert_alpha()
		self.rect = self.image.get_rect()
		self.mask = pygame.mask.from_surface(self.image)
		self.rect.center = pygame.mouse.get_pos()
		
		
	def update(self):
		self.rect.center = pygame.mouse.get_pos()
	
	
	
	def select(self, regions):
		global Click
		
		for reg in regions:
			if(pygame.sprite.collide_mask(self, reg)):
				if Click:
					return reg


def dice(attackers, defenders): #number of attacking dice 1-3, defending dice 1-2 returns True if attack is succesful
	att_dice = []
	def_dice = []
	
	if(attackers > 3):
		attackers = 3
	if(defenders > 2):
		defenders = 2
	
	for i in range(attackers):
		att_dice.append(random.randint(1, 6))
	att_dice.sort(reverse=True)
	
	#print("attackers: ", att_dice)
	
	for i in range(defenders):
		def_dice.append(random.randint(1, 6))
	def_dice.sort(reverse=True)
	
	#print("defenders: ",def_dice)
	
	orig_att_dice = att_dice.copy()
	orig_def_dice = def_dice.copy()#keep the original dice to show the dice
	
	
	while(def_dice != [] and att_dice != []):
		if(att_dice[0] > def_dice[0]):
			return True, orig_att_dice, orig_def_dice
		elif(att_dice[0] < def_dice[0]):
			return False, orig_att_dice, orig_def_dice
		else:
			att_dice.pop(0)
			def_dice.pop(0)
	
	return False, orig_att_dice, orig_def_dice


class Button(pygame.sprite.Sprite):
	normal = pygame.image.load(os.path.join(img_folder, "button.png")).convert_alpha()
	hover = pygame.image.load(os.path.join(img_folder, "button_hover.png")).convert_alpha()
	clicked= pygame.image.load(os.path.join(img_folder, "button_clicked.png")).convert_alpha()
	
	
	def __init__(self, text, x, y, size=(200, 50, 30)):#size=(width, height, textsize)
		pygame.sprite.Sprite.__init__(self)
		
		self.size = (size[0], size[1])
		self.textsize = size[2]
		
		self.normal_img = pygame.transform.scale(Button.normal, self.size)
		self.hover_img = pygame.transform.scale(Button.hover, self.size)
		self.clicked_img = pygame.transform.scale(Button.clicked, self.size)
		
		self.image = self.normal_img
		self.rect = self.image.get_rect()
		self.mask = pygame.mask.from_surface(self.image)
		self.rect.center = (x, y)
		
		
		self.text = text
		self.hover = False
		self.pressed = False
		self.released = False
		#self.active = False
		
		
	def check_clicked(self, cursor, CLICK):
		hit = pygame.sprite.collide_mask(self, cursor)
		
		if hit:
			self.hover = True
		else:
			self.hover = False
			self.pressed = False
			
		if (self.hover and CLICK):
			self.hover = False
			self.pressed = True
			
		if (self.pressed and not CLICK):
			self.pressed = False
			return True
		return False

	def update(self):
		if (self.hover):
			self.image = self.hover_img
		if (self.pressed):
			self.image = self.clicked_img
		if(not self.hover and not self.pressed):
			self.image = self.normal_img
	
	def draw_button_text(self, window):
		if(not self.pressed):
			draw_text(window, self.text, self.textsize, self.rect.centerx, self.rect.centery, BLACK, True)
		else:
			draw_text(window, self.text, self.textsize, self.rect.centerx-int(self.size[0]/25), self.rect.centery-int(self.size[1]/25), BLACK, True)


class Region(pygame.sprite.Sprite):
	
	font = pygame.font.Font(font_name, 15)
	h = font.get_height()
	
	
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
		
		#scaled version of the orignial image
		self.orig_unselected_image = pygame.transform.scale(self.orig_image, (int(self.orig_image.get_width()*Region.width_ratio), int(self.orig_image.get_height()*Region.height_ratio)))
		
		
		#making the image that will be the region when selected
		pixels = pygame.PixelArray(self.orig_unselected_image.copy())
		pixels.replace(self.unselected_colour, self.selected_colour)
		self.orig_selected_image = pixels.make_surface()
		
		self.unselected_image = self.orig_unselected_image
		self.selected_image = self.orig_selected_image
		
		#making the rectangle that contains the image
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
		self.continent = continent
		
		self.player = 0
		self.armies = 0
		self.min_armies = 0
		self.adjacent = []
	
	def change_colour(self):
		pixels = pygame.PixelArray(self.orig_unselected_image.copy())
		pixels.replace((0, 255, 0), self.player.colour)
		self.unselected_image = pixels.make_surface()
		self.image = self.unselected_image
		
		pixels = pygame.PixelArray(self.orig_selected_image.copy())
		pixels.replace((0, 255, 0), self.player.colour)
		self.selected_image =  pixels.make_surface()
		
	
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
	
	def draw_armies(self, window): #draws the number of armies currently in this region
		
		font = Region.font
		text_surface = font.render(str(self.armies), False, BLACK)
		text_rect = text_surface.get_rect()
		text_rect.topleft = (self.rect.centerx+self.xoffset, self.rect.centery+self.yoffset)
		window.blit(text_surface, text_rect)
	
	def path(self, player, target, visited=[], level=0):
		
		
	
		if(level > 43 or self.player != player):
			return False
		
		# print(self.name)
		# for a in self.adjacent:
		# 	print("______", a.name)
		# 
		# for v in visited:
		# 	print("______________", v.name)
		# time.sleep(0.1)
		
		if(target in self.adjacent):
			return True
		else:
			
			visited.append(self)
			not_visited = list(set(self.adjacent) - set(visited)) #so as to not visit the same region twice
			
			level += 1
			
			for r in not_visited:
				connected = r.path(player, target, visited, level)
				if(connected):
					return True
			return False



class Dice(pygame.sprite.Sprite):
	d1 = pygame.image.load(os.path.join(img_folder, "dice1.png")).convert_alpha()
	d2 = pygame.image.load(os.path.join(img_folder, "dice2.png")).convert_alpha()
	d3 = pygame.image.load(os.path.join(img_folder, "dice3.png")).convert_alpha()
	d4 = pygame.image.load(os.path.join(img_folder, "dice4.png")).convert_alpha()
	d5 = pygame.image.load(os.path.join(img_folder, "dice5.png")).convert_alpha()
	d6 = pygame.image.load(os.path.join(img_folder, "dice6.png")).convert_alpha()
	
	images = [d1, d2, d3, d4, d5, d6]
	
	BLUE = (0, 0, 255)
	RED = (255, 0, 0,)
	
	positions = [[WIDTH/2], [(WIDTH/2)-60, (WIDTH/2)+60], [(WIDTH/2)-110, (WIDTH/2), (WIDTH/2)+110]]
	#1 dice(1st dice), 2 dice(1st dice, 2nd dice), 3 dice(1st dice, 2nd dice, 3rd dice) # X position only
	
	
	
	def __init__(self, colour, number, xpos):#xpos : (number of dice, which dice this is (left, middle, right))
		pygame.sprite.Sprite.__init__(self)
		if(colour == "red"):
			self.colour = Dice.RED
			y = HEIGHT/2 - 60
		else:
			self.colour = Dice.BLUE
			y = HEIGHT/2 + 60
		
		x = Dice.positions[xpos[0]][xpos[1]]
		
		self.orig_image = Dice.images[number-1].copy()
		pixels = pygame.PixelArray(self.orig_image)
		pixels.replace((255, 255, 255), self.colour)
		self.image = pixels.make_surface()
		
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)



class Card(pygame.sprite.Sprite):
	card_size = (50, 75)
	infantry_img = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, "infantry.png")).convert_alpha(), card_size)
	artillery_img = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, "artillery.png")).convert_alpha(), card_size)
	cavalry_img = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, "cavalry.png")).convert_alpha(), card_size)
	
	positions = [(40,  HEIGHT-250), (100,  HEIGHT-250), (160,  HEIGHT-250), (80,  HEIGHT-150), (140,  HEIGHT-150)]
	
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		
		self.type = random.choice(["infantry", "artillery", "cavalry"])
		
		if(self.type == "infantry"):
			self.image = Card.infantry_img
		elif(self.type == "artillery"):
			self.image = Card.artillery_img
		else:
			self.image = Card.cavalry_img
		
		self.rect = self.image.get_rect()



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
	
	eastern_US = Region("eastern_US.png", "Eastern United States", 0.17685714285714287, 0.31142857142857144, 0, 13, "North America")
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



#randomly distribute regions to players
def distribute(players, Regions):
	
	regs = []
	for r in Regions:
		regs.append(r)
	
	random.shuffle(regs)
	
	i = 0
	for r in regs:
		# if(i < 41):
		# 	r.player = players[0]
		# 	r.change_colour()
		# 	players[0].num_regions += 1
		# else:
		# 	r.player = players[1]
		# 	r.change_colour()
		# 	players[1].num_regions += 1
		r.player = players[i % len(players)]
		r.change_colour()
		players[i % len(players)].num_regions += 1
		i+=1

	
#create player list and region list
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


#deploy armies
def deploy(player, Sprites, Regions, cursor):
	global window
	global background
	
	redeemable = player.redeemable() #number of armies player can redeem their cards for
	
	if(len(player.cards) >= 5): #players cards are automatically redeemed if player has 5 cards
		player.armies_left += redeemable
		player.redeem_cards(redeemable)
		redeemed = redeemable
		redeemable = 0
	else:
		redeemed = 0
	
	
	Buttons = pygame.sprite.Group()
	if(redeemable > 0):
		redeem = Button("Redeem", 150, HEIGHT-50)
		Buttons.add(redeem)
	
	
	i=0 #add player cards to a sprite group to be drawn
	Cards = pygame.sprite.Group()
	for c in player.cards:
		c.rect.center = Card.positions[i]
		Cards.add(c)
		i+=1
	
	
	CLICK = False
	LEFT = 1
	RIGHT = 3 #mouse buttons
	
	
	for r in Regions: #player cannot remove armies from regions that already have armies
		r.min_armies = r.armies
	
	running = True
	
	while(running):
		clock.tick(MAX_FPS)
		
		
		
		for r in Regions:
			r.check_hover(cursor)
		
		
		if(player.armies_left <= 0):
			running = False
		
		key_state = pygame.key.get_pressed()
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT: 
				#running = False
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				CLICK = True
			elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:#detect which region is being clicked
				CLICK = False
				for r in Regions:
					if(r.selected and r.player == player):
						if(key_state[K_LCTRL]):
							if(player.armies_left > 5):
								r.armies += 5
								player.armies_left -= 5
							else:
								r.armies += player.armies_left
								player.armies_left = 0
							
						else:
							r.armies += 1
							player.armies_left -= 1
						
			elif event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT:
				CLICK = False
				for r in Regions:
					if(r.selected and r.player == player and r.armies > r.min_armies):
						if(key_state[K_LCTRL]):
							if(r.armies - r.min_armies > 5):
								r.armies -= 5
								player.armies_left += 5
							else:
								player.armies_left += (r.armies - r.min_armies)
								r.armies = r.min_armies
								
							
						else:
							r.armies -= 1
							player.armies_left += 1
		
		if(redeemable > 0):
			if(redeem.check_clicked(cursor, CLICK)):
				Buttons.empty()
				player.armies_left += redeemable
				player.redeem_cards(redeemable)
				redeemed = redeemable
				redeemable = 0
				Cards.empty()
				i=0
				for c in player.cards:
					c.rect.center = Card.positions[i]
					Cards.add(c)
					i+=1
		
		Regions.update()
		Buttons.update()
		Sprites.update()
		
		
		window.fill(SEA_COLOUR)
		window.blit(background, (0, 0)) #map with just the borders of each region makes the map looks cleaner + names and bridges
		
		
		Sprites.draw(window)
		Buttons.draw(window)
		Cards.draw(window)
		
		
		
		
		draw_text(window, str(clock.get_fps()//1), 30, WIDTH-100, 20, BLACK)
		
		if(redeemed > 0):
			draw_text(window, ("Your cards have been"), 20, 10, HEIGHT-80, BLACK)
			draw_text(window, ("redeemed for " + str(redeemed) + " armies"), 20, 10, HEIGHT-50, BLACK)
		
		message = "Player " + str(player.number) + " you have " + str(player.armies_left) + " armies left to deploy"
		draw_text_outlined( message, 20, 500, HEIGHT-50, player.colour)
		
		for r in Regions:
			r.draw_armies(window)
		
		for b in Buttons:
			b.draw_button_text(window)
		
		pygame.display.flip()
	
	
	
#determine how many reinforcements the player is owed
def reinforcements(player, Sprites, Regions, cursor): 
	N_america = 5
	S_america = 2
	Europe = 5
	Africa = 3
	Asia = 7
	Australia = 2
	
	for reg in Regions:
		if (reg.continent == "North America" and reg.player != player):
			N_america = 0
		elif (reg.continent == "South America" and reg.player != player):
			S_america = 0
		elif (reg.continent == "Europe" and reg.player != player):
			Europe = 0
		elif (reg.continent == "Africa" and reg.player != player):
			Africa = 0
		elif (reg.continent == "Asia" and reg.player != player):
			Asia = 0
		elif (reg.continent == "Australia" and reg.player != player):
			Australia = 0
	
	region_reinforecements = (player.num_regions // 3)
	
	if(region_reinforecements < 3):
		region_reinforecements = 3
	
	
	player.armies_left = N_america + S_america + Europe + Africa + Asia + Australia + region_reinforecements
	deploy(player, Sprites, Regions, cursor)




def attack(player, Sprites, Regions, cursor, num_att_armies, num_def_armies, def_region, def_player, att_region, conquered, players):
	global window
	global background
	
	if(num_att_armies > att_region.armies-1): #should not happen but just in case
		choose_attack(player, Sprites, Regions, cursor, window, None, None, 0, players)
		return
	
	
	
	Buttons = pygame.sprite.Group()
	next = Button("Next", WIDTH-300, HEIGHT-50)
	Buttons.add(next)
	
	Dice_group = pygame.sprite.Group()
	result, att_dice, def_dice = dice(num_att_armies, num_def_armies)
	
	for i in range(len(att_dice)):
		d = Dice("red", att_dice[i], (len(att_dice)-1, i))
		Dice_group.add(d)
	
	for i in range(len(def_dice)):
		d = Dice("blue", def_dice[i], (len(def_dice)-1, i))
		Dice_group.add(d)
	
	if(result):
		winner_number = player.number
		winner_colour = player.colour
		def_region.armies -= 1
	else:
		winner_number = def_player.number
		winner_colour = def_player.colour
		att_region.armies -=1
	
	if(def_region.armies == 0):
		conquered = True
		def_region.player = player
		def_region.change_colour()
		player.num_regions += 1
		def_player.num_regions -= 1
		def_region.armies = num_att_armies
		att_region.armies -= num_att_armies
		def_region.change_colour()
	
	CLICK = False
	running = True

	while(running):
		clock.tick(MAX_FPS)
		
		for r in Regions:
			r.check_hover(cursor)
		
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				#running = False
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				CLICK = True
			elif event.type == pygame.MOUSEBUTTONUP:
				CLICK = False
		
		
		
		if(next.check_clicked(cursor, CLICK)): #find out how to recall the choose attack function
			if(def_region.player == player): #player conquered the region
				#print(1)
				choose_attack(player, Sprites, Regions, cursor, None, None, 0, conquered, players)
				return 
				
			else:
				#print ("attack armies: ", num_att_armies, ",   total attack region armies left: ", att_region.armies)
				
				if(att_region.armies == 1): #only 1 army is left on the region, the player can no longer attack from here
					# print(2)
					choose_attack(player, Sprites, Regions, cursor, None, None, 0, conquered, players)
					return 
				
				elif(num_att_armies == att_region.armies-1 and result): #player attacked with all possible armies and won
					# print(3)
					choose_attack(player, Sprites, Regions, cursor, att_region, def_region, num_att_armies, conquered, players)
					return 
					
				elif(num_att_armies == att_region.armies and not result): #player attacked with all possible armies and lost
					# print(4
					choose_attack(player, Sprites, Regions, cursor, att_region, def_region, num_att_armies-1, conquered, players)
					return
				
				elif(num_att_armies <= att_region.armies-1): #player attacked with x armies  x < max_armies , the player can attack with the same number
					# print(5)
					choose_attack(player, Sprites, Regions, cursor, att_region, def_region, num_att_armies, conquered, players)
					return
				
				else:
					# print(6, num_att_armies, attack.armies)
					return choose_attack(player, Sprites, Regions, cursor, None, None, 0, conquered, players)
		
		
		Regions.update()
		Sprites.update()
		Buttons.update()
		
		window.fill(SEA_COLOUR)
		window.blit(background, (0, 0))
		
		Sprites.draw(window)
		Buttons.draw(window)
		
		for r in Regions:
			r.draw_armies(window)
		
		Dice_group.draw(window)
		
		
		
		draw_text(window, str(clock.get_fps()//1), 30, WIDTH-100, 20, BLACK)
		draw_text_outlined("Player " + str(winner_number) + " wins!", 20, 500, HEIGHT-50, winner_colour)
		
		
		
		for b in Buttons:
			b.draw_button_text(window)
		
		
		pygame.display.flip()



#choose region to attack, from where, with x number of armies
def choose_attack(player, Sprites, Regions, cursor, arg_attackers, arg_defenders, arg_num_armies, conquered, players):
	global window
	global background
	
	for p in players:
		if (p.num_regions <= 0):#check if any players have lost (have no regions left)
			p.lose(cursor)
			players.remove(p)
			if(len(players) == 1):
				players[0].win(cursor)
				return
	
	
	
	Buttons = pygame.sprite.Group()
	end_turn = Button("Done", 150, HEIGHT-50)
	up = Button("+", 900, 560, (50, 50, 30))
	down = Button("-", 900, 660, (50, 50, 30))
	attack_button = Button("Attack", WIDTH-150, HEIGHT-50)
	
	Buttons.add(attack_button)
	Buttons.add(end_turn)
	Buttons.add(up)
	Buttons.add(down)


	CLICK = False	
	attackers = arg_attackers
	defenders = arg_defenders
	num_armies = arg_num_armies
	
	
	running = True

	while(running):
		clock.tick(MAX_FPS)
		
		
		# print(pygame.mouse.get_pos())
		
		for r in Regions:
			r.check_hover(cursor)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				#running = False
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				CLICK = True
			elif event.type == pygame.MOUSEBUTTONUP:
				CLICK = False
				for r in Regions: #choose attacking and defending regions
					if(r.selected):
						if(r.player == player):
							if(r.armies > 1):
								if(defenders == None or defenders in r.adjacent):
									attackers = r
									num_armies = r.armies-1
								else:
									attackers = r
									num_armies = r.armies-1
									defenders = None
						else:
							if(attackers == None or attackers in r.adjacent):
								defenders = r
							else:
								defenders = r
								attackers = None
		
		
		
		#important to have mouse click as arg
		if(up.check_clicked(cursor, CLICK) and attackers != None):
			if(num_armies < attackers.armies-1):
				num_armies+=1
		
		if(down.check_clicked(cursor, CLICK) and attackers != None):
			if(num_armies > 1):
				num_armies-=1
		
		if(end_turn.check_clicked(cursor, CLICK)):
			if(conquered):
				c = Card()
				player.cards.append(c)
			redeploy(player, Sprites, Regions, cursor)
			return
		
		if(attack_button.check_clicked(cursor, CLICK) and attackers != None and defenders != None):
			attack(player, Sprites, Regions, cursor, num_armies, defenders.armies, defenders, defenders.player, attackers, conquered, players)
			return
			
		
		Regions.update()
		Buttons.update()
		Sprites.update()
		
		
		window.fill(SEA_COLOUR)
		window.blit(background, (0, 0)) #map with just the borders of each region makes the map looks cleaner + names and bridges
		
		
		Sprites.draw(window)
		Buttons.draw(window)
		
		
		draw_text(window, str(clock.get_fps()//1), 30, WIDTH-100, 20, BLACK)
		
		draw_text_outlined("Player " + str(player.number) + " choose your attack", 20, 400, 575, player.colour)
		
		if (attackers == None):
			draw_text(window, "Attacking Region: ", 20, 400, 620, BLACK)
			draw_text(window, "_", 30, 892, 595, BLACK)
		else:
			draw_text(window, "Attacking Region: " + attackers.name, 20, 400, 620, BLACK)
			if(num_armies > 1):
				draw_text(window, str(num_armies) + " armies", 30, 892, 595, BLACK)
			else:
				draw_text(window, str(num_armies) + " army", 30, 892, 595, BLACK)
		
		
		if (defenders == None):
			draw_text(window, "Defending Region: ", 20, 400, 670, BLACK)
		else:
			draw_text(window, "Defending Region: " + defenders.name, 20, 400, 670, BLACK)
		
		
		for r in Regions:
			r.draw_armies(window)
		
		for b in Buttons:
			b.draw_button_text(window)
		
		
		pygame.display.flip()



def redeploy(player, Sprites, Regions, cursor):
	global window
	global background
	
	
	
	Buttons = pygame.sprite.Group()
	up = Button("+", 900, 560, (50, 50, 30))
	down = Button("-", 900, 660, (50, 50, 30))
	move = Button("Move/End Turn", WIDTH-150, HEIGHT-50, (200, 50, 20))
	switch = Button("Switch", 450, 655, (110, 30, 20))
	
	Buttons.add(move)
	Buttons.add(up)
	Buttons.add(down)
	Buttons.add(switch)
	
	from_region = None
	to_region = None
	num_armies = 0
	
	CLICK = False
	LEFT = 1
	RIGHT = 3 #mouse buttons
	
	running = True

	while(running):
		clock.tick(MAX_FPS)
		
		
		for r in Regions:
			r.check_hover(cursor)
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT: 
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					CLICK = True
				
				elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:#detect which region is being clicked
					CLICK = False
					for r in Regions:
						if(r.selected and r.player == player):
							if(to_region != None and r.armies > 1 and to_region.path(player, r, [])):#to_region is chosen and path exists with the selected region
								from_region = r
								num_armies = from_region.armies-1
								# print(1)
							elif(to_region != None and r.armies > 1 and not to_region.path(player, r, [])):#to_region is chosen but no path exists with the selected region
								from_region = r
								num_armies = from_region.armies-1
								to_region = None
								# print(2)
							elif(to_region == None and r.armies > 1):#to_region is not chosen
								from_region = r
								num_armies = from_region.armies-1
								# print(3)
						
				elif event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT:
					CLICK = False
					for r in Regions:
						if(r.selected and r.player == player):
							if(from_region != None and from_region.path(player, r, [])):#from_region is chosen and path exists with the selected region
								to_region = r
								# print(4)
							elif(from_region != None and not from_region.path(player, r, [])):#from_region is chosen but no path exists with the selected region
								to_region = r
								from_region = None
								# print(5)
							elif(from_region == None):#from_region is not chosen
								to_region = r
								# print(6)
		
		
		if(up.check_clicked(cursor, CLICK) and from_region != None):
			if(num_armies < from_region.armies-1):
				num_armies+=1
		
		if(down.check_clicked(cursor, CLICK) and from_region != None):
			if(num_armies > 1):
				num_armies-=1
		
		if(switch.check_clicked(cursor, CLICK)):
			if(to_region.armies > 1):
				temp = from_region
				from_region = to_region
				num_armies = from_region.armies-1
				to_region = temp
		
		if(move.check_clicked(cursor, CLICK)):
			if(to_region != None and from_region != None):
				from_region.armies -= num_armies
				to_region.armies += num_armies
			return
		
		
		Regions.update()
		Buttons.update()
		Sprites.update()
		
		
		window.fill(SEA_COLOUR)
		window.blit(background, (0, 0)) #map with just the borders of each region makes the map looks cleaner + names and bridges
		
		
		Sprites.draw(window)
		Buttons.draw(window)
		
		
		draw_text(window, str(clock.get_fps()//1), 30, WIDTH-100, 20, BLACK)
		
		draw_text_outlined("Player " + str(player.number) + " may move armies", 20, 400, 575, player.colour)
		
		
		
		if (from_region == None):
			draw_text(window, "From: (left click)", 20, 400, 620, BLACK)
			draw_text(window, "_", 30, 892, 595, BLACK)
		else:
			draw_text(window, "From: " + from_region.name, 20, 400, 620, BLACK)
			if(num_armies == 1):
				draw_text(window, str(num_armies) + " army", 30, 892, 595, BLACK)
			else:
				draw_text(window, str(num_armies) + " armies", 30, 892, 595, BLACK)
		
		
		if (to_region == None):
			draw_text(window, "To: (right click)", 20, 400, 670, BLACK)
		else:
			draw_text(window, "To: " + to_region.name, 20, 400, 670, BLACK)
		
		
		for r in Regions:
			r.draw_armies(window)
		
		for b in Buttons:
			b.draw_button_text(window)
		
		
		pygame.display.flip()
	
	
	


def testlevel2():
	
	turn = 0
	
	players, Regions = start(2)
	
	Sprites = Regions.copy()
	
	background = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, "name_bridge.png")).convert_alpha(), (WIDTH, HEIGHT))
	
	
	cursor = Cursor()
	Sprites.add(cursor)
		
	
	for p in players:
		deploy(p, Sprites, Regions, cursor)
	
	for p in players:
			choose_attack(p, Sprites, Regions, cursor, None, None, 0, False)
			for l in players:
				if (l.num_regions == 0):
					players.remove(l)
	
	running = True

	while(running):
		clock.tick(MAX_FPS)
		window.fill((146, 216, 228))
		
		
		
		window.blit(background, (0, 0)) #map with just the borders of each region makes the map looks cleaner + names and bridges

		for r in Regions:
			r.check_hover(cursor)
		
		
		
		for p in players:
			reinforcements(p, Sprites, Regions, cursor)
			choose_attack(p, Sprites, Regions, cursor, None, None, 0, False)
			for l in players:
				if (l.num_regions == 0):
					players.remove(l)
					if(len(players) == 1):
						#congratulate(players[0])
						return
		
		
		
		Sprites.draw(window)
		
		Regions.update()
		
		
		draw_text(window, str(clock.get_fps()//1), 30, WIDTH-100, 20, BLACK)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				running = False
			
			
		
		pygame.display.flip()
		
		Sprites.update()
		turn += 1



def testlevel3(num_players):
	
	music = random.choice(["music1.mp3", "music2.mp3", "music3.mp3"])
	
	
	pygame.mixer.music.load(os.path.join(snd_folder, music))
	pygame.mixer.music.set_volume(0.4)
	pygame.mixer.music.play(loops = -1)
	
	turn = 0
	
	players, Regions = start(num_players)
	Sprites = Regions.copy()
	
	cursor = Cursor()
	Sprites.add(cursor)
	
	
	for p in players:
		deploy(p, Sprites, Regions, cursor)
	
	for p in players:
			choose_attack(p, Sprites, Regions, cursor, None, None, 0, False, players)
			for l in players:
				if (l.num_regions == 0):
					players.remove(l)
	
	
	running = True

	while(running):#game loop
		
		
		
		for p in players:
			reinforcements(p, Sprites, Regions, cursor)
			choose_attack(p, Sprites, Regions, cursor, None, None, 0, False, players)
		turn += 1


	
testlevel3(2)














