from random import randint
import re


RarityList = ["Common",
              "Uncommon",
              "Rare",
              "Very rare",
              "Legendary",
              "Artifact"]


class GlobalParameters:
    MAIN_TOOL_STRETCH = 6
    MIDDLE_FRAME_STRETCH = 5
    RIGHT_FRAME_STRETCH = 5

    MAIN_TOOL_POSITION = 0
    MIDDLE_FRAME_POSITION = 1
    RIGHT_FRAME_POSITION = 2

    MONSTER_VIEWER_INDEX = 0
    SPELL_VIEWER_INDEX = 1
    ITEM_VIEWER_INDEX = 2

    TEXT_BOX_INDEX = 3

# Global = GlobalParameters()


def roll_function(dice):
    p = "[+\-,]"
    matches = re.finditer(p, dice)
    idx = [match.start() for match in matches]
    idx.append(0)
    idx.append(len(dice))
    idx.sort()
    rolls = [dice[idx[i]:idx[i+1]] for i in range(len(idx)-1)]
    output = []
    # print("\tauxiliaries - roll_function: {}".format(rolls))
    for roll in rolls:
        roll = roll.strip('+').strip(' ')
        if roll == "":
            continue
        if "d" in roll:
            rolled = 0
            amount, size = roll.split("d")
            for i in range(int(amount)):
                t = randint(1, int(size))
                rolled = rolled + t
            output.append(t)
        else:
            if len(output) is 0:
                output.append(int(roll))
            else:
                output[-1] = output[-1] + int(roll)
    # print("\tauxiliaries - roll_function: {}".format(output))
    if len(output) is 0:
        return None
    elif len(output) is 1:
        return output[0]
    return output