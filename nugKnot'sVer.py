import pygame as pg, math, random

pg.init()
width, height = 1200, 600
screen = pg.display.set_mode((width, height))
pg.mouse.set_visible(False)
clock = pg.time.Clock()
def mapGen():
    matrix = [[0 for _ in range(12)] for _ in range(12)]
    for i in range(12):
        matrix[i][0] = matrix[i][-1] = 1
        matrix[0][i] = matrix[-1][i] = 1

    for i in range(1, 11):
        for j in range(1, 11):
            neighbors = [matrix[x][y] for x in range(i-1, i+2) for y in range(j-1, j+2)]
            if any(neighbors):
                matrix[i][j] = 0
            else:
                if random.random() < 0.5:
                    matrix[i][j] = random.choice([2, 3, 4])
    return matrix

MAP = list(mapGen())

coords = [1.5, 1.5]
angle = 0
fov = math.pi // 3
maxDepth = 10
rayCount = width // 2
deltaAngle = fov / rayCount

scale = width // rayCount
minScale = 20
minimap = pg.Surface((12 * minScale, 12 * minScale))

screenDist = (width / 2) / math.tan(fov / 2)

move = 0.04
rotate = 0.04

objects = {}
colors = {1: (0, 255, 255), 2: (0, 0, 255), 3: (0, 255, 0), 4: (255, 0, 255)}

def setupMap():
    for i in range(len(MAP)):
        for j in range(len(MAP[i])):
            if MAP[i][j]:
                objects[(j, i)] = MAP[i][j]

    pg.draw.rect(screen, (50, 50, 50), (0, height // 2, width, height))
    pg.draw.rect(screen, (30, 30, 30), (0, 0, width, height // 2))

def movePlayer():
    global angle, coords
    mx = move * math.cos(angle)
    my = move * math.sin(angle)
    dx, dy = 0, 0

    pressed = pg.key.get_pressed()
    if pressed[pg.K_w]:
        dx += mx
        dy += my
    if pressed[pg.K_s]:
        dx += -mx
        dy += -my
    if pressed[pg.K_a]:
        dx += my
        dy += -mx
    if pressed[pg.K_d]:
        dx += -my
        dy += mx

    if (int(coords[0] + dx), int(coords[1])) not in objects:
        coords[0] += dx
    if (int(coords[0]), int(coords[1] + dy)) not in objects:
        coords[1] += dy

    if pressed[pg.K_LEFT]:
        angle -= rotate
    if pressed[pg.K_RIGHT]:
        angle += rotate

    angle %= 2 * math.pi

def castRays():
    rayAngle = (angle - (fov / 2)) + 0.000001

    for ray in range(rayCount):
        sinAngle = math.sin(rayAngle)
        cosAngle = math.cos(rayAngle)

        xVert, dx = (int(coords[0]) + 1, 1) if cosAngle > 0 else (int(coords[0]) - 0.000001, -1)
        depthVrt = (xVert - coords[0]) / cosAngle
        yVert = (depthVrt * sinAngle) + coords[1]
        deltaDepth = dx / cosAngle
        dy = deltaDepth * sinAngle

        for i in range(maxDepth):
            tileVrt = (int(xVert), int(yVert))
            if tileVrt in objects:
                break
            xVert += dx
            yVert += dy
            depthVrt += deltaDepth

        yHoriz, dy = (int(coords[1]) + 1, 1) if sinAngle > 0 else (int(coords[1]) - 0.000001, -1)
        depthHrt = (yHoriz - coords[1]) / sinAngle
        xHoriz = (depthHrt * cosAngle) + coords[0]
        deltaDepth = dy / sinAngle
        dx = deltaDepth * cosAngle

        for i in range(maxDepth):
            tileHrt = (int(xHoriz), int(yHoriz))
            if tileHrt in objects:
                break
            xHoriz += dx
            yHoriz += dy
            depthHrt += deltaDepth

        if depthHrt < depthVrt:
            depth = depthHrt
            color = objects[tileHrt]
            side = 0
        elif depthVrt < depthHrt:
            depth = depthVrt
            color = objects[tileVrt]
            side = 1

        depth = depth * (math.cos(angle - rayAngle))
        
        projectionH = screenDist / (depth + 0.000001)
        if side == 0:
            pg.draw.rect(screen, colors[color], (ray * scale, (height // 2) - projectionH // 2, scale, projectionH))
        else:
            pg.draw.rect(screen, [x // 2 for x in colors[color]],
                         (ray * scale, (height // 2) - projectionH // 2, scale, projectionH))

        rayAngle += deltaAngle

def drawMiniMap():
    minimap.fill((0, 0, 0))
    pg.draw.rect(minimap, (255, 255, 255), (0, 0, 12 * minScale, 12 * minScale), 2)
    pg.draw.circle(minimap, (255, 0, 0), (int(coords[0] * minScale), int(coords[1] * minScale)), 3)

    for i in range(len(MAP)):
        for j in range(len(MAP[i])):
            if MAP[i][j]:
                pg.draw.rect(minimap, 'white', [j * minScale, i * minScale, minScale, minScale], 2)
            
    screen.blit(minimap, (0, 0))

running = True
while running:
    screen.fill('black')

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYUP:
            if event.key == pg.K_q:
                running = False

    setupMap()
    castRays()
    movePlayer()
    drawMiniMap()

    pg.display.update()
    clock.tick(60)

pg.quit()
