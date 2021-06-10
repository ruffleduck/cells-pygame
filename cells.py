from text import Text
import random
import pygame
import json
import math
import time

pygame.init()

# Constants
P1_NAME = ''
P2_NAME = ''

P1_IMG = None
P2_IMG = None

WIDTH = 1821
HEIGHT = 925

PELLET_COUNT = 300


def distance(x1, y1, x2, y2):
    # Gets the distance between two points
    return abs(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))


class Pellet:
    min_size = 2
    max_size = 5
    mass_size = 15
    start_speed = 30
    friction = 0.8
    
    def __init__(self, cells, cell=None, xvel=None, yvel=None):
        if cell == None:
            # Get random coordinates
            self.get_coords()
            while self.in_cell(cells):
                self.get_coords()

            # Set color and mass attributes
            self.color = random.choice(colors['colors'])
            min = Pellet.min_size
            max = Pellet.max_size
            self.mass = random.random() * (max - min) + min
            
            self.sliding = False
            self.large = False
        else:
            # Set coordinates
            self.x = cell.x + (xvel * cell.mass)
            self.y = cell.y + (yvel * cell.mass)

            # Set color and mass attributes
            self.color = cell.color
            self.mass = Pellet.mass_size
            
            self.sliding = True
            self.large = True

            # Set sliding properties
            self.split_direction = [xvel, yvel]
            self.speed = Pellet.start_speed

    def in_cell(self, cells):
        for cell in cells:
            if distance(cell.x, cell.y, self.x, self.y) < cell.mass:
                return True
        return False

    def get_coords(self):
        self.x = random.randint(Pellet.max_size, WIDTH - Pellet.max_size)
        self.y = random.randint(Pellet.max_size, HEIGHT - Pellet.max_size)

    def render(self):
        rect = False

        # Renders the pellet
        size = math.ceil(self.mass * (1.5 if rect else 1))
        
        if rect:
            pygame.draw.rect(screen, self.color, (self.x, self.y, size, size))
        else:
            pygame.draw.circle(screen, self.color, (math.ceil(self.x), math.ceil(self.y)), size)

        self.check()

    def check(self):
        # Makes sure the pellet isn't off screen.
        # This fixes a minor glitch with large pellets.
        if self.x + self.mass > WIDTH:
            self.x = WIDTH - self.mass
        if self.x - self.mass < 0:
            self.x = self.mass
        if self.y + self.mass > HEIGHT:
            self.y = HEIGHT - self.mass
        if self.y - self.mass < 0:
            self.y = self.mass

    def slide(self):
        if self.sliding:
            # Slides the pellet
            self.x += self.split_direction[0] * self.speed
            self.y += self.split_direction[1] * self.speed

            self.speed *= Pellet.friction

            # Bounces the pellet if it is colliding with an edge
            if self.x + self.mass > WIDTH or self.x - (self.mass * 2) < 0:
                self.split_direction[0] *= -1
            if self.y + self.mass > HEIGHT or self.y - (self.mass * 2) < 0:
                self.split_direction[1] *= -1

            if self.speed < 0.3:
                self.sliding = False


class JoystickError(Exception):
    pass


