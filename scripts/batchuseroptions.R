## Batch process USER_OPTIONS.csv's for GeodataCrawler 'multithreading'
## Jon Skaggs
## initated 25 November 2019

# -------------------------------------------------------------------------

# Modify these parameters
projectname <- "2020_Acanthonus"
outputname <- "Acanthonus2"
setwd("Z:/current_projects/Acanthonus/toGeodatacrawler/2020_Acanthonus")
#useroptionsall <- c("08 Acanthonus10km", "09 Acanthonus25km", "10 Acanthonus50km", "11 Acanthonus5km")
groups <- 0:9
hucs <- c("0306", "0307", "0311", "0312", "0313", "0315", "0601", "0602")

# -------------------------------------------------------------------------


#for(useroptions in useroptionsall){
    uo <- read.csv(paste0("USER_OPTIONS.csv"))
    for (huc in hucs){
        for (group in groups){
            uo[,1] <- as.character(uo[,1])
            uo[2,1] <- paste(projectname, huc, group, sep = "_")
            uo[3,1] <- paste(outputname, huc, group, sep = "_")
            savepath <- paste0(projectname, "_", huc, "/", projectname, "_", huc, "_Group_", group, "/USER_OPTIONS.csv")
            write.csv(x = uo, file = savepath, row.names = FALSE)
        }
    }
#}