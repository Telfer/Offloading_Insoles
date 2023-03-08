# make FE components

# =============================================================================

# modules required
import rhinoscriptsyntax as rs
import math
import os
import Rhino
import scriptcontext as sc


# =============================================================================

# add layers for FE parts
rs.AddLayer("FE Bones")
rs.AddLayer("FE Tissue")
rs.AddLayer("FE Insole")
rs.AddLayer("FE MT2")
rs.AddLayer("FE MT2 Tissue")


# =============================================================================

def FE_parts():
    # helper functions
    def build_met(rad, wid, sag_ang, cor_ang, fsz):
        # outline
        line1 = rs.AddLine([wid / 2, 0, 0], [wid / 2, 0, rad - fsz])
        line2 = rs.AddLine([0, 0, rad], [wid / 2 - fsz, 0, rad])
        arc = rs.AddArc(rs.WorldZXPlane(), fsz, 90.0)
        arc = rs.MoveObject(arc, [wid / 2 - fsz, 0, rad - fsz])
        line = rs.JoinCurves([line1, arc, line2], delete_input = True)
        plane = rs.WorldYZPlane()
        xform = rs.XformMirror(plane.Origin, plane.Normal)
        linea = rs.TransformObject(line, xform, True)
        line = rs.JoinCurves([line, linea], delete_input = True)
        axis = rs.AddLine([0, 0, 0], [1, 0, 0])
        head = rs.AddRevSrf(line, axis)
        rs.DeleteObjects([line, axis])
        
        # shaft
        shaft = rs.AddCylinder(rs.WorldZXPlane(), -50, (wid / 2) - 0.5)
        shaft = rs.RotateObject(shaft, [0, 0, 0], sag_ang * -1, [1, 0, 0])
        
        # Union
        met = rs.BooleanUnion([head, shaft])
        met = rs.RotateObject(met, [0, 0, 0], cor_ang, [0, 0, 1])
        
        # return
        return met
    
    def make_ses(ses_rad, ses_length, ses_height):
        ses_length = ses_length + 0.01
        sph1 = rs.AddSphere([0, 0, 0], ses_rad)
        sph2 = rs.CopyObject(sph1, [0, (ses_length - ses_rad * 2) * -1, 0])
        cyl1 = rs.AddCylinder(rs.WorldZXPlane(), (ses_length - ses_rad * 2) * -1, ses_rad)
        cyl2 = rs.AddCylinder(rs.WorldXYPlane(), ses_height, ses_rad)
        cyl3 = rs.CopyObject(cyl2, [0, (ses_length - ses_rad * 2) * -1, 0])
        box_points = [[ses_rad, 0, 0], 
                      [ses_rad, (ses_length - ses_rad * 2) * -1, 0],
                      [ses_rad * -1, (ses_length - ses_rad * 2) * -1, 0], 
                      [ses_rad * -1, 0, 0],
                      [ses_rad, 0, ses_height], 
                      [ses_rad, (ses_length - ses_rad * 2) * -1, ses_height],
                      [ses_rad * -1, (ses_length - ses_rad * 2) * -1, ses_height], 
                      [ses_rad * -1, 0, ses_height]]
        box = rs.AddBox(box_points)
        ses = rs.BooleanUnion([sph1, sph2, cyl1, cyl2, cyl3, box])
        return(ses)
    
    def export_stl(directory, part, fn):
        fn = fn + ".stl"
        ffp = os.path.join(directory, fn) 
        rs.SelectObject(part)
        rs.Command('-_Export "{}" _Enter _Enter'.format(ffp))
    
    def meshBoolSplit(x, y, dir):
        cmd_str = ("-_MeshBooleanSplit SelID " + str(x) + 
                   " _Enter SelID " + str(y) + " _Enter")
        rs.Command(cmd_str)
        cut_scan = rs.LastCreatedObjects()
        cs1a = rs.MeshAreaCentroid(cut_scan[0])
        cs2a = rs.MeshAreaCentroid(cut_scan[1])
        if dir == "prox":
            if cs1a[1] > cs2a[1]:
                rs.DeleteObject(cut_scan[0])
                return cut_scan[1]
            else:
                rs.DeleteObject(cut_scan[1])
                return cut_scan[0]
        if dir == "dors":
            if cs1a[2] > cs2a[2]:
                rs.DeleteObject(cut_scan[1])
                return cut_scan[0]
            else:
                rs.DeleteObject(cut_scan[0])
                return cut_scan[1]
        if dir == "plant":
            if cs1a[2] < cs2a[2]:
                rs.DeleteObject(cut_scan[1])
                return cut_scan[0]
            else:
                rs.DeleteObject(cut_scan[0])
                return cut_scan[1]
        if dir == "dist":
            if cs1a[1] > cs2a[1]:
                rs.DeleteObject(cut_scan[1])
                return cut_scan[0]
            else:
                rs.DeleteObject(cut_scan[0])
                return cut_scan[1]
        if dir == "med":
            if cs1a[0] > cs2a[0]:
                rs.DeleteObject(cut_scan[0])
                return cut_scan[1]
            else:
                rs.DeleteObject(cut_scan[1])
                return cut_scan[0]
        if dir == "lat":
            if cs2a[0] > cs1a[0]:
                rs.DeleteObject(cut_scan[0])
                return cut_scan[1]
            else:
                rs.DeleteObject(cut_scan[1])
                return cut_scan[0]
    
    def meshBoolDiff(x, y):
        cmd_str = ("-_MeshBooleanDifference SelID " + str(x) + 
                   " _Enter SelID " + str(y) + " _Enter")
        rs.Command(cmd_str)
        cut_scan = rs.LastCreatedObjects()
        return(cut_scan)
    
    def moveLive(message):
        while True:
            arrObject = rs.GetObjectEx(message,0,False,True)
            if arrObject is None: break
            idObject = arrObject[0]
            arrP = arrObject[3]
            rs.Command("_Move " + str(arrP) + " _Pause _EnterEnd", False)
            if rs.LastCommandResult() != 0:
                break
        return
    
    def pointFromMeshCurveInt(lm, scan):
        # define vline
        vline = rs.AddLine([lm[0], lm[1], 0], [lm[0], lm[1], 40])
        
        # find mesh intersect point
        if (rs.CurveMeshIntersection(vline, scan)):
            int_point = rs.CurveMeshIntersection(vline, scan)[0]
        else:
            int_point = [point[0], point[1], lm[1][2]]
        
        rs.DeleteObject(vline)
        return int_point
    
    
    # =========================================================================
    
    # get side 
    side = rs.ObjectsByLayer("Side")[0]
    side_dir = rs.coerce3dpoint(side)
    if side_dir[2] < 0:
        side = "RIGHT"
    else:
        side = "LEFT"
    
    
    # =========================================================================
    
    # import US measurements
    fnm = rs.OpenFileName("Open US data file", ".txt|", None, None, None)
    f = open(fnm)
    data = f.read().split()
    f.close()
    
    
    # =========================================================================
    
    # Dimensions and Angles
    ## PTT_x - Plantar tissue thickness under each MTH and sesamoid
    PTT_1 = float(data[1])
    PTT_LS = float(data[3])
    PTT_MS = float(data[5])
    PTT_2 = float(data[7])
    print(PTT_2)
    PTT_3 = float(data[9])
    PTT_4 = float(data[11])
    PTT_5 = float(data[13])
    
    ## MTHw_x - Metatarsal head width (MTH1 defined later)
    MTHw_LS = float(data[15])
    MTHw_MS = float(data[17])
    MTHw_2 = float(data[19])
    MTHw_3 = float(data[21])
    MTHw_4 = float(data[23])
    MTHw_5 = float(data[25])
    
    ## MTHsr_x - Metatarsal head sagittal head radius (2-5 only)
    MTHsr_2 = float(data[27])
    MTHsr_3 = float(data[29])
    MTHsr_4 = float(data[31])
    MTHsr_5 = float(data[33])
    
    ## MTr_x - Metatarsal shaft radius, calculated as 80% of met head radius
    MTr_2 = MTHw_2 * 0.4
    MTr_3 = MTHw_3 * 0.4
    MTr_4 = MTHw_4 * 0.4
    MTr_5 = MTHw_5 * 0.4
    
    ## MTl_x - Metatarsal/Sesamoid length 
    MTl_1 = float(data[35])
    MTl_LS = float(data[37])
    MTl_MS = float(data[39])
    MTl_2 = float(data[41])
    MTl_3 = float(data[43])
    MTl_4 = float(data[45])
    MTl_5 = float(data[47])
    
    ## MTsr_x - Metatarsal sagittal plane angle
    MTsa_1 = float(data[49])
    MTsa_2 = float(data[51])
    MTsa_3 = float(data[53])
    MTsa_4 = float(data[55])
    MTsa_5 = float(data[57])
    
    ## MTca_x - Metatarsal coronal plane angle
    if side == "RIGHT":
        MTca_1 = float(data[59])
        MTca_4 = float(data[61]) * -1
        MTca_5 = float(data[63]) * -1
    else:
        MTca_1 = float(data[59]) * -1
        MTca_4 = float(data[61])
        MTca_5 = float(data[63])
    
    ## MLD_x - Mediolateral displacement of metatarsals(relative to 3MTH)
    MLD_LS = float(data[65])
    MLD_MS = float(data[67])
    MLD_1 = (MLD_LS + MLD_MS) * 0.5
    MLD_2 = float(data[69])
    MLD_4 = float(data[71]) * -1
    MLD_5 = float(data[73]) * -1
    
    ## MTH1 width and shaft radius
    MTHw_1 = (MLD_MS - MLD_LS) + (MTHw_LS * 0.5) + (MTHw_MS * 0.5) + 2
    MTr_1 = MTHw_1 * 0.4
    
    ## Sesamoids
    APmidpoint_LS = (MTl_LS * 0.5) - (MTHw_LS * 0.5)
    APmidpoint_MS = (MTl_MS * 0.5) - (MTHw_MS * 0.5)
    
    ## MAP_x - Metatarsal anterior posterior displacement (relative to 3MTH)
    MAP_LS = float(data[75]) - APmidpoint_LS
    MAP_MS = float(data[77]) - APmidpoint_MS
    MAP_1 = (MAP_LS + APmidpoint_LS + MAP_MS + APmidpoint_MS) * 0.5 
    MAP_2 = float(data[79]) * -1
    MAP_4 = float(data[81])
    MAP_5 = float(data[83])
    
    ## MVD_x Metatarsal vertical displacement
    MVD_LS = PTT_LS + (MTHw_LS * 0.5)
    MVD_MS = PTT_MS + (MTHw_MS * 0.5)
    
    
    # =========================================================================
    
    # make mets
    ## layers
    rs.CurrentLayer("FE Bones")
    rs.LayerVisible("FO Build", False)
    rs.LayerVisible("Position Scan", False)
    
    ## Make met 1
    MTH1 = rs.AddSphere([0, 0, 0], MTHw_1 / 2)
    MTsh_1 = rs.AddCylinder(rs.WorldZXPlane(), MTl_1 * -1, MTHw_1 / 2 - 0.5)
    MTH1 = rs.BooleanUnion([MTH1, MTsh_1])
    MTH1 = rs.RotateObject(MTH1, [0, 0, 0], MTsa_1 * -1, [1, 0, 0])
    MTH1 = rs.RotateObject(MTH1, [0, 0, 0], MTca_1, [0, 0, 1])
    
    ## Make MT parts
    MTH2 = build_met(MTHsr_2, MTHw_2, MTsa_2, MTca_1 / 2, 1)
    MTH3 = build_met(MTHsr_3, MTHw_3, MTsa_3, 0, 1)
    MTH4 = build_met(MTHsr_4, MTHw_4, MTsa_4, MTca_4, 1)
    MTH5 = build_met(MTHsr_5, MTHw_5, MTsa_5, MTca_5, 1)
    
    ## position MT parts
    MTH1 = rs.MoveObject(MTH1, [MLD_1, MAP_1 * -1, PTT_1 + (MTHw_1 * 0.5)])
    MTH2 = rs.MoveObject(MTH2, [MLD_2, MAP_2 * -1, PTT_2 + MTHsr_2])
    MTH2_IFE = rs.CopyObject(MTH2)
    MTH3 = rs.MoveObject(MTH3, [0, 0, PTT_3 + MTHsr_3])
    MTH4 = rs.MoveObject(MTH4, [MLD_4, MAP_4 * -1, PTT_4 + MTHsr_4])
    MTH5 = rs.MoveObject(MTH5, [MLD_5, MAP_5 * -1, PTT_5 + MTHsr_5])
    #MTH2_ = rs.CopyObject(MTH2)
    #MTH3_ = rs.CopyObject(MTH3)
    #MTH4_ = rs.CopyObject(MTH4)
    #MTH5_ = rs.CopyObject(MTH5)
    
    ## make sesamoids
    L_ses = make_ses(MTHw_LS / 2, MTl_LS, PTT_1 + (MTHw_1 * 0.5) - PTT_LS)
    M_ses = make_ses(MTHw_MS / 2, MTl_MS, PTT_1 + (MTHw_1 * 0.5) - PTT_MS)
    
    ## position sesamoids
    L_ses = rs.MoveObject(L_ses, [MLD_LS, MAP_LS * -1, PTT_LS + MTHw_LS / 2])
    M_ses = rs.MoveObject(M_ses, [MLD_MS, MAP_MS * -1, PTT_MS + MTHw_MS / 2])
    
    ## trim top of sesamoids
    cyl = rs.AddCylinder(rs.WorldXYPlane(), 30,100)
    cyl = rs.MoveObject(cyl, [0, 0, PTT_1 + (MTHw_1 / 2)])
    cyl2 = rs.CopyObject(cyl)
    L_ses = rs.BooleanDifference(L_ses, cyl)
    M_ses = rs.BooleanDifference(M_ses, cyl2)
    
    
    # =========================================================================
    
    # copy scan and insole
    scan = rs.ObjectsByLayer("Position scan")[0]
    scanFE = rs.ObjectLayer(rs.CopyObject(scan), "FE Tissue")
    insole = rs.ObjectsByLayer("FO Build")[0]
    insole_FE = rs.ObjectLayer(rs.CopyObject(insole), "FE Insole")
    scanFE = rs.ObjectsByLayer("FE Tissue")[0]
    insole_FE = rs.ObjectsByLayer("FE Insole")[0]
    
    
    # =========================================================================
    
    # position tissue against mets
    pt = rs.GetPoint("Select MT3 point")
    scanFE, insole_FE = rs.MoveObjects([scanFE, insole_FE], pt * -1)
    x = rs.MessageBox("Scan position correct?", 3)
    
    while x == 7:
        pt = rs.GetPoint()
        scanFE, insole_FE = rs.MoveObjects([scanFE, insole_FE], pt * -1)
        x = rs.MessageBox("Scan position correct?", 3)
    
    
    # =========================================================================
    
    # adjust met height
    ## get points on tissue
    LS_adj = pointFromMeshCurveInt([MLD_LS, MAP_LS, 0], scanFE)
    MS_adj = pointFromMeshCurveInt([MLD_MS, MAP_MS, 0], scanFE)
    MT1_adj = pointFromMeshCurveInt([MLD_1, MAP_1, 0], scanFE)
    MT2_adj = pointFromMeshCurveInt([MLD_2, MAP_2, 0], scanFE)
    MT3_adj = pointFromMeshCurveInt([0, 0, 0], scanFE)
    MT4_adj = pointFromMeshCurveInt([MLD_4, MAP_4, 0], scanFE)
    MT5_adj = pointFromMeshCurveInt([MLD_5, MAP_5, 0], scanFE)
    
    ## move mets/sesamoids
    MTH1 = rs.MoveObject(MTH1, [0, 0, MT1_adj[2]])
    MTH2 = rs.MoveObject(MTH2, [0, 0, MT2_adj[2]])
    MTH3 = rs.MoveObject(MTH3, [0, 0, MT3_adj[2]])
    MTH4 = rs.MoveObject(MTH4, [0, 0, MT4_adj[2]])
    MTH5 = rs.MoveObject(MTH5, [0, 0, MT5_adj[2]])
    L_ses = rs.MoveObject(L_ses, [0, 0, LS_adj[2]]) 
    M_ses = rs.MoveObject(M_ses, [0, 0, MS_adj[2]]) 
    
    ## Make Met 1
    MTH1 = rs.BooleanUnion([MTH1, L_ses, M_ses])
    #MTH1_ = rs.CopyObject(MTH1)
    
    
    # =========================================================================
    
    # Make soft tissue part
    ## dorsal cut
    MT1_prox_h = (math.sin(math.radians(MTsa_1)) * MTl_1) + PTT_1 + MTHw_1 * 0.5 + MT1_adj[2]
    MT1_prox_ml = (math.sin(math.radians(MTca_1)) * MTl_1) + MLD_1
    MT1_prox_ap = ((math.cos(math.radians(MTsa_1)) * MTl_1) + MAP_1) * -1
    MT2_prox_h = math.sin(math.radians(MTsa_2)) * MTl_2 + PTT_2 + MTHsr_2 + MT2_adj[2]
    #MT2_prox_ap
    MT3_prox_h = math.sin(math.radians(MTsa_3)) * MTl_3 + PTT_3 + MTHsr_3 + MT3_adj[2]
    #MT3_prox_ap
    MT4_prox_h = math.sin(math.radians(MTsa_4)) * MTl_4 + PTT_4 + MTHsr_4 + MT4_adj[2]
    MT4_prox_ml = math.sin(math.radians(MTca_4)) * MTl_4 + MLD_4
    #MT4_prox_ap
    MT5_prox_h = math.sin(math.radians(MTsa_5)) * MTl_5 + PTT_5 + MTHsr_5 + MT5_adj[2]
    MT5_prox_ml = math.sin(math.radians(MTca_5)) * MTl_5 + MLD_5
    #MT5_prox_ap
    
    curve_MT1 = rs.AddPolyline([[MLD_1, 100, PTT_1 + MTHw_1 * 0.5],
                                [MLD_1, MAP_1 * -1, PTT_1 + MTHw_1 * 0.5],
                                [MT1_prox_ml, MT1_prox_ap, MT1_prox_h], 
                                [MT1_prox_ml, -300, MT1_prox_h]])
    curve_MT2 = rs.AddPolyline([[MLD_2, 100, PTT_2 + MTHsr_2],
                                [MLD_2, MAP_2 * -1, PTT_2 + MTHsr_2],
                                [MLD_2, MTl_2 * -1 - MAP_2, MT2_prox_h], 
                                [MLD_2, -300, MT2_prox_h]])
    curve_MT3 = rs.AddPolyline([[0, 100, PTT_3 + MTHsr_3],
                                [0, 0, PTT_3 + MTHsr_3],
                                [0, MTl_3 * -1, MT3_prox_h],
                                [0, -300, MT3_prox_h]])
    curve_MT4 = rs.AddPolyline([[MLD_4, 100, PTT_4 + MTHsr_4],
                                [MLD_4, MAP_4 * -1, PTT_4 + MTHsr_4],
                                [MT4_prox_ml, MTl_4 * -1 - MAP_4, MT4_prox_h], 
                                [MT4_prox_ml, -300, MT4_prox_h]])
    curve_MT5 = rs.AddPolyline([[MLD_5, 100, PTT_5 + MTHsr_5],
                                [MLD_5, MAP_5 * -1, PTT_5 + MTHsr_5],
                                [MT5_prox_ml, MTl_5 * -1 - MAP_5, MT5_prox_h],
                                [MT5_prox_ml, -300, MT5_prox_h]])
    
    if side == "RIGHT":
        curve_lat = rs.CopyObject(curve_MT5, [50, 0, 0])
        curve_med = rs.CopyObject(curve_MT1, [-50, 0, 0])
        MLD_5_ofs = MLD_5 + 50
        MLD_1_ofs = MLD_1 - 50
        MLD_5_ofs_prox = MT5_prox_ml + 50
        MLD_1_ofs_prox = MT1_prox_ml - 50
    else:
        curve_lat = rs.CopyObject(curve_MT5, [-50, 0, 0])
        curve_med = rs.CopyObject(curve_MT1, [50, 0, 0])
        MLD_5_ofs = MLD_5 - 50
        MLD_1_ofs = MLD_1 + 50
        MLD_5_ofs_prox = MT5_prox_ml - 50
        MLD_1_ofs_prox = MT1_prox_ml + 50
    
