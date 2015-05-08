import random
import os, sys
from threading import Thread
from subprocess import *
import math
import msvcrt

def checkKey():
  ch = msvcrt.getch()
  if( ch == 'q' or ch == 'Q' ):
    return 1
  else:
    return False

#--------------------------------------------------
# Generate data points
# Each point = [0, x_1,...,x_NumPoints]
def genData(dimension, NumPoints, vmin, vmax, uniform=False):
  db = []
  for i in range(NumPoints):
    d = [0]
    for j in range(dimension):
      if( uniform ):
        e = random.random()*(vmax - vmin) + vmin
      else:
        e = random.gauss((vmax - vmin)/2, vmax - vmin)
      d.append(e)
    db.append(d)
  return db

# generate 2D data points centered around cx and cy within the diameter
def genDataXY(NumPoints, sigma, cx, cy, uniform=False):
  db = []
  for i in range(NumPoints):
    if( uniform ):
      x = (random.random() - 0.5) * sigma + cx
      y = (random.random() - 0.5) * sigma + cy
    else:
      x = random.gauss(cx, sigma)
      y = random.gauss(cy, sigma)
    db.append([0,x,y])
  return db

def getGnuPlot():
  # svmtrain and gnuplot executable
  is_win32 = (sys.platform == 'win32')
  if not is_win32:
    gnuplot_exe = "/usr/bin/gnuplot"
  else:
    # example for windows
    gnuplot_exe = r"C:\Users\Alienware\Desktop\DM Assignment\DM-Git\isclust\gnuplot\pgnuplot.exe"

  assert os.path.exists(gnuplot_exe),"gnuplot executable not found"
  gnuplot = Popen(gnuplot_exe,stdin = PIPE).stdin
  return gnuplot

#--------------------------------------------------
# Draw data points in dataPoints and center points in centerPoints
#
# Each data point: [center_index, x, y]
# Each center point: [0, x, y]
#
#--------------------------------------------------
def redraw(gnuplot, dataPoints, centerPoints, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile=False):
  if len(dataPoints) == 0: return
  openGnuPlotTerm(gnuplot, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)

  i = 1
  for p in dataPoints:
    gnuplot.write(("set arrow %s from %s,%s to %s,%s nohead linetype %s\n" % (i, p[1], p[2], centerPoints[p[0]][1], centerPoints[p[0]][2], p[0])).encode())
    i += 1

  # plot dataPoints
  gnuplot.write("plot \"-\" title \"Data\" ls 1 with points, \"-\" title \"Medoids\" ls 3 with circles\n".encode())
  for p in dataPoints:
    c = ("%s %s\n" % (p[1],p[2])).encode()
    #print c
    gnuplot.write(c)
  gnuplot.write("e\n".encode())

  for p in centerPoints:
    c = ("%s %s 0.1\n" % (p[1],p[2])).encode()
    #print c
    gnuplot.write(c)
  gnuplot.write("e\n".encode())
  gnuplot.write("\n".encode()) # force gnuplot back to prompt when term set failure

  gnuplot.flush()

#--------------------------------------------------
#
# Draw data points in dataPoints
#
# Each data point: [cluster_index, x, y]
#
#--------------------------------------------------
def plotDBSCAN(gnuplot, data, clusters, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile=False):
  #if len(clusters) == 0: return
  openGnuPlotTerm(gnuplot, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)

  dd = []
  i = 1
  for dataPoints in clusters:
    dd += dataPoints
    pp = []
    for p in dataPoints:
      if( len(pp) == 0):
        pp = p
      print p[0],
      gnuplot.write(("set arrow %s from %s,%s to %s,%s nohead ls %s\n" % (i, p[1], p[2], pp[1], pp[2], p[0])).encode())
      i += 1
      pp = p
    print "---"

  # plot dataPoints
  gnuplot.write("plot \"-\" title \"Data\" ls 1 with points\n".encode())
  for p in data:
    c = ("%s %s\n" % (p[1],p[2])).encode()
    #print c
    gnuplot.write(c)
  gnuplot.write("e\n".encode())
  gnuplot.write("\n".encode()) # force gnuplot back to prompt when term set failure

  gnuplot.flush()

