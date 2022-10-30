import cairo
from matplotlib import colors
import math

def draw_tree(tree, outputFileName="tree.png", drawSpace=[-0.5,0.5,0,1]):
    treeDrawer = TreeDrawingObj(tree)
    treeDrawer.draw_tree(drawSpace=drawSpace)
    treeDrawer.surface.write_to_png(outputFileName)

def draw_forest(forest, outputFileName="forest.png"):
    forestDrawer = ForestDrawingObj(forest)
    forestDrawer.draw_forest()
    forestDrawer.surface.write_to_png(outputFileName)

class TreeDrawingObj:
    def __init__(self, tree):
        
        self.tree = tree

        WIDTH, HEIGHT = 512, 512
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        self.ctx = cairo.Context(self.surface)
        self.ctx.scale(WIDTH, HEIGHT)  # Normalizing the canvas

        #set background color
        self.ctx.save()
        self.ctx.set_source_rgb(1, 1, 1)
        self.ctx.paint()
        self.ctx.restore()
    
    def flip_branch_leaf_y_coords(self):
        for branch in self.tree.branches:
            branch.loc0 = (branch.loc0[0], 1-branch.loc0[1])
            branch.loc1 = (branch.loc1[0], 1-branch.loc1[1])
            if branch.leaf:
                branch.leaf.loc = (branch.leaf.loc[0], 1-branch.leaf.loc[1])
    
    def adjust_drawspace(self,drawSpace):
        self.ctx.translate(0.5 - (drawSpace[1]+drawSpace[0])/2, (drawSpace[2]+drawSpace[3])/2 - 0.5)
        self.ctx.scale(1/(drawSpace[1]-drawSpace[0]),1/(drawSpace[3]-drawSpace[2]))

    def set_color_and_linewidth(self, color, linewidth):
        rgba = colors.to_rgba(color)
        self.ctx.set_source_rgb(rgba[0], rgba[1], rgba[2])  # Solid color
        self.ctx.set_line_width(linewidth)

    def draw_tree(self, flipY=True, drawSpace=[-0.5,0.5,0,1]):

        if flipY:
            self.flip_branch_leaf_y_coords()
            
        self.adjust_drawspace(drawSpace)
        
        #draw branches
        for branch in self.tree.branches:
            self.draw_branch(branch)
        self.set_color_and_linewidth('brown', 0.005)
        self.ctx.stroke()

        #draw leaves
        for branch in self.tree.branches:
            if branch.leaf:
                self.draw_leaf(branch.leaf)
        self.set_color_and_linewidth(self.tree.leafColor, 0.005)
        self.ctx.stroke()


    def draw_branch(self, branch):
        self.ctx.move_to(branch.loc0[0], branch.loc0[1])
        self.ctx.line_to(branch.loc1[0], branch.loc1[1])
    
    def draw_leaf(self, leaf):
        self.ctx.move_to(leaf.loc[0]+leaf.r, leaf.loc[1])
        self.ctx.arc(leaf.loc[0], leaf.loc[1], leaf.r, 0, 2*math.pi)


class ForestDrawingObj(TreeDrawingObj):
    def __init__(self, forest):
        super().__init__(forest)

        self.forest = forest
        #self.drawSpace = self.forest.get_draw_space_limits()
        self.drawSpace = [-1,1,0,2]

    def draw_forest(self):

        for tree in self.forest.trees:
            self.flip_branch_leaf_y_coords(tree)
            
        self.adjust_drawspace(self.drawSpace)
        
        #draw branches
        for tree in self.forest.trees:
            for branch in tree.branches:
                self.draw_branch(branch)
        self.set_color_and_linewidth('brown', 0.005)
        self.ctx.stroke()

        #draw leaves
        for tree in self.forest.trees:
            for branch in tree.branches:
                if branch.leaf:
                    self.draw_leaf(branch.leaf)
            self.set_color_and_linewidth(tree.leafColor, 0.005)
            self.ctx.stroke()

    def flip_branch_leaf_y_coords(self, tree):
        for branch in tree.branches:
            branch.loc0 = (branch.loc0[0], 1-branch.loc0[1])
            branch.loc1 = (branch.loc1[0], 1-branch.loc1[1])
            if branch.leaf:
                branch.leaf.loc = (branch.leaf.loc[0], 1-branch.leaf.loc[1])