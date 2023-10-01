# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com

# from document Astron.Astrophys 282
# Numerical expressions for precession formulae and mean elements for the moon and the planets

from AstroTypes import pn

# Keplerian elements and their rates, with respect to the mean ecliptic
# and equinox of J2000  (t per millenium)
arcs=3600.0
PlanetElm =  {
    pn.Mercury :
            ((0.3870983098,),        #SemiMajorAxis  [au,au/cy]
             (0.2056317526,       0.0002040653,  -2834e-10),        #Eccentricity   [1,1/cy]
             (7.00498625*arcs,      -214.25629,   0.28977),       #Inclination    [deg,deg/cy]
             (252.25090552*arcs,5381016286.88982,-1.92789), #MeanLongitude  [deg,deg/cy]
             (77.45611904*arcs,     5719.11590,  -4.83016),       #LongitudePerihelion  (periapsis) [deg,deg/cy]
             (48.3308930*arcs,     -4515.21727,  -31.79892),      #LongitudeAscendingNode  [deg,deg/cy]
             (6023600,)),                         #Mass
    pn.Venus : 
            ((0.7233298200,),  # a
             (0.0067719164,      -0.0004776521,      98127e-10),  # e
             (3.39466189*arcs,       -30.84437, -11.67836),  # I (dinc)
             (181.97980085*arcs,2106641364.33548,   0.59381),  # L (dlm)
             (131.56370300*arcs,     175.48640, -498.48184),  # w (pi)
             (76.67992019*arcs,   -10008.48154,  -51.32614),  # W (omega)
             (408523.71,)),   # Mass
    pn.Earth: # plus moon
            ((1.0000010178,),  # a
             (0.0167086342,      -0.0004203654, -0.0000126734),  # e
             (0,  469.97289,          -3.35053),  # I (dinc)
             (100.46645683*arcs,1295977422.83429,  -2.04411),  # L (dlm)
             (102.93734808*arcs,   11612.35290,   53.27577),  # w (pi)
             (174.87317577*arcs,   -8679.27034,   15.34191),  # W (omega)
             (328900.56,)),   # Mass
    pn.Mars:  
            ((1.5236793419,              3e-10,    0.0),  # a
             (0.0934006477,       0.0009048438,     -80641e-10),  # e
             (1.84972648*arcs,      -293.31722,  -8.11830),  # I (dinc)
             (355.43299958*arcs,689050774.93988,   0.94264),  # L (dlm)
             (336.06023395*arcs,   15980.45908,  -62.32800),  # w (pi)
             (49.55809321*arcs,   -10620.90088, -230.57416),  # W (omega)
             (3098708,)),   # Mass
    pn.Jupiter:
            ((5.2026032092,          19132e-10,  -39e-10),  # a
             (0.0484979255,       0.0016322542, -0.0000471366),  # e
             (1.30326698*arcs,       -71.55890,  11.95297),  # I (dinc)
             (34.35151874*arcs,109256603.77991, -30.60378),  # L (dlm)
             (14.33120687*arcs,     7758.75163,  259.95938),  # w (pi)
             (100.46440702*arcs,    6362.03561,  326.52178),  # W (omega)
             (1047.3486,)),   # Mass
    pn.Saturn: 
            ((9.5549091915,     -0.0000213896,  444e-10),  # a
             (0.0555481426,     -0.0034664062, -0.0000643639),  # e
             (2.48887878*arcs,       91.85195, -17.66225),  # I (dinc)
             (50.07744430*arcs,43996098.55732,  75.61614),  # L (dlm)
             (93.05723748*arcs,   20395.49439,  190.25952),  # w (pi)
             (113.66550252*arcs,  -9240.19942,  -66.23743),  # W (omega)
             (3497.90,)),   # Mass
    pn.Uranus: 
            ((19.2184460618,        -3716e-10,  979e-10),  # a
             (0.0463812221,     -0.0002729293,  0.0000078913),  # e
             (0.77319689*arcs,      -60.72723,   1.25759),  # I (dinc)
             (314.05500511*arcs,15424811.93933,  -1.75083),  # L (dlm)
             (173.00529106*arcs,   3215.56238,  -34.09288),  # w (pi)
             (74.00595701*arcs,    2669.15033,  145.93964),  # W (omega)
             (22902.94,)),   # Mass
    pn.Neptune:
            ((30.1103868694,       -16635e-10,  686e-10),  # a
             (0.0094557470,      0.0000603263),  # e
             (1.76995259*arcs,        8.12333,   0.08135),  # I (dinc)
             (304.34866548*arcs,7865503.20744,   0.21103),  # L (dlm)
             (48.12027554*arcs,    1050.71912,   27.39717),  # w (pi)
             (131.78405702*arcs,   -221.94322,  -0.78728),  # W (omega)
             (19412.24,)),   # Mass
    pn.Pluto:  #JPL
            ((39.48211675,        -0.00031596,   0.0),        #SemiMajorAxis
             (0.24882730,          0.00005170,   0.0),        #Eccentricity
             (17.14001206*arcs,    0.00004818*arcs,0.0),       #Inclination
             (238.92903833*arcs, 145.20780515*arcs,0.0), #MeanLongitude
             (224.06891629*arcs,  -0.04062942*arcs,0.0),       #LongitudePerihelion
             (110.30393684*arcs,  -0.01183482*arcs,0.0),      #LongitudeAscendingNode
             ()),                         #Mass
    pn.Moon:       # t per century, J2000 frame, 1992 const
            ((383397.7725,              0.004,0.0),        #SemiMajorAxis [km]
             (0.055545526,       -0.000000016,0.0),        #Eccentricity
             (5.15668983*arcs,       -0.00008,0.02966,-0.000042,-0.00000013),       #Inclination
             (218.31664563*arcs,1732559343.4847,-6.391,0.006588,-0.00003169), #MeanLongitude  
             (83.35324312*arcs, 14643420.2669,-38.2702,-0.045047,0.00021301),  #LongitudePerigee
             (125.04455501*arcs,-6967919.3631,6.3602,0.007625,-0.00003586 ),   #LongitudeAscendingNode  
             ())           #Mass
                }                        

