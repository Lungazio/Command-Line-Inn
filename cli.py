import os
import time
from pynput import keyboard
import random
from colorama import init, Fore, Style, Back
import string
import sys
import select
import openai
import readline
import termios
import tty
import shutil
from dotenv import load_dotenv
load_dotenv()

BEER_MUG_ASCII_ART = r"""
  .   *   ..  . *  *
*  * @()Ooc()*   o  .
    (Q@*0CG*G*OO()  ___
   |\____________/|/ _ \
   |   |  |   |  | / | |
   |   |  |   |  | | | |
   |   |  |   |  | | | |
   |   |  |   |  | | | |
   |   |  |   |  | | | |
   |   |  |   |  | \_| |
   |   |  |   |  |\___/
   |\_ |__|___|_/|
    \___________/
    
"""

PERSON_ASCII = r"""
                ▒▒▒▒▒▒▒▒▒
             ▒▒▒▒▒▒▒▒▒▒▒▒▒▒
         ░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░ 
         ▒▒▒▒▒▒▒▒░░░░░░▒▒▒▒▒▒▒▒                     
         ▒▒▒▒░░░░░░░░░░░░░░▒▒▒▒ 
        ▒▒▒▒░░░░    ░░    ░░░░▒▒▒▒                    
    ░░░░▒▒▒▒░░░░    ░░    ░░░░▒▒▒▒
        ▒▒▒▒░░░░░░░░░░░░░░░░░░▒▒▒▒
    ░░░░▒▒▒▒░░░░░░░░░░░░░░░░░░▒▒▒▒          
    ░░░░▒▒▒▒▒▒░░░░░░░░░░░░░░▒▒▒▒▒▒
        ▒▒▒▒▒▒▒▒░░░░░░▒▒▒▒▒▒▒▒░░ 
            ▒▒▒▒▒▒▒▒▒▒▒▒▒▒   
          ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒         
        ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░
   ░░░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
       ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
"""
openai.api_key = os.getenv("OPENAI_API_KEY")
# Initialize colorama
init()
# Define custom colors
BROWN = '\x1b[38;2;139;69;19m'
GRAY = '\x1b[38;2;128;128;128m'
DARK_YELLOW = '\x1b[38;2;204;204;0m'
BRIGHT_YELLOW = '\x1b[38;2;255;255;0m'
# Define constants
PLAYER_ICON = '@'
EMPTY_SPACE = ' '
WALL_ICON = '#'
BAR_ICON = '|'
TABLE_ICON = '■'
DOOR_ICON = '-'
GATE_ICON = ']'
BARKEEPER= 'Ɓ'
FIREPLACE_ICONS = ['a', '&']
LIGHTING_ICONS = ['=', '≡']
LIGHTING_COLOR = Fore.YELLOW

# Define the list of available colors
AVAILABLE_COLORS = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.MAGENTA, Fore.YELLOW, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTYELLOW_EX]

# Create a list of all uppercase letters from A to Z
letters = list(string.ascii_uppercase)

# Shuffle the available colors
random.shuffle(AVAILABLE_COLORS)

# Create a dictionary of characters with a random color assigned to each letter
CHARACTERS = {letter: AVAILABLE_COLORS[i % len(AVAILABLE_COLORS)] for i, letter in enumerate(letters)}

# Update the colors in the code
PLAYER_COLOR = Fore.GREEN
WALL_COLOR = Fore.LIGHTBLACK_EX
BAR_COLOR = Fore.WHITE
TABLE_COLOR = Fore.WHITE
FIREPLACE_COLOR = Fore.RED
BARKEEPER_COLOR = Fore.RED
DEFAULT_COLOR = Fore.WHITE
GATE_COLOR = Fore.WHITE



def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def loading_message(character_name, action):
    print("\n" + f"{character_name}: *{action}*", end="")
    for i in range(2):
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(0.5)