class Cell:
    starting_mass = 50
    start_speed = 55
    friction = 0.8
    tag = 0
    
    def __init__(self, joystick, name, other=None, xvel=None, yvel=None, img=None):
        self.joystick = joystick
        self.name = name

        self.id = Cell.tag
        Cell.tag += 1

        self.xvel = 0
        self.yvel = 0

        self.last_did_action = time.time()

        if other == None:
            # Choose a random position for the cell
            self.get_pos()
            while self.close(cells):
                self.get_pos()

            # Set color and mass attributes
            self.color = random.choice(colors['colors'])
            self.mass = Cell.starting_mass

            self.sliding = False

            self.img = img
        else:
            # If the new cell being created is split from another
            # cell, fill in the information from the old cell.

            self.x = other.x + (xvel * other.mass)
            self.y = other.y + (yvel * other.mass)
 
            self.color = other.color
            self.mass = other.mass
            self.img = other.img

            # Set sliding properties
            self.sliding = True
            self.split_direction = [xvel, yvel]
            self.speed = Cell.start_speed
            self.end_speed = (70 / other.mass)

    def close(self, cells):
        for cell in cells:
            cell_distance = distance(cell.x, cell.y, self.x, self.y)
            if cell_distance < Cell.starting_mass * 2 + 30:
                return True
        return False

    def get_pos(self):
        self.x = random.randint(Cell.starting_mass, WIDTH - Cell.starting_mass)
        self.y = random.randint(Cell.starting_mass, HEIGHT - Cell.starting_mass)

    def render(self):
        if self.img == None:
            # Renders the main circle
            pygame.draw.circle(screen, self.color, (math.ceil(self.x), math.ceil(self.y)), math.ceil(self.mass))
        else:
            # Renders the image
            img = pygame.transform.scale(self.img, [math.ceil(self.mass) * 2, math.ceil(self.mass) * 2])
            screen.blit(img, [math.ceil(self.x - self.mass), math.ceil(self.y - self.mass)])
        
        # Sets up the text
        font = pygame.font.Font('assets/8bitFontBold.ttf', math.ceil(self.mass / 3))
        text = Text(font, (self.x, self.y), self.name,
                    color=colors['white'], center=True)

        # Renders the text
        text.render(screen)

    def move(self, xvel, yvel):
        if self.sliding:
            # Slides the cell
            self.x += self.split_direction[0] * self.speed
            self.y += self.split_direction[1] * self.speed

            self.speed *= Cell.friction

            # Bounces the pellet if it is colliding with an edge
            if self.x + self.mass > WIDTH or self.x - self.mass < 0:
                self.split_direction[0] *= -1
            if self.y + self.mass > HEIGHT or self.y - self.mass < 0:
                self.split_direction[1] *= -1

            if self.speed <= self.end_speed:
                self.sliding = False
        else:
            self.xvel = xvel
            self.yvel = yvel

            # Moves the cell. Size may affect the size.
            self.x += xvel * (200 / self.mass)
            self.y += yvel * (200 / self.mass)

    def check(self):
        # Makes sure you won't go off edges
        if self.x + self.mass > WIDTH:
            self.x = WIDTH - self.mass
        if self.x - self.mass < 0:
            self.x = self.mass
        if self.y + self.mass > HEIGHT:
            self.y = HEIGHT - self.mass
        if self.y - self.mass < 0:
            self.y = self.mass

    def split(self):
        # Splits, and returns the new split cell
        self.mass = math.floor(self.mass / 2)
        if self.sliding:
            return Cell(self.joystick, self.name,
                        other=self, xvel=self.split_direction[0],
                        yvel=self.split_direction[1])
        return Cell(self.joystick, self.name,
                    other=self, xvel=self.xvel,
                    yvel=self.yvel)

    def eat(self, cell):
        large_enough = cell.mass <= self.mass
        covering = distance(self.x, self.y, cell.x, cell.y) <= self.mass - cell.mass
        # mass = cell.mass if cell.joystick == self.joystick else math.ceil(cell.mass / 3)

        if self.joystick == cell.joystick:
            covering = distance(self.x, self.y, cell.x, cell.y) <= self.mass - cell.mass + (cell.mass / 10)
            large_enough = True
        
        # If the cell is edible and it is covered, return True and gain its mass.
        # Otherwise, return False.
        if large_enough and covering:
            self.mass += cell.mass
            self.check()
            if cell_count(cell.joystick) <= 0:
                joysticks.remove(cell.joystick)
            return True
        else:
            return False

    def multiply_vel(self, vel):
        # Use to increase/decrease player velocity
        self.xvel *= vel
        self.yvel *= vel

    def __lt__(self, other):
        return self.mass < other.mass


def cell_count(joystick):
    # Gets the amount of cells a player hass
    res = 0
    for cell in cells:
        if cell.joystick == joystick:
            res += 1
    return res


def play_cell(cell, i):
    # Moves the cell
    cell.move(cell.joystick.get_axis(0), cell.joystick.get_axis(1))
    cell.check()

    # Checks to see if the cell ate any other cells
    for i, other in enumerate(cells):
        if other.id != cell.id:
            if cell.eat(other):
                cells.remove(other)

    # Checks to see if the cell ate a pellet
    for j, pellet in enumerate(pellets):
        if distance(cell.x, cell.y, pellet.x, pellet.y) < cell.mass + pellet.mass:
            del pellets[j]
            cell.mass += pellet.mass / 8
            pellets.append(Pellet(cells))

    cell.render()


def do_action(joystick, action):
    split = action == 'split'
    double_split = action == 'double_split'
    mass = action == 'mass'
    temp = cells[:]
    for cell in sorted(temp)[::-1]:
        action_paused = time.time() - cell.last_did_action > 0.2
        
        # Split
        if cell.joystick == joystick and (split or double_split) and action_paused:
            if cell.mass >= (20 if split else 40) and cell_count(cell.joystick) <= 10:
                if split:
                    cells.append(cell.split())
                else:
                    cell.multiply_vel(2)
                    cells.append(cell.split())
                    cell.multiply_vel(-0.5)
                    cells.append(cell.split())
                    cell.multiply_vel(-1)
                cell.last_did_action = time.time()
        
        # Give out mass
        if cell.joystick == joystick and mass and action_paused:
            if cell.mass >= 20:
                del pellets[0]
                cell.mass -= Pellet.mass_size / 8
                pellets.append(Pellet(cells, cell=cell, xvel=cell.xvel, yvel=cell.yvel))
                cell.last_did_action = time.time()


