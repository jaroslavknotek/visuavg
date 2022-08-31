import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib import pyplot as plt
from animplayer import Player

from triangulation import point_intersection

class TriangulationPlayer:

    def __init__(self, triangulation):
        self.triangulation = triangulation
        self._dummy_path=Path([(0,0)])
    
    
    def _sort_triangles(self, triangles,aux_points):
        auxiliary_triangles,non_aux_triangles = [],[]
        
        for triangle in triangles:
            pi = point_intersection(triangle.vertices, aux_points)
            if len(pi) == 0:
                non_aux_triangles.append(triangle)
            else:
                auxiliary_triangles.append(triangle)
        return auxiliary_triangles,non_aux_triangles
                
        
    def _reset_canvas(self, auxiliary_patch,triangle_patch_plt ):
        auxiliary_patch.set_path(self._dummy_path)
        triangle_patch_plt.set_path(self._dummy_path)
        
    def _get_used_points(self, triangles, aux_points):
        all_v = sum([list(t.vertices) for t in triangles],[])
        non_aux = [ p for p in all_v if p not in aux_points ]
        return np.array(non_aux)
    
    def _draw_triangles(self, snapshot, aux_points, triangle_patch_plt, auxiliary_patch ):
        auxiliary_triangles,non_aux_triangles=self._sort_triangles(snapshot.triangles,aux_points)
        
        if len(non_aux_triangles) >0:
            non_aux_triangle_path = self._get_triangle_path(non_aux_triangles)
            triangle_patch_plt.set(path=non_aux_triangle_path,fill=False)
        
        if len(auxiliary_triangles) > 0 and snapshot.draw_auxiliary:
            aux_triangle_path = self._get_triangle_path(auxiliary_triangles)
            auxiliary_patch.set(path=aux_triangle_path,fill=False, color='orange')

        
    def _draw_step(self, i, points, snapshot, points_plt, triangle_patch_plt,auxiliary_patch, xlim, ylim):
        
        self._reset_canvas(auxiliary_patch,triangle_patch_plt)
        
        aux_points = [ (x,y) for x,y in self.triangulation.auxiliary_points]
        
        used_points = self._get_used_points(snapshot.triangles, aux_points)
        
        if used_points.any():
             points_plt.set_data(used_points[:, 0], used_points[:, 1])
        
        self._draw_triangles(snapshot, aux_points,triangle_patch_plt, auxiliary_patch)
        plt.show()

    def _resolve_lim(self, arr, padding=10):
        return np.min(arr) - padding, np.max(arr) + padding

    def _get_triangle_path(self,triangles):
    
        triangle_codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY,
        ]

        verts = sum([[*triangle.vertices,triangle.vertices[0]] for triangle in triangles],[])
        codes = sum([triangle_codes for _ in range(len(triangles))],[])

        return Path(verts, codes)

    def _prepare_animation(self, points, triangulation_runs, xlim, ylim):

        xlim = xlim if xlim is not None else self._resolve_lim(points[:, 0])
        ylim = ylim if ylim is not None else self._resolve_lim(points[:, 1])

        fig = plt.figure()
        ax = plt.axes(xlim=xlim, ylim=ylim)
        
        (points_not_used_plt,) = ax.plot(points[:,0], points[:,1], "o",color="navy", alpha = .3)
        (points_plt,) = ax.plot([-100], [-100], "o",color="navy")
        
        auxiliary_patch = ax.add_patch(patches.PathPatch(self._dummy_path))
        triangle_patch=ax.add_patch(patches.PathPatch(self._dummy_path))
        
        def _animate(i):
            snapshot = triangulation_runs[i]
            ax.set_title(f"Step {i+1} - {snapshot.snapshot_type}")
            self._draw_step(i, points, snapshot, points_plt, triangle_patch,auxiliary_patch, xlim, ylim)
    
        return fig, _animate

    def get_function(self, xlim=None, ylim=None, interval=1000):

        fig, anim_fn = self._prepare_animation(self.triangulation.points, self.triangulation.snapshots, xlim, ylim)
        return FuncAnimation(fig, anim_fn, frames=len(self.triangulation.snapshots), interval=interval)

    def play_interactive(self, xlim=None, ylim=None, interval=1000):
        # TODO: the player uses only the last triangulation
        fig, anim_fn = self._prepare_animation(self.triangulation.points, self.triangulation.snapshots, xlim, ylim)

        return Player(fig, anim_fn, maxi=len(self.triangulation.snapshots), interval=interval)

    