def place_characters_around_table(table_position):
    """Place a random number of characters around the table icon at the given position."""
    table_x, table_y = table_position
    table_neighbors = [(table_x, table_y - 1), (table_x - 1, table_y), (table_x + 1, table_y), (table_x, table_y + 1)]
    available_spaces = [neighbor for neighbor in table_neighbors if game_state['tavern_layout'][neighbor[1]][neighbor[0]] == EMPTY_SPACE]
    if not available_spaces:
        return
    placed_characters = []
    for row in game_state['tavern_layout']:
        for cell in row:
            if isinstance(cell, tuple) and cell[0] in CHARACTERS:
                placed_characters.append(cell[0])
    num_characters = random.choices([0, 1, 2, 3, 4], weights=[35, 30, 20, 10, 5])[0]
    for _ in range(num_characters):
        if not available_spaces:
            break
        x, y = random.choice(available_spaces)
        available_spaces.remove((x, y))
        available_letters = [l for l in CHARACTERS.keys() if l not in placed_characters]
        if available_letters:
            letter = random.choice(available_letters)
            placed_characters.append(letter)
            color = CHARACTERS[letter]
            game_state['tavern_layout'][y][x] = (letter, color)



# Define the initial game state
game_state = {
    'player_position': (1, 1),
    'lighting': [[0 for _ in range(20)] for _ in range(9)],
    'fireplace_position': (16, 7),
    'fireplace_frame': 0,
    'freeze_scene': False, 
    'awaiting_message_input': False,
    'previous_player_position': (1, 1),
    'lighting_frame': 0,
    'tavern_layout': [
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '-', '#'],
        ['#', '@', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', '■', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '■', ' ', ' ', ' ', '#'],
        ['#', ' ', '■', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '■', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '■', '#'],
        ['#', '|', '|', '|', '|', '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', '🐱 ', 'Ɓ', '','', '|',' ', ' ',' ', ' ', ' ', ' ', '■', ' ', ' ', '#', ' ', ' ', ' ', '#'],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
    ],
    'interaction_message': ''
}


def generate_fantasy_name(letter):
    prompt = f"Generate a fantasy name that starts with the letter {letter}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    name = response.choices[0].text.strip()
    return name


CHARACTER_CONVERSATION_HISTORY = {}