#    dorsal_surface = rs.AddLoftSrf([curve_med, curve_MT1, curve_MT2, curve_MT3, 
#                                    curve_MT4, curve_MT5, curve_lat], 
#                                    loft_type = 2)
#    
#    ## Distal cut
#    distal_curve = rs.AddPolyline([[MLD_1_ofs, MAP_1 * -1, PTT_1 + MTHw_1 * 0.5], 
#                                      [MLD_1, MAP_1 * -1, PTT_1 + MTHw_1 * 0.5], 
#                                      [MLD_2, MAP_2 * -1, PTT_2 + MTHsr_2], 
#                                      [0, 0, PTT_3 + MTHsr_3], 
#                                      [MLD_4, MAP_4 * -1, PTT_4 + MTHsr_4], 
#                                      [MLD_5, MAP_5 * -1, PTT_5 + MTHsr_5], 
#                                      [MLD_5_ofs, MAP_5 * -1, PTT_5 + MTHsr_5]])
#    distal_curve = rs.MoveObject(distal_curve, [0, MAP_2 + MTHsr_2 + 10, -50])
#    distal_surface = rs.ExtrudeCurveStraight(distal_curve, 
#                                             [0, 0, -50], [0, 0, 100])
#    rs.DeleteObject(distal_curve)
    
