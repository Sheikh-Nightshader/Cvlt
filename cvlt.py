#!/usr/bin/env python3

import os, sys, random, time

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

WIDTH, HEIGHT = 40, 20
MAX_PLAYER_HP = 20

def make_player():
    return {
        "x": WIDTH//2,
        "y": HEIGHT//2,
        "symbol": RED + "𖨆" + RESET,
        "hp": 15,
        "inventory": []
    }

def generate_map():
    m = [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for x in range(WIDTH):
        m[0][x] = m[HEIGHT-1][x] = "#"
    for y in range(HEIGHT):
        m[y][0] = m[y][WIDTH-1] = "#"
    for _ in range(60):
        x, y = random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2)
        m[y][x] = random.choice(["𖠿", "𖠰", "ᨒ"])
    return m

def place_random(symbol, name, color):
    while True:
        x, y = random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2)
        if game_map[y][x] == ".":
            return {"x": x, "y": y, "symbol": color + symbol + RESET, "name": name}

def place_high_priest():
    while True:
        hx, hy = random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2)
        if game_map[hy][hx] != ".": 
            continue
        if (hx,hy) in [(quest_giver["x"],quest_giver["y"]), (healer["x"],healer["y"])]:
            continue
        collision = False
        for e in enemies:
            if (hx,hy) == (e["x"], e["y"]):
                collision = True; break
        if not collision:
            return {"x": hx, "y": hy, "symbol": CYAN + "𖨆" + RESET, "name": "High Priest", "hp": 30, "alive": True}

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def pause(msg):
    print(YELLOW + msg + RESET)
    input("Press ENTER to continue...")

def draw():
    clear()
    print(RED + "="*15 + " ⛧ CvL⸸ ⛧ " + "="*15 + RESET)
    for y in range(HEIGHT):
        line = ""
        for x in range(WIDTH):
            if x == player["x"] and y == player["y"]:
                line += player["symbol"]
            elif x == quest_giver["x"] and y == quest_giver["y"]:
                line += quest_giver["symbol"]
            elif x == healer["x"] and y == healer["y"]:
                line += healer["symbol"]
            elif high_priest["alive"] and x == high_priest["x"] and y == high_priest["y"]:
                line += high_priest["symbol"]
            else:
                drawn = False
                for e in enemies:
                    if e["alive"] and x == e["x"] and y == e["y"]:
                        line += e["symbol"]; drawn = True; break
                if not drawn:
                    line += game_map[y][x]
        print(line)
    status = "None"
    if quest_given and not quest_complete:
        status = "Kill High Priest"
    elif quest_complete and not returned:
        status = "Return to Cult Leader"
    print(RED + f"HP: {player['hp']}/{MAX_PLAYER_HP}" + RESET +
          YELLOW + f"  Quest: {status}" + RESET +
          CYAN + f"  Inventory: {player['inventory']}" + RESET)
    print("W/A/S/D = move | E = interact | Q = quit")

def find_enemy_at(x,y):
    for e in enemies:
        if e["alive"] and e["x"]==x and e["y"]==y:
            return e
    return None

def fight_enemy(e):
    pause(f"You prepare to fight the {e['name']} (HP {e['hp']}).")
    while e["hp"] > 0 and player["hp"] > 0:
        p_atk = random.randint(4,8)
        e["hp"] -= p_atk
        pause(f"You strike the {e['name']} for {p_atk} damage! Enemy HP: {max(0,e['hp'])}")
        if e["hp"] <= 0:
            e["alive"] = False
            loot = f"{e['name']} fang"
            player["inventory"].append(loot)
            pause(f"You've slain the {e['name']}! Loot: {loot}")
            return
        player["hp"] -= e["damage"]
        pause(f"The {e['name']} hits you for {e['damage']}! Your HP: {player['hp']}")
        if player["hp"] <= 0:
            pause("You have died in battle... You Failed the Cult.")
            game_over()

def fight_high_priest():
    pause("Defeat the High Priest!")
    while high_priest["hp"] > 0 and player["hp"] > 0:
        p_atk = random.randint(5,10)
        high_priest["hp"] -= p_atk
        pause(f"You hit the High Priest for {p_atk}! HP: {max(0, high_priest['hp'])}")
        if high_priest["hp"] <= 0:
            high_priest["alive"] = False
            pause("The High Priest collapses. The quest is done.")
            player["inventory"].append("Priest's Head")
            return
        priest_dmg = random.randint(2,5)
        player["hp"] -= priest_dmg
        pause(f"The High Priest strikes you for {priest_dmg}! Your HP: {player['hp']}")
        if player["hp"] <= 0:
            pause("You were slain by the High Priest... You Failed the Cult.")
            game_over()

