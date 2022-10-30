import math

from tree_v1 import Tree, Forest
from tree_draw import draw_tree, draw_forest

def tree_demo():
    tree = Tree(f=0.8, dTheta=0.9*0.25*math.pi)
    tree.grow()
    tree.bloom()
    draw_tree(tree, drawSpace=[-1,1,0,2])

def forest_demo():
    forest = Forest([
        Tree(f=0.75, dTheta=0.75*0.25*math.pi, root = (-0.5,0), leafColor='red'),
        Tree(f=0.8, dTheta=0.85*0.25*math.pi, root = (0,0), leafColor='green'),
        Tree(f=0.85, dTheta=0.8*0.25*math.pi, root = (0.5,0), leafColor='blue')
    ])
    forest.grow()
    forest.bloom()
    draw_forest(forest)

forest_demo()