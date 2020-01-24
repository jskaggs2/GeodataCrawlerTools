## Batch process USER_OPTIONS.csv's for GeodataCrawler 'multithreading'
## Jon Skaggs
## initated 25 November 2019

# -------------------------------------------------------------------------

# Modify these parameters
setwd("Z:/current_projects/DNR_Georgia_Biotics")
useroptionsall <- c("08 Acanthonus10km", "09 Acanthonus25km", "10 Acanthonus50km", "11 Acanthonus5km")
groups <- 0:13
hucs <- c("0311", "0312")

# -------------------------------------------------------------------------


for(useroptions in useroptionsall){
    uo <- read.csv(paste("./data/landscape/toGeodatacrawler/2019 Acanthonus/00 setup/", useroptions, ".csv", sep = ""))
    for (huc in hucs){
        for (group in groups){
            uo[,1] <- as.character(uo[,1])
            uo[2,1] <- paste("Acanthonus_", huc, "_Group_", group, sep = "")
            uo[3,1] <- paste(substr(useroptions, start = 4, stop = nchar(useroptions)))
            savepath <- paste("./data/landscape/toGeodatacrawler/2019 Acanthonus/", useroptions, "/2019_Acanthonus_", huc, "/2019_Acanthonus_", huc, "_Group_", group, "/USER_OPTIONS.csv", sep = "")
            write.csv(x = uo, file = savepath, row.names = FALSE)
        }
    }
}