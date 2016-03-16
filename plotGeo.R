library(rworldmap)

dataset <- read.csv('aa',sep=' ', col.names = c('LON','LAT'))
dataset = dataset[dataset$LON <= 180,]
dataset = dataset[dataset$LON >= -180,]
dataset = dataset[dataset$LAT <= 90,]
dataset = dataset[dataset$LAT >= -90,]
summary(dataset)

newmap <- getMap(resolution = "high")
plot(newmap, xlim = c(-190, 190), ylim = c(-90, 190), asp = 1)
plot(newmap, xlim = c(10.5, 12), ylim = c(44, 45), asp = 1)
points(dataset$LON, dataset$LAT, col="red", cex = 0.2)
