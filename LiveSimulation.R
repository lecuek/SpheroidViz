library(R.matlab)
library(ggplot2)
library(sp)
library(tidyr)
library(dplyr)
library(plot3D)
library(viridis)
library(oce)
library(reshape2)

sliceZ <- 0
#setwd("../")
#getwd()
#print(getwd())
folder <- "../output/output_data/"

GET_MEDIUM_OBJECT<-function(TIME){
  files.names <- dir(folder, pattern = "*_microenvironment0.mat")
  path_file <-
    paste("../output/output_data/", files.names[TIME], sep = "")
  MEDIUM <- readMat(path_file)
  MEDIUM <- MEDIUM$multiscale.microenvironment
  MEDIUM <- t(MEDIUM)
  MEDIUM <- data.frame(MEDIUM, TIME)
  colnames(MEDIUM) <-
    c("x",
      "y",
      "z",
      "constant",
      "oxygen",
      "glucose",
      "lactate",
      "H",
      "TIME")
  MEDIUM$pH <- -log10(MEDIUM$H / 1000)
  MEDIUM$Distance <-
    sqrt((MEDIUM$x - 0) ^ 2 + (MEDIUM$y - 0) ^ 2 + (MEDIUM$z - 0) ^
           2 * 1.0)
  
  return(MEDIUM)
}


EnvironmentMAP <- function(PARAMETER, TIME) {
  MEDIUM_OBJECT<-GET_MEDIUM_OBJECT(TIME)
  rangePARAMETER <- range(MEDIUM_OBJECT[, PARAMETER])
  scalePARAMETER <-
    scale_fill_viridis_c(PARAMETER,
                         option = "plasma",
                         limits = c(floor(rangePARAMETER[1]), ceiling(rangePARAMETER[2])))
  themeNoLegends <-
    theme(
      axis.title.x = element_blank(),
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      axis.title.y = element_blank(),
      axis.text.y = element_blank(),
      axis.ticks.y = element_blank(),
      legend.justification = c(1, 0),
      legend.position = c(1, 0)
    )

    ggplot(data = MEDIUM_OBJECT, aes(x = MEDIUM_OBJECT$x, y = MEDIUM_OBJECT$y, fill = MEDIUM_OBJECT[,PARAMETER])) + geom_raster(interpolate = TRUE) +
      scalePARAMETER + themeNoLegends + scale_x_continuous(expand = c(0, 0)) + scale_y_continuous(expand = c(0, 0)) +
      coord_equal()
    # path <-
    #   paste("./output/pngtemp/",PARAMETER,"/", TIME, ".png", sep = "")
    # print(path)
    # ggsave(
    #   path,
    #   width = 10,
    #   height = 10,
    #   dpi = 72,
    #   units = "in",
    #   device = "png"
    # )
}

GET_CELL_OBJECT<-function(TIME){
  files.names2 <- dir(folder, pattern = "*_cells_physicell.mat")
cells <- data.frame()
  path_file <-
    paste("../output/output_data/", files.names2[TIME], sep = "")
  cells_temp <- readMat(path_file)
  cells_temp <- cells_temp$cells
  cells_temp <- t(cells_temp)
  cells_temp <- as.data.frame(cells_temp)
  colnames(cells_temp) <-
    c(
      "ID",
      "x",
      "y",
      "z",
      "total_volume",
      "cell_type",
      "cycle_model",
      "current_phase",
      "elapsed_time_in_phase",
      "nuclear_volume",
      "cytoplasmic_volume",
      "fluid_fraction",
      "calcified_fraction",
      "oriX",
      "oriY",
      "oriZ",
      "polarity",
      "migration_speed",
      "motility_vector",
      "motility_vector2",
      "motility_vector3",
      "migration_bias",
      "motility_bias_direction1",
      "motility_bias_direction2",
      "motility_bias_direction3",
      "persistence_time",
      "motility_reserved",
      "ATP",
      "Energy_mode",
      "pressure",
      "local_density",
      "overlap",
      "oncoprotein",
      "uptake_glucose",
      "uptake_oxygen",
      "secretion_lactate",
      "uptake_lactate",
      "pH",
      "Pyruvate"
    )
  cells_temp$distance <-
    with(cells_temp, sqrt((cells_temp$x ^ 2) + (y ^ 2) + (z ^ 2)))
  cells_temp$simulation_time <- TIME
  cells <- rbind(cells, cells_temp)
  return(cells)
}


plotCellatTime<-function(PARAMETER, time){
  CELL_OBJECT<-GET_CELL_OBJECT(time+1)
  CELL_OBJECT <- CELL_OBJECT[, c("x", "y", "z", "distance", PARAMETER, "simulation_time")]
  plot<-ggplot(
    data = CELL_OBJECT,
    aes_string(x = "distance", y = PARAMETER)
  ) +
    geom_point(col="red",alpha = 0.5) +
    geom_smooth(alpha = 0.02) +
    ggtitle(PARAMETER,"/Distance") +
    scale_x_continuous(breaks = scales::pretty_breaks(n = 13)) +
    xlab("Distance") + ylab(PARAMETER) + theme(axis.text.x = element_text(angle = 0, hjust = 1))
  return(plot)
}

plotSpheroidAtTIME<-function(PARAMETER, time){
  CELL_OBJECT<-GET_CELL_OBJECT(time+1)
    ggplot(
    data = CELL_OBJECT,
    mapping = aes(x = CELL_OBJECT$x, y = CELL_OBJECT$y)
  ) + geom_point(aes(colour = CELL_OBJECT[[PARAMETER]]),
    alpha = 1,
    size = 1.5 * (0.5 * (3 * CELL_OBJECT$total_volume / (4 * pi))^(1 /3))
  ) + scale_colour_viridis(
    option = "plasma",
    direction = -1,
    discrete = FALSE
  ) + coord_equal()
}


# plotCellatTime("ATP",1)
# EnvironmentMAP("oxygen",200)
# plotSpheroidAtTIME("uptake_oxygen",50)
# 