#    ## Proximal cut
#    proximal_curve = rs.AddPolyline([[MLD_1_ofs_prox, MTl_1 * -1 - MAP_1, MT1_prox_h], 
#                                        [MT1_prox_ml, MTl_1 * -1 - MAP_1, MT1_prox_h],
#                                        [MLD_2, MTl_2 * -1 - MAP_2, MT2_prox_h], 
#                                        [0, MTl_3 * -1, MT3_prox_h], 
#                                        [MT4_prox_ml, MTl_4 * -1 - MAP_4, MT4_prox_h], 
#                                        [MT5_prox_ml, MTl_5 * -1 - MAP_5, MT5_prox_h], 
#                                        [MLD_5_ofs_prox, MTl_5 * -1 - MAP_5, MT5_prox_h]])
#    proximal_curve = rs.MoveObject(proximal_curve, [0, 5, -100])
#    proximal_surface = rs.ExtrudeCurveStraight(proximal_curve, 
#                                               [0, 0, -100], [0, 0, 100])
#    rs.DeleteObjects([proximal_curve, distal_curve, curve_lat, curve_med,
#                      curve_MT1, curve_MT2, curve_MT3, curve_MT4, curve_MT5])
    
    ## trim insole
#    insole_FE = meshBoolSplit(insole_FE, distal_surface, "prox")
#    insole_FE = meshBoolSplit(insole_FE, proximal_surface, "dist")
    
    ## boolean difference of tissue block and mets
