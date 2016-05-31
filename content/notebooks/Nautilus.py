
def nautilus(n):
    x, y = 0, 0
    return walk(n, x, y, 'north')

def increment(x, y, direction):
    if direction == 'north':
        return x, y + 1
    elif direction == 'south':
        return x, y - 1
    elif direction == 'east':
        return x + 1, y
    else:
        return x - 1, y

def change_direction(x, y, direction, max_pos):
    if x > max_pos['east']:
        return 'south'
    elif x < max_pos['west']:
        return 'north'
    elif x > max_pos['north']:
        return 'east'
    elif x < max_pos['south']:
        return 'west'
    else:
        return direction

def walk(n, x, y, direction, max_pos):
    if n == 0:
        return x, y
    else:
        xnew, ynew = increment(x, y, direction)
        direction = change_direction(xnew, ynew, direction, max_pos)
        walk(n - 1, x, y)

if __name__ == '__main__':
    print(nautilus(10))