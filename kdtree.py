from queue import Queue

import numpy as np

# code adapted from https://en.wikipedia.org/wiki/K-d_tree
TOP, BOTTOM, LEFT, RIGHT = 0, 1, 2, 3


class NNNode:
    def __init__(
        self, median_point, direction, boundaries, boundaries_projection, left, right
    ):
        self.median_point = median_point
        self.direction = direction
        self.boundaries = boundaries
        self.boundaries_projection = boundaries_projection
        self.left = left
        self.right = right

    def __repr__(self):
        left_str = "\n-".join(str(self.left).split("\n"))
        right_str = "\n-".join(str(self.right).split("\n"))
        return f"{self.median_point}\n-L:{left_str}\n-R:{right_str}"


def nnkdtree(point_list, boundaries=None, depth: int = 0):
    if point_list.size == 0:
        return None

    if boundaries is None:
        boundaries = [None, None, None, None]

    k = len(point_list[0])
    axis = depth % k
    direction = "tb" if axis == 0 else "lr"
    point_list = point_list[point_list[:, axis].argsort()]
    median_idx = len(point_list) // 2
    median = point_list[median_idx]

    # intended copy
    left_boundaries, right_boundaries = list(boundaries), list(boundaries)

    if axis == 0:  # vertical split
        left_boundaries[RIGHT] = median[0]
        right_boundaries[LEFT] = median[0]
    else:  # horizontal split
        left_boundaries[TOP] = median[1]
        right_boundaries[BOTTOM] = median[1]

    boundaries_projections = _get_boundaries_projection(median, boundaries)
    return NNNode(
        median,
        direction,
        boundaries,
        boundaries_projections,
        nnkdtree(point_list[:median_idx], left_boundaries, depth + 1),
        nnkdtree(point_list[median_idx + 1 :], right_boundaries, depth + 1),
    )


def _get_boundaries_projection(point, boundaries):
    top_boundary, bottom_boundary, left_boundary, right_boundary = boundaries
    x, y = point

    return [
        (x, top_boundary) if top_boundary is not None else None,
        (x, bottom_boundary) if bottom_boundary is not None else None,
        (left_boundary, y) if left_boundary is not None else None,
        (right_boundary, y) if right_boundary is not None else None,
    ]


def _bfs(node):
    q = Queue()
    q.put(node)
    nodes = []
    while not q.empty():
        current = q.get()
        if current is None:
            continue
        nodes.append(current)

        q.put(current.left)
        q.put(current.right)
    return nodes


def collect_lines(node):
    lines = []
    nodes = _bfs(node)

    for node in nodes:
        p_x, p_y = node.median_point
        # axs.plot(p_x,p_y,'o')
        start_point = []
        end_point = []
        tb_boundaries = node.boundaries[TOP], node.boundaries[BOTTOM]
        lr_boundaries = node.boundaries[LEFT], node.boundaries[RIGHT]
        if node.direction == "tb":

            top_boundary, bottom_boundary = tb_boundaries
            y1 = top_boundary if top_boundary else np.inf
            y2 = bottom_boundary if bottom_boundary else -np.inf
            x1, x2 = p_x, p_x

            start_point = [x1, y1]
            end_point = [x2, y2]
        else:  # direction = lr
            left_boundary, right_boundary = lr_boundaries

            y1, y2 = p_y, p_y

            x1 = left_boundary if left_boundary else -np.inf
            x2 = right_boundary if right_boundary else np.inf

            start_point = [x1, y1]
            end_point = [x2, y2]
        lines.append([start_point, end_point])
    return np.array(lines)


def collect_points(node):
    nodes = _bfs(node)
    return np.array([node.median_point for node in nodes])