def generate_fantasy_dialogue(name):
    prompts = [
f"You're a gruff dwarf named {name}, sitting alone at the bar, nursing a mug of ale. When I approach you, how do you greet me?",
f"You're a charming half-elf named {name}, playing a game of cards with the other patrons. When I approach you to join the game, how do you greet me?",
f"You're a stoic human named {name}, sitting in a corner of the tavern, reading a book. When I approach you, how do you greet me?",
f"You're a mischievous halfling named {name}, sitting at the bar and eavesdropping on the other patrons' conversations. When I approach you, how do you greet me?",
f"You're a curious gnome named {name}, sitting at a table with a pile of books and scrolls. When I approach you to ask about your research, how do you greet me?",
f"You're a surly half-orc named {name}, sitting alone at a table, sharpening your weapon. When I approach you, how do you greet me?",
f"You're a flamboyant tiefling named {name}, performing a fire-dance for the other patrons. When I approach you after your performance, how do you greet me?",
f"You're a reserved elf named {name}, sitting at the bar, sipping on a glass of wine. When I approach you, how do you greet me?",
f"You're a jovial half-elf named {name}, sitting at a table, enjoying a meal with a group of friends. When I approach you, how do you greet me?",
f"You're a stoic dragonborn named {name}, keeping watch over the tavern's patrons. When I approach you, how do you greet me?",
f"You're a mysterious halfling named {name}, sitting in a dark corner of the tavern. When I approach you, how do you greet me?",
f"You're a grizzled dwarf named {name}, sitting at the bar and regaling the other patrons with tall tales. When I approach you, how do you greet me?",
f"You're a mischievous tiefling named {name}, playing pranks on the other patrons. When I confront you about it, how do you greet me?",
f"You're a dour human named {name}, sitting alone at a table, brooding. When I approach you, how do you greet me?",
f"You're a gregarious gnome named {name}, sitting at the bar, chatting with the other patrons. When I approach you, how do you greet me?",
f"You're a reserved half-elf named {name}, sitting at a table, quietly enjoying a drink. When I approach you, how do you greet me?",
f"You're a surly half-orc named {name}, sitting at a table, playing a game of darts. When I approach you to join the game, how do you greet me?",
f"You're a friendly elf named {name}, sitting at the bar, buying rounds of drinks for the other patrons. When I approach you, how do you greet me?",
f"You're a jovial dwarf named {name}, sitting at a table with a group of friends, singing bawdy songs. When I approach you, how do you greet me?",
f"You're a curious half-elf named {name}, sitting at a table, studying a map of the surrounding area. When I approach you, how do you greet me?",
f"You're a sly gnome named {name}, sitting at the bar, quietly observing the other patrons. When I approach you, how do you greet me?",
f"You're a fierce dragonborn named {name}, sitting at a table with a group of adventurers. When I approach you, how do you greet me?",
f"You're a friendly halfling named {name}, sitting at the bar and striking up conversations with the other patrons. When I approach you, how do you greet me?",
f"You're a brooding tiefling named {name}, sitting alone at a table and nursing a drink. When I approach you, how do you greet me?",
f"You're a mischievous gnome named {name}, playing pranks on the other patrons. When I confront you about it, how do you greet me?",
f"You're a stoic dwarf named {name}, sitting at the bar and keeping a watchful eye on the other patrons. When I approach you, how do you greet me?",
f"You're a curious half-elf named {name}, sitting at a table with a pile of notes and sketches. When I approach you to ask about your work, how do you greet me?",
f"You're a surly half-orc named {name}, sitting alone in a dark corner of the tavern. When I approach you, how do you greet me?",
f"You're a jovial human named {name}, sitting at the bar and buying rounds of drinks for the other patrons. When I approach you, how do you greet me?",
f"You're a flamboyant elf named {name}, performing a sword dance for the other patrons. When I approach you after your performance, how do you greet me?",
f"You're a mysterious tiefling named {name}, sitting at the bar and keeping to yourself. When I approach you, how do you greet me?",
f"You're a reserved dwarf named {name}, sitting at a table with a group of friends and enjoying a quiet drink. When I approach you, how do you greet me?",
f"You're a mischievous halfling named {name}, sitting at the bar and making witty comments to the other patrons. When I approach you, how do you greet me?",
f"You're a stoic half-elf named {name}, sitting alone at a table and watching the door. When I approach you, how do you greet me?",
f"You're a friendly gnome named {name}, sitting at the bar and striking up conversations with anyone who sits next to you. When I approach you, how do you greet me?",
f"You're a surly dragonborn named {name}, sitting alone at the bar and nursing a glass of ale. When I approach you, how do you greet me?",
f"You're a curious elf named {name}, sitting at a table with a map of the surrounding area. When I approach you to ask about it, how do you greet me?",
f"You're a jovial halfling named {name}, sitting at a table with a group of friends and telling funny stories. When I approach you, how do you greet me?",
f"You're a brooding half-orc named {name}, sitting alone at the bar and staring into your drink. When I approach you, how do you greet me?",
f"You're a flamboyant gnome named {name}, performing a juggling act for the other patrons. When I approach you after your performance, how do you greet me?"
]
    initial_prompt = random.choice(prompts).format(name=name)

    initial_dialogue = character_chat_ai_response(name, initial_prompt + 'you CANNOT assume a role of tavern staff')

    return initial_dialogue 

def character_chat_ai_response(character_name, message):
    global CHARACTER_CONVERSATION_HISTORY

    conversation_history = CHARACTER_CONVERSATION_HISTORY.get(character_name, [])
    conversation_history.append(f"You: {message}")
    prompt = "\n".join(conversation_history) + f"\n{character_name}:"

    loading_message(character_name, "Taking a sip")

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt + 'it should follow the format(*ACTION* Dialogue) DO NOT PUT THE CHARACTER NAME JUST THE DIALOGUE',
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )

        reply = response.choices[0].text.strip()
        reply_lines = reply.split('\n')
        reply = ' '.join(reply_lines)
    except Exception as e:
        print("Error:", e)
        reply = f"{character_name}: *Ignores you*"

    print("\r" + " " * (len(character_name) + len("Taking a sip") + 6), end="")  # Clear the line
    conversation_history.append(f"{character_name}: {reply}")
    CHARACTER_CONVERSATION_HISTORY[character_name] = conversation_history

    return reply

