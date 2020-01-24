## PART 4: Subset output from acanthonusAll.py by HUC4 basin
## in order to use multithreading in Geodatacrawler.
## Jon Skaggs
## 28 August 2019

print "  ___                  _   _                           	"
print " / _ \                | | | |                          	"
print "/ /_\ \ ___ __ _ _ __ | |_| |__   ___  _ __  _   _ ___ 	"
print "|  _  |/ __/ _` | '_ \| __| '_ \ / _ \| '_ \| | | / __|	"
print "| | | | (_| (_| | | | | |_| | | | (_) | | | | |_| \__ \	"
print "\_| |_/\___\__,_|_| |_|\__|_| |_|\___/|_| |_|\__,_|___/	"
print ""
print ""

## ----------------------------------------------------------------------------
print "## Settings"
print "## Setting workspace and user variables"
## ----------------------------------------------------------------------------

## Import global modules.
print "Importing modules"
import arcpy
import os
import timeit
import numpy
import pandas
import shutil

## Start master timer.
start_master = timeit.default_timer()

print "Setting global constants"
arcpy.CheckOutExtension("Highways")
## Setting other variables
#workspace_parent = os.path.dirname(os.path.abspath(__file__))
workspace_parent = "D:\\users_data\\jskaggs\\Acanthonus"
arcpy.env.workspace = workspace_parent
arcpy.env.overwriteOutput = True
print "Setting parent workspace to:",
print workspace_parent
os.chdir(r"D:/users_data/jskaggs/Acanthonus")  #pandas path
gdb = "AcanthonusAll.gdb"
workspace_output = workspace_parent + "\\" + gdb
WGS84 = arcpy.SpatialReference("WGS 1984")
pathGDC = workspace_parent + "\\NAD_1983_Albers_GDC.prj"
GDC = arcpy.SpatialReference(pathGDC)

## Set paths for inputs.
thegoodones = "export\\selectedgenericsites.csv"
aoi_GDC = "AcanthonusAll.gdb\\aoi_GDC"
globalsiteall = "AcanthonusAll.gdb\\globalsiteall"
globalsiteall_gdc_csv = "export\\globalsiteall.csv"

## Set paths for outputs.
genericsite_f = gdb + "\\genericsite_f"

## Define custom functions.
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})
      
print ""

## Toggle method (mutually exclusive)
SubsetByHUC4 = "FALSE"
SubsetEvenly = "FALSE"
SubsetByHUC4ThenNGroups = "TRUE"
n = 10

## ----------------------------------------------------------------------------
print ""
print "## Read input data"
print "## Check projections"
## ----------------------------------------------------------------------------

# Get projection information for input data and GDC projection. Check if list 
# of projections is a SET equal to 1 (meaning they are all equivalent). If not,
# project the data using the GDC projection.
# print "Checking data projections"
# sr = [arcpy.Describe(globalsiteall).spatialReference.name,
      # arcpy.Describe(aoi_GDC).spatialReference.name,
      # arcpy.Describe(GDC)]
# if not len(set(sr)) == 1:
    # print "Data were not in the correct projection."
    # print "Projecting sites"
    # arcpy.Project_management(
            # in_dataset = globalsiteall,
            # out_dataset = globalsiteall_GDC,
            # out_coor_system = GDC)
    # print "Projecting AOI"
    # arcpy.Project_management(
            # in_dataset = AOI,
            # out_dataset = aoi_GDC,
            # out_coor_system = GDC)
# else:
    # aoi_GDC = aoi
    # globalsiteall_GDC = globalsiteall

## ----------------------------------------------------------------------------

print ""
print "## Split data for multithreading"
if SubsetEvenly == "TRUE":
    print "You selected 'SubsetEvenly'"
    print "The number of groups to create is: " + str(n)
elif SubsetByHUC4 == "TRUE":
    print "You selected SubsetByHUC4"
elif SubsetByHUC4ThenNGroups == "TRUE":
    print "You selected SubsetByHUC4ThenNGroups"
else: print "Select a method with the boolean toggles."

## ----------------------------------------------------------------------------

