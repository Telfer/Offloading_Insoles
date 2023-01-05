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
    
    def lm_inter(insole_curve, lm, dir):
        if dir == "R":
            x_curve = rs.AddLine([0, lm[1], 0], [100, lm[1], 0])
            x = rs.CurveCurveIntersection(insole_curve, x_curve)[0][1]
        else:
            x_curve = rs.AddLine([0, lm[1], 0], [-100, lm[1], 0])
            x = rs.CurveCurveIntersection(insole_curve, x_curve)[0][1]
        rs.DeleteObject(x_curve)
        return x
    
    
    # =========================================================================
    
    # get scan
    scan = rs.ObjectsByLayer("Position scan")[0]
    
    
    # =========================================================================
    
    # get landmark coordinates
    heel_medial_lm = get_layer_point_coords("Heel Medial")
    heel_lateral_lm = get_layer_point_coords("Heel Lateral")
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
    size = int(rs.coerce3dpoint(size)[2]) * 2
    
    ## heel cup height
    heel_cup_height = rs.ObjectsByLayer("Heel Cup Height")[0]
    heel_cup_height = rs.coerce3dpoint(heel_cup_height)[2]
    
    ## base thickness
    base_thickness = rs.ObjectsByLayer("Base thickness")[0]
    base_thickness = rs.coerce3dpoint(base_thickness)[2]
    
    
    # =========================================================================
    
    # surface outlines
    ## outline data points
    heel_center_pt_y = [-126, -132, -126, -134, -115, -122]
    heel_lateral_pt_x = [-24, -30, -22.5, -28.9, -22, -27]
    heel_lateral_pt_y = [-100, -100, -100, -102, -100, -100]
    heel_medial_pt_x = [29, 36, 24.9, 33.1, 26.0, 33]
    heel_medial_pt_y = [-100, -100, -100, -100, -100, -100]
    heel_center_medial_x = [18, 20, 16.8, 20.5, 17, 24]
    heel_center_medial_y = [-121, -128, -120, -127, -110, -115]
    heel_center_lateral_x = [-15, -17.5, -13.9, -17.8, -10, -22]
    heel_center_lateral_y = [-121, -124.5, -119, -125.4, -110, -110]
    arch_medial_pt_x = [25, 36, 17.2, 37.4, 21, 38]
    arch_medial_pt_y = [-10, -12.7, -10, -13.3, -10, -10]
    mtpj1_prox_x = [32, 41, 25.6, 43.4, 25, 44]
    mtpj1_prox_y = [25, 25, 25, 23.4, 25, 25]
    mtpj1_pt_x = [37, 44, 35, 46.6, 30, 46]
    mtpj1_pt_y = [40, 40, 40, 38.1, 40, 40]
    mtpj1_dist1_x = [39, 45.5, 38.6, 47.3, 33, 47]
    mtpj1_dist1_y = [46, 46, 46.4, 42, 46, 46]
    mtpj1_dist2_x = [40, 46, 40.6, 48.4, 36, 47]
    mtpj1_dist2_y = [50, 50, 50, 50, 50, 50]
    toe_med_x = [32, 35, 31, 34.2, 30, 35]
    toe_med_y = [135, 136.7, 134.2, 135.9, 124, 124]
    toe_pt_x = [12, 13, 11.4, 12.2, 12, 11]
    toe_pt_y = [145, 146, 143.9, 147.8, 134, 140]
    toe_lat_x = [-13, -15.4, -12.3, -15.4, -11, -19]
    toe_lat_y = [136, 137.7, 135.3, 137.7, 124, 124]
    mtpj5_pt_x = [-38, -41, -36.9, -45, -35, -41]
    mtpj5_pt_y = [17, 17, 17, 17, 17, 17]
    mtpj5_prox_x = [-37, -40, -34.5, -43.4, -34, -41]
    mtpj5_prox_y = [9, 9, 9, 6.4, 9, 9]
    mtpj5_dist1_x = [-38.5, -42, -37.5, -46, -36, -42]
    mtpj5_dist1_y = [22, 22, 22, 22, 22, 22]
    mtpj5_dist2_x = [-39, -42.5, -38.6, -47, -37, -42]
    mtpj5_dist2_y = [27, 27, 27, 26, 27, 27]
    arch_lateral_pt_x = [-31, -34, -27.7, -36.4, -26, -35]
    arch_lateral_pt_y = [-40, -40, -40, -41, -40, -40]
    ff_med_x = [46, 51, 44.5, 49.4, 40, 45]
    ff_med_y = [80, 80, 80, 80, 80, 80]
    ff_lat_x = [-40, -44.5, -40, -47.6, -37, -43]
    ff_lat_y = [60, 60, 60, 60, 60, 60]
    
    ## bottom outline
    ### bottom outline points
    heel_center = [0, heel_center_pt_y[size], 0]
    heel_lateral = [heel_lateral_pt_x[size], heel_lateral_pt_y[size], 0]
    heel_medial = [heel_medial_pt_x[size], heel_lateral_pt_y[size], 0]
    heel_center_medial = [heel_center_medial_x[size], heel_center_medial_y[size], 0]
    heel_center_lateral = [heel_center_lateral_x[size], heel_center_lateral_y[size], 0]
    arch_medial = [arch_medial_pt_x[size], arch_medial_pt_y[size], 0]
    mtpj1_prox = [mtpj1_prox_x[size], mtpj1_prox_y[size], 0]
    mtpj1 = [mtpj1_pt_x[size], mtpj1_pt_y[size], 0]
    mtpj1_dist1 = [mtpj1_dist1_x[size], mtpj1_dist1_y[size], 0]
    mtpj1_dist2 = [mtpj1_dist2_x[size], mtpj1_dist2_y[size], 0]
    ff_med = [ff_med_x[size], ff_med_y[size], 0]
    toe = [toe_pt_x[size], toe_pt_y[size], 0]
    toe_med = [toe_med_x[size], toe_med_y[size], 0]
    toe_lat = [toe_lat_x[size], toe_lat_y[size], 0]
    ff_lat =[ff_lat_x[size], ff_lat_y[size], 0]
    mtpj5_prox = [mtpj5_prox_x[size], mtpj5_prox_y[size], 0]
    mtpj5 = [mtpj5_pt_x[size], mtpj5_pt_y[size], 0]
    mtpj5_dist1 = [mtpj5_dist1_x[size], mtpj5_dist1_y[size], 0]
    mtpj5_dist2 = [mtpj5_dist2_x[size], mtpj5_dist2_y[size], 0]
    arch_lateral = [arch_lateral_pt_x[size], arch_lateral_pt_y[size], 0]
    
    ### bottom outline curve
    bottom_outline = make_curve([heel_center, heel_center_medial, 
                                 heel_medial, arch_medial, mtpj1_prox, mtpj1,
                                 mtpj1_dist1, mtpj1_dist2, ff_med, toe_med, toe,
                                 toe_lat, ff_lat, mtpj5_dist2, mtpj5_dist1, 
                                 mtpj5, mtpj5_prox, arch_lateral, heel_lateral, 
                                 heel_center_lateral, heel_center])
    
    ### mid outline points
    heel_center_mo = [0, heel_center_pt_y[size + 1], 0]
    heel_lateral_mo = [heel_lateral_pt_x[size + 1], heel_lateral_pt_y[size + 1], 0]
    heel_medial_mo = [heel_medial_pt_x[size + 1], heel_medial_pt_y[size + 1], 0]
    heel_center_medial_mo = [heel_center_medial_x[size + 1], heel_center_medial_y[size + 1], 0]
    heel_center_lateral_mo = [heel_center_lateral_x[size + 1], heel_center_lateral_y[size + 1], 0]
    arch_medial_mo = [arch_medial_pt_x[size + 1], arch_medial_pt_y[size + 1], 0]
    mtpj1_prox_mo = [mtpj1_prox_x[size + 1], mtpj1_prox_y[size + 1], 0]
    mtpj1_mo = [mtpj1_pt_x[size + 1], mtpj1_pt_y[size + 1], 0]
    mtpj1_dist1_mo = [mtpj1_dist1_x[size + 1], mtpj1_dist1_y[size + 1], 0]
    mtpj1_dist2_mo = [mtpj1_dist2_x[size + 1], mtpj1_dist2_y[size + 1], 0]
    toe_mo = [toe_pt_x[size + 1], toe_pt_y[size + 1], 0]
    toe_med_mo = [toe_med_x[size + 1], toe_med_y[size + 1], 0]
    toe_lat_mo = [toe_lat_x[size + 1], toe_lat_y[size + 1], 0]
    mtpj5_prox_mo = [mtpj5_prox_x[size + 1], mtpj5_prox_y[size + 1], 0]
    mtpj5_mo = [mtpj5_pt_x[size + 1], mtpj5_pt_y[size + 1], 0]
    mtpj5_dist1_mo = [mtpj5_dist1_x[size + 1], mtpj5_dist1_y[size + 1], 0]
    mtpj5_dist2_mo = [mtpj5_dist2_x[size + 1], mtpj5_dist2_y[size + 1], 0]
    arch_lateral_mo = [arch_lateral_pt_x[size + 1], arch_lateral_pt_y[size + 1], 0]
    ff_med_mo = [ff_med_x[size + 1], ff_med_y[size + 1], 0]
    ff_lat_mo = [ff_lat_x[size + 1], ff_lat_y[size + 1], 0]
    
    ### create mid outline curve
    mid_outline = make_curve([heel_center_mo, heel_center_medial_mo, 
                              heel_medial_mo, arch_medial_mo, mtpj1_prox_mo, 
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
    
    
    # =========================================================================
    
    # met bar
    ## get met bar curve
    mb_curve = rs.ObjectsByLayer("Pressure curve")[0]
    
    ## find intersect points
    ### mtpj1 and mtpj5
    mtpj1_mb = intersect_outline(mid_outline, mb_curve, side)[0]
    mtpj5_mb = intersect_outline(mid_outline, mb_curve, side)[1]
    
    ### mtpj1 prox and mtpj5 prox
    mb_curve_prox = rs.CopyObject(mb_curve, [0, -5, 0])
    mtpj1_mb_prox = intersect_outline(mid_outline, mb_curve_prox, side)[0]
    mtpj5_mb_prox = intersect_outline(mid_outline, mb_curve_prox, side)[1]
    rs.DeleteObject(mb_curve_prox)
    
    ### mtpj1 dist1 and mtpj5 dist1
    mb_curve_dist1 = rs.CopyObject(mb_curve, [0, 8, 0])
    mtpj1_mb_dist1 = intersect_outline(mid_outline, mb_curve_dist1, side)[0]
    mtpj5_mb_dist1 = intersect_outline(mid_outline, mb_curve_dist1, side)[1]
    rs.DeleteObject(mb_curve_dist1)
    
    ### mtpj1 dist1 and mtpj5 dist2
    mb_curve_dist2 = rs.CopyObject(mb_curve, [0, 12, 0])
    mtpj1_mb_dist2 = intersect_outline(mid_outline, mb_curve_dist2, side)[0]
    mtpj5_mb_dist2 = intersect_outline(mid_outline, mb_curve_dist2, side)[1]
    rs.DeleteObject(mb_curve_dist2)
    
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
    arch_lateral = lm_inter(mid_outline, arch_lateral_lm, dir2)
    arch_lateral[2] = arch_lateral_lm[2]
    
    ### mtpj1 points
    mtpj1 = [mtpj1_mb[0], mtpj1_mb[1], mtpj1_lm[2]]
    mtpj1_prox = point_on_line(mtpj1, arch_medial, -3)
    mtpj1_prox[2] = mtpj1_prox[2] + 1
    mtpj1_dist1 = [mtpj1_mb_dist1[0], mtpj1_mb_dist1[1], -2]
    mtpj1_dist2 = [mtpj1_mb_dist2[0], mtpj1_mb_dist2[1], -3]
    
    ### mtpj2 points
    mtpj2 = [mtpj2_lm[0], mtpj2_lm[1], mtpj2_lm[2]]
    mtpj2_prox = point_on_line(mtpj2, arch_center_med_lm, -3)
    mtpj2_prox = [mtpj2_prox[0], mtpj2_prox[1], mtpj2_prox[2] + 1]
    mtpj2_dist1 = [mtpj2[0], mtpj2[1] + 5, -2]
    mtpj2_dist2 = [mtpj2[0], mtpj2[1] + 10, -3]
    
    ### mtpj3 points
    mtpj3 = [mtpj3_lm[0], mtpj3_lm[1], mtpj3_lm[2]]
    mtpj3_prox = point_on_line(mtpj3, arch_center_lm, -3)
    mtpj3_prox = [mtpj3_prox[0], mtpj3_prox[1], mtpj3_prox[2] + 1]
    mtpj3_dist1 = [mtpj3[0], mtpj3[1] + 5, -2]
    mtpj3_dist2 = [mtpj3[0], mtpj3[1] + 10, -3]
    
    ### mtpj4 points
    mtpj4 = [mtpj4_lm[0], mtpj4_lm[1], mtpj4_lm[2]]
    mtpj4_prox = point_on_line(mtpj4, arch_center_lat_lm, -3)
    mtpj4_prox = [mtpj4_prox[0], mtpj4_prox[1], mtpj4_prox[2] + 1]
    mtpj4_dist1 = [mtpj4[0], mtpj4[1] + 5, -2]
    mtpj4_dist2 = [mtpj4[0], mtpj4[1] + 10, -3]
    
    ### mtpj5 points
    mtpj5 = [mtpj5_mb[0], mtpj5_mb[1], mtpj5_lm[2]]
    mtpj5_prox = point_on_line(mtpj5, arch_lateral, -3)
    mtpj5_prox = [mtpj5_prox[0], mtpj5_prox[1], mtpj5_prox[2] + 1]
    mtpj5_dist1 = [mtpj5_mb_dist1[0], mtpj5_mb_dist1[1], -2]
    mtpj5_dist2 = [mtpj5_mb_dist2[0], mtpj5_mb_dist2[1], -3]
    
    ### forefoot points
    #mtpj_mid_prox = [mtpj3[0], mtpj3[1] - 1, mtpj3[2] + 0.5]
    mtpj_mid_prox = mtpj3_prox
    mtpj_mid = mtpj3
    mtpj_mid_dist1 = [mtpj_mid[0], mtpj_mid[1] + 8, -2]
    mtpj_mid_dist2 = [mtpj_mid[0], mtpj_mid[1] + 12, -3]
    if side == "LEFT":
        toe = [toe_pt_x[size + 1], toe_pt_y[size + 1], -3]
        toe_med = [toe_med_x[size + 1], toe_med_y[size + 1], -3]
        toe_lat = [toe_lat_x[size + 1], toe_lat_y[size + 1], -3]
        ff_med = [ff_med_x[size + 1], ff_med_y[size + 1], -3]
        ff_lat = [ff_lat_x[size + 1], ff_lat_y[size + 1], -3]
        ff_mid = [(ff_med[0] + ff_lat[0]) / 2, mtpj3_dist2[1] + 10, -3]
    else:
        toe = [toe_pt_x[size + 1] * - 1, toe_pt_y[size + 1], -3]
        toe_med = [toe_med_x[size + 1] * -1, toe_med_y[size + 1], -3]
        toe_lat = [toe_lat_x[size + 1] * -1, toe_lat_y[size + 1], -3]
        ff_med = [ff_med_x[size + 1] * -1, ff_med_y[size + 1], -3]
        ff_lat = [ff_lat_x[size + 1] * -1, ff_lat_y[size + 1], -3]
        ff_mid = [(ff_med[0] + ff_lat[0]) / 2, mtpj3_dist2[1] + 10, -3]
    
    ### heel points
    heel_center = [0, heel_center_pt_y[size + 1], heel_cup_height]
    heel_mid_post = [heel_center[0], heel_center[1] +5, heel_cup_height - 6]
    heel_mid = [0, (heel_medial[1] + heel_lateral[1]) / 2, 0]
    if side == "LEFT":
        heel_lateral = [heel_lateral_pt_x[size + 1], -100, heel_cup_height]
        heel_medial = [heel_medial_pt_x[size + 1], -100, heel_cup_height]
        heel_center_medial = [heel_center[0] + 18, heel_center[1] + 5, heel_cup_height]
        heel_center_lateral = [heel_center[0] - 15, heel_center[1] + 5, heel_cup_height]
        heel_midm = [heel_mid[0] + 15, heel_mid[1], 2]
        heel_midl = [heel_mid[0] - 15, heel_mid[1], 2]
    else:
        heel_lateral = [heel_lateral_pt_x[size + 1] * -1, -100, heel_cup_height]
        heel_medial = [heel_medial_pt_x[size + 1] * -1, -100, heel_cup_height]
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
                               arch_medial, mtpj1_prox, mtpj1, mtpj1_dist1, 
                               mtpj1_dist2, ff_med, toe_med, toe])
    
    ### construct lateral curve
    lateral_curve = make_curve([toe, toe_lat, ff_lat, mtpj5_dist2, mtpj5_dist1, 
                                mtpj5, mtpj5_prox, arch_lateral, heel_lateral, 
                                heel_center_lateral, heel_center])
    
    ### construct central curve (runs along long axis of foot)
    central_curve = make_curve([heel_center, heel_mid_post, heel_mid, arch_center,
                                mtpj_mid_prox, mtpj_mid, mtpj_mid_dist1,
                                mtpj_mid_dist2, ff_mid, toe])
    
    ### construct arch curve (runs mediolateral across arch of foot)
    arch_curve = make_curve([arch_medial, arch_center_med, arch_center,
                             arch_center_lat, arch_lateral])
    
    ### construct forefoot curve
    forefoot_curve1 = make_curve([mtpj1_prox, mtpj2_prox, mtpj3_prox, 
                                  mtpj4_prox, mtpj5_prox])
    forefoot_curve2 = make_curve([mtpj1, mtpj2, mtpj3, mtpj4, mtpj5]) 
    forefoot_curve3 = make_curve([mtpj1_dist1, mtpj2_dist1, mtpj3_dist1, 
                                  mtpj4_dist1, mtpj5_dist1])
    forefoot_curve4 = make_curve([mtpj1_dist2, mtpj2_dist2, mtpj3_dist2, 
                                  mtpj4_dist2, mtpj5_dist2])
    forefoot_curve5 = make_curve([ff_lat, ff_mid, ff_med])
    
    ### construct heel curve
    cross_curve_heel = make_curve([heel_medial, heel_midm, heel_mid, heel_midl, 
                                   heel_lateral])
    
    ### make top surface
    top = rs.AddNetworkSrf([medial_curve, lateral_curve, arch_curve,
                            forefoot_curve1, forefoot_curve2, forefoot_curve3, 
                            forefoot_curve4, forefoot_curve5, 
                            cross_curve_heel, central_curve])
    
    ### tidy up
    #rs.DeleteObjects([medial_curve, lateral_curve, central_curve, 
    #                  arch_curve, forefoot_curve1, forefoot_curve2, 
    #                  forefoot_curve3, forefoot_curve4, cross_curve_heel])
    
    
    # =========================================================================
    
    # rebuild mid outline
    #mtpj1_prox_mo = lm_inter(mid_outline, mtpj1_prox, dir1)
    #mtpj1_prox_mo[2] = mtpj1_prox_mo[2] + 2
    #mtpj1_mo = lm_inter(mid_outline, mtpj1, dir1)
    #mtpj1_dist1_mo = lm_inter(mid_outline, mtpj1_dist1, dir1)
    #mtpj1_dist2_mo = lm_inter(mid_outline, mtpj1_dist2, dir1)
    #mtpj5_prox_mo = lm_inter(mid_outline, mtpj5_prox, dir2)
    #mtpj5_prox_mo[2] = mtpj5_prox_mo[2] + 1
    #mtpj5_mo = lm_inter(mid_outline, mtpj5, dir2)
    #mtpj5_dist1_mo = lm_inter(mid_outline, mtpj5_dist1, dir2)
    #mtpj5_dist2_mo = lm_inter(mid_outline, mtpj5_dist2, dir2)
    #mtpj5_dist1_mo[1] = mtpj5_dist1_mo[1] - 3 
    #mtpj5_dist2_mo[1] = mtpj5_dist2_mo[1] - 3
    #heel_center_mo[2] = 10
    #heel_center_medial_mo[2] = 10
    #heel_medial_mo[2] = 10
    #arch_medial_mo[2] = 15
    #arch_lateral_mo[2] = 10
    #heel_lateral_mo[2] = 10
    #heel_center_lateral_mo[2] = 10
    #heel_center_mo = [heel_center_mo[0], heel_center_mo[1], 10]
    
    
    # =========================================================================
    
    # bottom surface
    #bottom_outline = rs.MoveObject(bottom_outline, [0, 0, -10])
    #bottom = rs.AddPlanarSrf([bottom_outline])
    
    
    # =========================================================================
    
    # Assemble Insole
    ## smooth bottom edge
    #mid_outline = rs.MoveObject(mid_outline, [0, 0, -6])
    #arc = rs.AddArc3Pt([0, heel_center_mo[1], -6], 
    #                   [heel_center[0], heel_center_pt_y[size], -10], 
    #                   [0, heel_center_mo[1] + 1.5, -8])
    #bottom_corner = rs.AddSweep2([bottom_outline, mid_outline], [arc])
    #rs.DeleteObject(bottom_outline)
    
    ## create surface joining top and bottom
    #top_edge = rs.DuplicateSurfaceBorder(top)
    ##bottom_edge = rs.DuplicateSurfaceBorder(bottom)
    #side_surf = rs.AddLoftSrf([top_edge, mid_outline])#bottom_edge])
    #rs.DeleteObject(mid_outline)
    
    ## join all surfaces to maek solid
    #FO = rs.JoinSurfaces([side_surf, bottom, bottom_corner, top], delete_input = True)
    
    ## delete curve
    #rs.DeleteObjects(rs.ObjectsByType(4))
    
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