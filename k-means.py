import pygame, math, random, os, copy
from Grapher import Grapher

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (30,30)


random.seed()
pygame.init()
pygame.display.set_caption("K-means cluster")
SCREEN_WIDTH, SCREEN_HEIGHT = 500,500

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
grapher = Grapher(screen, 10, 10)
grapher.showGrid()

def euclid_distance(point1, point2, dimensions=2):
    sum = 0
    for i in range(dimensions):
        sum += (point1[i]-point2[i])**2
    return math.sqrt(sum)

def random_color():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    return (r,g,b)

def darker_color(color, percent=0.7):
    r,g,b = color
    return r*percent, g*percent, b*percent

def transparent_color(color, a):
    r,g,b = color
    return (r,g,b,a)

class Cluster:
    def __init__(self, nodes):
        self.nodes = nodes
        self.calcCentroid()
        self.color = random_color()

    def calcCentroid(self):
        xSum = 0
        ySum = 0
        for node in self.nodes:
            xSum += node[0]
            ySum += node[1]
        l = len(self.nodes)
        if(l == 0):
            self.centroid = [0,0]
        else:
            self.centroid = [float(xSum)/l, float(ySum)/l]

    def addNode(self, node, updateCentroid=True):
        self.nodes.append(node)
        if(updateCentroid):
            self.calcCentroid()

    def removeNode(self, node):
        self.nodes.remove(node);
        self.calcCentroid()

    def clearNodes(self):
        self.nodes = []
        self.centroid = (0,0)

    def setColor(self, color=None):
        if(not color):
            color = self.color
        for node in self.nodes:
            node[2] = color

    def draw(self):
        centroid = (self.centroid[0], self.centroid[1])
        grapher.plot(self.centroid[0], self.centroid[1],darker_color(self.color))
        max_distance = -1
        max_node = None
        for node in self.nodes:
            distance = euclid_distance(centroid, (node[0], node[1]))
            if(distance > max_distance):
                max_distance = distance
                max_node = node
            grapher.plotLine(centroid, (node[0], node[1]), darker_color(self.color))
            grapher.plot(node[0], node[1], node[2])

        if(max_node):
            grapher.plotFilledCircle(centroid, max_distance, transparent_color(self.color, 100))


class Dataset:
    def __init__(self, subjects):
        self.data = [[0,0,(0,0,0)] for x in range(0,subjects)]
        self.clusters = []

    def setSubject(self, index, value):
        self.data[index] = value

    def setSubjects(self, subjects):
        self.data = subjects

    def plot(self):
        for subject in self.data:
            grapher.plot(subject[0], subject[1], subject[2])

    def two_furthest_points(self):
        chosen_one = self.data[0]
        max_distance = -1
        max_point = None
        for i in range(1,len(self.data)):#get furthest point from the chosen one
            point = self.data[i]
            distance = euclid_distance(chosen_one, point)
            if(distance > max_distance):
                max_distance = distance
                max_point = point
        max_distance = -1
        for i in range(len(self.data)): #get furthest point from max_point
            point = self.data[i]
            distance = euclid_distance(max_point, point)
            if(distance > max_distance):
                max_distance = distance
                max_point2 = point
        return [max_point, max_point2]

    def k_means_cluster(self, k=4):
        if(not self.clusters):
            max_point, max_point2 = (None, None)
            if(k == 2):
                max_point, max_point2 = self.two_furthest_points()
                self.clusters = [Cluster([max_point]), Cluster([max_point2])]
                for point in self.data:
                    if(point == max_point2):
                        self.clusters[0].addNode(point)
                    else:
                        self.clusters[1].addNode(point)
            else:
                rData = copy.deepcopy(self.data)
                for point in random.sample(range(0, len(self.data)), k):
                    rData.remove(self.data[point])
                    self.clusters.append(Cluster([self.data[point]]))

                for point in rData:
                    self.clusters[0].addNode(point)


        for i in range(len(self.clusters)):
            cluster = self.clusters[i]
            for point in cluster.nodes:
                distance = euclid_distance(point, cluster.centroid)
                # for otherCluster in (self.clusters[:i]+self.clusters[i+1:]):
                for otherCluster in self.clusters:
                    if(otherCluster == cluster):
                        continue
                    if(euclid_distance(point, otherCluster.centroid) < distance):
                        cluster.removeNode(point)
                        otherCluster.addNode(point)
                        break
        for cluster in self.clusters:
            cluster.setColor()
        # print("Group 1: "+str(self.clusters[0].centroid))
        # print("Group 2: "+str(self.clusters[1].centroid))

    def drawClusters(self):
        for cluster in self.clusters:
            cluster.draw()

data = Dataset(7)
data.setSubject(0, [1.0,1.0,BLACK])
data.setSubject(1, [1.5,2.0,BLACK])
data.setSubject(2, [3.0,4.0,BLACK])
data.setSubject(3, [5.0,7.0,BLACK])
data.setSubject(4, [3.5,5.0,BLACK])
data.setSubject(5, [4.5,5.0,BLACK])
data.setSubject(6, [3.5,4.0,BLACK])

DATA_SIZE = 200
data = Dataset(DATA_SIZE)

for i in range(DATA_SIZE):
    data.setSubject(i, [random.uniform(0,10), random.uniform(0,10), BLACK])

# data.setSubject(7, (9.0,4.0,BLACK))
# data.setSubject(8, (8.0,2.0,BLACK))
# data.setSubject(9, (9.0,5.0,BLACK))
# data.setSubject(9, (2.0,2.0,BLACK))
data.plot()
# grapher.plot(5,5, RED)
# grapher.plotLine((1,1), (5,5), BLUE)

clock = pygame.time.Clock()

def handle_events():
    clock.tick(10)
    for e in pygame.event.get():
        if(e.type == pygame.QUIT):
            return False
        elif(e.type == pygame.KEYDOWN):
            if(e.key == pygame.K_ESCAPE):
                grapher.save("screenshot.png")
                return False
    return True

while handle_events():
    screen.fill(WHITE)

    data.k_means_cluster()
    data.drawClusters()

    grapher.render()
    grapher.clear()

    pygame.display.flip()

pygame.quit()
