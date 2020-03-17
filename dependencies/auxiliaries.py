from random import randint

def roll_function(dice):
    output = []
    split = dice.split("+")
    if len(split) is 1 and "d" not in split[0]:  # in the case of X damage, without a roll
        return int(split[0])
    for itt, each in enumerate(split):
        if "d" in each:
            amount, size = each.split("d")
            rolled = 0
            for i in range(int(amount)):
                roll = randint(1, int(size))
                rolled = rolled + roll
            output.append(rolled)
        else:
            if itt is 0:
                output[0] = int(each)
            else:
                output[itt - 1] = output[itt - 1] + int(each)
    if len(output) == 1:
        return output[0]
    return output