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
update_activity = "BH_DK"
update_date_text = "_03202023_Cumulative"
in_table = project_path + "\\Spreadsheets\\Map_Update_Test\\Doorknocking\\Updates_03202023.xlsx\\Sheet1$"

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

desired_fields = ["Start_Date", "End_Date", "Recorded_Date", "Team_Member_First_Name", "Team_Member_Last_Name", "Affiliation", "Team_Name",\
                  "Date_of_visit", "Address", "Able_to_speak_to_resident_", "Interested_in_filter_", "Disposition", "Filter_Type", "Assistance_",\
                  "Notes", "Resident_First_Name", "Resident_Last_Name", "Phone_Number", "Phone_Type", "Follow_up_Preference", "Email", "Column1", \
                  "Column2", "Input_JoinID", "LAT", "LONG", "COORD_SOURCE", "CLEANSED_ADDRESS"]

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
Team_Member_First_Name "Team Member First Name" true true false 255 Text 0 0,First,#,target_features_w,Team_Member_First_Name,0,255;\
Team_Member_Last_Name "Team Member Last Name" true true false 255 Text 0 0,First,#,target_features_w,Team_Member_Last_Name,0,255;\
Affiliation "Affiliation" true true false 255 Text 0 0,First,#,target_features_w,Affiliation,0,255;\
Team_Name "Team Name" true true false 255 Text 0 0,First,#,target_features_w,Team_Name,0,255;\
Date_of_visit "Date of visit" true true false 8 Date 0 0,First,#,target_features_w,Date_of_visit,-1,-1;\
Address "Address" true true false 255 Text 0 0,First,#,target_features_w,Address,0,255;\
Able_to_speak_to_resident_ "Able to speak to resident?" true true false 255 Text 0 0,First,#,target_features_w,Able_to_speak_to_resident_,0,255;\
Interested_in_filter_ "Interested in filter?" true true false 255 Text 0 0,First,#,target_features_w,Interested_in_filter_,0,255;\
Disposition "Disposition" true true false 255 Text 0 0,First,#,target_features_w,Disposition,0,255;\
Filter_Type "Filter Type" true true false 255 Text 0 0,First,#,target_features_w,Filter_Type,0,255;\
Assistance_ "Assistance?" true true false 255 Text 0 0,First,#,target_features_w,Assistance_,0,255;\
Notes "Notes" true true false 255 Text 0 0,First,#,target_features_w,Notes,0,255;\
Resident_First_Name "Resident First Name" true true false 255 Text 0 0,First,#,target_features_w,Resident_First_Name,0,255;\
Resident_Last_Name "Resident Last Name" true true false 255 Text 0 0,First,#,target_features_w,Resident_Last_Name,0,255;\
Phone_Number "Phone Number" true true false 255 Text 0 0,First,#,target_features_w,Phone_Number,0,255;\
Phone_Type "Phone Type" true true false 255 Text 0 0,First,#,target_features_w,Phone_Type,0,255;\
Follow_up_Preference "Follow up Preference" true true false 255 Text 0 0,First,#,target_features_w,Follow_up_Preference,0,255;\
Email "Email" true true false 255 Text 0 0,First,#,target_features_w,Email,0,255;\
Column1 "Column1" true true false 255 Text 0 0,First,#,target_features_w,Column1,0,255;\
Column2 "Column2" true true false 255 Text 0 0,First,#,target_features_w,Column2,0,255;\
Input_JoinID "Input_JoinID" true true false 255 Text 0 0,First,#,target_features_w,Input_JoinID,0,255;\
LAT "LAT" true true false 8 Double 0 0,First,#,target_features_w,LAT,-1,-1;\
LONG "LONG" true true false 8 Double 0 0,First,#,target_features_w,LONG,-1,-1;\
COORD_SOURCE "COORD_SOURCE" true true false 255 Text 0 0,First,#,target_features_w,COORD_SOURCE,0,255;\
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
Team_Member_First_Name "Team Member First Name" true true false 255 Text 0 0,First,#,target_features_p,Team_Member_First_Name,0,255;\
Team_Member_Last_Name "Team Member Last Name" true true false 255 Text 0 0,First,#,target_features_p,Team_Member_Last_Name,0,255;\
Affiliation "Affiliation" true true false 255 Text 0 0,First,#,target_features_p,Affiliation,0,255;\
Team_Name "Team Name" true true false 255 Text 0 0,First,#,target_features_p,Team_Name,0,255;\
Date_of_visit "Date of visit" true true false 8 Date 0 0,First,#,target_features_p,Date_of_visit,-1,-1;\
Address "Address" true true false 255 Text 0 0,First,#,target_features_p,Address,0,255;\
Able_to_speak_to_resident_ "Able to speak to resident?" true true false 255 Text 0 0,First,#,target_features_p,Able_to_speak_to_resident_,0,255;\
Interested_in_filter_ "Interested in filter?" true true false 255 Text 0 0,First,#,target_features_p,Interested_in_filter_,0,255;\
Disposition "Disposition" true true false 255 Text 0 0,First,#,target_features_p,Disposition,0,255;\
Filter_Type "Filter Type" true true false 255 Text 0 0,First,#,target_features_p,Filter_Type,0,255;\
Assistance_ "Assistance?" true true false 255 Text 0 0,First,#,target_features_p,Assistance_,0,255;\
Notes "Notes" true true false 255 Text 0 0,First,#,target_features_p,Notes,0,255;\
Resident_First_Name "Resident First Name" true true false 255 Text 0 0,First,#,target_features_p,Resident_First_Name,0,255;\
Resident_Last_Name "Resident Last Name" true true false 255 Text 0 0,First,#,target_features_p,Resident_Last_Name,0,255;\
Phone_Number "Phone Number" true true false 255 Text 0 0,First,#,target_features_p,Phone_Number,0,255;\
Phone_Type "Phone Type" true true false 255 Text 0 0,First,#,target_features_p,Phone_Type,0,255;\
Follow_up_Preference "Follow up Preference" true true false 255 Text 0 0,First,#,target_features_p,Follow_up_Preference,0,255;\
Email "Email" true true false 255 Text 0 0,First,#,target_features_p,Email,0,255;\
Column1 "Column1" true true false 255 Text 0 0,First,#,target_features_p,Column1,0,255;\
Column2 "Column2" true true false 255 Text 0 0,First,#,target_features_p,Column2,0,255;\
Input_JoinID "Input_JoinID" true true false 255 Text 0 0,First,#,target_features_p,Input_JoinID,0,255;\
LAT "LAT" true true false 8 Double 0 0,First,#,target_features_p,LAT,-1,-1;\
LONG "LONG" true true false 8 Double 0 0,First,#,target_features_p,LONG,-1,-1;\
COORD_SOURCE "COORD_SOURCE" true true false 255 Text 0 0,First,#,target_features_p,COORD_SOURCE,0,255;\
CLEANSED_ADDRESS "CLEANSED_ADDRESS" true true false 255 Text 0 0,First,#,target_features_p,CLEANSED_ADDRESS,0,255;\
WARD "WARD" true true false 8 Double 0 0,First,#,target_features_p,WARD,-1,-1;\
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

