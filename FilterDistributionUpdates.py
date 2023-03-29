# THIS SCRIPT WILL NOT RUN DUE TO REDACTED FEATURE SERVICE PATHS

# Before running this script, do the following:

# PREPARE ADDRESSES FOR CLEANSING
# 1. Check new door knocking and filter distribution addresses against the master address lookup table created from the last update.
# 2. Add an ID to each un-look-up-able address that indicates whether it's a door knocking address or a filter address.
# 3. Send un-look-up-able addresses for cleansing and geocoding.

# RECONCILE ADDRESSES
# 4. Add two columns to each activity's cleansed table (what comes back from Saha): AC_FULL_ADDRESS_NJ in column F and AC_PRIMARY_ADDRESS_NJ in column I.
#    These will be useful for cleansing the cleansed addresses where needed, and if not needed, it'll keep the table the same shape as the rest.
#    Incorporate the addresses into each activity's lookup table and the master lookup table. Remember to remove duplicates based on the input address.
#    Reason for keeping separate lookup tables is to be able to quickly tell # of unique addresses, if needed.
# 5. See which addresses from step 4 have a match in the state address point data (either cleansed address or uncleansed address (the latter
#    being addresses that fall outside the city limits--these got messed up in the address point data cleansing process and all read 
#    "[Name of] Township" instead of "123 Main St" etc.))
# 6. For the addresses that don't have a match in the state address point data, see if can find a manual match.
# 7. For any addresses for which the cleansing process provided coordinates but no better coordinates could be found, indicate that in
#    the coord source field (and same for any address for which no coordinates could be obtained).

# PREPARE UPDATE FOR MAPPING
# 8. Going back to the spreadsheet sent over, sort descending on Recorded Date and grab just the update (e.g., after 5:00 PM March 1, 2023).
#    Copy to a new spreadsheet. Use the lookup table to get coordinates for each address. MAKE SURE THE FIELDS ARE FORMATTED CORRECTLY. Arc will
#    sometimes bring in a text field as date and then nothing imports.

# Not importing arcpy because I'll always run this in the notebook/in Pro so that I can immediately check the outputs

# Plot the coordinates in the spreadsheet

project_path = "C:\\Users\\JohnsonN35\\Local_Work\\BentonHarbor_DoorKnockingFilterDistribution"
gdb_path = project_path + "\\BentonHarbor_Eva.gdb"

# Update these:
update_activity = "BH_FD"
update_date_text = "_03202023_Cumulative"
in_table = project_path + "\\Spreadsheets\\Map_Update_Test\\Filters\\Updates_03202023_.xlsx\\Sheet1$"

out_feature_class = gdb_path + "\\" + update_activity + update_date_text
x_field = "LONG"
y_field = "LAT"
coordinate_system = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],\
UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'

arcpy.management.XYTableToPoint(in_table, out_feature_class, x_field, y_field, None, coordinate_system)

# Access project, then map, then updates and parcel layers within map

aprx = arcpy.mp.ArcGISProject("CURRENT")
bh_updates_map = aprx.listMaps("UpdatesMap")[0]
updates = bh_updates_map.listLayers(update_activity + update_date_text)[0]
parcels = bh_updates_map.listLayers("BerrienParcels_IntersectWithBHandSurroundingMCDs")[0]
print(updates)
print(parcels)

# Test whether the field names in the spreadsheet match the field names being used below for joins

desired_fields = ["Start_Date", "End_Date", "Recorded_Date", "Response_ID", "Team_Member_First_Name", "Team_Member_Last_Name", "Affiliation",\
                 "Team_Name", "Date_of_visit__mm_dd_yyyy_", "Source", "Num_of_Cartridges", "Filter_Type", "Assistance", "Notes", "Resident_First_Name",\
                 "Resident_Last_Name", "Address", "Ward__Values_", "Ward__Formula_", "Phone", "Phone_Type", "Follow_Up_Preference", "Email", "Notes2",\
                 "Distribution_Notes", "Input_JoinID", "LAT", "LONG", "COORD_SOURCE", "SINGLE_LINE_INPUT_ADDR", "CLEANSED_ADDRESS", "WARD"]