def chat_with_character(character_name, character_dialogue):
    clear_screen()
    print_chat_frame_with_person()

    print(f"{character_name}: {character_dialogue}\n")
    
    # Start a conversation with the character
    while True:
        user_message = custom_input("You: ")
        if user_message.lower() == "bye" or user_message.lower() == "goodbye" or user_message.lower() == "exit" or user_message.lower() == "see you":
            break

        character_response = character_chat_ai_response(character_name, user_message)
        print(f"\n{character_name}: {character_response}\n")


def print_chat_frame_with_beer_mug():
    print(BEER_MUG_ASCII_ART, end="")
    print("\n")

def print_chat_frame_with_person():
    print(PERSON_ASCII, end="")
    print("\n")



def custom_input(prompt):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        sys.stdout.write(prompt)
        sys.stdout.flush()
        buffer = ""
        while True:
            ch = sys.stdin.read(1)
            if ch == '\r' or ch == '\n':  # Enter key pressed
                break
            elif ord(ch) == 127:  # Backspace key pressed
                if len(buffer) > 0:
                    buffer = buffer[:-1]
                    sys.stdout.write('\b \b')  # Erase the last character from the terminal
                    sys.stdout.flush()

            else:
                buffer += ch
                sys.stdout.write(ch)  # Echo the character back to the user
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return buffer
conversation_history = [ "You are a friendly barkeeper in a tavern set in a medieval fantasy"]

def barkeeper_chat_ai_response(message):
    global conversation_history

    conversation_history.append(f"You: {message}")
    prompt = "\n".join(conversation_history) + "\nBarkeeper:"

    loading_message("Barkeeper", "Wiping Mugs")

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt +'it should follow the format(*ACTION* Dialogue) DO NOT PUT THE CHARACTER NAME JUST THE DIALOGUE',
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )

        reply = response.choices[0].text.strip()
        reply_lines = reply.split('\n')
        reply = ' '.join(reply_lines)
    except Exception as e:
        print("Error:", e)
        reply = "Barkeeper: *Appears to be busy*"

    print("\r" + " " * (len("Barkeeper") + len("Wiping Mugs") + 6), end="")
    conversation_history.append(f"Barkeeper: {reply}")

    return reply
def chat_with_barkeeper():
    clear_screen()
    print_chat_frame_with_beer_mug()

    if 'username' in game_state:
        username = game_state['username']
        print(f"Barkeeper: Welcome back, {username}! What can I get for you today?")
    else:
        username = custom_input("Barkeeper: Welcome to the Command Line Inn! What's your name? ")
        game_state['username'] = username
        print(f"\nBarkeeper: Nice to meet you, {username}! Enjoy your stay!")

    # Start a conversation with the barkeeper
    while True:
        user_message = custom_input("You: ")
        if user_message.lower() == "bye" or user_message.lower() == "goodbye" or user_message.lower() == "exit" or user_message.lower() == "see you":
            break

        barkeeper_response = barkeeper_chat_ai_response(user_message)
        print(f"\nBarkeeper: {barkeeper_response}\n")



