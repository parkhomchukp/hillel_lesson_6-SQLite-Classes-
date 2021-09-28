class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Circle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def contains(self, point):
        if ((point.x - self.x)**2) + ((point.y - self.y)**2) <= self.r**2:
            return True
        else:
            return False


point = Point(1, 42)
circle = Circle(0, 0, 10)
result = circle.contains(point)
print(result)