def get_name(joystick):
    # Gets a player's name
    for cell in cells:
        if cell.joystick == joystick:
            if cell.name == '':
                return "Cell " + str(joysticks.index(cell.joystick) + 1) 
            return cell.name


def get_score(joystick):
    # Gets a player's score
    score = 0
    for cell in cells:
        if cell.joystick == joystick:
            score += cell.mass
    return score * 10


def render_scores():
    # Render the scores
    font_color = 'white' if dark_theme else 'black'
    y = 20
    for joystick in joysticks:
        string_text = "%s's Score: %i" % (get_name(joystick), get_score(joystick))
        text = Text(score_font, (20, y), string_text, color=colors[font_color])
        # If the player wasn't found, don't render the score
        if get_name(joystick) != None:
            text.render(screen)
            y += 30


def setup_cells(joysticks):
    global cells

    # Sets up the cells
    cells = []
    for i in range(len(joysticks)):
        name = eval('P' + str(i + 1) + '_NAME')
        img = eval('P' + str(i + 1) + '_IMG')
        if img == None:
            cell_img = None
        else:
            cell_img = pygame.image.load(img)
        cells.append(Cell(joysticks[i], name, img=cell_img))


def setup_joysticks():
    global joysticks

    # Sets up the joysticks
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        joysticks.append(pygame.joystick.Joystick(i))
        joysticks[-1].init()


def pause():
    global paused, pause_time

    # Pauses/unpauses game
    paused = True if not paused else False

    # Resumes/pauses music
    if paused:
        pause_time = time.time()
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()


def render_paused():
    # Render the paused text
    font_color = 'white' if dark_theme else 'black'
    text = Text(paused_font, (WIDTH // 2, HEIGHT // 2), "Paused",
                color=colors[font_color], center=True)
    text.render(screen)


def render_countdown():
    # Render the countdown
    countdown_text = Text(countdown_font, [WIDTH // 2, HEIGHT // 2 + 60],
                          "Reset in %i seconds..." % (4 - int(hold_time)),
                          color=colors['white' if dark_theme else 'black'],
                          center=True)
    countdown_text.render(screen)


def reset():
    global cells, pellets, paused
    global pause_button_down, pause_time
    
    # Makes sure there's joysticks plugged in
    if pygame.joystick.get_count() == 0:
        pygame.quit()
        raise JoystickError("No joysticks detected.")

    setup_joysticks()

    # Setup cells and pellets
    setup_cells(joysticks)
    pellets = [Pellet(cells) for _ in range(PELLET_COUNT)]

    paused = False
    pause_button_down = False
    pause_time = 0

    # Start the music
    pygame.mixer.music.unpause()
    pygame.mixer.music.play(-1)


# Sets up the window
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Cells %s' % open('version.txt').read().strip())

dark_theme = False

colors = json.load(open('colors.json'))

# Sets up the fonts
score_font = pygame.font.Font('assets/8bitFontBold.ttf', 26)
paused_font = pygame.font.Font('assets/8bitFontBold.ttf', 48)
countdown_font = pygame.font.Font('assets/8bitFontBold.ttf', 32)

# Player controls
controls = {
    6: 'split',
    8: 'double_split',
    7: 'mass',
    9: 'pause',
    4: 'dark_theme',
    5: 'light_theme'
}

# Load background music
music = pygame.mixer.music.load('assets/cells.wav')

reset()

# Game loop
done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        
        if event.type == pygame.JOYBUTTONDOWN:
            try:
                button_down = controls[event.button] == 'pause'
            except KeyError:
                button_down = False

            # If dark theme is toggled, activate it
            if controls[event.button] == 'dark_theme':
                dark_theme = True

            # If light theme is toggled, activate it
            if controls[event.button] == 'light_theme':
                dark_theme = False

            # If the pause button is pressed, pause/unpause game
            if button_down:
                pause_button_down = True
                pause()

        if event.type == pygame.JOYBUTTONUP:
            try:
                button_up = controls[event.button] == 'pause' 
            except KeyError:
                button_up = False

            if button_up:
                pause_button_down = False

    screen.fill(colors['black' if dark_theme else 'white'])

    if paused:
        render_paused()
    else:
        # Render and move pellets
        for pellet in pellets:
            pellet.render()
            pellet.slide()

        # Render and move cells
        for i, cell in enumerate(sorted(cells)):
            play_cell(cell, i)

    # Watch for joystick input
    for joystick in joysticks:
        for button in range(joystick.get_numbuttons()):
            if joystick.get_button(button) and button in controls:
                do_action(joystick, controls[button])

    # If the pause button is being held, show a countdown.
    # Hold it even longer, the game will reset.
    hold_time = time.time() - pause_time
    if pause_button_down and hold_time > 4 and paused:
        reset()
    elif pause_button_down and hold_time > 1 and paused:
        render_countdown()

    render_scores()

    pygame.display.update()

pygame.quit()
