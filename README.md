# File browser

This file browser allows you to explore a directory tree and produce quick
summary plots of data files.

## Installation

This project is currently only a script. To use,

```
$ git clone https://github.com/gfetterman/file_browser.git
$ cd file_browser
$ python fb.py
```

## Custom plot display

Only rudimentary plotting of `.npy` files is supported by default, but the
browser supports displaying user-defined plots as well.

To create a custom plot, you must place a new `.py` file into the
`plotting_modules` subdirectory. To be usable by the file browser, the file must
meet the following criteria:

1. its name must not begin with double underscores
2. it must contain valid Python code, and be importable
3. it must define a top-level variable named `FILE_EXTENSION`, which contains a
   string describing a file extension that the associated plotting function will
   handle
   
   Example:
   ```Python
   FILE_EXTENSION = '.npy'
   ```
4. it must define a top-level variable named `DEFAULT_PLOTTER` containing a
   function object
   
   Example:
   ```Python
   DEFAULT_PLOTTER = basic_npy_plot
   ```
5. `DEFAULT_PLOTTER` must be a function that takes one string argument,
   representing a data file to be loaded and plotted, and one `matplotlib`
   `Figure` object, onto which the function will plot the data. The function may
   raise any exception; they will be caught and displayed in place of a plot.
   Its return value will be discarded.
   
   For an example, see the included `plotting_modules/plot_npy.py` file.

## Caveats

This browser is very much a work in progress, and is likely to be brittle.

The most obvious current limitations (there are surely others):

* only one plotting function can be specified for each file extension
* the user has no run-time control over plot display

Hopefully these will be addressed when I have time...
