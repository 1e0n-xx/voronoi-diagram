from random import randint
from collections import defaultdict
import cv2
import numpy as np
from voronoi import Point


def set_neighboors_as_chosen(already_chosen, x, y, height, width):

    for j in range(max(0, y-1), min(height-1, y+2)):
        for i in range(max(0, x-1), min(width-1, x+2)):
            if not (i == x and j == y):
                already_chosen[(i,j)] = 1


def random_points(img, n):

    height = img.shape[0]
    width = img.shape[1]

    points = []
    already_chosen = defaultdict(int) 

    for i in range(n):
        x = randint(0, width-1)
        y = randint(0, height-1)
        while already_chosen[(x,y)] == 1:
            x = randint(0, width-1)
            y = randint(0, height-1)
        already_chosen[(x,y)] = 1
        set_neighboors_as_chosen(already_chosen, x, y, height, width)
        points.append(Point(x, y))

    return points


def weighted_random(img, n):

    height = img.shape[0]
    width = img.shape[1]

    img = cv2.GaussianBlur(img, (5,5), 0)


    edges = np.zeros((height, width, 1), np.uint8)
    for channel in cv2.split(img):
        channel_edges = np.zeros((height, width, 1), np.uint8)
        higher_t = 255
        lower_t = higher_t//3
        for i in range(10):
            aux = cv2.Canny(channel, lower_t, higher_t)
            channel_edges = cv2.add(channel_edges, aux)
            higher_t -= 25
            lower_t = higher_t//3
        edges = cv2.add(edges, channel_edges)


    kernel = np.ones((21,21), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations = 1)

    close_to_edges = cv2.subtract(dilated_edges, edges)

    #cv2.imshow('image', close_to_edges)
    #cv2.waitKey(0)

    points = []
    already_chosen = defaultdict(int) # start from 0

    # when not choose N
    while len(points) != n:
        x = randint(0, width-1)
        y = randint(0, height-1)
        while already_chosen[(x,y)] == 1:
            x = randint(0, width-1)
            y = randint(0, height-1)

        value = randint(1, 6)

        if close_to_edges[y][x] == 255:
            if value >= 3:
                already_chosen[(x,y)] = 1
                set_neighboors_as_chosen(already_chosen, x, y, height, width)
                points.append(Point(x,y))
        else:
            if value >= 6:
                already_chosen[(x,y)] = 1
                set_neighboors_as_chosen(already_chosen, x, y, height, width)
                points.append(Point(x,y))

    return points
