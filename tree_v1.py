#Very simple version of tree classes.
# - trees always split into 2 branches
# - each branch has a predetermined length of a factor f of it's predecessor
# - branches cannot grow to intercept each other
# - branches cannot grow to intercept the ground

import math
import cairo
from matplotlib import colors
import random
import time
import numpy as np

def check_intersect(line1, line2):

    x1,y1 = line1[0]
    x2,y2 = line1[1]
    x3,y3 = line2[0]
    x4,y4 = line2[1]

    try:
        u = ((y4-y3)*(x2-x1)-(x4-x3)*(y2-y1))/((x4-x3)*(y2-y1)-(y4-y3)*(x2-x1))
    except ZeroDivisionError as e:
        return False
    return (0<u<1)

def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect
def intersect(line1, line2):
    A,B = line1
    C,D = line2
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

class Tree:

    def __init__(self, l0=0.2, f=0.8, dTheta=math.pi/4, root=(0,0), leafColor='green'):
        self.f = f
        self.dTheta = dTheta
        self.branches = [Branch(root, l0, 0, self)]
        self.init_drawing()
        self.leafColor = leafColor
    
    def init_drawing(self):

        WIDTH, HEIGHT = 512, 512
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        self.ctx = cairo.Context(self.surface)
        self.ctx.scale(WIDTH, HEIGHT)  # Normalizing the canvas

        #set background color
        self.ctx.save()
        self.ctx.set_source_rgb(1, 1, 1)
        self.ctx.paint()
        self.ctx.restore()

    def refresh_leaf_nodes(self):
        self.leafNodeBranches = [branch for branch in self.branches if branch.leafNode]

    def split_branch(self, branch):
        theta0 = branch.theta
        newBranchCount = 0
        for theta in [theta0+self.dTheta, theta0-self.dTheta]:
            newBranch = Branch(branch.loc1, self.f*branch.l, theta, parent=branch)
            if not any(newBranch.check_branch_intersect(branch2) for branch2 in self.branches):
                self.branches.append(newBranch)
                newBranchCount+=1
                
        if newBranchCount==0:
            branch.bloom()
        
        branch.leafNode = False
    
    def bloom(self):
        self.refresh_leaf_nodes()
        for branch in self.leafNodeBranches:
            branch.bloom()

        self.canopy = Canopy(self)
        
    def grow(self, nBranchIters=10):
        for i in range(nBranchIters):
            self.refresh_leaf_nodes()
            for branch in self.leafNodeBranches:
                branch.split()
  
class Branch:
    def __init__(self, loc0, l, theta0, tree, parent=None, leaf=None):
        self.loc0 = loc0
        self.l = l
        self.theta = theta0
        self.tree = tree
        self.parent = parent
        self.leaf = None
        self.loc1 = (loc0[0]+l*math.sin(theta0), loc0[1]+l*math.cos(theta0))

        self.leafNode=True
    
    def check_branch_intersect(self, branch2):
        if self.parent == branch2:
            return False
        else:
            return intersect((self.loc0, self.loc1), (branch2.loc0, branch2.loc1))

    def split(self):
        
        newBranchCount = 0
        for theta in [self.theta+self.tree.dTheta, self.theta-self.tree.dTheta]:
            newBranch = Branch(self.loc1, self.tree.f*self.l, theta, self.tree, parent=self)
            if ((not any(newBranch.check_branch_intersect(branch2) for branch2 in self.tree.branches)) 
                and (newBranch.loc1[1]>0)):
                    self.tree.branches.append(newBranch)
                    newBranchCount+=1

        if newBranchCount==0:
            self.bloom()
        
        self.leafNode = False
            
    def bloom(self):
        self.leaf = Leaf(self.loc1, parent=self)   

class Canopy:
    def __init__(self, tree, leaves=[]):
        self.tree = tree
        self.refresh_leaves()
        self.evaluate_area()
    
    def refresh_leaves(self):
        self.leaves = [branch.leaf for branch in self.tree.branches if branch.leaf]

    def evaluate_area(self, nTest=500):
        """assume overlapping leaves do not stack, what is the total surface area of leaves?"""
        """use a quasi monte carlo method here. nTest=500 deemed acceptable by testing"""
        self.refresh_leaves()
        leafLocs = [leaf.loc for leaf in self.leaves]
        locsX = [leafLoc[0] for leafLoc in leafLocs]
        locsY = [leafLoc[1] for leafLoc in leafLocs]
        maxLeafRadius = max([leaf.r for leaf in self.leaves])
        canopySpaceRange = [min(locsX)-maxLeafRadius, max(locsX)+maxLeafRadius, min(locsY)-maxLeafRadius, max(locsY)+maxLeafRadius]
        totalArea = (canopySpaceRange[1]-canopySpaceRange[0])*(canopySpaceRange[3]-canopySpaceRange[2])
        nInside = 0
        for i in range(nTest):
            randomLoc = (random.uniform(canopySpaceRange[0], canopySpaceRange[1]), random.uniform(canopySpaceRange[2], canopySpaceRange[3]))
            if any(((randomLoc[0]-leaf.loc[0])**2 + (randomLoc[1]-leaf.loc[1])**2)**0.5 <= leaf.r for leaf in self.leaves):
                nInside += 1
        
        self.estArea = nInside/nTest * totalArea
        return self.estArea

class Leaf:
    def __init__(self, loc, r=0.02, parent=None):
        self.loc = loc
        self.r = r
        self.parent=parent

class Forest:
    def __init__(self, trees):
        self.trees = trees

    def grow(self, nBranchIters=10):
        for i in range(nBranchIters):
            for tree in self.trees:
                tree.grow(nBranchIters=1)
        
            #validate no overlaps between branches of different trees
            for tree in self.trees:
                tree.refresh_leaf_nodes()
                for tree2 in self.trees:
                    if tree==tree2:
                        continue

                    for branch in tree.leafNodeBranches:
                        if any(branch.check_branch_intersect(branch2) for branch2 in tree2.branches):
                            branch.parent.bloom()
                            tree.branches.remove(branch)
    
    def bloom(self):
        [tree.bloom() for tree in self.trees]

    def get_draw_space_limits(self):
        """returns x and y limits of the space taken up by the forest"""
        allLeafX = [item for sublist in [[leaf.loc[0] for leaf in tree.canopy.leaves] for tree in self.trees] for item in sublist]
        allLeafY = [item for sublist in [[leaf.loc[1] for leaf in tree.canopy.leaves] for tree in self.trees] for item in sublist]
        maxMagX = allLeafX[np.argmax(allLeafX)].__abs__()
        maxMagY = allLeafY[np.argmax(allLeafY)].__abs__()
        mag = max([maxMagX, maxMagY])
        self.drawSpace = [-mag, mag, 0, 2*mag]
        print(self.drawSpace)
        return self.drawSpace




