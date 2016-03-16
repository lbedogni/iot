set term postscript enhanced color eps
set out 'bars.eps'

set xdata time
set timefmt "%s"
#set format x "%m/%d/%Y %H:%M:%S"
set format x "%m/%Y"
set grid

set xtics "1291382783.0",31536000,"1458036574.0"

set ylabel "Number of new Data Streams"
set y2label "Number of updated Data Streams"

set key outside below


set ytics
set y2tics

plot 'dataCreated' u 1:2 with points pointtype 5 ps .3 lc "red" t "Created Streams", '' u 1:2 with lines smooth bezier lw 6 lc rgb "#990000" t "", 'dataUpdated' u 1:2 with points pointtype 5 ps .3 lc "gray" axes x1y2 t "Updated Streams", '' u 1:2 with lines smooth bezier lw 6 lc rgb "#000000" axes x1y2 t ""
