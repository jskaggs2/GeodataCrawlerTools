## Dole (split) sites into groups for GDC 'multithreading'
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

import arcpy
import os
import timeit
# import numpy
# import pandas


## ----------------------------------------------------------------------------
print "## Specify user settings"
## ----------------------------------------------------------------------------


# Input and output paths
project = "2020_Acanthonus"
workspace_parent = "C:\\Acanthonus\\"
os.chdir("C:\\Acanthonus\\") #pandas path
gdb = "genericsites.gdb"
points = workspace_parent + gdb + "\\genericsite" # csv, shapefile, or fc
aoi =  workspace_parent + gdb + "\\aoi_GDC" # shapefile or fc
outpath = "C:\\Acanthonus\\toGeodataCrawler\\"
# thegoodones = "export\\selectedgenericsites.csv"
# aoi_GDC = "AcanthonusAll.gdb\\aoi_GDC"
# globalsiteall = "AcanthonusAll.gdb\\globalsiteall"
# globalsiteall_gdc_csv = "export\\globalsiteall.csv"
# workspace_parent = "D:\\users_data\\jskaggs\\Acanthonus"
# os.chdir(r"D:/users_data/jskaggs/Acanthonus") #pandas path
# gdb = "AcanthonusAll.gdb"

# Projections
pathGDC = workspace_parent + "NAD_1983_Albers_GDC.prj"
WGS84 = arcpy.SpatialReference("WGS 1984")

# Method
SubsetByHUC4 = "FALSE"
SubsetEvenly = "FALSE"
SubsetByHUC4ThenNGroups = "TRUE"
n = 10
hucs = ["0306", "0307", "0311", "0312", "0313", "0315", "0602", "0601"]


## ----------------------------------------------------------------------------
print "## Setting workspace and user variables"
## ----------------------------------------------------------------------------


start_master = timeit.default_timer()
print "Setting global constants"
arcpy.CheckOutExtension("Highways")
arcpy.env.workspace = workspace_parent
arcpy.env.overwriteOutput = True
GDC = arcpy.SpatialReference(pathGDC)
print "Setting parent workspace to:",
print workspace_parent
workspace_output = workspace_parent + "\\" + gdb
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})
def cummulative_sum(a_list):
    new_list = []
    cumsum = 0
    for item in a_list:
        cumsum += item
        new_list.append(cumsum)
    return new_list


## ----------------------------------------------------------------------------
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
print "## Check method"
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

# UNDER CONSTRUCAO

# Save inputs in a temporary gdb
print ""
print "## Converting data"
if points.endswith(".csv"):
    arcpy.MakeXYEventLayer_management(
        table = points,
        in_x_field = "NEAR_X", 
        in_y_field = "NEAR_Y", 
        out_layer = "points_layer", 
        spatial_reference = GDC)
    arcpy.CreateFileGDB_management(project)
    points_gdb = project + ".gdb\\points"
    arcpy.CopyFeatures_management(
        in_features = "points_layer",
        out_feature_class = points_gdb)
elif points.endswith(".shp"): print "shp"
else: print "input data type not accepted"

## ----------------------------------------------------------------------------


if (SubsetByHUC4 == "TRUE"):
    hucs = unique_values(aoi, "HUC4")
    for huc in hucs:
        print ""
        print huc
        folder = outpath + "\\" + str(huc)
        if not os.path.exists(folder):
            os.makedirs(folder)
        elif os.path.exists(folder):
            raw_input("The destination folder already exists - delete it and try again.")
        else: raw_input("Something weird happened.")
        arcpy.MakeFeatureLayer_management(
            in_features = aoi,
            out_layer = "aoi_layer")
        arcpy.SelectLayerByAttribute_management(
            in_layer_or_view = "aoi_layer",
            selection_type = "NEW_SELECTION",
            where_clause = "HUC4 = '{0}'".format(str(huc)))
        AOI = folder + "\\AOI"
        arcpy.CopyFeatures_management(
            in_features = "aoi_layer",
            out_feature_class = AOI)
        pointsf = folder + "\\points"
        AOI_shp = AOI + ".shp"
        arcpy.Clip_analysis(
            in_features = points,
            clip_features = AOI_shp,
            out_feature_class = pointsf)


