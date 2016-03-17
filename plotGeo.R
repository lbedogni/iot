library(rworldmap)
library(sp)
library(ggplot2)
library(rgdal)
library(rgeos)

datasetTS <- read.csv('gpsTS',sep=' ', col.names = c('LON','LAT'))
datasetTS$SOURCE = "ThingSpeak"
datasetSF <- read.csv('gpsSF',sep=' ', col.names = c('LON','LAT'))
datasetSF$SOURCE = "SparkFun"

head(datasetTS)
head(datasetSF)

dataset = rbind(datasetTS, datasetSF)
head(dataset)

dataset$LON = as.numeric(dataset$LON)
dataset$LAT = as.numeric(dataset$LAT)

dataset = dataset[dataset$LON <= 180,]
dataset = dataset[dataset$LON >= -180,]
dataset = dataset[dataset$LAT <= 90,]
dataset = dataset[dataset$LAT >= -90,]
summary(dataset)

#newmap <- getMap(resolution = "high")
#summary(newmap)
#plot(newmap, xlim = c(-190, 190), ylim = c(-90, 190), asp = 1)
#plot(newmap, xlim = c(10.5, 12), ylim = c(44, 45), asp = 1)
#points(dataset$LON, dataset$LAT, col="red", cex = 0.2)


world <- readOGR("ne_50m_admin_0_countries.geojson", "OGRGeoJSON")
outline <- bbox(world)
outline <- data.frame(xmin=outline["x","min"],
                      xmax=outline["x","max"],
                      ymin=outline["y","min"],
                      ymax=outline["y","max"])

world <- fortify(world)

gg <- ggplot()
gg <- gg + geom_rect(data=outline, 
                     aes(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax), 
                     color=1, fill="white", size=0.3)
gg <- gg + geom_map(data=world, map=world,
                    aes(x=long, y=lat, map_id=id), 
                    fill="gray90", color="gray10", size=0.3)
gg <- gg + geom_point(data=dataset, aes(x=LON, y=LAT, group=SOURCE, color=SOURCE), size=.5)
gg <- gg + labs(x=NULL, y=NULL)
gg <- gg + coord_map("mollweide")
gg <- gg + theme_bw()
gg <- gg + theme(panel.grid=element_blank())
gg <- gg + theme(panel.border=element_blank())
gg <- gg + theme(axis.ticks=element_blank())
gg <- gg + theme(axis.text=element_blank())
gg
