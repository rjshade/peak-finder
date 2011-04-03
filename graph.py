import sys
from numpy import NaN, Inf, arange, isscalar, asarray
import csv

import matplotlib

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook


def peakdet(v, delta, numnei):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    
    Currently returns two lists of tuples, but maybe arrays would be better
    
    function [maxtab, mintab]=peakdet(v, delta, numnei)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %      
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.
    
    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.
    
    """
    maxtab = []
    mintab = []
    bstab = []
       
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
    
    bs = v[0] 
    bspos = NaN
    
    lookformax = True
    lookforbs = True
    
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

                bs,bspos = getLowestInNeighbourhood( v, mxpos, numnei )
                bstab.append((bspos,bs))

                lookformax = False

        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return maxtab, mintab, bstab



def getLowestInNeighbourhood( data, index, numnei ):
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


def annotate( ax, caption, point, offset=0.1, color='red' ):
    ax.annotate(caption, xy=(time_series[point[0]], point[1]),  xycoords='data',
                xytext=(time_series[point[0]], point[1] + offset), textcoords='data',
                arrowprops=dict(facecolor=color, shrink=0.05),
                horizontalalignment='center', verticalalignment='top',
                )


def findPeaks( fig, time_series, data_series, delta, numnei, plotNum ):

    peaks,mintab,bases= peakdet(data_series, delta, numnei)

    if len(peaks) != len(bases):
        print 'ERROR: unequal number of peaks/bases...'


    ax = fig.add_subplot(6,1,plotNum)
    ax.plot(time_series,data_series)


    peak_times = [time_series[j] for j in [ peaks[i][0] for i in arange(len(peaks)) ]]
    base_times = [time_series[j] for j in [ bases[i][0] for i in arange(len(bases)) ]]

    isp_times = []
    for i in range(1,len(peaks)):
        isp_times.append( peak_times[i] - peak_times[i-1] )

    deltas = [peaks[i][1] - bases[i][1] for i in arange(len(peaks))]

    if len(peaks) == 0:
        print 'No peaks found'
        return

    print '        \tTime\tBase\tPeak\tDelta\tISP'
    print "----------|---------------------------------------------"
    for i in arange(len(peaks)):

        peak = peaks[i];
        base = bases[i];
        peak_time = peak_times[i]
        base_time = base_times[i]

        annotate( ax, 'peak %d' % i, peak )
        annotate( ax, 'base %d' % i, base, -0.1, 'blue' )

        print 'Peak %4d |\t%4d\t%4.3f\t%4.3f\t%4.3f\t' % (i,peak_time,base[1],peak[1],deltas[i]),

        if( i > 0):
            isp = isp_times[i-1]
            print '%4.3f' % (isp),

        print
 
    avg_delta = (sum(deltas)/len(deltas))
    avg_isp   = (sum(isp_times)/len(isp_times));
    print 'Average   |\t\t\t\t%4.3f\t%4.3f' % (avg_delta,avg_isp)
    print "\n"

if __name__=="__main__":
    test_data = csv.reader(open("new_data.csv", "rb" ))
    test_data_list = []
    test_data_list.extend(test_data)
    time_series = []
    data_series = [ [] for i in range(len(test_data_list[0]))]

    for data in test_data_list:
        time_series.append(float(data[0]))
        for i in range(1,len(data)):
            data_series[i-1].append(float(data[i]))

    fig = plt.figure()
    for i in arange(len(data_series)-1):
        print
        print "****************   Data set %2d   ***********************" % i
        print
        findPeaks( fig, time_series, data_series[i], 0.2, 10, i )

    plt.show()