def interact():
    global quest_given, quest_complete, returned

    e = find_enemy_at(player["x"], player["y"])
    if e:
        fight_enemy(e)
        return

    if high_priest["alive"] and player["x"]==high_priest["x"] and player["y"]==high_priest["y"]:
        if not quest_given:
            pause("You have not been given the task yet. Speak to the Cult Leader first.")
            return
        confirm = input(RED + "Strike the High Priest now? (y/n): " + RESET).strip().lower()
        if confirm == "y":
            fight_high_priest()
            if not high_priest["alive"]:
                quest_complete = True
                pause("Quest complete! Return to the Cult Leader to claim your place.")
        else:
            pause("You step back from the quest for now.")
        return

    if player["x"]==quest_giver["x"] and player["y"]==quest_giver["y"]:
        if not quest_given:
            quest_given = True
            pause(f"{quest_giver['name']}: Your task — Slay the High Priest. Return to me with his Head when you are done.")
            return
        elif quest_complete and not returned:
            returned = True
            pause(f"{quest_giver['name']}: You have done well. The Cult hails you as one our own.")
            pause("ENDING: You return with the cult to learn the forbidden knowledge. Hail Satan!!!")
            game_over()
        else:
            pause(f"{quest_giver['name']}: The task awaits. Find the High Priest and strike him.")
            return

    if player["x"]==healer["x"] and player["y"]==healer["y"]:
        heal = random.randint(4,9)
        player["hp"] = min(MAX_PLAYER_HP, player["hp"] + heal)
        pause(f"The {healer['name']} restores {heal} HP. Your HP: {player['hp']}")
        return

    pause("There is nothing to interact with here.")

def check_bump():
    e = find_enemy_at(player["x"], player["y"])
    if e:
        player["hp"] -= e["damage"]
        pause(f"You bumped into a {e['name']} and took {e['damage']} damage! HP: {player['hp']}")
        if player["hp"] <= 0:
            pause("You died from your wounds... Game Over.")
            game_over()

def move_enemies():
    for e in enemies:
        if not e["alive"]: continue
        dx,dy = random.choice([-1,0,1]), random.choice([-1,0,1])
        nx, ny = e["x"]+dx, e["y"]+dy
        if 0 < nx < WIDTH-1 and 0 < ny < HEIGHT-1 and game_map[ny][nx] == "." and (nx,ny) not in [(quest_giver["x"],quest_giver["y"]), (healer["x"],healer["y"]), (high_priest["x"],high_priest["y"])]:
            if find_enemy_at(nx, ny) is None:
                e["x"], e["y"] = nx, ny

def game_over():
    again = input(RED + "Play again? (y/n): " + RESET).strip().lower()
    if again == "y":
        start_game()
    else:
        sys.exit()

def start_game():
    global game_map, player, quest_giver, healer, enemies, high_priest, quest_given, quest_complete, returned
    game_map = generate_map()
    player = make_player()
    quest_giver = place_random("𖨆", "Cult Leader", GREEN)
    healer = place_random("𖨆", "Cult Healer", BLUE)
    enemy_types = [
        {"symbol": MAGENTA+"𖨆"+RESET, "name":"Zealot","damage":1,"hp":8},
        {"symbol": YELLOW+"𖨆"+RESET, "name":"Priest Hunter","damage":2,"hp":10},
        {"symbol": WHITE+"𖨆"+RESET, "name":"Paladin","damage":3,"hp":14},
    ]
    enemies = []
    for _ in range(12):
        et = random.choice(enemy_types)
        while True:
            ex, ey = random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2)
            if game_map[ey][ex] == "." and (ex,ey) not in [(quest_giver["x"],quest_giver["y"]), (healer["x"],healer["y"])]:
                enemies.append({
                    "x": ex, "y": ey,
                    "symbol": et["symbol"], "name": et["name"],
                    "damage": et["damage"], "hp": et["hp"], "alive": True
                })
                break
    high_priest = place_high_priest()
    quest_given = False
    quest_complete = False
    returned = False

    while True:
        draw()
        action = input("Action: ").strip().lower()
        if action == "q":
            pause("Exiting. Hail Darkness.")
            game_over()
        if action == "e":
            interact()
        else:
            if action == "w" and game_map[player["y"]-1][player["x"]] != "#":
                player["y"] -= 1
            elif action == "s" and game_map[player["y"]+1][player["x"]] != "#":
                player["y"] += 1
            elif action == "a" and game_map[player["y"]][player["x"]-1] != "#":
                player["x"] -= 1
            elif action == "d" and game_map[player["y"]][player["x"]+1] != "#":
                player["x"] += 1
            check_bump()
            move_enemies()

start_game()
