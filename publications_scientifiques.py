# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 09:31:40 2022

@author: Nolwenn Dhennin
"""

import pymongo
import networkx as nx
from bokeh.plotting import figure, from_networkx
from bokeh.io import output_file, show
from bokeh.models import BoxZoomTool, Circle, HoverTool, ResetTool
from bokeh.layouts import column
from bokeh.models import Div

############################################
#1. Appel à la base publications sur MongoDB
############################################

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/?tls=true&tlsAllowInvalidCertificates=true"
client = pymongo.MongoClient(db_uri)
db=client["publications"]

# Collections de la base
# print(db.list_collection_names())

coll = db["hal_irisa_2021"]
# print(coll.index_information())

# On récupère les 20 auteurs ayant le plus publiés d'articles ainsi que leurs publications, du plus au moins prolifique

pipeline = [ 
    {"$project":{"halId":1,"authors":1}},
    {"$unwind" : "$authors"},
    {"$group":{"_id" : {"nom": "$authors.name", 
    "prenom":"$authors.firstname"},                                                                                                                                                                                                                                         
    "nb_publications" : {"$sum":1},
    "publi" : {"$push":"$halId"}}},
    {"$sort":{"nb_publications":pymongo.DESCENDING}},
    {"$limit":20}
]

results = coll.aggregate(pipeline)

# print("Auteurs ayant le plus publiés d'articles")
# for auteur in results:
#     print(auteur["_id"]["nom"],auteur["_id"]["prenom"],"\nQuelques identifiants de publications :",auteur["publi"][0:4])
#     print("***********************")


##########################
#2. Visualisation
##########################

# On veut récupérer la liste  des publications pour chaque auteur
liste_auteur_publi = []
for auteur in results:
    l1=[]
    l2=[]
    l3=[]
    l4=[]
    l1.append(auteur["_id"]["nom"])
    l1.append(auteur["_id"]["prenom"])
    l1 = ' '.join((str(n) for n in l1))
    l2.append(auteur["publi"])
    l4.append(auteur["nb_publications"])
    l3.append(l1)
    l3.append(l2[0])
    l3.append(l4[0])
    liste_auteur_publi.append(l3)
# print("Auteur ayant publié le plus d'articles :",liste_auteur_publi[0][0],"\nId de ses publications :",liste_auteur_publi[0][1])

graph = {}
dico_color = {}
weights = {}

for auteur1 in liste_auteur_publi:
    liste1=auteur1[:][1]
    set1=set(liste1)
    # print(liste1)
    # print(set1)
    for auteur2 in liste_auteur_publi:
        if auteur1 != auteur2:
            liste2=auteur2[:][1]
            set2=set(liste2)
            intersection = list(set1 & set2)
            if len(intersection) != 0:
                weights[(auteur1[0],auteur2[0])]=len(intersection)
                if auteur1[0] in graph:
                    graph[auteur1[0]].append(auteur2[0]) 
                else: 
                    graph[auteur1[0]] = [auteur2[0]]
    if auteur1[0] not in graph.keys():
        graph[auteur1[0]]=[]
        
    #Choix des couleurs de noeuds    
    if auteur1[2]>=20:
        dico_color[auteur1[0]] = "red"
    elif auteur1[2]>10 and auteur1[2]<=19:
        dico_color[auteur1[0]] = "orange"
    else:
        dico_color[auteur1[0]] = "yellow"

# print(graph)

# Création du graphique
G = nx.Graph(graph)
G.add_nodes_from(graph.keys())

# On récupère les poids pour les liens entre chaque auteur        
edges_with_weights=[(a,b,weights[(a,b)]) for (a,b) in G.edges]
G.add_weighted_edges_from(edges_with_weights)

# Ajout des couleurs aux noeuds
nx.set_node_attributes(G, dico_color, 'node_color')

# Plot avec Bokeh
graphique = from_networkx(G, nx.spring_layout, scale=1, center=(0,0))
graphique.node_renderer.glyph = Circle(size=17, fill_color='node_color')
fig = figure(title="Liens entre les 20 auteurs de publications scientifiques étant les plus prolifiques", x_range=(-1.1,1.1), y_range=(-1.1,1.1),
               toolbar_location=None)
# Mettre les poids entre les auteurs
graphique.edge_renderer.data_source.data["line_width"] = [G.get_edge_data(a,b)['weight'] for a, b in G.edges()]
graphique.edge_renderer.glyph.line_width = {'field': 'line_width'}
fig.renderers.append(graphique)

# Création de la légende
fig.circle(40,30, color="yellow", legend_label="Moins de 10")
fig.circle(40,30, color="orange", legend_label="Entre 10 et 19")
fig.circle(40,30, color="red", legend_label="Au moins 20")
fig.xgrid.grid_line_color = None
fig.legend.location = "bottom_right"
fig.legend.title = "Nombre de publications écrites"

node_hover_tool = HoverTool(tooltips=[ ("Auteur", "@index")])
fig.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())

div = Div(text="""
<a href="index.html ">Accueil</a>""")


layout = column(div,fig)
output_file("publications_scientifiq.html")
show(layout)


