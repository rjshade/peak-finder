import sys
from numpy import NaN, Inf, arange, isscalar, asarray
import csv

import matplotlib

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook


def peakdet(v, delta, x = None):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    
    Currently returns two lists of tuples, but maybe arrays would be better
    
    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %      
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.
    
    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.
    
    """
    maxtab = []
    mintab = []
       
    if x is None:
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
                lookformax = False
        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return maxtab, mintab

if __name__=="__main__":
    series = [0,0,0,2,1,1,0,-2,0,0,1,2,0,0,0,-2,0]
    print peakdet(series,1)

    test_data = csv.reader(open("test_data.csv", "rb" ))
    test_data_list = []
    test_data_list.extend(test_data)
    time_series = []
    data_series = []
    for data in test_data_list:
        time_series.append(float(data[0]))
        data_series.append(float(data[1]))

    print "-------------------"
    print data_series
    print "-------------------"

    maxtab,mintab= peakdet(data_series,0.1)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    #ax.plot(time_series, data_series)

    ax.plot(time_series,data_series)

    for peak in maxtab:
        print "Peak found at time %f with height %f" % (time_series[peak[0]], peak[1])

        ax.annotate('peak', xy=(time_series[peak[0]], peak[1]),  xycoords='data',
                xytext=(time_series[peak[0]], peak[1] + 0.1), textcoords='data',
                arrowprops=dict(facecolor='red', shrink=0.05),
                horizontalalignment='center', verticalalignment='top',
                )


    




    plt.show()



