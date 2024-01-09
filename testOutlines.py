import rhinoscriptsyntax as rs

fnm = rs.OpenFileName("Open outline data file", ".txt|", None, None, None)
f = open(fnm)

data = []
for line in f:
    row = line.split()
    row[1] = float(row[1])
    row[2] = float(row[2])
    data.append(row)
f.close()
size = 11

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

## bottom outline curve
bottom_outline = rs.AddInterpCurve([heel_center, heel_center_medial, 
                             heel_medial, arch_medial, mtpj1_prox, mtpj1,
                             mtpj1_dist1, mtpj1_dist2, ff_med, toe_med, toe,
                             toe_lat, ff_lat, mtpj5_dist2, mtpj5_dist1, 
                             mtpj5, mtpj5_prox, arch_lateral, heel_lateral, 
                             heel_center_lateral, heel_center], degree = 3, knotstyle = 2)
#bottom_outline = rs.RebuildCurve(bottom_outline, point_count = 50)
rs.ObjectColor(bottom_outline, [255,0,0])

rs.AddPoints([heel_center, heel_center_medial, 
                             heel_medial, arch_medial, mtpj1_prox, mtpj1,
                             mtpj1_dist1, mtpj1_dist2, ff_med, toe_med, toe,
                             toe_lat, ff_lat, mtpj5_dist2, mtpj5_dist1, 
                             mtpj5, mtpj5_prox, arch_lateral, heel_lateral, 
                             heel_center_lateral, heel_center])
