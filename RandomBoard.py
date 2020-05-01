from __future__ import print_function
import random


def print2DArray(array):
    for y in range(10):
        for x in range(10):
            print(array[y][x], end='')
        print("")

def findSum(array):
    i = 0
    for y in range(10):
        for x in range(10):
            i += array[y][x]
    print(i)

array = [[0 for x in range(10)] for y in range(10)]
for y in range(10):
    for x in range(10):
        array[y][x] = random.randint(1, 9)

print2DArray(array)
print("")
findSum(array)