#    scanFE = meshBoolSplit(scanFE, distal_surface, "prox")
#    scanFE = meshBoolSplit(scanFE, proximal_surface, "dist")
#    rs.HideObjects([distal_surface, proximal_surface])
#    scanFE = meshBoolDiff(scanFE, MTH1[0])
#    scanFE = meshBoolDiff(scanFE[0], MTH2)
#    scanFE = meshBoolDiff(scanFE[0], MTH3)
#    scanFE = meshBoolDiff(scanFE[0], MTH4)
#    scanFE = meshBoolDiff(scanFE[0], MTH5)
#    soft_tissue_FE = meshBoolSplit(scanFE[0], dorsal_surface[0], "plant")
#    soft_tissue_FE2 = rs.CopyObject(soft_tissue_FE)
#    rs.HideObject(dorsal_surface)
    
    
    # =========================================================================
    
    # Parts for inverse FE tissue
    ## bone
    rs.CurrentLayer("FE MT2")
    MTH2_i = build_met(MTHsr_2, MTHw_2, MTsa_2, 0, 1)
    MTH2_i = rs.MoveObject(MTH2_i, [0, 0, MTHsr_2 + PTT_2])
    
    ## tissue
    rs.CurrentLayer("FE MT2 Tissue")
    points = [[-5, 15, 0], [-5, -15, 0], [5, -15, 0], [5, 15, 0],
              [-5, 15, MTHsr_2 + PTT_2], [-5, -15, MTHsr_2 + PTT_2], 
              [5, -15, MTHsr_2 + PTT_2], [5, 15, MTHsr_2 + PTT_2]]
    MTH2_tissue = rs.AddBox(points)
    
    ## boolean
    MTH2_tis = rs.BooleanDifference(MTH2_tissue, MTH2_i, delete_input = False)
    rs.DeleteObject(MTH2_tissue)