trigonometric_terms =  {
    pn.Mercury :
            ((69613, 75645, 88306, 59899, 15746, 71087, 142173,  3086),        # kp (pmu)
             (    4,    -13,    11,    -9,    -9,    -3,    -1,     4),        # ca ()
             (   -29,     -1,     9,     6,    -6,     5,     4,     0),        # sa ()
             ( 3086,  15746, 69613, 59899, 75645, 88306,  12661,  2658),        # kq (qmu)
             (     21,   -95, -157,   41,   -5,   42,   23,   30),        # cl ()
             (   -342,   136,  -23,   62,   66,  -52,  -33,   17)),       # sl ()
    pn.Venus : 
            ((21863, 32794, 26934, 10931, 26250, 43725,  53867, 28939),        # kp (pmu)
             ( -156,     59,   -42,     6,    19,   -20,   -10,   -12),        # ca ()
             (   -48,   -125,   -26,   -37,    18,   -13,   -20,    -2),        # sa ()
             (21863,  32794, 10931,    73,  4387, 26934,   1473,  2157),        # kq (qmu)
             (   -160,  -313, -235,   60,  -74,  -76,  -27,   34),        # cl ()
             (    524,  -149,  -35,  117,  151,  122,  -71,  -62)),       # sl ()
    pn.Earth: 
            ((16002, 21863, 32004, 10931, 14529, 16368,  15318, 32794),        # kp (pmu)
             (   64,   -152,    62,    -8,    32,   -41,    19,   -11),        # ca ()
             (  -150,    -46,    68,    54,    14,    24,   -28,    22),        # sa ()
             (   10,  16002, 21863, 10931,  1473, 32004,   4387,    73),        # kq (qmu)
             (   -325,  -322,  -79,  232,  -52,   97,   55,  -41),        # cl ()
             (   -105,  -137,  258,   35, -116,  -88, -112,  -80)),       # sl ()
    pn.Mars:  
            ((6345,   7818, 15636,  7077,  8184, 14163,   1107,  4872),        # kp (pmu)
             (  124,    621,  -145,   208,    54,   -57,    30,    15),        # ca ()
             (  -621,    532,  -694,   -20,   192,   -94,    71,   -73),        # sa ()
             (   10,   6345,  7818,  1107, 15636,  7077,   8184,   532),        # kq (qmu)
             (   2268,  -979,  802,  602, -668,  -33,  345,  201),        # cl ()
             (    854,  -205, -936, -240,  140, -341,  -97, -232)),       # sl ()
    pn.Jupiter:
            ((1760,   1454,  1167,   880,   287,  2640,     19,  2047),        # kp (pmu)
             (-23437,  -2634,  6601,  6259, -1507, -1821,  2620, -2115),        # ca ()
             (-14614, -19828, -5869,  1881, -4372, -2255,   782,   930),        # sa ()
             (   19,   1760,  1454,   287,  1167,   880,    574,  2640),        # kq (qmu)
             (   7610, -4997,-7689,-5841,-2617, 1115, -748, -607),        # cl ()
             ( -56980,  8016, 1012, 1448,-3024,-3710,  318,  503)),       # sl ()
    pn.Saturn: 
            (( 574,      0,   880,   287,    19,  1760,   1167,   306),        # kp (pmu)
             (62911,-119919, 79336, 17814,-24241, 12068,  8306, -4893),        # ca ()
             (139737,      0, 24667, 51123, -5102,  7429, -4095, -1976),        # sa ()
             (   19,    574,   287,   306,  1760,    12,     31,    38),        # kq (qmu)
             ( -18549, 30125,20012, -730,  824,   23, 1289, -352),        # cl ()
             (138606,-13478,-4964, 1441,-1319,-1482,  427, 1236)),       # sl ()
    pn.Uranus: 
            (( 204,      0,   177,  1265,     4,   385,    200,   208),        # kp (pmu)
             (389061,-262125,-44088,  8387,-22976, -2093,  -615, -9720),        # ca ()
             (-138081,      0, 37205,-49039,-41901,-33872,-27037,-12474),        # sa ()
             (    4,    204,   177,     8,    31,   200,   1265,   102),        # kq (qmu)
             (-135245,-14594, 4197,-4030,-5630,-2898, 2540, -306),        # cl ()
             ( 71234,-41116, 5334,-4935,-1848,   66,  434,-1748)),       # sl ()
    pn.Neptune:
            ((   0,    102,   106,     4,    98,  1367,    487,   204),        # kp (pmu)
             (-412235,-157046,-31430, 37817, -9740,   -13, -7449,  9644),        # ca ()
             (0,  28492,133236, 69654, 52322,-49577,-26430, -3593),        # sa ()
             (    4,    102,   106,     8,    98,  1367,    487,   204),        # kq (qmu)
             (  89948,  2103, 8963, 2695, 3682, 1648,  866, -154),        # cl ()
             (-47645, 11647, 2166, 3194,  679,    0, -244, -419)),       # sl ()
    pn.Pluto: 
            ((),        # kp (pmu)
             (),        # ca ()
             (),        # sa ()
             (),        # kq (qmu)
             (),        # cl ()
             ()),       # sl ()
    pn.Moon:       # preliminary
            ((),        # kp (pmu)
             (),        # ca ()
             (),        # sa ()
             (),        # kq (qmu)
             (),        # cl ()
             ())       # sl ()
                }                        

