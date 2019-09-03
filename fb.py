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
        self.tree = DirectoryViewer(self)
        self.canvas = GraphPlotter(self)
        self.bind(TREEVIEW_SELECT_EVENT, self.treeview_new_selection)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=10)

    def treeview_new_selection(self, event):
        self.canvas.draw_plot(self.tree.get_selected_file())

class DirectoryViewer(tk.Frame):
    def __init__(self, master=None, path='.'):
        super().__init__(master)
        self.master = master
        self.grid(row=0, column=0, sticky='nswe')
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
        self.tree.grid(row=0, column=0, sticky='nswe')

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
        self.opened = set([root_node])
        for p in os.listdir(path):
            self.insert_node(root_node, p, os.path.join(path, p))
        self.tree.bind('<<TreeviewOpen>>', self.open_node)

    # insert_node() and open_node() are for lazy loading
    def insert_node(self, parent, text, path):
        node = self.tree.insert(parent, 'end', text=text, open=False)
        if os.path.isdir(path):
            self.tree.insert(node, 'end') # dummy to show the dir icon

    def open_node(self, event):
        curr_node = self.tree.focus()
        abspath = self.build_path(curr_node)
        if os.path.isdir(abspath) and curr_node not in self.opened:
            self.tree.delete(self.tree.get_children(curr_node))
            for p in os.listdir(abspath):
                self.insert_node(curr_node, p, os.path.join(abspath, p))
            self.opened.add(curr_node)

    # process_directory() does eager loading
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
        self.load_plotters()
        self.setup_canvas()
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def setup_canvas(self):
        self.figure = matplotlib.figure.Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.draw_plot(None)
        self.canvas.get_tk_widget().grid(column=0, row=0, sticky='nsew')

    def load_plotters(self):
        import plotting_modules
        self.plotters = {module.FILE_EXTENSION: module.DEFAULT_PLOTTER
                         for module
                         in plotting_modules.__all__}

    def draw_plot(self, file):
        self.figure.clf()
        if file is None or os.path.isdir(file):
            plot_dir(file, self.figure)
        elif os.path.splitext(file)[1] in self.plotters:
            try:
                self.plotters[os.path.splitext(file)[1]](file, self.figure)
            except Exception as e:
                plot_error(e, self.figure)
        else:
            plot_error(ValueError('cannot plot {}'.format(file)), self.figure)
        self.canvas.draw_idle()

def plot_error(error, fig):
    msg = 'An error occurred:\n'
    msg += type(error).__name__ + '\n'
    msg += '\n'.join(textwrap.wrap(str(error), 60))
    ax = fig.add_subplot(111)
    ax.text(0, 0, msg)
    ax.set_axis_off()

def plot_dir(file, fig):
    ax = fig.add_subplot(111)
    ax.set_axis_off()

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('800x500')
    app = FullDisplay(master=root)
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    app.mainloop()