if (SubsetByHUC4 == "TRUE"):
    arcpy.MakeXYEventLayer_management(
        table = thegoodones,
        in_x_field = "NEAR_X", 
        in_y_field = "NEAR_Y", 
        out_layer = "allpoints_layer", 
        spatial_reference = GDC)
    # Save site features as a feature class.
    print "Saving group as a feature class"  
    allpoints = gdb + "\\allpoints"
    arcpy.CopyFeatures_management(
        in_features = "allpoints_layer",
        out_feature_class = allpoints)
    aoi_GDC = gdb + "\\aoi_GDC"
    hucs = unique_values(aoi_GDC, "HUC4")
    for huc in hucs:
        print huc
        folder = "export//2019 Acanthonus " + str(huc)
        if not os.path.exists(folder):
            os.makedirs(folder)
        elif os.path.exists(folder):
            raw_input("The destination folder already exists - delete it and re-run.")
        else: raw_input("Something weird happened.")
        # Select points by HUC4
        aoi_GDC = gdb + "\\aoi_GDC"
        arcpy.MakeFeatureLayer_management(
            in_features = aoi_GDC,
            out_layer = "aoi_GDC_layer")
        print "Saving AOI"
        arcpy.SelectLayerByAttribute_management(
            in_layer_or_view = "aoi_GDC_layer",
            selection_type = "NEW_SELECTION",
            where_clause = "HUC4 = '{0}'".format(str(huc)))
        AOI = folder + "\\AOI"
        arcpy.CopyFeatures_management(
            in_features = "aoi_GDC_layer",
            out_feature_class = AOI)
        points = folder + "\\points"
        AOI_shp = AOI + ".shp"
        print "Clipping points to AOI"
        arcpy.Clip_analysis(
            in_features = allpoints,
            clip_features = AOI_shp,
            out_feature_class = points)

## ----------------------------------------------------------------------------

if (SubsetEvenly == "TRUE"):
    # Read .csv of globalsites
    globalsiteall_df = pandas.read_csv(
        thegoodones,
        dtype = "str")
    # Drop lentic sites
    globalsiteall_df2 = globalsiteall_df[globalsiteall_df["globalsite_group"] != "globalsite1"]
    # Split into equal groups
    globalsiteall_split = numpy.array_split(globalsiteall_df, n)
    for group in range(0, n):
        print ""
        # Save each group as a 'points.shp' in a new folder.
        # IF THROWS ERROR 5; OPEN SCRIPT AS ADMIN
        folder = "export\\2019 Acanthonus Group " + str(group)
        if os.path.exists(folder):
            raw_input("The destination folder already exists - delete it and re-run.")
        elif not os.path.exists(folder):
            os.makedirs(folder)
        else: raw_input("Something weird happened.")
        # Load site table as an XYEvent.
        print "Make XY table"
        table = globalsiteall_split[group]
        tempcsv = r"pandas/temp.csv"
        table.to_csv(tempcsv)
        arcpy.MakeXYEventLayer_management(
            table = tempcsv,
            in_x_field = "NEAR_X", 
            in_y_field = "NEAR_Y", 
            out_layer = "group_layer", 
            spatial_reference = GDC)
        # Save site features as a feature class.
        print "Saving group as a feature class"  
        points = gdb + "\\points"
        arcpy.CopyFeatures_management(
            in_features = "group_layer",
            out_feature_class = points)
        print "Converting feature class to shapefile"
        arcpy.FeatureClassToShapefile_conversion(
            Input_Features = points,
            Output_Folder = folder)
        # Get AOI for each groups
        print "Getting AOI"
        aoi_GDC = gdb + "\\aoi_GDC"
        arcpy.MakeFeatureLayer_management(
            in_features = aoi_GDC,
            out_layer = "aoi_GDC_layer")
        arcpy.SelectLayerByLocation_management(
            in_layer = "aoi_GDC_layer",
            overlap_type = "CONTAINS",
            select_features = points,
            selection_type = "NEW_SELECTION")
        AOI = gdb + "\\AOI"
        arcpy.CopyFeatures_management(
            in_features = "aoi_GDC_layer",
            out_feature_class = AOI)
        print "Converting feature class to shapefile"
        arcpy.FeatureClassToShapefile_conversion(
            Input_Features = AOI,
            Output_Folder = folder)

## ----------------------------------------------------------------------------

