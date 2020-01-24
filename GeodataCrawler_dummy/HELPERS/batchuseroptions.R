## Batch process USER_OPTIONS.csv's GeodataCrawler 'multithreading'
## Jon Skaggs
## initated 25 November 2019

# -------------------------------------------------------------------------

# Modify these parameters
useroptions <- "8 Acanthonus10km"
groups <- 0:9
huc <- "0307"

# -------------------------------------------------------------------------

setwd("Z:/current_projects/DNR_Georgia_Biotics")

uo <- read.csv(paste("data/landscape/toGeodatacrawler/2019 Acanthonus/0 setup/", useroptions, ".csv", sep = ""))
for (group in groups){
    
    uo[,1] <- as.character(uo[,1])
    uo[2,1] <- paste("Acanthonus_", huc, "_Group_", group, sep = "")
    uo[3,1] <- paste(substr(useroptions, start = 3, stop = nchar(useroptions)))
    savepath <- paste("data/landscape/toGeodatacrawler/2019 Acanthonus/", useroptions, "/2019_Acanthonus_", huc, "/2019_Acanthonus_", huc, "_Group_", group, "/USER_OPTIONS.csv", sep = "")
    write.csv(x = uo, file = savepath, row.names = FALSE)
    
}
