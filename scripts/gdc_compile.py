## Compile results from a multithreaded GDC output
## Jon Skaggs
## 18 November 2019


print "  ___                  _   _                            "
print " / _ \                | | | |                           "
print "/ /_\ \ ___ __ _ _ __ | |_| |__   ___  _ __  _   _ ___  "
print "|  _  |/ __/ _` | '_ \| __| '_ \ / _ \| '_ \| | | / __| "
print "| | | | (_| (_| | | | | |_| | | | (_) | | | | |_| \__ \ "
print "\_| |_/\___\__,_|_| |_|\__|_| |_|\___/|_| |_|\__,_|___/ "
print ""


## ----------------------------------------------------------------------------
print "## Specify User Settings"
## ----------------------------------------------------------------------------


## Where are target GeodataCrawler data?
#infolder = "Z:\\current_projects\\DNR_Georgia_Biotics\\data\\landscape\\fromGeodatacrawler\\2019 Acanthonus (1km)" # path to input folder 
infolder = "C:\\GeodataCrawlerTools\\data\\fromGeodataCrawler\\2019 Acanthonus (1km)"
projectname = "Acanthonus" # your project name
hucs = ["0313"] # string list of huc4s JUST DO ONE HUC4 PER RUN FOR NOW
groups = [0,1,2,3,4,5,6,7,8,9,10,11,12,13] # numeric list of groups
#groups = [0,1,2,3,4,5,6,7,8,9] # numeric list of groups
outputs = ["Acanthonus5km", "Acanthonus10km", "Acanthonus25km", "Acanthonus50km"] # data collection scales
#outputs =  ["DelineateData5km", "NewSampleAreasData", "DelineateData25km", "DelineateData50km"]


## Where should compiled data be saved?
#outfolder = "Z:\\current_projects\\DNR_Georgia_Biotics\\data\\landscape\\compiled" # path to output folder
outfolder = "C:\\GeodataCrawlerTools\\data\\fromGeodataCrawler\\compiled"
gdb = "2019_Acanthonus_0313" # name of output file geodatabase to be created


## ----------------------------------------------------------------------------
print "## Compile GeodataCrawler Results"
## ----------------------------------------------------------------------------


# Import modules, set workspace, set constants
print "Importing modules"
import arcpy
import pandas
import os
arcpy.env.workspace = infolder
arcpy.env.overwriteOutput = True
os.chdir(outfolder)

# Create output GDB if it doesn't exist already
pathgdb = outfolder + "\\" + gdb
if not arcpy.Exists(pathgdb + ".gdb"):
    print "Creating a new geodatabase"
    arcpy.CreateFileGDB_management(outfolder, gdb)
else: 
    print "Using an existing geodatabase"

# Loop to extract data from each project and add to the target GDB
print "Initiating data lasso"
for huc in hucs:
    for group in groups:
        for output in outputs:
            outfc = None
            outfc = pathgdb + ".gdb\\" + projectname + "_" + str(huc) + "_Group_" + str(group) + "_" + output
            if not arcpy.Exists(outfc):
                print "Extracting " + projectname + "_" + str(huc) + "_Group_" + str(group)
                infc = infolder + "\\" + projectname + "_" + str(huc) + "_Group_" + str(group) + "\\OUTPUT.gdb\\" + output
                arcpy.CopyFeatures_management(
                    in_features = infc,
                    out_feature_class = outfc)
            else:
                print outfc + " already exists in the target GDB."

# Pause script to allow user to examine target GDB
# raw_input("This script is paused. Press enter to continue.")

# Add FC name as a value in each FC
arcpy.env.workspace = pathgdb + ".gdb"
fcs = []
fcs = ["{0}_{1}_Group_{2}_{3}".format(projectname, str(huc), str(group), output) for huc in hucs for group in groups for output in outputs]
for fc in fcs:
    print "Adding field gdcgroup to " + fc
    expression = str(fc)
    # Crate a new field with a new name
    arcpy.AddField_management(
        in_table = fc,
        field_name = "gdcgroup",
        field_type = "TEXT")
    # Write field values
    arcpy.CalculateField_management(
        in_table = fc,
        field =  "gdcgroup",
        expression = '"'+expression+'"',
        expression_type = "PYTHON")

# Merge feature classes in target file geodatabase based on HUC
arcpy.env.workspace = pathgdb + ".gdb"
targets_leftjoin = []
for huc in hucs:
    for output in outputs:
        outfc = None
        outfc = "{0}_{1}_AllGroups_{2}".format(projectname, huc, output)
        arcpy.env.workspace = pathgdb + ".gdb"
        if not arcpy.Exists(outfc):
            fcs = []
            fcs = arcpy.ListFeatureClasses("{0}_{1}_Group_*_{2}".format(projectname, huc, output))
            print fcs
            print "Merging " + outfc
            arcpy.Merge_management(inputs = fcs, output = outfc)
            rows = arcpy.GetCount_management(outfc)
            print outfc + " contains " + str(rows) + " records"
            # Save results as a CSV
            arcpy.env.workspace = infolder
            print "Saving " + outfc + " as a csv"
            arcpy.TableToTable_conversion(
                    in_rows = "{0}.gdb\\{1}".format(pathgdb, outfc),
                    out_path = outfolder,
                    out_name = "{0}.csv".format(outfc))
            targets_leftjoin.append(outfc)
        else: 
            print outfc + " already exists (not merging nor writing to csv)"
            targets_leftjoin.append(outfc)
    
    ## EMBAIXO CONSTRUCAO ##
    # Combine data from all sample scales into same spreadsheet
    # First, get left side of left-join
    template = None
    template = targets_leftjoin[1] + ".csv" # Keep index as 1 (W scale data in 10km file)!
    df = pandas.read_csv(template, index_col = None)
    LJout = pandas.DataFrame(df["coords_gen"])
    # Then, get right side of left-join
    #for i in range(len(targets_leftjoin)):
    # 0307, 03015 used [1,0,2,3]
    for i in [1,0,2,3]:
        target = None
        target = targets_leftjoin[i] + ".csv"
        target = pandas.read_csv(target, index_col = 0, low_memory = False) # SET DTYPES MANUALLY?
        #dropme = "dropme" + str(i)
        LJout = pandas.merge(
                LJout,
                right = target,
                on = "coords_gen",
                how = "left",
                suffixes = ("", "dropme"))
    # Drop useless columns and save result as CSV to user specified directory
    LJoutdrop = LJout.loc[:,~LJout.columns.str.endswith("dropme")]
    csvout = projectname + "_" + huc + "_AllGroups_AllOutputs.csv"
    LJoutdrop.to_csv(csvout, index = False)
    #LJout.to_csv(csvout, index = False)
    print("Saving ") + csvout