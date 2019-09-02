import numpy as np
import os
import textwrap
import tkinter as tk
import tkinter.ttk as tk_ttk

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

TREEVIEW_SELECT_EVENT = '<<treeview_select>>'

class FullDisplay(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=0, column=0, sticky='nsew')
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        self.tree = DirectoryViewer(self)
        self.canvas = GraphPlotter(self)
        self.bind(TREEVIEW_SELECT_EVENT, self.treeview_new_selection)

    def treeview_new_selection(self, event):
        self.canvas.draw_plot(self.tree.get_selected_file())

class DirectoryViewer(tk.Frame):
    def __init__(self, master=None, path='.'):
        super().__init__(master)
        self.master = master
        self.grid(row=0, column=0, sticky='nsw')
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        self.setup_tree(path)

    def tell_master_select(self, event):
        self.master.event_generate(TREEVIEW_SELECT_EVENT)

    def get_selected_file(self):
        return self.build_path(self.tree.focus())

    def build_path(self, curr_id):
        curr_item = self.tree.item(curr_id)
        parent_id = self.tree.parent(curr_id)
        curr_item_path = curr_item['text']
        while parent_id != '':
            parent = self.tree.item(parent_id)
            curr_item_path = os.path.join(parent['text'], curr_item_path)
            curr_id = parent_id
            curr_item = self.tree.item(curr_id)
            parent_id = self.tree.parent(curr_id)
        return curr_item_path

    def setup_tree(self, path):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.tree = tk_ttk.Treeview(self)
        self.tree.bind('<<TreeviewSelect>>', self.tell_master_select)
        self.tree.grid(row=0, column=0, sticky='nsw')

        ysb = tk_ttk.Scrollbar(self,
                               orient='vertical',
                               command=self.tree.yview)
        ysb.grid(row=0, column=1, sticky='ns')

        xsb = tk_ttk.Scrollbar(self,
                               orient='horizontal',
                               command=self.tree.xview)
        xsb.grid(row=1, column=0, sticky='ew')

        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)

        path = os.path.abspath(path)
        self.path = path
        self.tree.heading('#0', text=path, anchor='w')

        root_node = self.tree.insert('', 'end', text=path, open=True)
        self.process_directory(root_node, path)

    def process_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            oid = self.tree.insert(parent, 'end', text=p, open=False)
            if isdir:
                self.process_directory(oid, abspath)

class GraphPlotter(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=0, column=1, sticky='nsew')
        master.rowconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        self.load_plotters()
        self.setup_canvas()
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def setup_canvas(self):
        self.figure = matplotlib.figure.Figure(figsize=(5, 5), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.draw_plot(None)
        self.canvas.get_tk_widget().grid(column=0, row=0, sticky='nsew')

    def load_plotters(self):
        import plotting_modules
        self.plotters = {module.FILE_EXTENSION: module.DEFAULT_PLOTTER
                         for module
                         in plotting_modules.__all__}

    def draw_plot(self, file):
        self.axes.clear()
        if file is None or os.path.isdir(file):
            plot_dir(file, self.axes)
        elif os.path.splitext(file)[1] in self.plotters:
            try:
                self.plotters[os.path.splitext(file)[1]](file, self.axes)
            except Exception as e:
                plot_error(e, self.axes)
        else:
            plot_error(ValueError('cannot plot {}'.format(file)), self.axes)
        self.canvas.draw_idle()

def plot_error(error, ax):
    msg = 'An error occurred:\n'
    msg += type(error).__name__ + '\n'
    msg += '\n'.join(textwrap.wrap(str(error), 60))
    ax.text(0, 0, msg)
    ax.set_axis_off()

def plot_dir(file, ax):
    ax.set_axis_off()

if __name__ == '__main__':
    root = tk.Tk()
    app = FullDisplay(master=root)
    app.mainloop()