arcpy.management.DeleteField(out_name, "Start_Date;End_Date;Recorded_Date;Team_Member_First_Name;Team_Member_Last_Name;Affiliation;Team_Name;\
Date_of_visit;Address;Able_to_speak_to_resident_;Interested_in_filter_;Disposition;Filter_Type;Assistance_;Notes;Resident_First_Name;Resident_Last_Name;\
Phone_Number;Phone_Type;Follow_up_Preference;Email;Column1;Column2;Input_JoinID;LAT;LONG;COORD_SOURCE;CLEANSED_ADDRESS;WARD_1;SiteAdress_1;ObjectIDText_1", "KEEP_FIELDS")

# Create fields to hold UTC dates

input_table_addresses = target_features_p + "_Parcels"
input_table_parcels = target_features_w + "_MappedOnParcels"
arcpy.management.AddField(input_table_addresses, "Start_Date_UTC", "DATE")
arcpy.management.AddField(input_table_addresses, "End_Date_UTC", "DATE")
arcpy.management.AddField(input_table_addresses, "Recorded_Date_UTC", "DATE")
arcpy.management.AddField(input_table_addresses, "Date_of_visit_UTC", "DATE")
arcpy.management.AddField(input_table_parcels, "Start_Date_UTC", "DATE")
arcpy.management.AddField(input_table_parcels, "End_Date_UTC", "DATE")
arcpy.management.AddField(input_table_parcels, "Recorded_Date_UTC", "DATE")
arcpy.management.AddField(input_table_parcels, "Date_of_visit_UTC", "DATE")

