#!/usr/bin/env python

import getopt,sys,signal
from numpy import NaN, Inf, arange, isscalar, asarray
import csv

import matplotlib.pyplot as plt



def PeakDetector(v, delta, numnei=-1):
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
    
    base = v[0] 
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
                    base,basepos = getLowestInNeighbourhood( v, mxpos, numnei )
                    bases.append((basepos,base))

                lookformax = False

        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return maxtab, mintab, bases



def getLowestInNeighbourhood( data, index, numnei ):
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



def CheckOutput( peaks, bases ):
    if len(peaks) == 0:
        print 'Warning: No peaks found'
        return False

    if len(peaks) != len(bases):
        print 'Error: unequal number of peaks/bases...'
        return False

    return True


def PrintOutput( data_set, peaks, bases, times, filename ):

    f = open('output/' + filename + '_out.csv', 'a');

    print
    print "****************   Data set %2d   ***********************" % data_set
    print
    f.write('Data set %2d\n' % data_set)

    peak_times = [times[j] for j in [ peaks[i][0] for i in arange(len(peaks)) ]]
    base_times = [times[j] for j in [ bases[i][0] for i in arange(len(bases)) ]]
    deltas     = [peaks[i][1] - bases[i][1] for i in arange(len(peaks))]

    isp_times = []
    for i in range(1,len(peaks)):
        isp_times.append( peak_times[i] - peak_times[i-1] )

    print '        \tTime\tBase\tPeak\tDelta\tISP\tISP freq (s^-1)\tISP freq (min^-1)'
    f.write('Peak#,Time,Base,Peak,Delta,ISP,ISP freq (s^-1),ISP freq (min^-1)\n')
    print "----------|------------------------------------------------------------------------------"
    for i in arange(len(peaks)):

        peak = peaks[i];
        base = bases[i];
        peak_time = peak_times[i]
        base_time = base_times[i]

        print 'Peak %4d |\t%4d\t%4.3f\t%4.3f\t%4.3f\t' % (i+1,peak_time,base[1],peak[1],deltas[i]),
        f.write('%4d,%4d,%4.3f,%4.3f,%4.3f,' % (i+1,peak_time,base[1],peak[1],deltas[i]))

        if( i > 0):
            isp = isp_times[i-1]
            print '%4.3f' % (isp),
            f.write('%4.3f' % isp)

        print
        f.write('\n')
 
    if len(peaks) > 1:
        avg_delta = (sum(deltas)/len(deltas))
        avg_isp   = (sum(isp_times)/len(isp_times));
        print 'Average   |\t\t\t\t%4.3f\t%4.3f\t%4.6f\t%4.6f' % (avg_delta,avg_isp,1/avg_isp,60/avg_isp)
        f.write('Average,,,,%4.3f,%4.3f,%4.6f,%4.6f' % (avg_delta,avg_isp,1/avg_isp,60/avg_isp))

    print "\n\n",
    f.write('\n\n')


def ParseDataFromCSV( filename ):
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

def PlotOutput( fig, data, times, peaks, bases, subplot, clr ):
    ax = fig.add_subplot(subplot[0],subplot[1],subplot[2])
    ax.plot(times, data, color=clr)

    for i in arange(len(peaks)):
        annotate( ax, times, ('peak %d' % (i+1)), peaks[i])
        annotate( ax, times, ('base %d' % (i+1)), bases[i], -0.1, 'blue' )


def annotate( ax, times,  caption, point, offset=0.1, color='red' ):
    ax.annotate(caption, xy=(times[point[0]], point[1]),  xycoords='data',
                xytext=(times[point[0]], point[1] + offset), textcoords='data',
                arrowprops=dict(facecolor=color, shrink=0.05),
                horizontalalignment='center', verticalalignment='top',
                )


def ParseArgs( argv ):
    filename = "data.csv"
    delta    = 0.2 # jump in value to determine maxima/minima
    numnei   = 5 # +- numnei indices are searched to find bases
    a = 0
    b = 0
    c = 0

    try:
        opts, args = getopt.getopt(argv[1:], "f:d:n:pa:b:c:", ["file=", "delta=", "numnei=", "plot"])
    except getopt.GetoptError, err:
        print str(err)
        #usage()
        print 'usage: ', argv[0], ' --file data.csv --delta 0.2 --numnei 10'
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

    return filename, float(delta), int(numnei), plotfig, int(a), int(b), int(c)



def ProcessTimeSlice( data, times, fig, subplot, color, calcPeaks, delta = 1, numnei = 10 ):
    maxima = []; minima = []; bases = []
    if calcPeaks:
        maxima,minima,bases = PeakDetector(data, delta, numnei)

    PlotOutput( fig, data, times, maxima, bases, subplot, color )



def main():
    filename, delta, numnei, plotfig, a, b, c = ParseArgs( sys.argv )

    times,data = ParseDataFromCSV( filename )

    if plotfig:
        fig = plt.figure()

    print( "a,b,c=",a,b,c)
    for i in arange(len(data)):
        ProcessTimeSlice(  data[i][0:a], times[0:a], fig,[len(data), 1, i], 'k', False, delta, numnei )
        ProcessTimeSlice(  data[i][a:b], times[a:b], fig,[len(data), 1, i], 'r', True, delta, numnei  )
        ProcessTimeSlice(  data[i][b:c], times[b:c], fig,[len(data), 1, i], 'g', True , delta, numnei )
        ProcessTimeSlice(  data[i][c:],  times[c:],  fig,[len(data), 1, i], 'k', False, delta, numnei )
    if plotfig:
        plt.show()

if __name__=="__main__":
    main()

