import rhinoscriptsyntax as rs
import math

def DI_BUILD():
    # helper function
    def get_layer_point_coords(layer):
        point = rs.ObjectsByLayer(layer)[0]
        point_coords = rs.coerce3dpoint(point)
        return point_coords
    
    def point_on_line(x, y, distx):
        vec = [x[0] - y[0], x[1] - y[1], x[2] - y[2]] 
        normx = vec[0] / math.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
        normy = vec[1] / math.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
        normz = vec[2] / math.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
        dist_pointx = x[0] + (distx * normx)
        dist_pointy = x[1] + (distx * normy)
        dist_pointz = x[2] + (distx * normz)
        return([dist_pointx, dist_pointy, dist_pointz])
    
    def intersect_outline(insole_outline, curve, side):
        intersect = rs.CurveCurveIntersection(curve, insole_outline)
        if intersect[0][1][0] > intersect[1][1][0]:
            mtpj1_ = intersect[0][1]
            mtpj5_ = intersect[1][1]
        else:
            mtpj1_ = intersect[1][1]
            mtpj5_ = intersect[0][1]
        
        if side == "LEFT":
            mtpj1_mb = mtpj1_
            mtpj5_mb = mtpj5_
        else:
            mtpj1_mb = mtpj5_
            mtpj5_mb = mtpj1_
        return([mtpj1_mb, mtpj5_mb])
    
    def pointFromMeshCurveInt(lm, insole_outline, scan):
        if len(lm) == 2:
            add_to_line = point_on_line(lm[0], lm[1], 50)
            curve = rs.AddLine([add_to_line[0], add_to_line[1], 0], 
                               [lm[1][0], lm[1][1], 0])
            point = rs.CurveCurveIntersection(insole_outline, curve)[0][1]
            rs.DeleteObject(curve)
            vline = rs.AddLine(point, [point[0], point[1], 40])
        else:
            vline = rs.AddLine([lm[0], lm[1], 0], [lm[0], lm[1], 40])
        
        # find mesh intersect point
        if (rs.CurveMeshIntersection(vline, scan)):
            int_point = rs.CurveMeshIntersection(vline, scan)[0]
        else:
            int_point = [point[0], point[1], lm[1][2]]
        
        rs.DeleteObject(vline)
        return int_point
    
    def make_curve(points):
        curve = rs.AddInterpCurve(points, degree = 3, knotstyle = 2)
        return curve
    
    def lm_inter(insole_curve, lm_y, dir):
        if dir == "R":
            x_curve = rs.AddLine([0, lm_y, 0], [100, lm_y, 0])
            x = rs.CurveCurveIntersection(insole_curve, x_curve)[0][1]
        else:
            x_curve = rs.AddLine([0, lm_y, 0], [-100, lm_y, 0])
            x = rs.CurveCurveIntersection(insole_curve, x_curve)[0][1]
        rs.DeleteObject(x_curve)
        return x
    
    def lm_plane_inter(curve, point, side, ml):
        if side == "RIGHT" and ml == "med":
            plane_crv = rs.AddPolyline([[-100, point, 10], [0, point, 10], 
                                        [0, point, -11], [-100, point, -11], 
                                        [-100, point, 10]])
        if side == "RIGHT" and ml == "lat":
            plane_crv = rs.AddPolyline([[100, point, 10], [0, point, 10], 
                                        [0, point, -11], [100, point, -11], 
                                        [100, point, 10]])
        if side == "LEFT" and ml == "med":
            plane_crv = rs.AddPolyline([[100, point, 10], [0, point, 10], 
                                        [0, point, -11], [100, point, -11], 
                                        [100, point, 10]])
        if side == "LEFT" and ml == "lat":
            plane_crv = rs.AddPolyline([[-100, point, 10], [0, point, 10], 
                                        [0, point, -11], [-100, point, -11], 
                                        [-100, point, 10]])
        plane = rs.AddPlanarSrf(plane_crv)
        intersect_pt = rs.CurveBrepIntersect(curve, plane)[1]
        intersect_coords = rs.PointCoordinates(intersect_pt)
        rs.DeleteObjects([plane_crv, plane, intersect_pt])
        return intersect_coords
    
    
    # =========================================================================
    
    # get scan
    scan = rs.ObjectsByLayer("Position scan")[0]
    
    
    # =========================================================================
    
    # get landmark coordinates
    arch_medial_lm = get_layer_point_coords("Arch Medial")
    arch_center_med_lm = get_layer_point_coords("Arch Center Medial")
    arch_center_lm = get_layer_point_coords("Arch Center")
    arch_center_lat_lm = get_layer_point_coords("Arch Center Lateral")
    arch_lateral_lm = get_layer_point_coords("Arch Lateral")
    mtpj1_lm = get_layer_point_coords("MTPJ1")
    mtpj2_lm = get_layer_point_coords("MTPJ2")
    mtpj3_lm = get_layer_point_coords("MTPJ3")
    mtpj4_lm = get_layer_point_coords("MTPJ4")
    mtpj5_lm = get_layer_point_coords("MTPJ5")
    
    
    # =========================================================================
    
    # foot variables
    ## get side
    side = rs.ObjectsByLayer("Side")[0]
    side_dir = rs.coerce3dpoint(side)
    if side_dir[2] < 0:
        side = "RIGHT"
        dir1 = "L"
        dir2 = "R"
    else:
        side = "LEFT"
        dir1 = "R"
        dir2 = "L"
    
    ## Get shoe size
    size = rs.ObjectsByLayer("Shoe_size")[0]
    size = int(rs.coerce3dpoint(size)[2]) + 1
    
    ## heel cup height
    heel_cup_height = rs.ObjectsByLayer("Heel Cup Height")[0]
    heel_cup_height = rs.coerce3dpoint(heel_cup_height)[2]
    
    ## base thickness
    base_thickness = rs.ObjectsByLayer("Base thickness")[0]
    base_thickness = rs.coerce3dpoint(base_thickness)[2]
    
    
    # =========================================================================
    
    # surface outlines
    ## outline data points bottom
    f = open("C:/Users/telfe/Dropbox/Orthotic_Software/Offloading_Insoles/outlines.txt")
    data_bottom = []
    for line in f:
        row = line.split()
        row[1] = float(row[1])
        row[2] = float(row[2])
        row[3] = float(row[3])
        row[4] = float(row[4])
        row[5] = float(row[5])
        row[6] = float(row[6])
        row[7] = float(row[7])
        row[8] = float(row[8])
        row[9] = float(row[9])
        row[10] = float(row[10])
        row[11] = float(row[11])
        data_bottom.append(row)
    f.close()
    
    ## outline data points top
    f = open("C:/Users/telfe/Dropbox/Orthotic_Software/Offloading_Insoles/outlines2.txt")
    data_top = []
    for line in f:
        row = line.split()
        row[1] = float(row[1])
        row[2] = float(row[2])
        row[3] = float(row[3])
        row[4] = float(row[4])
        row[5] = float(row[5])
        row[6] = float(row[6])
        row[7] = float(row[7])
        row[8] = float(row[8])
        row[9] = float(row[9])
        row[10] = float(row[10])
        row[11] = float(row[11])
        data_top.append(row)
    f.close()
    
    ## bottom outline
    ### bottom outline points
    heel_center = [0, data_bottom[0][size], 0]
    heel_center_ = [0, data_bottom[0][size], 0]
    heel_center_lateral = [data_bottom[1][size], data_bottom[2][size], 0]
    heel_lateral = [data_bottom[3][size], data_bottom[4][size], 0]
    arch_lateral = [data_bottom[5][size], data_bottom[6][size], 0]
    mtpj5_prox = [data_bottom[7][size], data_bottom[8][size], 0]
    mtpj5 = [data_bottom[9][size], data_bottom[10][size], 0]
    mtpj5_dist1 = [data_bottom[11][size], data_bottom[12][size], 0]
    mtpj5_dist2 = [data_bottom[13][size], data_bottom[14][size], 0]
    ff_lat =[data_bottom[15][size], data_bottom[16][size], 0]
    toe_lat = [data_bottom[17][size], data_bottom[18][size], 0]
    toe = [data_bottom[19][size], data_bottom[20][size], 0]
    toe_med = [data_bottom[21][size], data_bottom[22][size], 0]
    ff_med = [data_bottom[23][size], data_bottom[24][size], 0]
    mtpj1_dist2 = [data_bottom[25][size], data_bottom[26][size], 0]
    mtpj1_dist1 = [data_bottom[27][size], data_bottom[28][size], 0]
    mtpj1 = [data_bottom[29][size], data_bottom[30][size], 0]
    mtpj1_prox = [data_bottom[31][size], data_bottom[32][size], 0]
    arch_medial = [data_bottom[33][size], data_bottom[34][size], 0]
    heel_medial = [data_bottom[35][size], data_bottom[36][size], 0]
    heel_center_medial = [data_bottom[37][size], data_bottom[38][size], 0]
    
    ### bottom outline curve
    bottom_outline = make_curve([heel_center, heel_center_medial, 
                                 heel_medial, arch_medial, mtpj1_prox, mtpj1,
                                 mtpj1_dist1, mtpj1_dist2, ff_med, toe_med, toe,
                                 toe_lat, ff_lat, mtpj5_dist2, mtpj5_dist1, 
                                 mtpj5, mtpj5_prox, arch_lateral, heel_lateral, 
                                 heel_center_lateral, heel_center])
    rs.RebuildCurve(bottom_outline, point_count = 50)
    
    ### mid outline points
    heel_center_mo = [0, data_top[0][size], 0]
    heel_center_lateral_mo = [data_top[1][size], data_top[2][size], 0]
    heel_lateral_mo = [data_top[3][size], data_top[4][size], 0]
    arch_lateral_mo = [data_top[5][size], data_top[6][size], 0]
    mtpj5_prox_mo = [data_top[7][size], data_top[8][size], 0]
    mtpj5_mo = [data_top[9][size], data_top[10][size], 0]
    mtpj5_dist1_mo = [data_top[11][size], data_top[12][size], 0]
    mtpj5_dist2_mo = [data_top[13][size], data_top[14][size], 0]
    ff_lat_mo =[data_top[15][size], data_top[16][size], 0]
    toe_lat_mo = [data_top[17][size], data_top[18][size], 0]
    toe_mo = [data_top[19][size], data_top[20][size], 0]
    toe_med_mo = [data_top[21][size], data_top[22][size], 0]
    ff_med_mo = [data_top[23][size], data_top[24][size], 0]
    mtpj1_dist2_mo = [data_top[25][size], data_top[26][size], 0]
    mtpj1_dist1_mo = [data_top[27][size], data_top[28][size], 0]
    mtpj1_mo = [data_top[29][size], data_top[30][size], 0]
    mtpj1_prox_mo = [data_top[31][size], data_top[32][size], 0]
    arch_medial_mo = [data_top[33][size], data_top[34][size], 0]
    heel_medial_mo = [data_top[35][size], data_top[36][size], 0]
    heel_center_medial_mo = [data_top[37][size], data_top[38][size], 0]
    
    ### create mid outline curve
    mid_outline = make_curve([heel_center_mo, heel_center_medial_mo, 
                              heel_medial_mo, arch_medial_mo, mtpj1_prox_mo, 
                              mtpj1_mo, mtpj1_dist1_mo, mtpj1_dist2_mo, 
                              ff_med_mo, toe_med_mo, toe_mo, toe_lat_mo,
                              ff_lat_mo, mtpj5_dist2_mo, mtpj5_dist1_mo, 
                              mtpj5_mo, mtpj5_prox_mo, arch_lateral_mo, 
                              heel_lateral_mo, heel_center_lateral_mo, 
                              heel_center_mo])
    
    ### mid outline 2
    mid_outline2 = make_curve([heel_center_mo, heel_center_medial_mo, 
                               heel_medial_mo, 
                               [arch_medial_mo[0], arch_medial_mo[1], 5], 
                               [mtpj1_prox_mo[0], mtpj1_prox_mo[1], 1],
                               mtpj1_mo, mtpj1_dist1_mo, mtpj1_dist2_mo, 
                               ff_med_mo, toe_med_mo, toe_mo, toe_lat_mo,
                               ff_lat_mo, mtpj5_dist2_mo, mtpj5_dist1_mo, 
                               mtpj5_mo, mtpj5_prox_mo, arch_lateral_mo, 
                               heel_lateral_mo, heel_center_lateral_mo, 
                               heel_center_mo])
    
    ### mirror if necessary
    if side == "RIGHT":
        plane = rs.WorldYZPlane()
        xform = rs.XformMirror(plane.Origin, plane.Normal)
        bottom_outline = rs.TransformObject(bottom_outline, xform, False)
        mid_outline = rs.TransformObject(mid_outline, xform, False)
        mid_outline2 = rs.TransformObject(mid_outline2, xform, False)
    
    
    # =========================================================================
    
    # met bar
    ## get met bar curve
    mb_curve = rs.ObjectsByLayer("Pressure curve")[0]
    
    ## find intersect points
    ### mtpj1 and mtpj5
    mtpj1_mb = intersect_outline(mid_outline, mb_curve, side)[0]
    mtpj5_mb = intersect_outline(mid_outline, mb_curve, side)[1]
    
    ### mtpj1 prox and mtpj5 prox
    mb_curve_prox = rs.CopyObject(mb_curve, [0, -10, 0])
    mtpj1_mb_prox = intersect_outline(mid_outline, mb_curve_prox, side)[0]
    mtpj5_mb_prox = intersect_outline(mid_outline, mb_curve_prox, side)[1]
    
    ### mtpj1 dist1 and mtpj5 dist1
    mb_curve_dist1 = rs.CopyObject(mb_curve, [0, 10, 0])
    mtpj1_mb_dist1 = intersect_outline(mid_outline, mb_curve_dist1, side)[0]
    mtpj5_mb_dist1 = intersect_outline(mid_outline, mb_curve_dist1, side)[1]
    
    ### mtpj1 dist1 and mtpj5 dist2
    mb_curve_dist2 = rs.CopyObject(mb_curve, [0, 15, 0])
    mtpj1_mb_dist2 = intersect_outline(mid_outline, mb_curve_dist2, side)[0]
    mtpj5_mb_dist2 = intersect_outline(mid_outline, mb_curve_dist2, side)[1]
    
    ## layer housekeeping
    rs.LayerVisible("Pressure curve", False)
    
    
    # =========================================================================
    
    # top surface
    ## outline data
    ### medial arch points
    if side == "LEFT":
        arch_medial_offset = [arch_medial_lm[0] + 30, arch_medial_lm[1], 
                              arch_medial_lm[2]]
        arch_lateral_offset = [arch_lateral_lm[0] - 30, arch_lateral_lm[1], 
                               arch_lateral_lm[2]]
    else:
        arch_medial_offset = [arch_medial_lm[0] - 30, arch_medial_lm[1], 
                              arch_medial_lm[2]]
        arch_lateral_offset = [arch_lateral_lm[0] + 30, arch_lateral_lm[1], 
                               arch_lateral_lm[2]]
    arch_medial = pointFromMeshCurveInt([arch_medial_lm, arch_medial_offset], 
                                         mid_outline, scan)
    
    ### lateral arch points
    arch_lateral = lm_inter(mid_outline, arch_lateral_lm[1], dir2)
    arch_lateral[2] = arch_lateral_lm[2]
    
    ### mtpj1 points
    mtpj1 = [mtpj1_mb[0], mtpj1_mb[1], mtpj1_lm[2]]
    mtpj1_prox1 = point_on_line(mtpj1, arch_medial, -5)
    mtpj1_prox1[2] = mtpj1_prox1[2] + 1
    mtpj1_prox2 = point_on_line(mtpj1, arch_medial, -10)
    mtpj1_prox2[2] = mtpj1_prox2[2] + 1
    mtpj1_dist1 = [mtpj1_mb_dist1[0], mtpj1_mb_dist1[1], -3]
    mtpj1_dist2 = [mtpj1_mb_dist2[0], mtpj1_mb_dist2[1], -4]
    
    ### mtpj2 points
    mtpj2 = [mtpj2_lm[0], mtpj2_lm[1], mtpj2_lm[2]]
    mtpj2_prox1 = point_on_line(mtpj2, arch_center_med_lm, -5)
    mtpj2_prox1 = [mtpj2_prox1[0], mtpj2_prox1[1], mtpj2_prox1[2] + 1]
    mtpj2_prox2 = point_on_line(mtpj2, arch_center_med_lm, -12)
    mtpj2_prox2 = [mtpj2_prox2[0], mtpj2_prox2[1], mtpj2_prox2[2] + 1]
    mtpj2_dist1 = [mtpj2[0], mtpj2[1] + 8, -3]
    mtpj2_dist2 = [mtpj2[0], mtpj2[1] + 12, -4]
    
    ### mtpj3 points
    mtpj3 = [mtpj3_lm[0], mtpj3_lm[1], mtpj3_lm[2]]
    mtpj3_prox1 = point_on_line(mtpj3, arch_center_lm, -5)
    mtpj3_prox1 = [mtpj3_prox1[0], mtpj3_prox1[1], mtpj3_prox1[2] + 1]
    mtpj3_prox2 = point_on_line(mtpj3, arch_center_lm, -12)
    mtpj3_prox2 = [mtpj3_prox2[0], mtpj3_prox2[1], mtpj3_prox2[2] + 1]
    mtpj3_dist1 = [mtpj3[0], mtpj3[1] + 8, -3]
    mtpj3_dist2 = [mtpj3[0], mtpj3[1] + 12, -4]
    
    ### mtpj4 points
    mtpj4 = [mtpj4_lm[0], mtpj4_lm[1], mtpj4_lm[2]]
    mtpj4_prox1 = point_on_line(mtpj4, arch_center_lat_lm, -5)
    mtpj4_prox1 = [mtpj4_prox1[0], mtpj4_prox1[1], mtpj4_prox1[2] + 1]
    mtpj4_prox2 = point_on_line(mtpj4, arch_center_lat_lm, -12)
    mtpj4_prox2 = [mtpj4_prox2[0], mtpj4_prox2[1], mtpj4_prox2[2] + 1]
    mtpj4_dist1 = [mtpj4[0], mtpj4[1] + 8, -3]
    mtpj4_dist2 = [mtpj4[0], mtpj4[1] + 12, -4]
    
    ### mtpj5 points
    mtpj5 = [mtpj5_mb[0], mtpj5_mb[1], mtpj5_lm[2]]
    mtpj5_prox1 = point_on_line(mtpj5, arch_lateral, -5)
    mtpj5_prox1 = [mtpj5_prox1[0], mtpj5_prox1[1], mtpj5[2] + 1]
    mtpj5_prox2 = point_on_line(mtpj5, arch_lateral, -10)
    mtpj5_prox2 = [mtpj5_prox2[0], mtpj5_prox2[1], mtpj5[2] + 2]
    mtpj5_dist1 = [mtpj5_mb_dist1[0], mtpj5_mb_dist1[1], -3]
    mtpj5_dist2 = [mtpj5_mb_dist2[0], mtpj5_mb_dist2[1], -4]
    
    ### forefoot points
    mtpj_mid_prox = mtpj3_prox1
    mtpj_mid = mtpj3
    mtpj_mid_dist1 = [mtpj_mid[0], mtpj_mid[1] + 8, -3]
    mtpj_mid_dist2 = [mtpj_mid[0], mtpj_mid[1] + 12, -4]
    if side == "LEFT":
        toe_ff = [toe_mo[0], toe_mo[1], -4]
        ff_dist = toe_ff[1] - mtpj5_dist2[1]
        ft_dist = toe_ff[1] - mtpj1_dist2[1]
        toe_med_ff = [toe_med_mo[0], toe_med_mo[1], -4]
        toe_lat_ff = [toe_lat_mo[0], toe_lat_mo[1], -4]
        toe_med1 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0] + 10, toe_ff[1] -10, 0], [toe_ff[0] + 10, toe_ff[1] + 10, 0]))[0][1]
        toe_med1[2] = -4
        toe_med2 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ft_dist * 0.1], [toe_ff[0] + 100, toe_ff[1] - ft_dist * 0.1]))[0][1]  
        toe_med2[2] = -4
        toe_med3 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ft_dist * 0.2], [toe_ff[0] + 100, toe_ff[1] - ft_dist * 0.2]))[0][1]    
        toe_med3[2] = -4
        toe_med4 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ft_dist * 0.4], [toe_ff[0] + 100, toe_ff[1] - ft_dist * 0.4]))[0][1]    
        toe_med4[2] = -4
        toe_med5 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ft_dist * 0.8], [toe_ff[0] + 100, toe_ff[1] - ft_dist * 0.8]))[0][1]    
        toe_med5[2] = -4
        toe_lat1 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0] - 10, toe_ff[1] -10, 0], [toe_ff[0] - 10, toe_ff[1] + 10, 0]))[0][1]
        toe_lat1[2] = -4
        toe_lat2 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ff_dist * 0.1], [toe_ff[0] - 100, toe_ff[1] - ff_dist * 0.1]))[0][1]    
        toe_lat2[2] = -4
        toe_lat3 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ff_dist * 0.2], [toe_ff[0] - 100, toe_ff[1] - ff_dist * 0.2]))[0][1]    
        toe_lat3[2] = -4
        toe_lat4 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ff_dist * 0.4], [toe_ff[0] - 100, toe_ff[1] - ff_dist * 0.4]))[0][1]    
        toe_lat4[2] = -4
        toe_lat5 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ff_dist * 0.8], [toe_ff[0] - 100, toe_ff[1] - ff_dist * 0.8]))[0][1]  
        toe_lat5[2] = -4
        ff_med_ff = [mtpj1_dist2_mo[0], mtpj1_dist2_mo[1], -4]
        ff_lat_ff = [mtpj5_dist2_mo[0], mtpj5_dist2_mo[1], -4]
        #ff_mid_ff = [(ff_med_ff[0] + ff_lat_ff[0]) / 2, mtpj3_dist2[1] + 10, -4]
        ff_mid_ff = [(toe_med3[0] + toe_lat3[0]) / 2, mtpj3_dist2[1] + 15, -4]
    else:
        toe_ff = [toe_mo[0] * - 1, toe_mo[1], -4]
        ff_dist = toe_ff[1] - mtpj5_dist2[1]
        ft_dist = toe_ff[1] - mtpj1_dist2[1]
        toe_med_ff = [toe_med_mo[0] * -1, toe_med_mo[1], -4]
        toe_lat_ff = [toe_lat_mo[0] * -1, toe_lat_mo[1], -4]
        toe_med1 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0] - 10, toe_ff[1] -10, 0], [toe_ff[0] - 10, toe_ff[1] + 10, 0]))[0][1]
        toe_med1[2] = -4
        toe_med2 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ft_dist * 0.1], [toe_ff[0] - 100, toe_ff[1] - ft_dist * 0.1]))[0][1]
        toe_med2[2] = -4
        toe_med3 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ft_dist * 0.2], [toe_ff[0] - 100, toe_ff[1] - ft_dist * 0.2]))[0][1]
        toe_med3[2] = -4
        toe_med4 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ft_dist * 0.4], [toe_ff[0] - 100, toe_ff[1] - ft_dist * 0.4]))[0][1]
        toe_med4[2] = -4
        toe_med5 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ft_dist * 0.8], [toe_ff[0] - 100, toe_ff[1] - ft_dist * 0.8]))[0][1]
        toe_med5[2] = -4
        toe_lat1 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0] + 10, toe_ff[1] -10, 0], [toe_ff[0] + 10, toe_ff[1] + 10, 0]))[0][1]
        toe_lat1[2] = -4
        toe_lat2 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ff_dist * 0.1], [toe_ff[0] + 100, toe_ff[1] - ff_dist * 0.1]))[0][1]    
        toe_lat2[2] = -4
        toe_lat3 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ff_dist * 0.2], [toe_ff[0] + 100, toe_ff[1] - ff_dist * 0.2]))[0][1]    
        toe_lat3[2] = -4
        toe_lat4 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ff_dist * 0.4], [toe_ff[0] + 100, toe_ff[1] - ff_dist * 0.4]))[0][1]    
        toe_lat4[2] = -4
        toe_lat5 = rs.CurveCurveIntersection(mid_outline, rs.AddLine([toe_ff[0], toe_ff[1] - ff_dist * 0.8], [toe_ff[0] + 100, toe_ff[1] - ff_dist * 0.8]))[0][1]
        toe_lat5[2] = -4
        ff_med_ff = [mtpj1_dist2_mo[0] * -1, mtpj1_dist2_mo[1], -4]
        ff_lat_ff = [mtpj5_dist2_mo[0] * -1, mtpj5_dist2_mo[1], -4]
        ff_mid_ff = [(toe_med3[0] + toe_lat3[0]) / 2, mtpj3_dist2[1] + 15, -4]
        #ff_mid_ff = [(ff_med_ff[0] + ff_lat_ff[0]) / 2, mtpj3_dist2[1] + 15, -4]
    
    ### heel points
    heel_center = [0, heel_center_mo[1], heel_cup_height]
    heel_mid_post = [heel_center[0], heel_center[1] +5, heel_cup_height - 6]
    heel_mid = [0, (heel_medial_mo[1] + heel_lateral_mo[1]) / 2, 0]
    if side == "LEFT":
        heel_lateral = [heel_lateral_mo[0], heel_lateral_mo[1], heel_cup_height]
        heel_medial = [heel_medial_mo[0], heel_medial_mo[1], heel_cup_height]
        heel_center_medial = [heel_center[0] + 18, heel_center[1] + 5, heel_cup_height]
        heel_center_lateral = [heel_center[0] - 15, heel_center[1] + 5, heel_cup_height]
        heel_midm = [heel_mid[0] + 15, heel_mid[1], 2]
        heel_midl = [heel_mid[0] - 15, heel_mid[1], 2]
    else:
        heel_lateral = [heel_lateral_mo[0] * -1, heel_lateral_mo[1], heel_cup_height]
        heel_medial = [heel_medial_mo[0] * -1, heel_medial_mo[1], heel_cup_height]
        heel_center_medial = [(heel_center[0] * - 1) - 18, heel_center[1] + 5, heel_cup_height]
        heel_center_lateral = [(heel_center[0] * - 1) + 15, heel_center[1] + 5, heel_cup_height]
        heel_midm = [(heel_mid[0] * - 1) - 15, heel_mid[1], 2]
        heel_midl = [(heel_mid[0] * - 1) + 15, heel_mid[1], 2]
    
    ### central arch points
    arch_center_med = [arch_center_med_lm[0], arch_center_med_lm[1], 
                       arch_center_med_lm[2]]
    arch_center = [arch_center_lm[0], arch_center_lm[1], arch_center_lm[2]]
    arch_center_lat = [arch_center_lat_lm[0], arch_center_lat_lm[1], 
                       arch_center_lat_lm[2]]
    
    ### construct medial curve
    medial_curve = make_curve([heel_center, heel_center_medial, heel_medial, 
                               arch_medial, mtpj1_prox2, mtpj1_prox1, mtpj1, mtpj1_dist1, 
                               mtpj1_dist2, toe_med5, toe_med4, toe_med3, 
                               toe_med2, toe_med1, toe_ff])
    
    ### construct lateral curve
    lateral_curve = make_curve([toe_ff, toe_lat1, toe_lat2, toe_lat3, toe_lat4, 
                                toe_lat5, mtpj5_dist2, mtpj5_dist1,
                                mtpj5, mtpj5_prox1, mtpj5_prox2, arch_lateral, heel_lateral, 
                                heel_center_lateral, heel_center])
    
    ### construct central curve (runs along long axis of foot)
    central_curve = make_curve([heel_center, heel_mid_post, heel_mid, arch_center,
                                mtpj3_prox2, mtpj_mid_prox, mtpj_mid, mtpj_mid_dist1,
                                mtpj_mid_dist2, ff_mid_ff, toe_ff])
    
    ### construct arch curve (runs mediolateral across arch of foot)
    arch_curve = make_curve([arch_medial, arch_center_med, arch_center,
                             arch_center_lat, arch_lateral])
    
    ### construct forefoot curve
    forefoot_curve = make_curve([mtpj1_prox2, mtpj2_prox2, mtpj3_prox2, 
                                 mtpj4_prox2, mtpj5_prox2])
    forefoot_curve1 = make_curve([mtpj1_prox1, mtpj2_prox1, mtpj3_prox1, 
                                  mtpj4_prox1, mtpj5_prox1])
    forefoot_curve2 = make_curve([mtpj1, mtpj2, mtpj3, mtpj4, mtpj5]) 
    forefoot_curve3 = make_curve([mtpj1_dist1, mtpj2_dist1, mtpj3_dist1, 
                                  mtpj4_dist1, mtpj5_dist1])
    forefoot_curve4 = make_curve([mtpj1_dist2, mtpj2_dist2, mtpj3_dist2, 
                                  mtpj4_dist2, mtpj5_dist2])
    forefoot_curve5 = make_curve([toe_lat5, ff_mid_ff, toe_med5])
    
    ### construct heel curve
    cross_curve_heel = make_curve([heel_medial, heel_midm, heel_mid, heel_midl, 
                                   heel_lateral])
    
    ### make top surface
    top = rs.AddNetworkSrf([medial_curve, lateral_curve, central_curve, 
                            arch_curve, forefoot_curve, forefoot_curve1, forefoot_curve2, 
                            forefoot_curve3, forefoot_curve4, forefoot_curve5, 
                            cross_curve_heel])
    rs.RebuildSurface(top, pointcount = (100, 12))
    
    ### add top skin
    top_skin = rs.ExtrudeSurface(top, rs.AddLine([0, 0, 0], [0, 0, 0.2]))
    
    
    # =========================================================================
    
    # bottom surface
    bottom_outline = rs.MoveObject(bottom_outline, [0, 0, -11])
    bottom = rs.AddPlanarSrf([bottom_outline])
    
    
    # =========================================================================
    
    # Assemble Insole
    ## round bottom edge
    rs.RebuildCurve(mid_outline2, point_count = 100)
    mid_outline2 = rs.MoveObject(mid_outline2, [0, 0, -6])
    arc1 = rs.AddArc3Pt([0, heel_center_mo[1], -6], 
                        [heel_center_[0], heel_center_[1], -11], 
                        [0, heel_center_mo[1] + 1.6, -7.9])
    rs.RebuildCurve(arc1)
    mtpj1_arc_mo = lm_plane_inter(mid_outline2, mtpj1[1], side, "med")
    mtpj1_arc_bo = lm_plane_inter(bottom_outline, mtpj1[1], side, "med")
    if side == "LEFT":
        arc2 = rs.AddArc3Pt(mtpj1_arc_mo, mtpj1_arc_bo,
                            [mtpj1_arc_bo[0] + 3, mtpj1_arc_bo[1], mtpj1_arc_bo[2] + 0.1])
    else:
        #arc2 = rs.AddArc3Pt(mtpj1_arc_mo, mtpj1_arc_bo,
        #                    [mtpj1_arc_mo[0], mtpj1_arc_mo[1], mtpj1_arc_mo[2]])
        arc2 = rs.AddArc3Pt(mtpj1_arc_mo, mtpj1_arc_bo,
                            [mtpj1_arc_bo[0] - 3, mtpj1_arc_bo[1], mtpj1_arc_bo[2] + 0.1])
    bottom_corner1 = rs.AddSweep2([bottom_outline, mid_outline2], [arc1, arc2])
    bottom_corner2 = rs.AddSweep2([bottom_outline, mid_outline2], [arc2, arc1])
    
    ## create surface joining top and bottom
    top_edge = rs.DuplicateSurfaceBorder(top)
    shape1 = rs.AddLine(heel_center, [heel_center_mo[0], heel_center_mo[1], heel_center_mo[2] - 6])
    mtpj1_fix_mo = lm_plane_inter(mid_outline2, mtpj1[1] + 20, side, "med")
    mtpj1_fix_top = lm_plane_inter(top_edge, mtpj1[1] + 20, side, "med")
    shape2 = rs.AddLine(mtpj1_fix_top, mtpj1_fix_mo)
    mtpj5_fix_mo = lm_plane_inter(mid_outline2, mtpj5[1] + 20, side, "lat")
    mtpj5_fix_top = lm_plane_inter(top_edge, mtpj5[1] + 20, side, "lat")
    shape3 = rs.AddLine(mtpj5_fix_top, mtpj5_fix_mo)
    side_surf1 = rs.AddSweep2([mid_outline2, top_edge], [shape1, shape2])
    side_surf2 = rs.AddSweep2([mid_outline2, top_edge], [shape2, shape3])
    side_surf3 = rs.AddSweep2([mid_outline2, top_edge], [shape3, shape1])
    
    ## join all surfaces to make solid
    FO = rs.JoinSurfaces([side_surf1, side_surf2, side_surf3, bottom, 
                          bottom_corner1, bottom_corner2, top], 
                          delete_input = True)
    
    ## delete curves
    rs.DeleteObjects(rs.ObjectsByType(4))
    
    ## trim bottom
    box = rs.AddBox([[200, 200, -20], [-200, 200, -20], [-200, -200, -20], [200, -200, -20],
                     [200, 200, -10.9], [-200, 200, -10.9], [-200, -200, -10.9], [200, -200, -10.9]])
    FO = rs.BooleanDifference(FO, box)
    
    ## tidy up layers
    rs.LayerVisible("Heel Medial", False)
    rs.LayerVisible("Heel Center", False)
    rs.LayerVisible("Heel Lateral", False)
    rs.LayerVisible("Arch Medial", False)
    rs.LayerVisible("Arch Center Medial", False)
    rs.LayerVisible("Arch Center", False)
    rs.LayerVisible("Arch Lateral", False)
    rs.LayerVisible("Arch Center Lateral", False)
    rs.LayerVisible("MTPJ1", False)
    rs.LayerVisible("MTPJ2", False)
    rs.LayerVisible("MTPJ3", False)
    rs.LayerVisible("MTPJ4", False)
    rs.LayerVisible("MTPJ5", False)

DI_BUILD()