# Convert times to UTC times

arcpy.management.ConvertTimeZone(input_table_addresses, "Start_Date", "Eastern_Standard_Time", "Start_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_addresses, "End_Date", "Eastern_Standard_Time", "End_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_addresses, "Recorded_Date", "Eastern_Standard_Time", "Recorded_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_addresses, "Date_of_visit", "Eastern_Standard_Time", "Date_of_visit_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_parcels, "Start_Date", "Eastern_Standard_Time", "Start_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_parcels, "End_Date", "Eastern_Standard_Time", "End_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_parcels, "Recorded_Date", "Eastern_Standard_Time", "Recorded_Date_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")
arcpy.management.ConvertTimeZone(input_table_parcels, "Date_of_visit", "Eastern_Standard_Time", "Date_of_visit_UTC", "UTC", "INPUT_ADJUSTED_FOR_DST", "OUTPUT_ADJUSTED_FOR_DST")

# Append address points to layer on production Portal

inputs = target_features_p + "_Parcels"
target = "https://.../hosting/rest/services/Hosted/Benton_Harbor_Door_Knocking_Addresses/FeatureServer/1"
schema_type = "NO_TEST"
x = gdb_path + "\\" + inputs
field_mapping = '\
input_joinid "input_JoinID" true true false 255 Text 0 0,First,#,x,Input_JoinID,0,255;\
address "Address" true true false 255 Text 0 0,First,#,x,Address,0,255;\
ward "WARD" true true false 0 Double 0 0,First,#,x,WARD,-1,-1;\
objectidtext "ObjectIDText" true true false 255 Text 0 0,First,#,x,ObjectIDText,0,255;\
team_member_first_name "Team Member First Name" true true false 255 Text 0 0,First,#,x,Team_Member_First_Name,0,255;\
team_member_last_name "Team Member Last Name" true true false 255 Text 0 0,First,#,x,Team_Member_Last_Name,0,255;\
affiliation "Affiliation" true true false 255 Text 0 0,First,#,x,Affiliation,0,255;\
team_name "Team Name" true true false 255 Text 0 0,First,#,x,Team_Name,0,255;\
able_to_speak_to_resident_ "Able to speak to resident?" true true false 255 Text 0 0,First,#,x,Able_to_speak_to_resident_,0,255;\
interested_in_filter_ "Interested in filter?" true true false 255 Text 0 0,First,#,x,Interested_in_filter_,0,255;\
disposition "Disposition" true true false 255 Text 0 0,First,#,x,Disposition,0,255;\
filter_type "Filter Type" true true false 255 Text 0 0,First,#,x,Filter_Type,0,255;\
assistance_ "Assistance?" true true false 255 Text 0 0,First,#,x,Assistance_,0,255;\
notes "Notes" true true false 255 Text 0 0,First,#,x,Notes,0,255;\
resident_first_name "Resident First Name" true true false 255 Text 0 0,First,#,x,Resident_First_Name,0,255;\
resident_last_name "Resident Last Name" true true false 255 Text 0 0,First,#,x,Resident_Last_Name,0,255;\
phone_number "Phone Number" true true false 255 Text 0 0,First,#,x,Phone_Number,0,255;\
phone_type "Phone Type" true true false 255 Text 0 0,First,#,x,Phone_Type,0,255;\
follow_up_preference "Follow up Preference" true true false 255 Text 0 0,First,#,x,Follow_up_Preference,0,255;\
email "Email" true true false 255 Text 0 0,First,#,x,Email,0,255;\
column1 "Column1" true true false 255 Text 0 0,First,#,x,Column1,0,255;\
column2 "Column2" true true false 255 Text 0 0,First,#,x,Column2,0,255;\
lat "LAT" true true false 0 Double 0 0,First,#,x,LAT,-1,-1;\
long "LONG" true true false 0 Double 0 0,First,#,x,LONG,-1,-1;\
coord_source "COORD_SOURCE" true true false 255 Text 0 0,First,#,x,COORD_SOURCE,0,255;\
cleansed_address "CLEANSED_ADDRESS" true true false 255 Text 0 0,First,#,x,CLEANSED_ADDRESS,0,255;\
date_of_visit "date_of_visit" true true false 29 Date 0 0,First,#,x,Date_of_visit_UTC,-1,-1;\
recorded_date "recorded_date" true true false 29 Date 0 0,First,#,x,Recorded_Date_UTC,-1,-1;\
end_date "end_date" true true false 29 Date 0 0,First,#,x,End_Date_UTC,-1,-1;\
start_date "start_date" true true false 29 Date 0 0,First,#,x,Start_Date_UTC,-1,-1'

