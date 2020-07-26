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
    rolled = None
    p = "[+\-,]"
    matches = re.finditer(p, dice)
    idx = [match.start() for match in matches]
    idx.append(0)
    idx.append(len(dice))
    idx.sort()
    rolls = [dice[idx[i]:idx[i+1]] for i in range(len(idx)-1)]
    output = []
    for roll in rolls:
        if "d" in roll:
            amount, size = roll.split("d")
            if rolled is not None:
                output.append(rolled)
            rolled = 0

            for i in range(int(amount)):
                t = randint(1, int(size))
                rolled = rolled + t
        else:
            if rolled is not None:
                output.append(rolled + int(roll))
                rolled = 0
            else:
                rolled = int(roll)
    #         if itt is 0:
    #             output[0] = int(each)
    #         else:
    #             output[itt - 1] = output[itt - 1] + int(each) * modifier
    print("auxiliaries - roll_function", output)
    if len(output) == 1:
        return output[0]
    # return output