#---------------------------------------------------------------------
# plot sin(x) lt rgb "#FF00FF"
# set format y "$%g$"
# set format x "$%.2f$"
# set format xy "$%g$"
# set xlabel "This is the $x$ axis"
# set ylabel "$\sin(x)$"
# set key at 15,-10
# plot x with lines, "eg3.dat" with linespoints
# plot "datafile.1" with lines, "datafile.2" with points
# set boxwidth 0.9 relative
# set style fill solid 1.0
#
# Color runs from white to green
#7,5,15   ... traditional pm3d (black-blue-red-yellow)
#3,11,6   ... green-red-violet
#23,28,3  ... ocean (green-blue-white); try also all other permutations
#21,22,23 ... hot (black-red-yellow-white)
#30,31,32 ... color printable on gray (black-blue-violet-yellow-white)
#33,13,10 ... rainbow (blue-green-yellow-red)
#34,35,36 ... AFM hot (black-red-yellow-white)
#3,2,2    ... red-yellow-green-cyan-blue-magenta-red   A full color palette in HSV color space
#
# plot dataPoints
# ps  point size
# pt 5   Rectangle
# pt 7   Circle
#---------------------------------------------------------------------

def openGnuPlotTerm(gnuplot, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile=False):
  is_win32 = (sys.platform == 'win32')
  if tofile:
      gnuplot.write( "set term png transparent small\n".encode())
      gnuplot.write( ("set output \"%s\"\n" % png_filename.replace('\\','\\\\')).encode())
      #gnuplot.write("set term postscript color solid\n".encode())
      #gnuplot.write(("set output \"%s.ps\"\n" % dataset_title).encode())
  elif is_win32:
      gnuplot.write("set term windows\n".encode())
  else:
      gnuplot.write( "set term x11\n".encode())

  gnuplot.write(("set xlabel \"%s\"\n" % xlabel).encode())
  gnuplot.write(("set ylabel \"%s\"\n" % ylabel).encode())
  gnuplot.write(("set xrange [%s:%s]\n" % (x_begin, x_end)).encode())
  gnuplot.write(("set yrange [%s:%s]\n" % (y_begin, y_end)).encode())

  gnuplot.write("set view 0,0\n".encode())
  gnuplot.write(("set title \"%s\"\n" % title).encode())
  gnuplot.write("unset label\n".encode())

#  gnuplot.write(("set label \"Best log2(C) = %s  log2(gamma) = %s  accuracy = %s%%\" \
#                at screen 0.5,0.85 center\n" % \
#                (best_log2c, best_log2g, best_rate)).encode())
#  gnuplot.write(("set label \"C = %s  gamma = %s\""
#                " at screen 0.5,0.8 center\n" % (2**best_log2c, 2**best_log2g)).encode())

  #gnuplot.write(("set boxwidth 0.9 relative\n").encode())
  gnuplot.write(("set style line 1 lt 2 lw 2 pt 3 ps 0.5 linecolor rgb \"red\"\n").encode())
  gnuplot.write(("set style line 2 lt 2 lw 2 pt 3 ps 0.5 linecolor rgb \"green\"\n").encode())
  gnuplot.write(("set style line 3 lt 2 lw 2 pt 3 ps 0.5 linecolor rgb \"blue\"\n").encode())
  gnuplot.write(("set style line 4 lt 2 lw 2 pt 3 ps 0.5 linecolor rgb \"black\"\n").encode())
  gnuplot.write(("set style line 5 lt 2 lw 2 pt 3 ps 0.5 linecolor rgb \"magenta\"\n").encode())
  gnuplot.write(("set style line 6 lt 2 lw 2 pt 3 ps 0.5 linecolor rgb \"yellow\"\n").encode())
  gnuplot.write(("set style line 7 lt 2 lw 2 pt 3 ps 0.5 linecolor rgb \"cyan\"\n").encode())
  gnuplot.write(("set style line 8 lt 2 lw 2 pt 3 ps 0.5 linecolor rgb \"orange\"\n").encode())
  gnuplot.write(("set style line 9 lt 2 lw 2 pt 3 ps 0.5 linecolor rgb \"violet\"\n").encode())

  #gnuplot.write("set key at 1,1\n".encode())
  #gnuplot.write("set arrow from -5,-5 to -3.3,-6.7\n".encode())
  #set label "Data" at -5,-5 right