if (SubsetByHUC4ThenNGroups == "TRUE"):
    arcpy.MakeXYEventLayer_management(
        table = thegoodones,
        in_x_field = "NEAR_X", 
        in_y_field = "NEAR_Y", 
        out_layer = "allpoints_layer", 
        spatial_reference = GDC)
    # Save site features as a feature class.
    print "Saving group as a feature class"  
    allpoints = gdb + "\\allpoints"
    arcpy.CopyFeatures_management(
        in_features = "allpoints_layer",
        out_feature_class = allpoints)
    aoi_GDC = gdb + "\\aoi_GDC"
    hucs = unique_values(aoi_GDC, "HUC4")
    for huc in hucs:
        print ""
        print huc
        folder = "export//2019_Acanthonus_" + str(huc)
        if not os.path.exists(folder):
            os.makedirs(folder)
        elif os.path.exists(folder):
            raw_input("The destination folder already exists - delete it and re-run.")
        else: raw_input("Something weird happened.")
        # Select points by HUC4
        aoi_GDC = gdb + "\\aoi_GDC"
        arcpy.MakeFeatureLayer_management(
            in_features = aoi_GDC,
            out_layer = "aoi_GDC_layer")
        print "Saving AOI"
        arcpy.SelectLayerByAttribute_management(
            in_layer_or_view = "aoi_GDC_layer",
            selection_type = "NEW_SELECTION",
            where_clause = "HUC4 = '{0}'".format(str(huc)))
        AOI = folder + "\\AOI"
        arcpy.CopyFeatures_management(
            in_features = "aoi_GDC_layer",
            out_feature_class = AOI)
        points = folder + "\\points"
        # FIX THIS SUFFIX
        AOI_shp = AOI + ".shp"
        print "Clipping points to AOI"
        arcpy.Clip_analysis(
            in_features = allpoints,
            clip_features = AOI_shp,
            out_feature_class = points)
        # PART 2 - split data into n groups
        # Convert points.shp (really .dbf) back to .csv to split with numpy
        print "Converting the points.shp to a points.csv"
        points = r"export/2019_Acanthonus_{0}/points.dbf".format(str(huc))
        arcpy.TableToTable_conversion(
            in_rows = points,
            out_path = r"export/2019_Acanthonus_{0}".format(str(huc)),
            out_name = "points.csv")
        # Read .csv
        print "Split the csv using pandas into n equal parts"
        points_df = pandas.read_csv(folder + "\\points.csv", dtype = "str")
        # Drop lentic sites
        points_df2 = points_df[points_df["globalsite"] != "globalsite1"]
        # Split into equal groups
        points_split = numpy.array_split(points_df, n)
        # Save a copy of each group for each HUC4 in a GDC-ready format
        for group in range(0, n):
            print ""
            print "Group: " + str(group)
            # Create folder
            folder = "export\\2019_Acanthonus_" + str(huc) + "\\2019_Acanthonus_" + str(huc) + "_Group_" + str(group)
            print folder
            if os.path.exists(folder):
                raw_input("The destination folder already exists - delete it and try again.")
            elif not os.path.exists(folder):
                os.makedirs(folder)
            else: raw_input("Something weird happened. Close this window and try again.")
            # Get each subdataframe and make it a csv
            table = points_split[group]
            tempcsv = r"pandas/temp.csv"
            table.to_csv(tempcsv)
            # Convert each subdataframe into a seperate points.shp and aoi.shp
            arcpy.MakeXYEventLayer_management(
                table = tempcsv,
                in_x_field = "NEAR_X", 
                in_y_field = "NEAR_Y", 
                out_layer = "group_layer", 
                spatial_reference = GDC)
            # Save site features as a feature class.
            print "Saving group as a feature class"  
            #points = gdb + "\\points_{0}_{1}".format(str(huc),group)
            POINTS = gdb + "\\POINTS"
            arcpy.CopyFeatures_management(
                in_features = "group_layer",
                out_feature_class = POINTS)
            print "Converting feature class to shapefile"
            arcpy.FeatureClassToShapefile_conversion(
                Input_Features = POINTS,
                Output_Folder = folder)
            AOI2 = folder + "\\AOI.shp"
            arcpy.CopyFeatures_management(
                in_features = AOI_shp,
                out_feature_class = AOI2)
print ""
end_master = timeit.default_timer()
master_elapsed = end_master - start_master
print "Total time elapsed:",
print int(master_elapsed/60)
print ""