## ----------------------------------------------------------------------------


if (SubsetEvenly == "TRUE"):
    # Calculate breaks
    points_shp = points
    count = int(arcpy.GetCount_management(points_shp).getOutput(0))
    g1 = []
    g1.extend([1])
    g2 = int(count/n)
    g3 = [g2]*(n-1)
    g1.extend(g3)
    g3 = [g2 + (count - g2*n)]
    g1.extend(g3)
    g = cummulative_sum(g1)
    arcpy.MakeFeatureLayer_management(
            in_features = points_shp,
            out_layer = "points_layer")
    for i in range(0, n):
        print ""
        print i
        # Create destination folder
        folder = outpath + project + "\\" + project + "_Group_" + str(i)
        if not os.path.exists(folder):
            os.makedirs(folder)
        # Save POINTS.shp
        arcpy.SelectLayerByAttribute_management(
                in_layer_or_view = "points_layer",
                selection_type = "NEW_SELECTION",
                where_clause = "FID >= {0} AND FID < {1}".format(g[i], g[i+1]))
        points_group = folder + "\\POINTS.shp"
        arcpy.CopyFeatures_management(
                in_features = "points_layer",
                out_feature_class = points_group)
        # Save AOI.shp
        aoi_shp_folder = folder + "\\AOI.shp"
        arcpy.CopyFeatures_management(
                in_features = aoi,
                out_feature_class = aoi_shp_folder)


## ----------------------------------------------------------------------------


if (SubsetByHUC4ThenNGroups == "TRUE"):
    hucs = unique_values(aoi, "HUC4")
    for huc in hucs:
        # Create destination folder
        print ""
        print huc
        folder = outpath + project + "_" + str(huc)
        if not os.path.exists(folder):
            os.makedirs(folder)
        elif os.path.exists(folder):
            raw_input("Folder already exists - delete it and try again.")
        else: raw_input("Something weird happened.")
        tempgdb = project + "_" + str(huc)
        arcpy.CreateFileGDB_management(folder, tempgdb)
        # Save AOI
        arcpy.MakeFeatureLayer_management(
            in_features = aoi,
            out_layer = "aoi_layer")
        arcpy.SelectLayerByAttribute_management(
            in_layer_or_view = "aoi_layer",
            selection_type = "NEW_SELECTION",
            where_clause = "HUC4 = '{0}'".format(str(huc)))
        aoi_shp = folder + "\\AOI.shp"
        arcpy.CopyFeatures_management(
            in_features = "aoi_layer",
            out_feature_class = aoi_shp)
        points_shp = folder + "\\POINTS.shp"
        arcpy.Clip_analysis(
                in_features = points,
                clip_features = aoi_shp,
                out_feature_class = points_shp)
        # Calculate breaks
        count = int(arcpy.GetCount_management(points_shp).getOutput(0))
        g1 = []
        g1.extend([1])
        g2 = int(count/n)
        g3 = [g2]*(n-1)
        g1.extend(g3)
        g3 = [g2 + (count - g2*n)]
        g1.extend(g3)
        g = cummulative_sum(g1)
        arcpy.MakeFeatureLayer_management(
                in_features = points_shp,
                out_layer = "points_layer")
        # Save POINTS.shp
        for i in range(0, n):
            print i
            folder = outpath + project + "_" + str(huc) + "\\" + project + "_" + str(huc) + "_Group_" + str(i)
            if not os.path.exists(folder):
                os.makedirs(folder)
            arcpy.SelectLayerByAttribute_management(
                    in_layer_or_view = "points_layer",
                    selection_type = "NEW_SELECTION",
                    where_clause = "FID >= {0} AND FID < {1}".format(g[i], g[i+1]))
            points_group = folder + "\\POINTS.shp"
            arcpy.CopyFeatures_management(
                    in_features = "points_layer",
                    out_feature_class = points_group)
            aoi_shp_folder = folder + "\\AOI.shp"
            arcpy.CopyFeatures_management(
                    in_features = aoi_shp,
                    out_feature_class = aoi_shp_folder)
print ""
end_master = timeit.default_timer()
master_elapsed = end_master - start_master
print "Total time elapsed:",
print int(master_elapsed/60)
print ""