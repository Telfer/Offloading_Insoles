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
    rs.TransformObjects([scan, heel_pt, MTH1_pt, MTH5_pt, arch_pt], trans_mat2)
    
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
    f = open("C:/Users/telfe/Dropbox/Orthotic_Software/Offloading_Insoles/outlines2.txt")
    data = []
    for line in f:
        row = line.split()
        row[1] = float(row[1])
        row[2] = float(row[2])
        data.append(row)
    f.close()

    ### bottom outline points
    heel_center = [0, data[0][size], 0]
    heel_center_lateral = [data[1][size], data[2][size], 0]
    heel_lateral = [data[3][size], data[4][size], 0]
    arch_lateral = [data[5][size], data[6][size], 0]
    mtpj5_prox = [data[7][size], data[8][size], 0]
    mtpj5 = [data[9][size], data[10][size], 0]
    mtpj5_dist1 = [data[11][size], data[12][size], 0]
    mtpj5_dist2 = [data[13][size], data[14][size], 0]
    ff_lat =[data[15][size], data[16][size], 0]
    toe_lat = [data[17][size], data[18][size], 0]
    toe = [data[19][size], data[20][size], 0]
    toe_med = [data[21][size], data[22][size], 0]
    ff_med = [data[23][size], data[24][size], 0]
    mtpj1_dist2 = [data[25][size], data[26][size], 0]
    mtpj1_dist1 = [data[27][size], data[28][size], 0]
    mtpj1 = [data[29][size], data[30][size], 0]
    mtpj1_prox = [data[31][size], data[32][size], 0]
    arch_medial = [data[33][size], data[34][size], 0]
    heel_medial = [data[35][size], data[36][size], 0]
    heel_center_medial = [data[37][size], data[38][size], 0]
    
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