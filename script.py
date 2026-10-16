import random

alive = 1
command = 1
rotate_p = 3
rotate_ptwo = 3
game_num = 0
gm = 1
turn = 11
turn_number = 1
bullet_num = 1
print("1. Play with player / 2. Play with bot")
gm = input("-")
print("\n"*100)
while True:
    print("\n" * 100)
    alive = 1
    game_num += 1
    rotate_p = 3
    rotate_ptwo = 3
    bullet_num = random.randint(1,9)
    print(f"Game {game_num}")
    #while bullet_num != turn_number and command != "1":
    while alive == 1:
        if gm == "1":
            print("\n" * 100)
            if turn == 1:
                print(f"➔ Player 1. Rotates {rotate_p}/3")
                print(f"Player 2. Rotates {rotate_ptwo}/3")
                print("")
                print("1.Shoot / 2.Rotate")
                print("  ○ ○ ○ ○ ○ ○ ○ ○ ○")
                print(f"  " * turn_number + "↑")
                command = input("-")
                if command == "1":
                    if bullet_num == turn_number:
                        print("lose")
                    else:
                        turn = 2
                        turn_number += 1
                else:
                    if rotate_p > 0:
                        turn_number = random.randint(1,9)
                        rotate_p -= 1

                    #print("\n" * 100)

            else:
                print(f"Player 1. Rotates {rotate_p}/3")
                print(f"➔ Player 2. Rotates {rotate_ptwo}/3")
                print("")
                print("1.Shoot / 2.Rotate")
                print("  ○ ○ ○ ○ ○ ○ ○ ○ ○")
                print(f"  " * turn_number + "↑")
                command = input("-")
                if command == "1":
                    if bullet_num == turn_number:
                        print("lose")
                    else:
                        turn = 1
                        turn_number += 1
                else:
                    if rotate_p > 0:
                        turn_number = random.randint(1,9)
                        rotate_ptwo -= 1
                    #print("\n" * 100)
        print("\n" * 100)
        if turn_number > 9 and command == "1":
            turn_number = 1
        #print(turn_number)
        #print(bullet_num)
        if bullet_num == turn_number:
            if turn == 1:
                print("Player 2 lose")
                alive = 0
                input("-")
            else:
                print("Player 1 lose")
                alive = 0
                input("-")
            exit(0)
        if gm == 2:
            pass
    print("\n" * 100)
    #print("\n"*100)