def interact_with_character(x, y):
    player_x, player_y = game_state['player_position']

    if player_x == 4 and player_y == 5:
        game_state['freeze_scene'] = True  # Freeze the scene
        clear_screen()
        chat_with_barkeeper()
        clear_screen()
        render_game()  # Render the game again after the conversation
        game_state['freeze_scene'] = False  # Unfreeze the scene

    elif player_x == 1 and player_y == 5:
        game_state['interaction_message'] = f"Mimi: Meow Meow!"
        print(game_state['interaction_message'])
    else:
        neighbors = [(player_x + dx, player_y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        for nx, ny in neighbors:
            cell = game_state['tavern_layout'][ny][nx]
            if isinstance(cell, tuple) and cell[0] in CHARACTERS:
                game_state['freeze_scene'] = True
                icon = cell[0]
                if icon in CHARACTER_CONVERSATION_HISTORY:
                    name, dialogue = CHARACTER_CONVERSATION_HISTORY[icon][0], CHARACTER_CONVERSATION_HISTORY[icon][1]
                else:
                    name = generate_fantasy_name(icon)
                    dialogue = generate_fantasy_dialogue(name)
                    CHARACTER_CONVERSATION_HISTORY[icon] = [name, dialogue]

                  # Freeze the scene
                clear_screen()
                chat_with_character(name, dialogue)
                clear_screen()
                render_game()  # Render the game again after the conversation
                game_state['freeze_scene'] = False  # Unfreeze the scene
                break

def render_game():
    clear_screen()
    for row in game_state['tavern_layout']:
        for cell in row:
            if isinstance(cell, tuple):
                icon, color = cell
                print(color + icon, end="")
            elif cell == PLAYER_ICON:
                print(PLAYER_COLOR + cell, end="")
            elif cell == WALL_ICON:
                print(WALL_COLOR + cell, end="")
            elif cell == BARKEEPER:
                print(BARKEEPER_COLOR + cell, end="")
            elif cell == GATE_ICON:
                print(GATE_COLOR + cell, end="")
            elif cell == BAR_ICON:
                print(BAR_COLOR + cell, end="")
            elif cell == TABLE_ICON:
                print(TABLE_COLOR + cell, end="")
            elif cell in FIREPLACE_ICONS:
                print(FIREPLACE_COLOR + cell, end="")
            elif cell in CHARACTERS:
                print(CHARACTERS[cell] + cell, end="")
            else:
                print(DEFAULT_COLOR + cell, end="")
        print()
    print(Style.RESET_ALL, end="")

    if game_state['interaction_message']:
        print(game_state['interaction_message'])


def update_fireplace():
    x, y = game_state['fireplace_position']
    current_frame = game_state['fireplace_frame']

    game_state['tavern_layout'][y][x] = FIREPLACE_ICONS[current_frame]
    game_state['tavern_layout'][y][x + 2] = FIREPLACE_ICONS[current_frame]
    game_state['tavern_layout'][y][x + 1] = FIREPLACE_ICONS[(current_frame + 1) % len(FIREPLACE_ICONS)]

    # Update the fireplace frame for the next iteration
    game_state['fireplace_frame'] = (current_frame + 1) % len(FIREPLACE_ICONS)


def move_player(dx, dy):
    x, y = game_state['player_position']
    new_x, new_y = x + dx, y + dy
    next_cell = game_state['tavern_layout'][new_y][new_x]

    if next_cell not in (WALL_ICON, BAR_ICON, TABLE_ICON, DOOR_ICON, GATE_ICON) and not any(letter in next_cell for letter in CHARACTERS.keys()) and next_cell not in FIREPLACE_ICONS:
        game_state['tavern_layout'][y][x] = EMPTY_SPACE
        game_state['tavern_layout'][new_y][new_x] = PLAYER_ICON
        game_state['player_position'] = (new_x, new_y)

        # Clear the interaction message only if the player has actually moved
        if (x, y) != (new_x, new_y):
            game_state['interaction_message'] = ''


def on_key_release(key):
    
    if game_state['awaiting_message_input']:
        if key == keyboard.Key.enter:
            game_state['awaiting_message_input'] = False
            return
        else:
            return  # Add this line to return immediately if awaiting_message_input is True

    try:
        if key.char == 'w':
            move_player(0, -1)
        elif key.char == 'a':
            move_player(-1, 0)
        elif key.char == 's':
            move_player(0, 1)
        elif key.char == 'd':
            move_player(1, 0)
        elif key.char == 'f':
            interact_with_character(*game_state['player_position'])
    
    except AttributeError:
        pass

    render_game()

    # Clear input from the terminal input buffer
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        sys.stdin.readline()


def main():
    # Call place_characters_around_table for every table in the tavern layout
    for y, row in enumerate(game_state['tavern_layout']):
        for x, cell in enumerate(row):
            if cell == TABLE_ICON:
                place_characters_around_table((x, y))
    render_game()
    with keyboard.Listener(on_release=on_key_release) as listener:
        while True:
            if not game_state['freeze_scene']:
                update_fireplace()
                render_game()
                time.sleep(0.5)


if __name__ == '__main__':
    main()

