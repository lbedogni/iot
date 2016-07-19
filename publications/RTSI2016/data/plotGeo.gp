set term postscript enhanced color eps
set out 'geo.eps'

set yrange [-90:90]
set xrange [-190:190]

set nokey

plot '/home/lbedogni/Downloads/gnuplot-5.0.2/demo/world.dat' with lines, 'aa' with points lc "#FF0000"