current_fields = arcpy.ListFields(updates)
for field in current_fields:
    if field.name in desired_fields:
        print(f"{field.name} is a {field.type} of length {field.length}")
    else: 
        print(field.name + "                                            does not exist")

# Query the updates layer to remove addresses for which there are no coordinates, then export the data

updates.definitionQuery = "COORD_SOURCE <> 'NONE'"
arcpy.conversion.FeatureClassToFeatureClass(updates, gdb_path, update_activity + update_date_text + "LessNACoord")

# Spatial-join to wards

target_features_w = update_activity + update_date_text + "LessNACoord"
join_features_w = "City of Benton Harbor Wards"
out_feature_class_w = gdb_path + "\\" + target_features_w + "_Wards"
field_mapping_w = '\
Start_Date "Start Date" true true false 8 Date 0 0,First,#,target_features_w,Start_Date,-1,-1;\
End_Date "End Date" true true false 8 Date 0 0,First,#,target_features_w,End_Date,-1,-1;\
Recorded_Date "Recorded Date" true true false 8 Date 0 0,First,#,target_features_w,Recorded_Date,-1,-1;\
Response_ID "Response ID" true true false 255 Text 0 0,First,#,target_features_w,Response_ID,0,255;\
Team_Member_First_Name "Team Member First Name" true true false 255 Text 0 0,First,#,target_features_w,Team_Member_First_Name,0,255;\
Team_Member_Last_Name "Team Member Last Name" true true false 255 Text 0 0,First,#,target_features_w,Team_Member_Last_Name,0,255;\
Affiliation "Affiliation" true true false 255 Text 0 0,First,#,target_features_w,Affiliation,0,255;\
Team_Name "Team Name" true true false 255 Text 0 0,First,#,target_features_w,Team_Name,0,255;\
Date_of_visit__mm_dd_yyyy_ "Date of visit (mm/dd/yyyy)" true true false 8 Date 0 0,First,#,target_features_w,Date_of_visit__mm_dd_yyyy_,-1,-1;\
Source "Source" true true false 255 Text 0 0,First,#,target_features_w,Source,0,255;\
Num_of_Cartridges "Num of Cartridges" true true false 8 Double 0 0,First,#,target_features_w,Num_of_Cartridges,-1,-1;\
Filter_Type "Filter Type" true true false 255 Text 0 0,First,#,target_features_w,Filter_Type,0,255;\
Assistance "Assistance" true true false 255 Text 0 0,First,#,target_features_w,Assistance,0,255;\
Notes "Notes" true true false 255 Text 0 0,First,#,target_features_w,Notes,0,255;\
Resident_First_Name "Resident First Name" true true false 255 Text 0 0,First,#,target_features_w,Resident_First_Name,0,255;\
Resident_Last_Name "Resident Last Name" true true false 255 Text 0 0,First,#,target_features_w,Resident_Last_Name,0,255;\
Address "Address" true true false 255 Text 0 0,First,#,target_features_w,Address,0,255;\
Ward__Values_ "Ward (Values)" true true false 255 Text 0 0,First,#,target_features_w,Ward__Values_,0,255;\
Ward__Formula_ "Ward (Formula)" true true false 255 Text 0 0,First,#,target_features_w,Ward__Formula_,0,255;\
Phone "Phone" true true false 255 Text 0 0,First,#,target_features_w,Phone,0,255;\
Phone_Type "Phone Type" true true false 255 Text 0 0,First,#,target_features_w,Phone_Type,0,255;\
Follow_Up_Preference "Follow-Up Preference" true true false 255 Text 0 0,First,#,target_features_w,Follow_Up_Preference,0,255;\
Email "Email" true true false 255 Text 0 0,First,#,target_features_w,Email,0,255;\
Notes2 "Notes2" true true false 255 Text 0 0,First,#,target_features_w,Notes2,0,255;\
Distribution_Notes "Distribution Notes" true true false 255 Text 0 0,First,#,target_features_w,Distribution_Notes,0,255;\
Input_JoinID "Input_JoinID" true true false 255 Text 0 0,First,#,target_features_w,Input_JoinID,0,255;\
LAT "LAT" true true false 8 Double 0 0,First,#,target_features_w,LAT,-1,-1;\
LONG "LONG" true true false 8 Double 0 0,First,#,target_features_w,LONG,-1,-1;\
COORD_SOURCE "COORD_SOURCE" true true false 255 Text 0 0,First,#,target_features_w,COORD_SOURCE,0,255;\
SINGLE_LINE_INPUT_ADDR "SINGLE_LINE_INPUT_ADDR" true true false 255 Text 0 0,First,#,target_features_w,SINGLE_LINE_INPUT_ADDR,0,255;\
CLEANSED_ADDRESS "CLEANSED_ADDRESS" true true false 255 Text 0 0,First,#,target_features_w,CLEANSED_ADDRESS,0,255;\
WARD "WARD" true true false 19 Double 0 0,First,#,City of Benton Harbor Wards,WARD,-1,-1' # From the wards data, I only want to keep the ward field

