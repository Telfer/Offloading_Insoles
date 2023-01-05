import rhinoscriptsyntax as rs
import math

def DI_POSITION():
    # Identify scan
    sca = rs.ObjectsByLayer("Position scan")
    scan = sca[0]
    
    
    # =========================================================================
    
    # make sure perspecitive view is maximized
    persp_max = rs.IsViewMaximized("Perspective")
    if persp_max:
        rs.ZoomExtents()
    else:
        rs.MaximizeRestoreView(view = "Perspective")
        rs.ZoomExtents()
    
    
    # =========================================================================
    
    # Identify points for positioning
    ## Make Position scan layer current
    rs.CurrentLayer("Position scan")
    
    ## Get coordinates of heel
    heel_pt = rs.GetPointOnMesh(scan, "Identify lowest point of heel on the plantar surface")
    
    ## Get coordinates of metatarsal head 1
    MTH1_pt = rs.GetPointOnMesh(scan, "Identify MTH1 on the plantar surface")
    
    ## Get coordinates of metatarsal head 5
    MTH5_pt = rs.GetPointOnMesh(scan, "Identify MTH5 on the plantar surface")
    
    ## Get coordinates of highest point on arch
    arch_pt = rs.GetPointOnMesh(scan, "Identify point on medial arch")
    
    
    # =========================================================================
    
    # align foot with world axes
    ## plane of bottom of foot
    foot_plane = rs.PlaneFitFromPoints([heel_pt, MTH1_pt, MTH5_pt])
    
    ## transformation matrix to align with global XY
    trans_mat = rs.XformRotation1(foot_plane, rs.WorldXYPlane())
    
    ## transform scan and points
    rs.TransformObjects([scan, heel_pt, MTH1_pt, MTH5_pt, arch_pt], trans_mat)
    
    ## forefoot mid point
    ff_mid = [(MTH1_pt[0] + MTH5_pt[0]) / 2,
              (MTH1_pt[1] + MTH5_pt[1]) / 2,
              (MTH1_pt[2] + MTH5_pt[2]) / 2]
    
    ## align foot axis with y
    foot_axis = rs.VectorCreate(heel_pt, ff_mid)
    global_axis = rs.VectorCreate([0, 0, 0], [0, 1, 0])
    trans_mat2 = rs.XformRotation3(foot_axis, global_axis, [0, 0, 0])
    rs.TransformObjects([scan, heel_pt, MTH1_pt, MTH5_pt, arch_pt], trans_mat2,)
    
    ## center
    ### Determine foot center point
    ff_mid = [(MTH1_pt[0] + MTH5_pt[0]) / 2, (MTH1_pt[1] + MTH5_pt[1]) / 2,
              (MTH1_pt[2] + MTH5_pt[2]) / 2]
    foot_mid = [(ff_mid[0] + heel_pt[0]) / 2, (ff_mid[1] + heel_pt[1]) / 2, 
                (ff_mid[2] + heel_pt[2]) / 2]
    center_shift = [foot_mid[0] * -1, foot_mid[1] * -1, foot_mid[2] * -1]
    
    ### move to center
    rs.MoveObjects([scan, heel_pt, MTH1_pt, MTH5_pt, arch_pt], center_shift)
    
    ## flip y if needed
    if arch_pt[2] < 0:
        scan = rs.RotateObject(scan, [0, 0, 0], 180, [0, 1, 0])
        arch_pt = rs.RotateObjects([heel_pt, MTH1_pt, MTH5_pt, arch_pt], 
                                   [0, 0, 0], 180, [0, 1, 0])
    
    # list of points
    points = rs.ObjectsByType(1, state = 1)
    
    
    # =========================================================================
    
    # get side
    rs.CurrentLayer("Side")
    
    ## remove any existing objects
    objs = rs.ObjectsByLayer("Side")
    rs.DeleteObjects(objs)
    
    ## add side direction point
    if MTH1_pt[0] > MTH5_pt[0]:
        rs.AddPoint(0, 0, 5)
    else:
        rs.AddPoint(0, 0, -5)
    rs.CurrentLayer("Position scan")
    rs.LayerVisible("Side", False)
    
    ## delete point objects
    rs.DeleteObjects(points)
    
    
    # =========================================================================
    
    # add shoe outline
    ## Get shoe size
    size = rs.ObjectsByLayer("Shoe_size")[0]
    size = (int(rs.coerce3dpoint(size)[2]) * 2) + 1
    
    ## outline data
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
    
    ## points
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
    
    ## layer 
    rs.CurrentLayer("Shoe outline")
    
    ## add curve
    curve2 = rs.AddInterpCurve([heel_center, heel_center_medial, heel_medial, 
                                arch_medial, mtpj1_prox, mtpj1, mtpj1_dist1, 
                                mtpj1_dist2, ff_med, toe_med, toe, toe_lat, 
                                ff_lat, mtpj5_dist2, mtpj5_dist1, mtpj5, 
                                mtpj5_prox, arch_lateral, heel_lateral,
                                heel_center_lateral, heel_center], 
                                degree = 3, knotstyle = 2)
    
    ## mirror if needed
    side = rs.ObjectsByLayer("Side")[0]
    side_dir = rs.coerce3dpoint(side)
    if side_dir[2] < 0:
        plane = rs.WorldYZPlane()
        xform = rs.XformMirror(plane.Origin, plane.Normal)
        curve3 = rs.TransformObject(curve2, xform, False)
    else:
        curve3 = rs.CopyObject(curve2)
        rs.DeleteObject(curve2)
    
    # change color to make clearer
    rs.ObjectColor(curve3, [255, 10, 10])
    
    
    # ========================================================================
    
    # Return to all views and zoom extent on all
    viewmax = rs.IsViewMaximized(view = "Top")
    if viewmax:
        rs.MaximizeRestoreView(view = "Top")
    viewmax = rs.IsViewMaximized(view = "Right")
    if viewmax:
        rs.MaximizeRestoreView(view = "Right")
    viewmax = rs.IsViewMaximized(view = "Front")
    if viewmax:
        rs.MaximizeRestoreView(view = "Front")
    viewmax = rs.IsViewMaximized(view = "Perspective")
    if viewmax:
        rs.MaximizeRestoreView(view = "Perspective")
    rs.ZoomExtents("Top")
    rs.ZoomExtents("Right")
    rs.ZoomExtents("Front")
    rs.ZoomExtents("Perspective")
    
    
    # =========================================================================
    
    # Request user to make further position adjustments as required
    rs.MessageBox("Make further position adjustments to align scan with plane")
    

DI_POSITION()