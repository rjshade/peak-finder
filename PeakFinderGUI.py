#!/usr/bin/env python
"""
This demo demonstrates how to embed a matplotlib (mpl) plot 
into a PyQt4 GUI application, including:

* Using the navigation toolbar
* Adding data to the plot
* Dynamically modifying the plot's properties
* Processing mpl events
* Saving the plot to a file from a menu

The main goal is to serve as a basis for developing rich PyQt GUI
applications featuring mpl plots (using the mpl OO API).

Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 19.01.2009
"""
import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import getopt

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

import PeakFinder


class PeakFinderGUI(QMainWindow):
    #def __init__(self, parent=None):
    def __init__( self, csv, delta, numnei, a, b, c, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Demo: PyQt with matplotlib')

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.spinboxes['a'].setValue(int(a))
        self.spinboxes['b'].setValue(int(b))
        self.spinboxes['c'].setValue(int(c))
        self.spinboxes['numnei'].setValue(int(numnei))
        self.spinboxes['delta'].setValue(float(delta))
        self.csv = csv

        self.myPeakFinder = PeakFinder.PeakFinder( csv, delta, numnei, a, b, c )
        self.myPeakFinder.Run()
        self.myPeakFinder.Print()

        self.on_draw()




    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:
        
         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    
    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        
        QMessageBox.information(self, "Click!", msg)
    
    def on_draw(self):
        """ Redraws the figure
        """
        self.fig.clear()

        self.myPeakFinder.Plot(self.fig)
        
        self.canvas.draw()
    
    def on_recalculate(self):
        A = self.spinboxes['a'].value()
        B = self.spinboxes['b'].value()
        C = self.spinboxes['c'].value()
        delta = self.spinboxes['delta'].value()
        numnei = self.spinboxes['numnei'].value()
        self.myPeakFinder.Reset( delta, numnei, A, B, C   )
        self.myPeakFinder.Print()

        self.on_draw()

    def new_spin_box( self, label, minval, maxval, double=False ):
        if double:
            spinbox = QDoubleSpinBox()
        else:
            spinbox = QSpinBox()
            
        spinbox.setMinimumWidth(100)
        spinbox.setMinimum(minval)
        spinbox.setMaximum(maxval)
        self.connect(spinbox, SIGNAL('editingFinished ()'), self.on_recalculate)
 
        #hbox.addWidget(spinbox)
        #hbox.setAlignment(spinbox, Qt.AlignVCenter)

        return spinbox

    def create_main_frame(self):
        self.main_frame = QWidget()
        #self.main_frame.resize(500,500)
        #self.main_frame.setGeometry(500,500,500,500)
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        #self.dpi = 100
        #self.fig = Figure((5.0, 4.0), dpi=self.dpi,linewidth=0.1)
        self.fig  = Figure()
        #self.fig  = Figure(figsize=(5,5),dpi=100)

        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        #self.axes = self.fig.add_subplot(111)
        




        # Bind the 'pick' event for clicking on one of the bars
        #
        #self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        #self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Other GUI controls
                      
        self.draw_button = QPushButton("&Recalculate")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.on_recalculate)
        
        #self.grid_cb = QCheckBox("Show &Grid")
        #self.grid_cb.setChecked(False)
        #self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        #
        # Layout with box sizers
        # 
        self.spinboxes = {
                'a':self.new_spin_box( 'a', 0, 2000 ) ,
                'b':self.new_spin_box( 'b', 0, 2000 ) ,
                'c':self.new_spin_box( 'c', 0, 2000 ) ,
                'numnei':self.new_spin_box( 'numnei', 0, 100 ) ,
                'delta':self.new_spin_box( 'delta',  0.001, 0.2,double=True ) }

        print self.spinboxes
        gridlayout = QGridLayout()
        layout_order = ['a','b','c','numnei','delta']
        row = 1
        for lbl in layout_order:
            print lbl
            v = self.spinboxes[lbl]

            label = QLabel(lbl)
            label.setMinimumWidth(50)
            gridlayout.addWidget(label,row,0)
            gridlayout.setAlignment(label, Qt.AlignVCenter)
            gridlayout.addWidget(v,row,1)
            gridlayout.setAlignment(v, Qt.AlignVCenter)
            row += 1

        # and the draw button...
        gridlayout.addWidget(self.draw_button,row,0)
        #gridlayout.setAlignment(self.draw_button, Qt.AlignVCenter)
        

        self.open_button = QPushButton("&Open CSV")
        self.connect( self.open_button, SIGNAL('clicked()'), self.on_new_file)
        gridlayout.addWidget( self.open_button, row,1 )
        gridlayout.setAlignment(self.open_button, Qt.AlignVCenter)


        hbox = QGridLayout()
        hbox.addWidget(self.canvas,0,0)
        #hbox.addWidget(self.mpl_toolbar)
        hbox.addLayout(gridlayout,0,1)
        

        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)
    
    def on_new_file(self):
        filename = QFileDialog.getOpenFileName( self, 'Open CSV file' )
        self.csv = filename
        self.myPeakFinder.OnNewFile( self.csv )
        self.myPeakFinder.Run()
        self.on_draw()


    def create_status_bar(self):
        self.status_text = QLabel("bugs: robbie.shade@gmail.com")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

def ParseArgs( argv ):
    filename = "data.csv"
    delta    = 0.2 # jump in value to determine maxima/minima
    numnei   = 10 # +- numnei indices are searched to find bases
    a = 50
    b = 500 
    c = 1500
    
    try:
        opts, args = getopt.getopt(argv[1:], "f:d:n:pa:b:c:", ["file=", "delta=", "numnei=", "plot"])
    except getopt.GetoptError, err:
        print str(err)
        #usage()
        print 'usage: ', argv[0], ' --file data.csv --delta 0.2 --numnei 10 -a 50 -b 500 -c 1500'
        sys.exit(2)
    
    output = None
    verbose = False
    plotfig = False
    for o, arg in opts:
        if o in ("-f", "--file"):
            filename = arg
        elif o in ("-d", "--delta"):
            delta = arg
        elif o in ("-n", "--numnei"):
            numnei = arg
        elif o in ("-p", "--plot"):
            plotfig = True
        elif o in ("-a"):
            a = arg
        elif o in ("-b"):
            b = arg
        elif o in ("-c"):
            c = arg
        else:
            assert False, "unhandled option"
    
    return filename, float(delta), int(numnei), plotfig, a, b, c
    
 

def main():
    app = QApplication(sys.argv)
    filename, delta, numnei, plotfig, a, b, c = ParseArgs( sys.argv )
    form = PeakFinderGUI( filename, delta, numnei, a, b, c )
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
