# Jugal Patel
# Lab 05: Places of Interest near Metro Stations on the Island of Montreal -- Part I
# Email: jugal.patel@mail.mcgill.ca
# April 15, 2020

# Lab focuses on introducing arcpy. Two objectives: i) execute spatial functions, and ii) convert to an arc toolbox

# importing relevant modules
# arcpy - for GIS tasks
import arcpy

# sys - for writing a log file
import sys

# functions
# projection normalization (returns input with 3857 projection applied)
def project3857(FC, outputname):
    in_FC = FC
    out_FC = outputname
    out_projection = arcpy.SpatialReference(3857)
    arcpy.Project_management(in_FC, out_FC, out_projection)
    return FC


# environment / working directory
dir = str("C:/Users/Raja/Dropbox/Coursework/Programming for Spatial Science (GEOG 407)/Lab/lab5")
wd = r'C:\Users\Raja\Dropbox\Coursework\Programming for Spatial Science (GEOG 407)\Lab\lab5'
arcpy.env.workspace = wd  # set wd
arcpy.env.overwriteOutput = True

# prompting user with questions
# prompt one - POI locations
POI_sourcename = str(raw_input("Please input the name of your points of interest file; contains locations of known POI")).lower()

# conditional statement to make sure use inputted file name exists in our working directory
if POI_sourcename == 'mtl_poi.shp' or 'mtl_poi' or 'mtl poi':
    print("Loading Montreal Points of Interest")
    POI = dir + '/MTL_POI.shp'
else:
    print("File not found. Please restart program")
    exit()

# project this shapefile to 3857
print("Projecting POI to 3857")
out_POI = dir + '/MTL_POI_3857.shp'
project3857(POI, out_POI)
POI = dir + '/MTL_POI_3857.shp'

# prompt two - metro station locations
metro_sourcename = str(raw_input("Please input the name of your centroids file; contains pts which will be origins for search radii.")).lower

# conditional statement to make sure use inputted file name exists in our working directory
if metro_sourcename == 'mtl_metrostations.shp' or 'mtl_metrostations' or 'mtl_metro_stations' or 'mtl metro stations':
    print("Loading Montreal Metro station locations")
    metro = dir + '/MTL_MetroStations.shp'
else:
    print("File not found. Please restart program")
    exit()

# project this shapefile to 3857
print("Projecting centroids to 3857")
out_metro = dir + '/MTL_MetroStations_3857.shp'
project3857(metro, out_metro)
metro = dir + '/MTL_MetroStations_3857.shp'

# prompt three - category of interest
category = raw_input("Which (select one) place category are you interested in?")
query = "fclass = '%s'"%category

# create a new feature class with just user's category of interest
# convert feature class of interest to feature layer
arcpy.MakeFeatureLayer_management(POI, "categories")

# select by attribute (based on category var, which is defined by user input)
arcpy.SelectLayerByAttribute_management("categories", "NEW_SELECTION", query)
arcpy.CopyFeatures_management("categories", "category.shp")

# prompt four - search radius
user_radius = int(round(float(raw_input("Please input a positive integer value to dertermine a search radius extent"))))

# Conditional statement to ensure input number was greater than 0:
if user_radius < 0:
    print("Sorry, we cannot accept a negative search radius. Please restart program.")
    exit()
else:
    pass

# geo-processing
print("Program is (geo)processing")

# we have a shapefiles of all known POI; POI of user's category of interest; and Metro locations.
# create a buffer surrounding metro locations w r = user_radius
metro_buffer = dir + '/MTL_MetroStations_3857_buffer.shp'
arcpy.Buffer_analysis(metro, metro_buffer, user_radius)
metro_buffer = dir + '/MTL_MetroStations_3857_buffer.shp'

# convert created buffer feature class into feature layer
arcpy.MakeFeatureLayer_management(metro_buffer, "search_radius")
arcpy.SelectLayerByLocation_management("search_radius", "INTERSECT", "category.shp")
arcpy.CopyFeatures_management("search_radius", "target.shp")

# count targets
target = dir + '/target.shp'
arcpy.MakeFeatureLayer_management(target, "targets")
target_count = arcpy.GetCount_management("targets")

# convert created buffer feature class into feature layer
arcpy.MakeFeatureLayer_management(POI, "all_poi")
arcpy.MakeFeatureLayer_management(metro_buffer, "search_radius")
arcpy.SelectLayerByLocation_management("all_poi", "INTERSECT", "search_radius")
arcpy.CopyFeatures_management("all_poi", "all_poi.shp")

# count all poi within buffered area
all_poi = dir + '/all_poi.shp'
arcpy.MakeFeatureLayer_management(all_poi, "all_pois")
all_poi_count = arcpy.GetCount_management("all_pois")

# count all known poi
arcpy.MakeFeatureLayer_management(POI, "known_poi")
known_poi = dir + '/known_poi.shp'
known_poi_count = arcpy.GetCount_management("known_poi")

# outputs
print("The program intersected all known {0} with buffers of {1} metres around each known metro loc. There were {2} targets that matched this criteria.".format(category, user_radius, target_count))

# sys formatting to write a .log file
old_stdout = sys.stdout
log_file = open("jugalp_lab05.log", "w")
sys.stdout = log_file
print("User supplied place category: {0}.\n User supplied radius: {1} metres.\n Number of {0} within {1} metres of a metro station: {2}.\n Total POI within this area: {3}.\n Total known POI: {4}".format(category, user_radius, target_count, all_poi_count, known_poi_count))
sys.stdout = old_stdout
log_file.close()