#--------------------------------------------------------------------
#
def SOMPlot(plotType, gnuplot, db, l2d, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile=False):

  if( plotType == 1):
    SOMColorMap(gnuplot, db, l2d, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)
  elif ( plotType == 2):
    SOMColorSqDots(gnuplot, db, l2d, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)
  elif ( plotType == 3):
    SOMHeatMap(gnuplot, db, l2d, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)
  elif ( plotType == 4):
    SOMColorDotGridMap(gnuplot, db, l2d, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)
  elif ( plotType == 5):
    SOMLineGridMap(gnuplot, db, l2d, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)

#--------------------------------------------------------------------
#
# Visualize SOM
# l2d = n by n neurons
#   Each neuron: [cluster_index, x1, x2,...xM]
# Use the first 3 components x1,x2,x3 as RGB color
# Use the row, column as coordinates of the neurons
#
#--------------------------------------------------------------------
maxR = 10
maxC = 10
def SOMColorMap(gnuplot, db, l2d, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile=False):
  global maxR, maxC
  if len(l2d) == 0: return

  openGnuPlotTerm(gnuplot, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)

  #gnuplot.write(("rgb(r,g,b) = 65536 * int(r) + 256 * int(g) + int(b)\n").encode())
  #using 1:2:(rgb($1,$2,$3)) lc rgb variable

  rn = 0
  i = 1
  for r in l2d:
    cn = 0
    for c in r:
      if( c[1] > maxR):
        maxR = c[1]
      if( c[2] > maxC):
        maxC = c[2]

      r = hex(int(c[1]*256/maxR))[2:]
      g = hex(int(c[2]*256/maxC))[2:]
      if( len(r) < 2):
        r = "0" + r
      if( len(g) < 2):
        g = "0" + g

      rgb = r + g + "00"
      #rgb = int(c[1]*65536*10 + c[2]*256*20) #65536*255 +
      gnuplot.write(("set object %s circle at %s, %s size 0.3 front lw 2.0 fc rgb \"#%s\" fs transparent solid 0.5 noborder\n" % (i,rn,cn,rgb)).encode())
      #cmd = ("%s %s 5 %s\n" % (rn, cn, 65536*255 + c[1]*256*50 + c[2]*50)).encode()
      #print cmd
      #gnuplot.write(cmd)
      cn += 1
      i+= 1
    rn += 1

  # plot dataPoints
  gnuplot.write("plot \"-\" title \"Data\" ls 1 with points\n".encode())
  for p in db:
    cmd = ("%s %s\n" % (p[1],p[2])).encode()
    gnuplot.write(cmd)

  gnuplot.write("e\n".encode())
  gnuplot.write("\n".encode()) # force gnuplot back to prompt when term set failure

  gnuplot.flush()

#--------------------------------------------------------------------
# try to plot without using circle
def SOMColorSqDots(gnuplot, db, l2d, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile=False):
  global maxR, maxC
  if len(l2d) == 0: return

  openGnuPlotTerm(gnuplot, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)

  # plot dataPoints
  # ps  point size
  # pt 5   Rectangle
  # pt 7   Circle
  gnuplot.write("plot \"-\" using 1:2:3 notitle with points pt 5 ps 10 lc rgb variable\n".encode())
  rn = 0
  i = 1
  for r in l2d:
    cn = 0
    for c in r:
      if( c[1] > maxR):
        maxR = c[1]
      if( c[2] > maxC):
        maxC = c[2]
      r = int(c[1]*256/maxR)
      g = int(c[2]*256/maxC)
      rgb = 65536*r + 256*g
      gnuplot.write(("%s %s %s\n" % (rn+0.5,cn+0.5,rgb)).encode())
      cn += 1
      i+= 1
    rn += 1
  gnuplot.write("e\n".encode())
  gnuplot.write("\n".encode()) # force gnuplot back to prompt when term set failure

  gnuplot.flush()

