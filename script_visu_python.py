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
from bokeh.models import HoverTool, ColumnDataSource, ColorPicker, Legend
from bokeh.models.widgets import Tabs, Panel
from bokeh.layouts import row, column

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri, tls=True, tlsAllowInvalidCertificates=True)

db_name ="doctolib"
db = client[db_name]
print(db.list_collection_names())

coll_name = "dump_Jan2022"
coll = db[coll_name]
print(coll.index_information())

# On récupère les centres de vaccination à moins de 50km de Rennes

c = coll.find(
    {"location": {'$near' : {'$geometry' : {"type": "Point", "coordinates": [-1.6777926,48.117266]},'$maxDistance': 50000}}}
)

# Représentation des centres de vaccination sur une carte

## Création d'un data frame avec le nom et les coordnnées du centre de vaccination

df_carte = {}
df_carte["centre"] = []
df_carte["coordx"] = []
df_carte["coordy"] = []
df_carte["nb_creneau"] = []


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

# Ajout de la couleur :
color = []
for i in df_carte["nb_creneau"] :
    if i < 5 :
        color.append('red')
    if i >= 5 and i < 10 :
        color.append('orange')
    if i >= 10 :
        color.append('green')

df_carte['color'] = color

df = pd.DataFrame(df_carte)
print(df)
source = ColumnDataSource(df)

p = figure(x_axis_type="mercator", y_axis_type="mercator", active_scroll="wheel_zoom", title="Centres de vaccination à moins de 50km de Rennes")

tile_provider = get_provider(Vendors.CARTODBPOSITRON)
p.add_tile(tile_provider)

p.triangle(x="coordx",y="coordy",source =source,size =10)

show(p)