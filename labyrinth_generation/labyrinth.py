import numpy
from numpy.random import randint as rand
import matplotlib.pyplot as pyplot

'''
This scripts generates a labyrinth, where each tile is a triangle, then it
also finds a path to reverse it from one corner to the other.

Everything is contstructed and held as graph, generate_mesh(x, y, shake) generates the graph,
whre x and y are size of the maze, and if shake is set to True, it offsetes each vertice to make it look random.

'''

#class for points
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # == operator overload
    def __eq__(self, other):
        if(isinstance(other, Point)):
            return self.x == other.x and self.y == other.y
        return False
    # != operator overload
    def __NE__(self, other):
        if(isinstance(other, Point)):
            return self.x != other.x or self.y != other.y
        return False
    # + operator overload
    def __add__(self, other):
        if(isinstance(other, Point)):
            return Point(self.x + other.x, self.y + other.y)

class Edge:
    #edge has two points
    def __init__(self, A, B):
        self.A = A
        self.B = B

    # == operator overload
    def __eq__(self, other):
        if(isinstance(other, Edge)):
            return self.A == other.A and self.B == other.B or self.A == other.B and self.B == other.A

class Triangle:
    #triangle has 3 points and 3 edges
    def __init__(self, A, B, C, id):
        self.A = A
        self.B = B
        self.C = C
        self.edge_A = Edge(self.A,self.B)
        self.edge_B = Edge(self.A,self.C)
        self.edge_C = Edge(self.C,self.B)
        self.mass_center = Point((self.A.x+self.B.x+self.C.x)/3, (self.A.y+self.B.y+self.C.y)/3)
        self.id = id
        self.visited = False

    def print(self):
        print("Triangle:\n","A: ",self.A.x, self.A.y,"B: ",self.B.x, self.B.y,"C: ",self.C.x, self.C.y)

    #function for checking if other triangle is a neighbour, is if has one common edge, or 2 common points
    def is_neighbour(self, other):
        if(isinstance(other, Triangle)):
            count = 0
            for i in [self.A, self.B, self.C]:
                for j in [other.A, other.B, other.C]:
                    if(i == j):
                        count = count+1
                        if(count == 2):
                            return True
            return False
    def common_edge(self, other):
        if(isinstance(other, Triangle)):
            for i in [self.edge_A, self.edge_B, self.edge_C]:
                for j in [other.edge_A, other.edge_B, other.edge_C]:
                    if(i == j):
                        return i

def generate_mesh(x: int, y: int, shake: bool = True) -> list:

    mesh = []
    if shake:
        for i in range(x):
            tmp = []
            for j in range(y):
                if i%2 == 0:
                    tmp.append(Point(i + rand(-1,1)/3,j + rand(-1,1)/3))
                else:
                    tmp.append(Point(i + rand(-1,1)/3,j-0.5 + rand(-1,1)/3))
            mesh.append(tmp.copy())
    else:
        for i in range(x):
            tmp = []
            for j in range(y):
                if i%2 == 0:
                    tmp.append(Point(i, j))
                else:
                    tmp.append(Point(i, j))
            mesh.append(tmp.copy())

    return mesh

def generate_edges(mesh):
    x = len(mesh)
    y = len(mesh[0])
    edges =[]
    z=0
    for i in range(x):
        z = z+1
        for j in range(y):
            if(i < x-1):
                edges.append(Edge(mesh[i][j],mesh[i+1][j]))
            if(j < y-1):
                edges.append(Edge(mesh[i][j],mesh[i][j+1]))
            if(i > 0 and j < y and j > 0 and z%2 == 0):
                edges.append(Edge(mesh[i-1][j-1],mesh[i][j]))
            if(i < x and j < y and i > 0 and j > 0 and  z%2 == 1):
                edges.append(Edge(mesh[i][j-1],mesh[i-1][j]))
            
    return edges

def generate_triangles(mesh):
    x = len(mesh)
    y = len(mesh[0])
    id = 0
    triangles = []
    for i in range(x-1):
        for j in range(y-1):
            if i%2 == 0:
                triangles.append(Triangle(mesh[i][j], mesh[i+1][j], mesh[i+1][j+1], id))
                id = id+1
                triangles.append(Triangle(mesh[i][j], mesh[i][j+1], mesh[i+1][j+1], id))
                id = id+1
            else:
                triangles.append(Triangle(mesh[i][j], mesh[i+1][j], mesh[i][j+1], id))
                id = id+1
                triangles.append(Triangle(mesh[i+1][j+1], mesh[i][j+1], mesh[i+1][j], id))
                id = id+1
    return triangles

def generate_maze(triangles, edges):

    print("Generating maze")
    # non-recursive randomized depth-first search
        
    #Choose the initial cell, mark it as visited and push it to the stack
    stack = []
    stack.append(triangles[0])
    triangles[0].visited = True
    stack[0].visited = True
    tree = []
    #While the stack is not empty
    while(len(stack) > 0):

        #Pop a cell from the stack and make it a current cell
        tmp = stack.pop()
        
        ##
        tree.append(tmp.id)
        ##

        #searching for neighbours
        neighbour_list = []
        for i in triangles:
            if(i.visited == False and i.is_neighbour(tmp)):
                neighbour_list.append(i.id)

        #If the current cell has any neighbours which have not been visited
        if(len(neighbour_list) > 0):
            #Push the current cell to the stack
            stack.append(tmp)

            #Choose one of the unvisited neighbours
            tmp_id = neighbour_list[rand(len(neighbour_list))]
            
            ##
            tree.append(tmp_id)
            ##

            #####Remove the wall between the current cell and the chosen cell
            tmp_edge = tmp.common_edge(triangles[tmp_id])
            for j in range(len(edges)-1):
                if(edges[j] == tmp_edge):
                    edges.pop(j)
                    break
            #Mark the chosen cell as visited and push it to the stack
            stack.append(triangles[tmp_id])
            triangles[tmp_id].visited = True
    edges.pop()
    return tree

def generate_path(tree, target_id):

    for i in range(len(tree)):
        if(tree[i] == target_id):
            del tree[i+1:]
            break
    out = []

    i = 0
    while i < len(tree)-1:
        j = i+1
        tmp = 0
        while j < len(tree) - 1:
            if(tree[i] == tree[j]):
                tmp = j
            j += 1
        for z in range(0,tmp - i):
            tree.pop(i)
            
        i += 1

def main():
    mesh = generate_mesh(15,10)
    edges = generate_edges(mesh)
    triangles = generate_triangles(mesh)

    tree = generate_maze(triangles, edges)

    generate_path(tree, triangles[-1].id)

    #collecting data for vertices for plotting
    x = []
    y = []
    for i in mesh:
        for j in i:
            x.append(j.x)
            y.append(j.y)

    #plotting edges
    for i in edges:
        pyplot.plot([i.A.x, i.B.x],[i.A.y, i.B.y])

    #collecting data for mass centers for plotting
    mx = []
    my = []
    for i in triangles:
        mx.append(i.mass_center.x)
        my.append(i.mass_center.y)
    mx.pop()
    my.pop()

    #collecting data for path for plotting
    path_x = []
    path_y = []
    for i in tree:
        path_x.append(triangles[i].mass_center.x)
        path_y.append(triangles[i].mass_center.y)

    pyplot.plot(path_x, path_y)
    pyplot.scatter(mx, my, s=1)
    pyplot.scatter(triangles[-1].mass_center.x, triangles[-1].mass_center.y)
    pyplot.scatter(x, y)
    pyplot.show()


if __name__ == '__main__':
    main()