#-------------------------------------------------------------
# Heat Map using sqaure
# Input: a list of lists of vectors. Each vector is a neuron: [ classLabel, w1, w2,....]
#-------------------------------------------------------------
def SOMHeatMap(gnuplot, db, l2d, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile=False):
  global maxR, maxC
  if len(l2d) == 0: return

  openGnuPlotTerm(gnuplot, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)
  gnuplot.write("set palette rgbformula 7,5,15\n".encode())
  gnuplot.write("set cbrange [ * : * ] noreverse nowriteback\n".encode())
  gnuplot.write("set cblabel \"Score\"\n".encode())
  gnuplot.write("unset cbtics\n".encode())
  gnuplot.write("set view map\n".encode())

  # plot dataPoints
  # ps  point size
  # pt 5   Rectangle
  # pt 7   Circle
  #gnuplot.write("plot \"-\" using 2:1:3 with image\n".encode())
  gnuplot.write("splot '-' matrix with image\n".encode())
  #i = 0
  for r in l2d:
    #j = 0
    for c in r:
      color = c[1]*25*256 + c[2]*25
      #gnuplot.write(("%s %s %s\n" % (i, j, color)).encode())
      gnuplot.write(("%s " % (color)).encode())
      #j+=1
    #i+=1
    gnuplot.write("\n".encode())
  gnuplot.write("e\n".encode())
  gnuplot.write("e\n".encode())
  gnuplot.write("\n".encode()) # force gnuplot back to prompt when term set failure

  gnuplot.flush()

#--------------------------------------------------------------------
# Plot squre dots over data points
def SOMColorDotGridMap(gnuplot, db, l2d, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile=False):
  global maxR, maxC
  if len(l2d) == 0: return

  openGnuPlotTerm(gnuplot, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)

  # plot neurons as square dots
  gnuplot.write("plot \"-\" using 1:2:3 notitle with points pt 5 ps 10 lc rgb variable, \"-\" title \"Data\" ls 1 with points\n".encode())
  rn = 0
  i = 1
  for r in l2d:
    cn = 0
    for c in r:
      if( c[1] > maxR):
        maxR = c[1]
      if( c[2] > maxC):
        maxC = c[2]
      r = int(c[1]*256/maxR)
      g = int(c[2]*256/maxC)
      rgb = 65536*r + 256*g
      gnuplot.write(("%s %s %s\n" % (c[1],c[2],rgb)).encode())
      cn += 1
      i+= 1
    rn += 1
  gnuplot.write("e\n".encode())
  # Data points
  for p in db:
    cmd = ("%s %s\n" % (p[1],p[2])).encode()
    gnuplot.write(cmd)

  gnuplot.write("e\n".encode())
  gnuplot.write("\n".encode()) # force gnuplot back to prompt when term set failure

  gnuplot.flush()

#--------------------------------------------------------------------
# Plot grid of SOM neurons over 2D data points
def SOMLineGridMap(gnuplot, db, l2d, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile=False):
  global maxR, maxC
  if len(l2d) == 0: return

  openGnuPlotTerm(gnuplot, xlabel, ylabel, x_begin, x_end, y_begin, y_end, title, tofile)

  # plot dataPoints
  gnuplot.write("plot \"-\" using 1:2:3 title \"Map\" with lines ls 1 pt 7 ps 10 lc rgb variable, \"-\" title \"Data\" ls 1 with points\n".encode())
  rn = 0
  i = 1
  for r in l2d:
    cn = 0
    for c in r:
      if( c[1] > maxR):
        maxR = c[1]
      if( c[2] > maxC):
        maxC = c[2]

      r = int(c[1]*256/maxR)
      g = int(c[2]*256/maxC)
      gnuplot.write(("%s %s %s\n" % (c[1],c[2],65536*r + 255*g)).encode())
      cn += 1
      i+= 1
    rn += 1
  gnuplot.write("e\n".encode())

  # Data points
  for p in db:
    cmd = ("%s %s\n" % (p[1],p[2])).encode()
    gnuplot.write(cmd)

  gnuplot.write("e\n".encode())
  gnuplot.write("\n".encode()) # force gnuplot back to prompt when term set failure
  gnuplot.flush()

# Measure disimilarity between x1 and x2
def disimilarity(x1,x2):
  # eclidian distance
  d = 0
  for i in range(len(x1)-1):
    #print x1
    d += math.pow(x1[i+1] - x2[i+1],2)
  return math.sqrt(d)

def zeros(k):
  d = []
  for i in range(k):
    d.append(0)
  return d
