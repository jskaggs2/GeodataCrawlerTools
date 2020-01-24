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
infolder = "Z:\\current_projects\\DNR_Georgia_Biotics\\data\\landscape\\fromGeodatacrawler\\2019 Acanthonus (1km)" # path to input folder 
projectname = "Acanthonus" # your project name
outputs = ["DelineateData25km", "DelineateData50km", "DelineateData5km", "NewSampleAreasData"] # data collection scales
groups = [0,1,2,3,4,5,6,7,8,9,10,11,12,13] # data subsets
hucs = ["0315"] # list of huc4s

## Where should compiled data be saved?
outfolder = "Z:\\current_projects\\DNR_Georgia_Biotics\\data\\landscape\\compiled" # path to output folder
gdb = "2019_Acanthonus_0315" # name of output file geodatabase to be created


## ----------------------------------------------------------------------------
print "## Compile GeodataCrawler Results"
## ----------------------------------------------------------------------------


# Import modules, set workspace, set constants
print "Importing modules"
import arcpy
import os
import sys
import timeit
sys.path.append(os.path.abspath("Z:\\current_projects\\DNR_Georgia_Biotics\\scripts\\helpers"))
from snippets import printTimeElapsed
arcpy.env.workspace = infolder
arcpy.env.overwriteOutput = True
start_master = timeit.default_timer()

printTimeElapsed(start_master)

# Create output GDB if it doesn't exist already
pathgdb = outfolder + "\\" + gdb
if not arcpy.Exists(pathgdb + ".gdb"):
    print "Creating a new geodatabase"
    arcpy.CreateFileGDB_management(outfolder, gdb)
else: 
    print "Using an existing geodatabase"

printTimeElapsed(start_master)

# Loop to extract data from each project's output GDB and add to the target GDB
print "Initiating data lasso"
for huc in hucs:
    for output in outputs:
        projects = ["{0}_{1}_Group_{2}".format(projectname, huc, str(group)) for group in groups]
        for project in projects:
            print "Extracting " + project + " " + output
            infc = infolder + "\\" + project + "\\OUTPUT.gdb\\" + output
            outfc = pathgdb + ".gdb\\" + project + "_" + output
            arcpy.CopyFeatures_management(in_features = infc, out_feature_class = outfc)

printTimeElapsed(start_master)

# Add feature class name as a value in each feature class
arcpy.env.workspace = pathgdb + ".gdb"
fcs, fc = [], None
for huc in hucs:
    fcs = ["{0}_{1}_Group_{2}_{3}".format(projectname, huc, str(group), output) for group in groups for output in outputs]
    for fc in fcs:
        print "Adding gdc_group to " + str(fc)
        # Crate a new field with a new name
        arcpy.AddField_management(
            in_table = fc,
            field_name = "gdc_group",
            field_type = "TEXT")
        # Write field values
        expression = str(fc)
        arcpy.CalculateField_management(
            in_table = fc,
            field =  "gdc_group",
            expression = '"'+expression+'"',
            expression_type = "PYTHON")
            
printTimeElapsed(start_master)

# Pause script to allow user to examine target GDB
raw_input("This script is paused. Press enter to continue.")
print "Continuing"
printTimeElapsed(start_master)

# Merge feature classes in target file geodatabase based on HUC
fcs, fc = [], None
for huc in hucs:
        arcpy.env.workspace = pathgdb + ".gdb"
        print "Merging all fcs in target gdb"
        fcs = ["{0}_{1}_Group_{2}_{3}".format(projectname, huc, str(group), output) for group in groups for output in outputs]
        outclass = "{0}_{1}_Group_All".format(projectname, huc)
        arcpy.Merge_management(inputs = fcs, output = outclass)
        rows = arcpy.GetCount_management(outclass)
        print outclass  + " contains " + str(rows) + " records"
        
        # Save results as a CSV
        arcpy.env.workspace = infolder
        arcpy.TableToTable_conversion(
                in_rows = "{0}.gdb\\{1}".format(pathgdb, outclass),
                out_path = outfolder,
                out_name = "{0}.csv".format(outclass))
        
        printTimeElapsed(start_master)

print "Total " + printTimeElapsed(start_master)