arcpy.analysis.SpatialJoin(target_features_w, join_features_w, out_feature_class_w, "JOIN_ONE_TO_ONE", "KEEP_ALL", field_mapping_w, "INTERSECT", None)

# Spatial-join to parcels

target_features_p = target_features_w + "_Wards"
join_features_p = "BerrienParcels_IntersectWithBHandSurroundingMCDs"
out_feature_class_p = gdb_path + "\\" + target_features_p + "_Parcels"
field_mapping_p = '\
Start_Date "Start Date" true true false 8 Date 0 0,First,#,target_features_p,Start_Date,-1,-1;\
End_Date "End Date" true true false 8 Date 0 0,First,#,target_features_p,End_Date,-1,-1;\
Recorded_Date "Recorded Date" true true false 8 Date 0 0,First,#,target_features_p,Recorded_Date,-1,-1;\
Response_ID "Response ID" true true false 255 Text 0 0,First,#,target_features_p,Response_ID,0,255;\
Team_Member_First_Name "Team Member First Name" true true false 255 Text 0 0,First,#,target_features_p,Team_Member_First_Name,0,255;\
Team_Member_Last_Name "Team Member Last Name" true true false 255 Text 0 0,First,#,target_features_p,Team_Member_Last_Name,0,255;\
Affiliation "Affiliation" true true false 255 Text 0 0,First,#,target_features_p,Affiliation,0,255;\
Team_Name "Team Name" true true false 255 Text 0 0,First,#,target_features_p,Team_Name,0,255;\
Date_of_visit__mm_dd_yyyy_ "Date of visit (mm/dd/yyyy)" true true false 8 Date 0 0,First,#,target_features_p,Date_of_visit__mm_dd_yyyy_,-1,-1;\
Source "Source" true true false 255 Text 0 0,First,#,target_features_p,Source,0,255;\
Num_of_Cartridges "Num of Cartridges" true true false 8 Double 0 0,First,#,target_features_p,Num_of_Cartridges,-1,-1;\
Filter_Type "Filter Type" true true false 255 Text 0 0,First,#,target_features_p,Filter_Type,0,255;\
Assistance "Assistance" true true false 255 Text 0 0,First,#,target_features_p,Assistance,0,255;\
Notes "Notes" true true false 255 Text 0 0,First,#,target_features_p,Notes,0,255;\
Resident_First_Name "Resident First Name" true true false 255 Text 0 0,First,#,target_features_p,Resident_First_Name,0,255;\
Resident_Last_Name "Resident Last Name" true true false 255 Text 0 0,First,#,target_features_p,Resident_Last_Name,0,255;\
Address "Address" true true false 255 Text 0 0,First,#,target_features_p,Address,0,255;\
Ward__Values_ "Ward (Values)" true true false 255 Text 0 0,First,#,target_features_p,Ward__Values_,0,255;\
Ward__Formula_ "Ward (Formula)" true true false 255 Text 0 0,First,#,target_features_p,Ward__Formula_,0,255;\
Phone "Phone" true true false 255 Text 0 0,First,#,target_features_p,Phone,0,255;\
Phone_Type "Phone Type" true true false 255 Text 0 0,First,#,target_features_p,Phone_Type,0,255;\
Follow_Up_Preference "Follow-Up Preference" true true false 255 Text 0 0,First,#,target_features_p,Follow_Up_Preference,0,255;\
Email "Email" true true false 255 Text 0 0,First,#,target_features_p,Email,0,255;\
Notes2 "Notes2" true true false 255 Text 0 0,First,#,target_features_p,Notes2,0,255;\
Distribution_Notes "Distribution Notes" true true false 255 Text 0 0,First,#,target_features_p,Distribution_Notes,0,255;\
Input_JoinID "Input_JoinID" true true false 255 Text 0 0,First,#,target_features_p,Input_JoinID,0,255;\
LAT "LAT" true true false 8 Double 0 0,First,#,target_features_p,LAT,-1,-1;\
LONG "LONG" true true false 8 Double 0 0,First,#,target_features_p,LONG,-1,-1;\
COORD_SOURCE "COORD_SOURCE" true true false 255 Text 0 0,First,#,target_features_p,COORD_SOURCE,0,255;\
SINGLE_LINE_INPUT_ADDR "SINGLE_LINE_INPUT_ADDR" true true false 255 Text 0 0,First,#,target_features_p,SINGLE_LINE_INPUT_ADDR,0,255;\
CLEANSED_ADDRESS "CLEANSED_ADDRESS" true true false 255 Text 0 0,First,#,target_features_p,CLEANSED_ADDRESS,0,255;\
WARD "WARD" true true false 8 Double 0 0,First,#,target_features_p,WARD,-1,-1,BerrienParcels_IntersectWithBHandSurroundingMCDs,Ward,0,50;\
SiteAdress "Physical Address" true true false 50 Text 0 0,First,#,BerrienParcels_IntersectWithBHandSurroundingMCDs,SiteAdress,0,50;\
ObjectIDText "ObjectIDText" true true false 255 Text 0 0,First,#,BerrienParcels_IntersectWithBHandSurroundingMCDs,ObjectIDText,0,255' # From the parcel data, I only want to keep the site address and object ID text fields

