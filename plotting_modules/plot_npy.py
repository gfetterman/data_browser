import numpy as np
import os

def basic_npy_plot(path, ax):
    assert os.path.splitext(path)[1] == FILE_EXTENSION
    data = np.load(path)
    if len(data.shape) == 1:
        ax.plot(data)
    elif len(data.shape) == 2:
        x_vals = data[0, :]
        for idx in range(1, data.shape[0]):
            ax.plot(x_vals, data[idx, :])
    else:
        raise ValueError('can only plot 1- or 2-dimensional time series')
    ax.set_title(os.path.split(path)[1])
    return ax

FILE_EXTENSION = '.npy'
DEFAULT_PLOTTER = basic_npy_plot
