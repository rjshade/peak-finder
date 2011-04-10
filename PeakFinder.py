#!/usr/bin/env python

import getopt,sys,signal
from numpy import NaN, Inf, arange, isscalar, asarray
import csv

import matplotlib.pyplot as plt

def valToIdx( val, data ):
    '''
        find the index of first element in data
        which is >= val

        assuming data is ordered list of values...
    '''
    idx = 0
    cur = 0
    val = float(val)
    while cur < val and idx < len(data):
        cur = data[idx]
        idx += 1

    return int(idx)

class PeakFinder:
    def __init__( self, csv, delta, numnei, a, b, c ):

        self.Times,self.Data = self.ParseDataFromCSV( csv )
        self.delta = delta
        self.numnei = numnei
        self.Results = []

        self.A,self.B,self.C = self.ConvertTimesToIndices( a,b,c )

    def OnNewFile( self, csv ):
        self.Times,self.Data = self.ParseDataFromCSV( csv )


    def ConvertTimesToIndices( self, a,b,c ):
        #print( "a,b,c=",a,b,c)
        # if b,c haven't been specified then just parse the whole file
        if b == 0:
            b = len(self.Times) - 1

        if c == 0:
            #print('c==0 len(times=',len(times),times)
            c = len(self.Times) - 1

        # conert a,b,c to idx values
        return valToIdx(a,self.Times), valToIdx(b,self.Times), valToIdx(c,self.Times)

    def Reset( self, delta, numnei, a, b, c ):
        self.delta = delta
        self.numnei = numnei
        self.A, self.B, self.C = self.ConvertTimesToIndices( a,b,c ) 
        self.Results = []
        self.Run()

    def Run( self ):
        self.Results = []
        for i in arange(len(self.Data)):
            self.Results.append([])
            self.Results[i].append( self.PeakDetector( self.Data[i][self.A:self.B], self.delta, self.numnei) )
            self.Results[i].append( self.PeakDetector( self.Data[i][self.B:self.C], self.delta, self.numnei) )

    def Print( self ):
        for i in arange(len(self.Data)):
            atob = self.Results[i][0]
            btoc = self.Results[i][1]

            print
            print "****************   Data set %2d   ***********************" % (i+1)
            print
            print "\t----------   A -> B   ------------\n"

            self.PrintPeaks( self.A, atob )

            print "\t----------   B -> C   ------------\n"
            self.PrintPeaks( self.B, btoc )
            
            print

    def PrintPeaks( self, offset, result ):
        peaks = result['Maxima']
        bases = result['Bases']

        if len(peaks) == 0:
            print '\t\t    No peaks!\n'
            return
    
        peak_times = [self.Times[j] for j in [ peaks[i][0] + offset for i in arange(len(peaks)) ]]
        base_times = [self.Times[j] for j in [ bases[i][0] + offset for i in arange(len(bases)) ]]
        deltas     = [peaks[i][1] - bases[i][1] for i in arange(len(peaks))]
    
        isp_times = []
        for i in range(1,len(peaks)):
            isp_times.append( peak_times[i] - peak_times[i-1] )

    
        print '        \tTime\tBase\tPeak\tDelta\tISP\tFreq'
        #print "----------|------------------------------------------------------------------------------"
        for i in arange(len(peaks)):
            peak = peaks[i];
            base = bases[i];
            peak_time = peak_times[i]
            base_time = base_times[i]
     
            #print 'Peak %4d |\t%4d\t%4.3f\t%4.3f\t%4.3f\t' % (i+1,peak_time,base[1],peak[1],deltas[i]),
            print 'Peak %d\t\t%4d\t%4.3f\t%4.3f\t%4.3f\t' % (i+1,peak_time,base[1],peak[1],deltas[i]),
     
            if( i > 0):
                isp = isp_times[i-1]
                print '%4.3f' % (isp),
     
            print
      
        if len(peaks) > 1:
            avg_delta = (sum(deltas)/len(deltas))
            avg_isp   = (sum(isp_times)/len(isp_times));
            print 'Average  \t\t\t\t%4.3f\t%4.3f\t%4.6f' % (avg_delta,avg_isp,1/avg_isp)
     
        print "\n\n",
    
    def PeakDetector( self, v, delta, numnei=-1):
        """
        Converted from MATLAB script at http://billauer.co.il/peakdet.html
        
        Currently returns two lists of tuples, but maybe arrays would be better
        
        function [maxtab, mintab]=PeakDetector(v, delta, numnei)
        %PeakDetector   Detect peaks in a vector
        %               [MAXTAB, MINTAB] = PEAKDETECTOR(V, DELTA) finds the local
        %               maxima and minima ("peaks") in the vector V,
        %               MAXTAB and MINTAB consists of two columns. Column 1
        %               contains indices in V, and column 2 the found values.
        %      
        %               A point is considered a maximum peak if it has the maximal
        %               value, and was preceded (to the left) by a value lower by
        %               DELTA.
        %
        %               [MAXTAB, MINTAB, BASES] = PEAKDETECTOR(V,DELTA,NUMNEI) works as
        %               above and additionally finds peak 'bases' - defined as the lowest
        %               point within +- NUMNEI indices of the peak index.
        
        % Based on code by Eli Billauer
        """
        maxtab = []
        mintab = []
        bases = []
           
        x = arange(len(v))
        
        v = asarray(v)
        
        if len(v) != len(x):
            sys.exit('Input vectors v and x must have same length')
        
        if not isscalar(delta):
            sys.exit('Input argument delta must be a scalar')
        
        if delta <= 0:
            sys.exit('Input argument delta must be positive')
        
        mn, mx = Inf, -Inf
        mnpos, mxpos = NaN, NaN
        
        base = 0 
        basepos = NaN
        
        lookformax = True
        
        for i in arange(len(v)):
            this = v[i]
            if this > mx:
                mx = this
                mxpos = x[i]
            if this < mn:
                mn = this
                mnpos = x[i]
    
            if lookformax:
                if this < mx-delta:
                    maxtab.append((mxpos, mx))
                    mn = this
                    mnpos = x[i]
    
                    if numnei > 0:
                        base,basepos = self.getLowestInNeighbourhood( v, mxpos, numnei )
                        bases.append((basepos,base))
    
                    lookformax = False
    
            else:
                if this > mn+delta:
                    mintab.append((mnpos, mn))
                    mx = this
                    mxpos = x[i]
                    lookformax = True
    
        return {'Maxima':maxtab,'Minima':mintab, 'Bases':bases}
    
    def getLowestInNeighbourhood( self, data, index, numnei ):
        """
        finds the lowest value in vector data in the range
        (data[index - numnei], data[index + numnei])
        """
    
        minIdx = max(index - numnei, 0)
        maxIdx = min(index + numnei, len(data))
    
        lowest = +Inf
        lowest_idx = minIdx
    
        for i in range(minIdx,maxIdx):
            if data[i] < lowest:
                lowest = data[i]
                lowest_idx = i
    
        #print minIdx, maxIdx, lowest, lowest_idx
        return lowest,lowest_idx
    
    def CheckOutput( self, peaks, bases ):
        if len(peaks) == 0:
            print 'Warning: No peaks found'
            return False
    
        if len(peaks) != len(bases):
            print 'Error: unequal number of peaks/bases...'
            return False
    
        return True
    
    def Plot( self, fig ):
        fig.clear()
        for i in arange(len(self.Data)):
            data = self.Data[i]
            atob = self.Results[i][0]
            btoc = self.Results[i][1]
            #times = [self.Times[j] for j in [ xima'][i][0] for i in arange(len(atob['Maxima'])) ]]
            times = self.Times
            ax = fig.add_subplot(len(self.Data),1,i+1)
            ax.clear()

            ax.plot(times, data, color='k')
            ax.grid(True)

            if( self.A < len(self.Times) ):
                ax.axvline( x=self.Times[self.A],ymin=0, ymax=2,color='k')
            if( self.B < len(self.Times) ):
                ax.axvline( x=self.Times[self.B],ymin=0, ymax=2,color='r')
            if( self.C < len(self.Times) ):
                ax.axvline( x=self.Times[self.C],ymin=0, ymax=2,color='k')
     
            self.PlotPeaks( ax, '', self.A, atob, times )
            self.PlotPeaks( ax, '', self.B, btoc, times )
    
    def PlotPeaks( self, ax, label, offset, result, times ):
        peaks = result['Maxima']
        bases = result['Bases']
        for i in arange(len(peaks)):
            peak = list(peaks[i])
            peak[0] = peak[0] + offset
            base = list(bases[i])
            base[0] = base[0] + offset
            self.annotate( ax, times, '', peak, +0.1)
            self.annotate( ax, times, '', base, -0.1, 'blue' )
    
    def annotate( self, ax, times,  caption, point, offset=0.1, color='red' ):
        ax.annotate(caption, xy=(times[point[0]], point[1]),  xycoords='data',
                    xytext=(times[point[0]], point[1] + offset), textcoords='data',
                    arrowprops=dict(facecolor=color, shrink=0.05),
                    horizontalalignment='center', verticalalignment='top',
                    )

    def ParseDataFromCSV( self, filename ):
        """
        expects filename to be a CSV file in which the first column
        is timestamps, and the remaining columns are data series
        """
    
        csv_file = csv.reader(open(filename, "rb" ))
        csv_data = []
        csv_data.extend(csv_file)
    
        times = []
    
        # fill data_series array with an array per column of data
        data = [ [] for i in range(len(csv_data[0])-1)]
    
        # now fill each array in data_series with the CSV data
        for row in csv_data:
            times.append(float(row[0]))
            for i in arange(len(row[1:])):
                data[i].append(float(row[i+1]))
    
        return times, data
    
    
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
    filename, delta, numnei, plotfig, a, b, c = ParseArgs( sys.argv )

    myPeakFinder = PeakFinder( filename, delta, numnei, a, b, c )

    myPeakFinder.Run()
    myPeakFinder.Print()

    if plotfig:
        fig = plt.figure()
        myPeakFinder.Plot(fig)
        plt.show()

if __name__=="__main__":
    main()