arcpy.analysis.SpatialJoin(target_features_p, join_features_p, out_feature_class_p, "JOIN_ONE_TO_ONE", "KEEP_ALL", field_mapping_p, "INTERSECT", None)

# Attribute-join to parcels based on object ID text

join_table = target_features_p + "_Parcels" 

arcpy.management.AddJoin(parcels, "ObjectIDText", join_table, "ObjectIDText", "KEEP_ALL")

# Export the results of the join, then remove the join and definition query

out_name = target_features_w + "_MappedOnParcels"

parcels.definitionQuery = "CLEANSED_ADDRESS IS NOT NULL"
arcpy.conversion.FeatureClassToFeatureClass(parcels, gdb_path, out_name)
arcpy.management.RemoveJoin(parcels)
parcels.definitionQuery = None

# Delete unnecessary fields that came over from the parcel data

arcpy.management.DeleteField(out_name, "Start_Date;End_Date;Recorded_Date;Response_ID;Team_Member_First_Name;Team_Member_Last_Name;Affiliation;\
                 Team_Name;Date_of_visit__mm_dd_yyyy_;Source;Num_of_Cartridges;Filter_Type;Assistance;Notes;Resident_First_Name;\
                 Resident_Last_Name;Address;Ward__Values_;Ward__Formula_;Phone;Phone_Type;Follow_Up_Preference;Email;Notes2;\
                 Distribution_Notes;Input_JoinID;LAT;LONG;COORD_SOURCE;SINGLE_LINE_INPUT_ADDR;CLEANSED_ADDRESS;WARD_1;SiteAdress_1;ObjectIDText_1", "KEEP_FIELDS")

# Create fields to hold UTC dates

