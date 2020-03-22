class Block(object):

    def __init__(self):
        self.width = 4
        self.rotation = 0
        self.offset_x = 4
        self.offset_y = 0

    def get_point(self, x, y):
        w = self.width
        # Alternate rotation algorithms
        # 90°  idx w * (w-1) + y - w * x
        # 180° idx w * w - 1 - w * y - x
        # 270° idx w - 1 - y + w * x
        idx = [
            y * w + x,
            (w - 1 - x) * w + y,            # new_x = y; new_y = width - 1 - x; idx = new_y * width + new_x
            (w - 1 - y) * w + (w - 1 - x),  # new_x = w - 1 - x; new_y = w - 1 - y; idx = new_y * width + new_x
            x * w + (w-1) - y               # new_x = (width - 1) - y; new_y = x; idx = new_y * width + new_x      
        ][self.rotation]
        return self.area[idx]

    def get_points(self):
        for i in range(0, len(self.area)):
            y = i // self.width
            x = i % self.width
            yield x, y

    def move_y(self, direction):
        self.offset_y += direction

    def move_x(self, direction):
        self.offset_x += direction

    def rotate(self, direction):
        if (self.rotation + direction) > 3:
            self.rotation = 0
        elif (self.rotation + direction) < 0:
            self.rotation = 3
        else:
            self.rotation += direction


class Hero(Block):
    def __init__(self):
        self.area = [
            0, 0, 1, 0,
            0, 0, 1, 0,
            0, 0, 1, 0,
            0, 0, 1, 0
        ]
        super().__init__()


class Smashboy(Block):
    def __init__(self):
        self.area = [
            0, 0, 0, 0,
            0, 2, 2, 0,
            0, 2, 2, 0,
            0, 0, 0, 0
        ]
        super().__init__()


class RhodeIslandZ(Block):
    def __init__(self):
        self.area = [
            0, 3, 0, 0,
            0, 3, 3, 0,
            0, 0, 3, 0,
            0, 0, 0, 0
        ]
        super().__init__()


class RhodeIslandZ(Block):
    def __init__(self):
        self.area = [
            0, 3, 0, 0,
            0, 3, 3, 0,
            0, 0, 3, 0,
            0, 0, 0, 0
        ]
        super().__init__()


class ClevelandZ(Block):
    def __init__(self):
        self.area = [
            0, 0, 4, 0,
            0, 4, 4, 0,
            0, 4, 0, 0,
            0, 0, 0, 0
        ]
        super().__init__()


class Pyramid(Block):
    def __init__(self):
        self.area = [
            0, 0, 0, 0,
            0, 0, 5, 0,
            0, 5, 5, 5,
            0, 0, 0, 0
        ]
        super().__init__()


class L(Block):
    def __init__(self):
        self.area = [
            0, 6, 6, 0,
            0, 0, 6, 0,
            0, 0, 6, 0,
            0, 0, 0, 0
        ]
        super().__init__()


class BackwardsL(Block):
    def __init__(self):
        self.area = [
            0, 7, 7, 0,
            0, 7, 0, 0,
            0, 7, 0, 0,
            0, 0, 0, 0
        ]
        super().__init__()


blocklist = [
    Hero,
    Smashboy,
    RhodeIslandZ,
    ClevelandZ,
    Pyramid,
    L,
    BackwardsL
]
