import matplotlib.pyplot as plt
import pandas as pd

city_coords = {
    "Marshalltown": [
        42.03585,
        -92.99877
    ],
    "Guthrie Center": [
        41.67721,
        -94.5033
    ],
    "Red Oak": [
        41.00972,
        -95.22555
    ],
    "Urbandale": [
        41.62666,
        -93.71217
    ],
    "Hiawatha": [
        42.03583,
        -91.68212
    ],
    "Osceola": [
        43.37857,
        -95.62369
    ],
    "Emmetsburg": [
        43.11274,
        -94.68304
    ],
    "Carroll": [
        42.03624,
        -94.86056
    ],
    "Rock Island, IL": [
        41.50948,
        -90.57875
    ],
    "Lincoln, NE": [
        40.8,
        -96.66696
    ],
    "Independence": [
        41.8261,
        -93.15159
    ],
    "Knoxville": [
        41.29902,
        -93.11163
    ],
    "Rochester, MN": [
        44.02163,
        -92.4699
    ],
    "Sheldon": [
        43.18109,
        -95.85613
    ],
    "Muscatine": [
        41.42447,
        -91.04321
    ],
    "De Witt": [
        41.82336,
        -90.53819
    ],
    "Waverly": [
        42.72581,
        -92.47546
    ],
    "Mason City": [
        43.15357,
        -93.20104
    ],
    "Waukee": [
        41.61166,
        -93.88523
    ],
    "Clarion": [
        42.74192,
        -93.75883
    ],
    "Pleasant Hill": [
        41.58388,
        -93.51994
    ],
    "Ida Grove": [
        42.3326,
        -95.44489
    ],
    "Guttenberg": [
        42.78582,
        -91.09957
    ],
    "Manchester": [
        42.48415,
        -91.45543
    ],
    "La Crosse, WI": [
        43.80136,
        -91.23958
    ],
    "Vermillion, SD": [
        42.77944,
        -96.92921
    ],
    "Corning": [
        40.99732,
        -94.75572
    ],
    "Oskaloosa": [
        41.3352,
        -92.64091
    ],
    "West Burlington": [
        40.82504,
        -91.15654
    ],
    "Primghar": [
        43.08692,
        -95.62723
    ],
    "Sioux City": [
        42.49999,
        -96.40031
    ],
    "Hamburg": [
        40.60445,
        -95.65777
    ],
    "Pella": [
        41.33445,
        -93.09944
    ],
    "Boone": [
        42.0597,
        -93.88023
    ],
    "Maquoketa": [
        42.11752,
        -90.78069
    ],
    "Humboldt": [
        42.7208,
        -94.21524
    ],
    "Mount Ayr": [
        40.71471,
        -94.23523
    ],
    "Omaha, NE": [
        41.25626,
        -95.94043
    ],
    "Manning": [
        41.90915,
        -95.06499
    ],
    "Spencer": [
        43.08258,
        -95.15092
    ],
    "New Hampton": [
        43.05914,
        -92.31768
    ],
    "Sibley": [
        43.39914,
        -95.75196
    ],
    "Creston": [
        41.02138,
        -94.36329
    ],
    "Ankeny": [
        41.72971,
        -93.60577
    ],
    "Moline, IL": [
        41.5067,
        -90.51513
    ],
    "Keokuk": [
        40.39727,
        -91.38487
    ],
    "Audubon": [
        41.68459,
        -94.90582
    ],
    "Grundy Center": [
        42.36165,
        -92.76853
    ],
    "Fairfield": [
        41.03176,
        -91.94887
    ],
    "Fort Madison": [
        40.62976,
        -91.31515
    ],
    "Webster City": [
        42.49747,
        -94.16802
    ],
    "Maryville, MO": [
        40.36077,
        -94.88343
    ],
    "Davenport": [
        41.52364,
        -90.57764
    ],
    "Onawa": [
        42.02665,
        -96.09724
    ],
    "Newton": [
        41.69971,
        -93.04798
    ],
    "Coralville": [
        41.6764,
        -91.58045
    ],
    "Worthington, MN": [
        43.61996,
        -95.5964
    ],
    "Hampton": [
        42.72538,
        -93.22474
    ],
    "Cresco": [
        43.38136,
        -92.11405
    ],
    "Dyersville": [
        42.48444,
        -91.12291
    ],
    "Shenandoah": [
        40.76555,
        -95.37221
    ],
    "Stuart": [
        41.50332,
        -94.31857
    ],
    "Chariton": [
        41.01389,
        -93.3066
    ],
    "Waukon": [
        43.26942,
        -91.4757
    ],
    "Sumner": [
        42.84748,
        -92.09156
    ],
    "Cedar Falls": [
        42.52776,
        -92.44547
    ],
    "Anamosa": [
        42.10834,
        -91.28516
    ],
    "Garner": [
        41.25861,
        -95.76056
    ],
    "Silvis, IL": [
        41.51226,
        -90.41513
    ],
    "Leon": [
        40.73972,
        -93.74772
    ],
    "Grinnell": [
        41.74305,
        -92.72241
    ],
    "Columbia, MO": [
        49.16638,
        -123.94003
    ],
    "Sioux Center": [
        43.07971,
        -96.17558
    ],
    "Council Bluffs": [
        41.29008,
        -95.99912
    ],
    "Osage": [
        43.28414,
        -92.81103
    ],
    "Cherokee": [
        42.73562,
        -95.62381
    ],
    "Decorah": [
        43.27525,
        -91.73932
    ],
    "Cedar Rapids": [
        42.00833,
        -91.64407
    ],
    "Britt": [
        43.09774,
        -93.80189
    ],
    "Jefferson City, MO": [
        38.5767,
        -92.17352
    ],
    "Dakota Dunes": [
        42.48749,
        -96.48642
    ],
    "Elkader": [
        42.85387,
        -91.40542
    ],
    "Omaha": [
        41.25626,
        -95.94043
    ],
    "Rock Valley": [
        41.44865,
        -90.50652
    ],
    "Nevada": [
        42.02277,
        -93.45243
    ],
    "Centerville": [
        40.73418,
        -92.87409
    ],
    "Mount Pleasant": [
        40.9473,
        -91.51382
    ],
    "Washington": [
        41.33559,
        -91.71787
    ],
    "Bettendorf": [
        41.52448,
        -90.51569
    ],
    "Johnston": [
        41.67304,
        -93.69772
    ],
    "West Union": [
        41.02773,
        -94.24238
    ],
    "Dakota Dunes, SD": [
        42.48749,
        -96.48642
    ],
    "Storm Lake": [
        42.73549,
        -95.15115
    ],
    "Lake City": [
        42.26748,
        -94.73387
    ],
    "Atlantic": [
        41.40721,
        -95.04666
    ],
    "Denison": [
        41.98638,
        -95.38055
    ],
    "Bloomfield": [
        40.75169,
        -92.41491
    ],
    "Kirksville, MO": [
        40.0933,
        -92.5412
    ],
    "West Des Moines": [
        41.60054,
        -93.60911
    ],
    "Vinton": [
        42.16861,
        -92.02351
    ],
    "Iowa City": [
        41.66113,
        -91.53017
    ],
    "Orange City": [
        42.98909,
        -96.06135
    ],
    "Clear Lake": [
        43.13802,
        -93.37937
    ],
    "Corydon": [
        40.75695,
        -93.31882
    ],
    "Albia": [
        41.02667,
        -92.80575
    ],
    "Ames": [
        42.03471,
        -93.61994
    ],
    "Spirit Lake": [
        43.37798,
        -95.15083
    ],
    "Sac City": [
        42.4222,
        -94.98971
    ],
    "Iowa Falls": [
        42.52776,
        -92.44547
    ],
    "Pocahontas": [
        42.73414,
        -94.67875
    ],
    "Hawarden": [
        42.99582,
        -96.48531
    ],
    "Clive": [
        41.60304,
        -93.72411
    ],
    "Ottumwa": [
        41.03058,
        -92.40945
    ],
    "Perry": [
        41.82841,
        -94.15933
    ],
    "Missouri Valley": [
        41.55638,
        -95.88779
    ],
    "Bellevue, NE": [
        41.13667,
        -95.89084
    ],
    "Le Mars": [
        42.77802,
        -96.19369
    ],
    "Belmond": [
        42.84608,
        -93.6141
    ],
    "Jefferson": [
        41.03176,
        -91.94888
    ],
    "Sioux Falls, SD": [
        43.54997,
        -96.70033
    ],
    "Dubuque": [
        42.50056,
        -90.66457
    ],
    "Winterset": [
        41.33082,
        -94.01384
    ],
    "Waterloo": [
        42.49276,
        -92.34296
    ],
    "Clinton": [
        41.84447,
        -90.18874
    ],
    "Estherville": [
        43.40718,
        -94.74637
    ],
    "Algona": [
        43.07774,
        -94.27191
    ],
    "Tama": [
        41.96666,
        -92.57686
    ],
    "Clarinda": [
        40.73981,
        -95.038
    ],
    "Keosauqua": [
        40.73031,
        -91.96239
    ],
    "Fort Dodge": [
        42.42794,
        -94.18176
    ],
    "Marengo": [
        41.79806,
        -92.07074
    ],
    "Des Moines": [
        41.60054,
        -93.60911
    ],
    "Charles City": [
        43.07247,
        -92.61074
    ],
    "Sigourney": [
        41.33334,
        -92.20463
    ],
    "Harlan": [
        41.65304,
        -95.32555
    ],
    "Greenfield": [
        41.30527,
        -94.46135
    ]
}


to_cities = set(dataset['Community'])
from_cities = set(dataset['Point of Origin'])

from_city_unique = from_cities - to_cities
cities = to_cities.update(from_cities)

row_header = ['city', 'latitude_from', 'longitude_from', 'to', 'latitude_to', 'longitude_to']

fig, ax = plt.subplots(figsize=(12, 8))


def plot_line(row):
    from_coord = city_coords[row['Point of Origin']]
    to_coord = city_coords[row['Community']]

    ax.plot([from_coord[1], to_coord[1]], [from_coord[0], to_coord[0]], marker='o')


dataset.apply(plot_line, axis=1)

# Set axis labels and titles
plt.title('Lines Between Coordinates')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

plt.show()

