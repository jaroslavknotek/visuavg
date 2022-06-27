import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from animplayer import Player


def _draw_step(i, points, lines, points_plt, line_plots, xlim, ylim):

    points_plt.set_data(points[:, 0], points[:, 1])
    [l_plt.set_data([], []) for l_plt in line_plots]
    [
        l_plt.set_data(line[:, 0], line[:, 1])
        for line, l_plt in zip(lines, line_plots[:i])
    ]

    plt.show()


def _replace_infs(lines, x_lim, y_lim):
    lines_pts = lines.reshape((len(lines) * 2, 2))
    x_cor = lines_pts[:, 0]
    x_cor[np.isinf(x_cor) * x_cor > 0] = x_lim[1]
    x_cor[np.isinf(x_cor) * x_cor < 0] = x_lim[0]

    y_cor = lines_pts[:, 1]
    y_cor[np.isinf(y_cor) * y_cor > 0] = y_lim[1]
    y_cor[np.isinf(y_cor) * y_cor < 0] = y_lim[0]
    return lines_pts.reshape(lines.shape)


def _resolve_lim(arr, padding=10):
    return np.min(arr) - padding, np.max(arr) + padding


def _prepare_animation(points, lines, xlim, ylim):

    xlim = xlim if xlim is not None else _resolve_lim(points[:, 0])
    ylim = ylim if ylim is not None else _resolve_lim(points[:, 1])

    lines_noinf = _replace_infs(lines, xlim, ylim)
    fig = plt.figure()
    ax = plt.axes(xlim=xlim, ylim=ylim)
    (points_plt,) = ax.plot([], [], "o")
    line_plots = [ax.plot([], [], c="k")[0] for _ in range(len(lines))]

    def _animate(i):
        ax.set_title(f"Step {i} out of {len(points)}")
        _draw_step(i, points, lines, points_plt, line_plots, xlim, ylim)

    return fig, _animate


def draw_static_animation(points, lines, xlim=None, ylim=None, interval=1000):
    fig, anim_fn = _prepare_animation(points, lines, xlim, ylim)
    return FuncAnimation(fig, anim_fn, frames=len(points) + 1, interval=interval)


def draw_interactive_animation(points, lines, xlim=None, ylim=None, interval=1000):
    fig, anim_fn = _prepare_animation(points, lines, xlim, ylim)
    return Player(fig, anim_fn, maxi=len(points) + 1, interval=interval)
