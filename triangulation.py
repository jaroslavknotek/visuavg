from typing import NamedTuple
import numpy as np

class Triangle():
    
    def __init__(self, vertices):
        self.adjacent = []
        self.vertices = vertices
        
        a,b,c = vertices
        self.edges = [(a,b),(b,c),(c,a)]
        
    
class TriangulationSnapshot(NamedTuple):
    triangles: list[Triangle]
    snapshot_type:str
    draw_auxiliary:bool = True

class Triangulation(NamedTuple):
    snapshots:list[TriangulationSnapshot]
    points:list[(int,int)]
    auxiliary_points:list[(int,int)]

def get_auxiliary_pts(pts):
    max_value = np.max(pts)
    padding = max_value/50
    max_x = int(max_value*2 + padding)
    max_y = int(max_value*2 + padding)
    
    return ((-1,-1),(-1,max_y), (max_x,-1))

from typing import NamedTuple


def _sort_on_circle(a,b,c):
    avg_pt = np.mean([a,b,c],axis =0)
    pp = np.array([a,b,c])
    complex_nums = np.array([  complex(x,y) for x,y in pp])
    ang = np.angle(complex_nums - complex(avg_pt[0],avg_pt[1]))
    
    pp_s_idxs = np.argsort(ang)
    return  [(x,y) for x,y in pp[pp_s_idxs]]

def is_in_circle(a,b,c,d):
    ax,ay = a
    bx,by = b
    cx,cy = c
    dx,dy = d
    mat = np.array([[ax-dx, ay-dy,(ax**2-dx**2) + (ay**2-dy**2)],
                    [bx-dx, by-dy,(bx**2-dx**2) + (by**2-dy**2)],
                    [cx-dx, cy-dy,(cx**2-dx**2) + (cy**2-dy**2)]     
    ])
    
    return np.linalg.det(mat)>0


def _sign(a,b,c):
    ax,ay = a
    bx,by = b
    cx,cy = c
    return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)


def _is_in_aabb( a, b, p):
    px,py = p
    ax,ay = a
    bx,by = b
    return bx <= px <= ax and by <= py <= ay

def is_in_triangle(a,b,c,p):
    s1 = _sign( a,b,p) <= 0
    s2 = _sign(b,c,p) <= 0
    s3 = _sign(c,a,p) <= 0
    
    # numerically unstable - comparing floats
    return (s1 == s2 and s2 == s3) and _is_in_aabb(map(max, a,b,c), map(min, a,b,c), p)


def get_intersected_triangle(triangles, point):
    for i,triangle in enumerate(triangles):
        if is_in_triangle(*triangle.vertices, point):
            return triangle

def replace_triangle(all_triangles, old_triangle, new_triangles):
    oa,ob,oc = old_triangle.vertices
    idx = -1
    for i,triangle in enumerate(all_triangles):
        a,b,c = triangle.vertices
        if a==oa and b==ob and c == oc:
            idx = i
            break
    
    all_triangles.pop(idx)
    [all_triangles.append(t) for t in new_triangles]

    
def get_triangle_adjacent_by_edge(triangles,edge):
    for t in triangles:
        for e in t.edges:
            
            # equality comparison
            pts = np.unique(np.array([e,edge]).reshape(4,2),axis=0)
            if len(pts)==2:
                return t
    
    return None


def subdivide_triangle(old_triangle, point):
    a,b,c = old_triangle.vertices
    
    old_adjacent_triangles =old_triangle.adjacent
    
    for old_adj in old_adjacent_triangles:
        old_adj.adjacent = [  t for t in old_adj.adjacent if t != old_triangle]
        
    triangles = [ Triangle(vertices=(*edge,point)) for edge in old_triangle.edges]
    
    for t,edge in zip(triangles,old_triangle.edges):
        t.adjacent = [  tt for tt in triangles if t != tt]
        adj = get_triangle_adjacent_by_edge(old_adjacent_triangles, edge)
        if adj is not None:
            t.adjacent.append(adj)
            adj.adjacent.append(t)

    return triangles    

def point_intersection(arr1,arr2):
    return [ p for p in arr1 if p in arr2]

 
