from pymongo import MongoClient
import pymongo
import matplotlib.pyplot as plt
import plotly as px
import pylab
import datetime
import numpy as np
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.tile_providers import  get_provider, Vendors
from bokeh.models import HoverTool, ColumnDataSource, ColorPicker, Legend, Div
from bokeh.models.widgets import Tabs, Panel
from bokeh.layouts import row, column
from bokeh.transform import factor_cmap

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri, tls=True, tlsAllowInvalidCertificates=True)

db_name = "doctolib"
db = client[db_name]
print(db.list_collection_names())

coll_name = "dump_Jan2022"
coll = db[coll_name]
print(coll.index_information())

# On récupère les centres de vaccination à moins de 50km de Rennes

c = coll.find(
    {"location": {'$near' : {'$geometry' : {"type": "Point", "coordinates": [-1.6777926,48.117266]},'$maxDistance': 50000}},
     "visit_motives.slots":{"$lte": datetime.datetime.strptime("2022/01/29", "%Y/%m/%d"), "$gte": datetime.datetime.strptime("2022/01/26", "%Y/%m/%d")}})

# Représentation des centres de vaccination sur une carte

## Création d'un data frame avec le nom et les coordnnées du centre de vaccination

df_carte = {}
df_carte["centre"] = []
df_carte["coordx"] = []
df_carte["coordy"] = []
df_carte["nb_creneau"] = []
df_carte["nb_creau_1S"] = []



def coor_wgs84_to_web_mercator(lon, lat):
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return (x,y)

for i in c :
    df_carte["centre"].append((i['name']))
    X, Y = coor_wgs84_to_web_mercator(i["location"]["coordinates"][0], i["location"]["coordinates"][1])
    df_carte["coordx"].append(X)
    df_carte["coordy"].append(Y)
    df_carte["nb_creneau"].append(len(i['visit_motives']))
    nb_1S = 0
    for j in i['visit_motives']:
        if j['first_shot_motive'] == True :
            nb_1S += 1
    df_carte["nb_creau_1S"].append(nb_1S)

# Ajout de la couleur toute dose :
color = []
legend = []
for i in df_carte["nb_creneau"] :
    if i < 5 :
        color.append('red')
        legend.append("Moins de 5 rendez-vous")
    if i >= 5 and i < 10 :
        color.append('orange')
        legend.append('Entre 5 et 10 rendez-vous')
    if i >= 10 :
        color.append('green')
        legend.append('Plus de 10 rendez-vous')

df_carte['color'] = color
df_carte['legende'] = legend
print(legend)

# Ajout de la couleur première dose dose :
color_1S = []
legend_1S = []
for i in df_carte["nb_creau_1S"] :
    if i < 2 :
        color_1S.append('red')
        legend_1S.append("Moins de 5 rendez-vous")
    if i >= 2 and i < 5 :
        color_1S.append('orange')
        legend_1S.append("Entre 5 et 10 rendez-vous")
    if i >= 5 :
        color_1S.append('green')
        legend_1S.append("Plus de 10 rendez-vous")

df_carte['color_1S'] = color_1S
df_carte['legend_1S'] = legend_1S

df = pd.DataFrame(df_carte)
print(df)
source = ColumnDataSource(df)

p = figure(x_axis_type="mercator", y_axis_type="mercator", active_scroll="wheel_zoom", title="Centres de vaccination à moins de 50km de Rennes")

tile_provider = get_provider(Vendors.CARTODBPOSITRON)
p.add_tile(tile_provider)

p.triangle(x="coordx",y="coordy",source = source,size =10, color=factor_cmap('color', palette= ['red','orange','green'],factors=['red','orange','green']),legend= "legende")

hover_tool = HoverTool(tooltips=[('Nombre de creneaux disponibles', '@nb_creneau'),( 'Nom du centre', '@centre')]) 
p.add_tools(hover_tool)

#Création de la légende
p.legend.location = "bottom_right"
p.legend.title = "Nombre de créneaux disponibles"

# Carte des first shots

p2 = figure(x_axis_type="mercator", y_axis_type="mercator", active_scroll="wheel_zoom", title="Centres de vaccination à moins de 50km de Rennes (1ère dose)")

tile_provider = get_provider(Vendors.CARTODBPOSITRON)
p2.add_tile(tile_provider)

p2.triangle(x="coordx",y="coordy",source = source,size =10, color=factor_cmap('color_1S', palette= ['red','orange','green'],factors=['red','orange','green']),legend= "legend_1S")

hover_tool = HoverTool(tooltips=[('Nombre de creneaux disponibles', '@nb_creneau'),( 'Nom du centre', '@centre')]) 
p2.add_tools(hover_tool)

#Création de la légende
p2.legend.location = "bottom_right"
p2.legend.title = "Nombre de créneaux disponibles"

div = Div(text="""
<a href="index.html ">Accueil</a>""")

div1 = Div(text="""
           <h3>Nombre de créneaux de vaccination disponibles</h3>
           """)

div2 = Div(text="""
           <h3>Nombre de créneaux de vaccination disponibles (1ère dose)</h3>
           """)

layout = row(div,column(div1,p),column(div2,p2))

show(layout)