trigonometric_terms_extra =  {
    pn.Mercury :
            ((),        # kp (pmu)
             (),        # ca ()
             (),        # sa ()
             (),        # kq (qmu)
             (),        # cl ()
             ()),       # sl ()
    pn.Venus : 
            ((),        # kp (pmu)
             (),        # ca ()
             (),        # sa ()
             (),        # kq (qmu)
             (),        # cl ()
             ()),       # sl ()
    pn.Earth: 
            ((),        # kp (pmu)
             (),        # ca ()
             (),        # sa ()
             (),        # kq (qmu)
             (),        # cl ()
             ()),       # sl ()
    pn.Mars:  
            ((),        # kp (pmu)
             (),        # ca ()
             (),        # sa ()
             (10,),        # kq (qmu)
             (-55,),        # cl ()
             ( 536,)),       # sl ()
    pn.Jupiter:
            ((1454,),        # kp (pmu)
             (-1489,),        # ca ()
             (913,),        # sa ()
             (19,1454),        # kq (qmu)
             (6074,  354),        # cl ()
             (3767,  577)),       # sl ()
    pn.Saturn: 
            ((574,),        # kp (pmu)
             (8902,),        # ca ()
             (-9566,),        # sa ()
             (19, 574),        # kq (qmu)
             (-14767,-2062),        # cl ()
             (-9167,-1918)),       # sl ()
    pn.Uranus: 
            ((204,),        # kp (pmu)
             (6633,),        # ca ()
             (18797,),        # sa ()
             (4, 204),        # kq (qmu)
             (2939, 1986),        # cl ()
             ( 3780, -701)),       # sl ()
    pn.Neptune:
            ((),        # kp (pmu)
             (),        # ca ()
             (),        # sa ()
             (4, 102),        # kq (qmu)
             (-1963, -283),        # cl ()
             (-2531,   48)),       # sl ()
    pn.Pluto: 
            ((),        # kp (pmu)
             (),        # ca ()
             (),        # sa ()
             (),        # kq (qmu)
             (),        # cl ()
             ()),       # sl ()
    pn.Moon:       # preliminary
            ((),        # kp (pmu)
             (),        # ca ()
             (),        # sa ()
             (),        # kq (qmu)
             (),        # cl ()
             ())       # sl ()
                }                        

#ref to mean ecliptic and equinox of date with IAU 1992 planet masses and P1=5028.82 arcs precession constant
# t per century
MoonElm  =  ((383397.7725,              0.004,0.0),        #SemiMajorAxis [km]
             (0.055545526,       -0.000000016,0.0),        #Eccentricity
             (5.15668983*arcs,       -0.00008),            #Inclination
             (218.31664563*arcs,1732564372.3047,-5.279,0.006665,-0.00005522), #MeanLongitude  
             (83.35324312*arcs, 14648449.0869,-37.1582,-0.04497,0.00018948),  #LongitudePerigee
             (125.04455501*arcs,-6962890.5431,7.4722,0.007702,-0.00005939 ))  #LongitudeAscendingNode
   

if __name__ == '__main__':
    from dbOscElm import dbOscElmObj
    dbOscElmObj.write_oscelm(pn.Moon, MoonElm, pnOrg=pn.aa282_moonmean)
    for p in range(len(PlanetElm)):
        dbOscElmObj.write_oscelm(p, PlanetElm[p], pnOrg=pn.aa282_planmean)
    for p in range(len(trigonometric_terms)):
        dbOscElmObj.write_oscelm(p, trigonometric_terms[p], pnOrg=pn.aa282_trigterms)
    for p in range(len(trigonometric_terms_extra)):
        dbOscElmObj.write_oscelm(p, trigonometric_terms_extra[p], pnOrg=pn.aa282_etrigterms)