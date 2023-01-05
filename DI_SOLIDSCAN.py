import rhinoscriptsyntax as rs

scan = rs.GetObject("Select scan")
plate = rs.GetObject("Select plate")

# split each
scan1 = rs.CopyObject(scan)
scan2 = rs.CopyObject(scan)
plate1 = rs.CopyObject(plate)
plate2 = rs.CopyObject(plate)
rs.Command("-_MeshSplit Selid " + str(scan1) + " _Enter selid " + str(plate1) + " _Enter ")
splitscan = rs.LastCreatedObjects()
rs.Command("-_MeshSplit Selid " + str(plate2) + " _Enter selid " + str(scan2) + " _Enter ")
splitplate = rs.LastCreatedObjects()
plate1_area = rs.MeshArea(splitplate[0])
plate2_area = rs.MeshArea(splitplate[1])
if plate1_area > plate2_area:
    top = splitplate[1]
    rs.DeleteObject(splitplate[0])
else:
    top = splitplate[0]
    rs.DeleteObject(splitplate[1])
scan1_centroid = rs.MeshAreaCentroid(splitscan[0])
scan2_centroid = rs.MeshAreaCentroid(splitscan[1])
if scan1_centroid[2] > scan2_centroid[2]:
    bottom = splitscan[1]
    rs.DeleteObject(splitscan[0])
else:
    bottom = splitscan[0]
    rs.DeleteObject(splitscan[1])
rs.JoinMeshes([top, bottom], delete_input = True)
rs.DeleteObjects([scan, scan1, scan2, plate, plate1, plate2])


#def soft_tissue_cut(scan, plate