def clean_auxiliary_points(triangles, auxiliary_pts):
    cleaned_triangles = [t for t in triangles if all([ v not in auxiliary_pts  for v in t.vertices ])]
    
    for c in cleaned_triangles:
        to_remove = []
        for a in c.adjacent:
            for v in a.vertices:
                if v in auxiliary_pts:
                    
                    to_remove.append(a)
        for t in to_remove:
            c.adjacent.remove(t)
    return cleaned_triangles

def get_flipped(a,b,c,p, common_segment):
    a_in = a in common_segment
    b_in = b in common_segment
    c_in = c in common_segment

    if a_in and b_in:
        new_triangle_1 = Triangle(vertices= [a,c,p])
        new_triangle_2 = Triangle(vertices= [b,c,p])
    elif a_in and c_in:
        new_triangle_1 = Triangle(vertices=[a,b,p])
        new_triangle_2 = Triangle(vertices=[b,c,p])
    else:
        new_triangle_1 = Triangle(vertices=[a,b,p])
        new_triangle_2 = Triangle(vertices=[a,c,p])

    new_triangle_1.adjacent.append(new_triangle_2)
    new_triangle_2.adjacent.append(new_triangle_1)
    return new_triangle_1, new_triangle_2

def get_triangle_center_of_mass(a,b,c):
    return (np.sum(np.array([a,b,c]),axis=0)/3)

def reconnect_flipped_triangles(t1,t2, all_adjacent):
    for t in [t1, t2]:
        for a in all_adjacent:
            intersection = point_intersection(a.vertices, t.vertices)
            if len(intersection)==2:
                a.adjacent.append(t)
                t.adjacent.append(a)

def legalize(triangles, triangles_snapshot):
    has_changed = True
    while has_changed:
        has_changed = False
        for triangle in triangles:
            for adj_triangle in triangle.adjacent:
                for p in adj_triangle.vertices:
                    a,b,c = _sort_on_circle(*triangle.vertices)
                    if is_in_circle(a,b,c,p):
                        all_adjacent = sum([a.adjacent for a in [adj_triangle, triangle] ],[]) 
                        all_adjacent.remove(triangle)
                        all_adjacent.remove(adj_triangle)

                        # remove 
                        for t in [adj_triangle, triangle]:
                            ad = list(t.adjacent)
                            for at in ad:
                                t.adjacent.remove(at)
                                at.adjacent.remove(t)


                        common_segment= point_intersection(triangle.vertices,adj_triangle.vertices)

                        new_triangle_1, new_triangle_2 = get_flipped(a,b,c,p, common_segment)
                        reconnect_flipped_triangles(new_triangle_1,new_triangle_2,all_adjacent)

                        triangles.remove(adj_triangle)
                        triangles.remove(triangle)

                        triangles.append(new_triangle_1)
                        triangles.append(new_triangle_2)

                        has_changed = True
                        triangles_snapshot.append( TriangulationSnapshot( triangles=list(triangles),snapshot_type='Legalization'))

    

def delaunay_triangulate_with_snapshots(pts_arr):
    pts = [(p1,p2) for (p1,p2) in pts_arr] 
    auxiliary_pts = get_auxiliary_pts(pts)
    
    
    triangles_snapshot = []
    triangles = [Triangle(vertices=auxiliary_pts)]
    
    triangles_snapshot.append( TriangulationSnapshot( triangles=list(triangles),snapshot_type='Auxiliary triangle'))
    for point in pts:
        triangle = get_intersected_triangle(triangles, point)
        new_triangles = subdivide_triangle(triangle,point)
        replace_triangle(triangles,triangle, new_triangles)
        
        
        #return triangles
        triangles_snapshot.append( TriangulationSnapshot( triangles=list(triangles),snapshot_type=f'Triangles - added {point}'))
        # delaunay
        legalize(triangles,triangles_snapshot)
              
        
    
    final = clean_auxiliary_points(triangles, auxiliary_pts)
    triangles_snapshot.append( TriangulationSnapshot( triangles=list(final),snapshot_type='Auxiliary data cleaned', draw_auxiliary=False))
    return Triangulation(snapshots=triangles_snapshot, auxiliary_points=np.array(auxiliary_pts),points=pts_arr)