input_table_addresses = target_features_p + "_Parcels"
input_table_parcels = target_features_w + "_MappedOnParcels"
arcpy.management.AddField(input_table_addresses, "Start_Date_UTC", "DATE")
arcpy.management.AddField(input_table_addresses, "End_Date_UTC", "DATE")
arcpy.management.AddField(input_table_addresses, "Recorded_Date_UTC", "DATE")
arcpy.management.AddField(input_table_addresses, "Date_of_visit__mm_dd_yyyy_UTC", "DATE")
arcpy.management.AddField(input_table_parcels, "Start_Date_UTC", "DATE")
arcpy.management.AddField(input_table_parcels, "End_Date_UTC", "DATE")
arcpy.management.AddField(input_table_parcels, "Recorded_Date_UTC", "DATE")
arcpy.management.AddField(input_table_parcels, "Date_of_visit__mm_dd_yyyy_UTC", "DATE")

# Convert times to UTC times

arcpy.management.ConvertTimeZone(input_table_addresses, "Start_Date", "Eastern_Standard_Time", "Start_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_addresses, "End_Date", "Eastern_Standard_Time", "End_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_addresses, "Recorded_Date", "Eastern_Standard_Time", "Recorded_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_addresses, "Date_of_visit__mm_dd_yyyy_", "Eastern_Standard_Time", "Date_of_visit__mm_dd_yyyy_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_parcels, "Start_Date", "Eastern_Standard_Time", "Start_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_parcels, "End_Date", "Eastern_Standard_Time", "End_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_parcels, "Recorded_Date", "Eastern_Standard_Time", "Recorded_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_parcels, "Date_of_visit__mm_dd_yyyy_", "Eastern_Standard_Time", "Date_of_visit__mm_dd_yyyy_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")

# Append address points to layer on production Portal

inputs = target_features_p + "_Parcels"
target = "https://.../hosting/rest/services/Hosted/BH_FD_CumulativeLessNACoord_Wards_Parcels/FeatureServer/26"
schema_type = "NO_TEST"
y = gdb_path + "\\" + inputs
field_mapping = '\
start_date "Start Date" true true false 29 Date 0 0,First,#,y,Start_Date_UTC,-1,-1;\
end_date "End Date" true true false 29 Date 0 0,First,#,y,End_Date_UTC,-1,-1;\
recorded_date "Recorded Date" true true false 29 Date 0 0,First,#,y,Recorded_Date_UTC,-1,-1;\
response_id "Response ID" true true false 255 Text 0 0,First,#,y,Response_ID,0,255;\
team_member_first_name "Team Member First Name" true true false 255 Text 0 0,First,#,y,Team_Member_First_Name,0,255;\
team_member_last_name "Team Member Last Name" true true false 255 Text 0 0,First,#,y,Team_Member_Last_Name,0,255;\
affiliation "Affiliation" true true false 255 Text 0 0,First,#,y,Affiliation,0,255;\
team_name "Team Name" true true false 255 Text 0 0,First,#,y,Team_Name,0,255;\
date_of_visit__mm_dd_yyyy_ "Date of visit (mm/dd/yyyy)" true true false 29 Date 0 0,First,#,y,Date_of_visit__mm_dd_yyyy_UTC,-1,-1;\
source "Source" true true false 255 Text 0 0,First,#,y,Source,-1,-1;\
num_of_cartridges "Num of cartridges" true true false 0 Double 0 0,First,#,y,Num_of_Cartridges,-1,-1;\
filter_type "Filter Type" true true false 255 Text 0 0,First,#,y,Filter_Type,0,255;\
assistance "Assistance" true true false 255 Text 0 0,First,#,y,Assistance,0,255;\
notes "Notes" true true false 255 Text 0 0,First,#,y,Notes,0,255;\
resident_first_name "Resident First Name" true true false 255 Text 0 0,First,#,y,Resident_First_Name,0,255;\
resident_last_name "Resident Last Name" true true false 255 Text 0 0,First,#,y,Resident_Last_Name,0,255;\
address "Address" true true false 255 Text 0 0,First,#,y,Address,0,255;\
phone "Phone" true true false 255 Text 0 0,First,#,y,Phone,-1,-1;\
phone_type "Phone Type" true true false 255 Text 0 0,First,#,y,Phone_Type,0,255;\
follow_up_preference "Follow-Up Preference" true true false 255 Text 0 0,First,#,y,Follow_Up_Preference,0,255;\
email "Email" true true false 255 Text 0 0,First,#,y,Email,0,255;\
notes2 "Notes2" true true false 255 Text 0 0,First,#,y,Notes2,0,255;\
distribution_notes "Distribution Notes" true true false 255 Text 0 0,First,#,y,Distribution_Notes,0,255;\
input_joinid "Input_JoinID" true true false 255 Text 0 0,First,#,y,Input_JoinID,0,255;\
lat "LAT" true true false 0 Double 0 0,First,#,y,LAT,-1,-1;\
long "LONG" true true false 0 Double 0 0,First,#,y,LONG,-1,-1;\
coord_source "COORD_SOURCE" true true false 255 Text 0 0,First,#,y,COORD_SOURCE,0,255;\
single_line_input_addr "SINGLE_LINE_INPUT_ADDR" true true false 255 Text 0 0,First,#,y,SINGLE_LINE_INPUT_ADDR,0,255;\
cleansed_address "CLEANSED_ADDRESS" true true false 255 Text 0 0,First,#,y,CLEANSED_ADDRESS,0,255;\
ward "WARD" true true false 0 Double 0 0,First,#,y,WARD,-1,-1;\
siteadress "Physical Address" true true false 50 Text 0 0,First,#,y,SiteAdress,0,50;\
objectidtext "ObjectIDText" true true false 255 Text 0 0,First,#,y,ObjectIDText,0,255' # Not including 'ward (value)' and 'ward (formula)' fields

arcpy.management.Append(inputs, target, schema_type, field_mapping)

# Update "filter possibly not distributed to address (points)" layer in web map
# This will take a few minutes. SQL would be much more efficient but need to be able to change the "heap size":
# https://pro.arcgis.com/en/pro-app/2.9/help/analysis/geoprocessing/share-analysis/geoprocessing-service-settings-advanced.htm#GUID-17815A98-2756-486F-AC2D-22672E0FCA28

address_points = "https://.../hosting/rest/services/Hosted/Benton_Harbor_Address_Points/FeatureServer/22"
fd_points = "https://.../hosting/rest/services/Hosted/BH_FD_CumulativeLessNACoord_Wards_Parcels/FeatureServer/26"

arcpy.management.SelectLayerByLocation(address_points, "INTERSECT", fd_points, "10 Feet", "NEW_SELECTION", "INVERT")
arcpy.management.CalculateField(address_points, "filterdistributed", "\"Filter possibly not distributed; address is at least 10\' away from a filter distribution point.\"", "PYTHON3")

arcpy.management.SelectLayerByLocation(address_points, "INTERSECT", fd_points, "10 Feet", "NEW_SELECTION")
arcpy.management.CalculateField(address_points, "filterdistributed", "\"Filter probably distributed; address is within 10\' of a filter distribution point.\"", "PYTHON3")

# Append address parcels to layer on production Portal

inputs = target_features_w + "_MappedOnParcels"
target = "https://.../hosting/rest/services/Hosted/Benton_Harbor_Filters_Distributed/FeatureServer/0"
schema_type = "NO_TEST"
y = gdb_path + "\\" + inputs
field_mapping = '\
siteadress "Physical Address" true true false 50 Text 0 0,First,#,y,SiteAdress_1,0,50;\
input_joinid "Input_JoinID" true true false 255 Text 0 0,First,#,y,Input_JoinID,0,255;\
objectidtext "ObjectIDText" true true false 255 Text 0 0,First,#,x,ObjectIDText_1,0,255;\
ward "WARD" true true false 0 Double 0 0,First,#,y,WARD_1,-1,-1;\
affiliation "Affiliation" true true false 255 Text 0 0,First,#,y,Affiliation,0,255;\
cleansed_address "CLEANSED_ADDRESS" true true false 255 Text 0 0,First,#,y,CLEANSED_ADDRESS,0,255;\
recorded_date "recorded_date" true true false 29 Date 0 0,First,#,y,Recorded_Date_UTC,-1,-1;\
date_of_visit__mm_dd_yyyy_ "date_of_visit__mm_dd_yyyy_" true true false 29 Date 0 0,First,#,y,Date_of_visit__mm_dd_yyyy_UTC,-1,-1'

arcpy.management.Append(inputs, target, schema_type, field_mapping)


