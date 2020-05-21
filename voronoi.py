from collections import defaultdict
import sys
import math
import time
import cv2
import numpy as np
import points_gen

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Point(object):

    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.color = color

    def __str__(self):
        return "Point({}, {})".format(self.x, self.y)

    def dist(self, p):
        dx = self.x - p.x
        dy = self.y - p.y
        return math.hypot(dx, dy)

    def is_in_circuncircle(self, triangle):

        return self.dist(triangle.center) <= triangle.cr


class Edge(object):

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return "Edge({}, {})".format(self.p1, self.p2)

    def is_equal(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2

    def is_unique(self, triangles):
        count = 0
        for triangle in triangles:
            for edge in triangle:
                if self.is_equal(edge):
                    count += 1
                    if count == 2:
                        return False
        return True


class Triangle(object):

    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.e1 = Edge(p1, p2)
        self.e2 = Edge(p2, p3)
        self.e3 = Edge(p1, p3)
        self.edges = [self.e1, self.e2, self.e3]
        self.cx, self.cy, self.cr = self.circumcenter()
        self.center = Point(self.cx, self.cy)

    def __iter__(self):
        return iter(self.edges)

    def __str__(self):
        return "Points:({}, {}, {})".format(self.p1, self.p2, self.p3)

    def circumcenter(self):
        p1 = self.p1
        p2 = self.p2
        p3 = self.p3
        d = (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

        if d == 0:
            print("Erro, pontos colineares")
            d = 1

        cx = (((p1.x - p3.x) * (p1.x + p3.x) + (p1.y - p3.y) * (p1.y + p3.y)) / 2 * (p2.y - p3.y) \
              - ((p2.x - p3.x) * (p2.x + p3.x) + (p2.y - p3.y) * (p2.y + p3.y)) / 2 * (p1.y - p3.y)) \
             / d

        cy = (((p2.x - p3.x) * (p2.x + p3.x) + (p2.y - p3.y) * (p2.y + p3.y)) / 2 * (p1.x - p3.x) \
              - ((p1.x - p3.x) * (p1.x + p3.x) + (p1.y - p3.y) * (p1.y + p3.y)) / 2 * (p2.x - p3.x)) \
             / d

        cr = np.hypot((p3.x - cx), (p3.y - cy))

        return cx, cy, cr

    def contains_super(self, super_tri):
        pontos = set([self.p1, self.p2, self.p3, super_tri.p1, super_tri.p2, super_tri.p3])
        return len(pontos) != 6


def bowyer_watson(image, height, width, points):
    # create a super triangle
    sp1 = Point(-math.ceil(width * 1.5), -1)  # top left
    sp2 = Point(math.ceil(width * 2.5), -1)  # right
    sp3 = Point(width // 2, math.ceil(height * 2.5))  # bot mid
    super_tri = Triangle(sp1, sp2, sp3)

    triangulation = []
    triangulation.append(super_tri)

    neighbors = defaultdict(list)
    neighbors[(super_tri.e1.p1, super_tri.e1.p2)].append(super_tri)
    neighbors[(super_tri.e2.p1, super_tri.e2.p2)].append(super_tri)
    neighbors[(super_tri.e3.p1, super_tri.e3.p2)].append(super_tri)

    # print("Delaunay Triangulating")
    # Vai inserindo um ponto de cada vez
    for point in points:

        bad_tri = set()
        for triangle in triangulation:
            if point.is_in_circuncircle(triangle):
                bad_tri.add(triangle)
    
        polygon = set()
        for triangle in bad_tri:
            for edge in triangle:
                if edge.is_unique(bad_tri):
                    polygon.add(edge)
        for triangle in bad_tri:
            triangulation.remove(triangle)
            neighbors[(triangle.e1.p1, triangle.e1.p2)].remove(triangle)
            neighbors[(triangle.e2.p1, triangle.e2.p2)].remove(triangle)
            neighbors[(triangle.e3.p1, triangle.e3.p2)].remove(triangle)

       
        for edge in polygon:
            new_tri = Triangle(edge.p1, edge.p2, point)
            triangulation.append(new_tri)
            neighbors[(new_tri.e1.p1, new_tri.e1.p2)].append(new_tri)
            neighbors[(new_tri.e2.p1, new_tri.e2.p2)].append(new_tri)
            neighbors[(new_tri.e3.p1, new_tri.e3.p2)].append(new_tri)
\
    # Remove the triangle containing the vertices from the super triangle.
    # #Result is delaunay triangulation
    delaunay_triangles = [tri for tri in triangulation if not tri.contains_super(super_tri)]
    delaunay = np.zeros((height, width, 1), np.uint8)
    for triangle in delaunay_triangles:
        for edge in triangle:
            p1 = (edge.p1.x, edge.p1.y)
            p2 = (edge.p2.x, edge.p2.y)
            cv2.line(delaunay, p1, p2, WHITE, 1)

    voronoi = voronoi_diagram(triangulation, neighbors, height, width)
    out = voronoi_painting(voronoi, image, height, width)

    return out, delaunay, voronoi


def voronoi_diagram(triangulation, neighbors, height, width):

    voronoi = np.zeros((height, width, 3), np.uint8)
    for triangle in triangulation:
        for edge in triangle:
            for neighbor in neighbors[(edge.p1, edge.p2)]:
                if neighbor is not triangle:
                    c1 = (math.ceil(triangle.cx), math.ceil(triangle.cy))
                    c2 = (math.ceil(neighbor.cx), math.ceil(neighbor.cy))
                    cv2.line(voronoi, c1, c2, WHITE, 1)

    return voronoi


def voronoi_painting(voronoi, image, height, width):

    voronoi_inv = cv2.cvtColor(voronoi, cv2.COLOR_BGR2GRAY)
    voronoi_inv = cv2.bitwise_not(voronoi_inv)

    components = cv2.connectedComponentsWithStats(voronoi_inv, connectivity=4)
    out = voronoi.copy()
    labels = components[1]
    centroids = components[3]

    for label in np.unique(labels):
        mask = (labels == label).astype(np.uint8)
        x, y = map(int, centroids[label])
        mean = cv2.mean(image, mask)
        cv2.floodFill(out, None, (x, y), mean)



    blurred = cv2.medianBlur(out, 11)

    edges = np.asarray(np.where(voronoi == WHITE)).T
    for y, x, _ in edges:
        out[y][x] = blurred[y][x]

    return out


def bruteforce(img, height, width, points):
    """ Para cada pixel da imagem, calcula a distância até todos os pontos e
    escolhe a cor do mais próximo
    """
    out = np.zeros((height, width, 1), np.uint8)
    for y in range(0, height):
        for x in range(0, width):
            min_dist = 10000000
            for point in points:
                dist = np.hypot((x - point.x), (y - point.y))
                if dist < min_dist:
                    min_dist = dist
                    x_min_dist = point.x
                    y_min_dist = point.y
            out[y, x] = img[y_min_dist, x_min_dist]
    return out


def show_img(img):

    cv2.imshow('image', img)
    cv2.waitKey(0)


def main():
    image_name = ("leonardo.jpg")
    num_points = int(2000)

    image = cv2.imread(image_name, 1)
    height = image.shape[0]
    width = image.shape[1]

    image_name, extension = image_name.split('.')

    # Blurs for noise
    image = cv2.GaussianBlur(image, (7, 7), 0)

    points = points_gen.random_points(image, num_points)
    # points = points_gen.weighted_random(image, num_points)

    points_img = np.zeros((height, width, 1), np.uint8)
    for point in points:
        points_img[point.y][point.x] = 255

    start_time = time.time()
    # out = brute_force(image, height, width, points)
    out, delaunay, voronoi = bowyer_watson(image, height, width, points)
    print("--- {:.2f} s ---".format(time.time() - start_time))

    for point in points:
        x = point.x
        y = point.y
        cv2.circle(voronoi, (x, y), 1, (0, 255, 0), -1)

    cv2.imwrite(image_name + '-1points.' + extension, points_img)
    cv2.imwrite(image_name + '-2delaunay.' + extension, delaunay)
    cv2.imwrite(image_name + '-3voronoi.' + extension, voronoi)
    cv2.imwrite(image_name + '-4out.' + extension, out)

    # show_img(points_img)
    # show_img(delaunay)
    # show_img(voronoi)
    show_img(out)


if __name__ == "__main__":
    main()
    # image_name = ("leonardo.jpg")
    # image = cv2.imread(image_name, 1)
    #
    # num_points = int(2000)
    # points = points_gen.weighted_random(image, num_points)
    # print(points)