arcpy.management.Append(inputs, target, schema_type, field_mapping)

# Update "addresses possibly not doorknocked (points)" layer in web map
# This will take a few minutes. SQL would be much more efficient but need to be able to change the "heap size":
# https://pro.arcgis.com/en/pro-app/2.9/help/analysis/geoprocessing/share-analysis/geoprocessing-service-settings-advanced.htm#GUID-17815A98-2756-486F-AC2D-22672E0FCA28

address_points = "https://.../hosting/rest/services/Hosted/Benton_Harbor_Address_Points/FeatureServer/22"
dk_points = "https://.../hosting/rest/services/Hosted/Benton_Harbor_Door_Knocking_Addresses/FeatureServer/1"

arcpy.management.SelectLayerByLocation(address_points, "INTERSECT", dk_points, "10 Feet", "NEW_SELECTION", "INVERT")
arcpy.management.CalculateField(address_points, "doorknocked", "\"Possibly not door knocked; address is at least 10\' away from a door knocking point.\"", "PYTHON3")

arcpy.management.SelectLayerByLocation(address_points, "INTERSECT", dk_points, "10 Feet", "NEW_SELECTION")
arcpy.management.CalculateField(address_points, "doorknocked", "\"Probably door knocked; address is within 10\' of a door knocking point.\"", "PYTHON3")

# Append address parcels to layer on production Portal

inputs = target_features_w + "_MappedOnParcels"
target = "https://.../hosting/rest/services/Hosted/Benton_Harbor_Door_Knocking_Parcels/FeatureServer/0"
schema_type = "NO_TEST"
y = gdb_path + "\\" + inputs
field_mapping = '\
siteadress "Physical Address" true true false 50 Text 0 0,First,#,y,SiteAdress_1,0,50;\
input_joinid "input_JoinID" true true false 255 Text 0 0,First,#,y,Input_JoinID,0,255;\
address "Address" true true false 255 Text 0 0,First,#,y,Address,0,255;\
ward "WARD" true true false 0 Double 0 0,First,#,y,WARD_1,-1,-1;\
recorded_date "recorded_date" true true false 29 Date 0 0,First,#,x,Recorded_Date_UTC,-1,-1;\
date_of_visit "date_of_visit" true true false 29 Date 0 0,First,#,x,Date_of_visit_UTC,-1,-1;\
cleansed_address "CLEANSED_ADDRESS" true true false 255 Text 0 0,First,#,y,CLEANSED_ADDRESS,0,255'

arcpy.management.Append(inputs, target, schema_type, field_mapping)