#    
#    
#    # =========================================================================
#    
#    # adjust position of soft tissue so just above insole
#    mmi = False
#    while (mmi == False):
#        results = rs.MeshMeshIntersection(soft_tissue_FE, insole_FE)
#        if results:
#            mmi = False
#            soft_tissue_FE = rs.MoveObject(soft_tissue_FE, [0, 0, 0.1])
#            MTH1, MTH2, MTH3, MTH4, MTH5 = rs.MoveObjects([MTH1, MTH2, MTH3, 
#                                                           MTH4, MTH5],
#                                                          [0, 0, 0.1])
#        else:
#            mmi = True
#    
#    
#    # =========================================================================
#    
#    # export parts
#    ## make folder
#    directory = rs.BrowseForFolder(message = "Select folder to save FE parts")
#    if not os.path.exists(directory):
#        os.makedirs(directory)
#    
#    ## export mets
#    export_stl(directory, MTH1_, "Met1_FE")
#    export_stl(directory, MTH2_, "Met2_FE")
#    export_stl(directory, MTH2_i, "Met2_Inv_FE")
#    export_stl(directory, MTH3_, "Met3_FE")
#    export_stl(directory, MTH4_, "Met4_FE")
#    export_stl(directory, MTH5_, "Met5_FE")
#    
#    ## export soft tissue parts
#    export_stl(directory, soft_tissue_FE, "SoftTissue_FE")
#    export_stl(directory, MTH2_tis, "SoftTissue_MT2_FE")
#    
#    ## export insole
#    export_stl(directory, insole_FE, "Insole_FE")

FE_parts()
