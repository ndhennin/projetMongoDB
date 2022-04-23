# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 20:23:31 2022

@author: Nolwenn Dhennin
"""
import pymongo
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

########################
#APPEL A LA BASE MONGODB
########################

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/?tls=true&tlsAllowInvalidCertificates=true"
client = pymongo.MongoClient(db_uri)

db=client["publications"]
#print(db.list_collection_names())

coll = db["hal_irisa_2021"]
#print(coll.index_information())

#On récupère les 20 auteurs ayant le + publiés d'articles ainsi que leurs publications

pipeline = [ 
    {"$project":{"title":1,"authors":1}},
    {"$unwind" : "$authors"},
    {"$group":{"_id" : {"nom": "$authors.name", 
    "prenom":"$authors.firstname"},                                                                                                                                                                                                                                         
    "nb_publications" : {"$sum":1},
    "titre" : {"$push":"$title"}}},
    {"$sort":{"nb_publications":pymongo.DESCENDING}},
    {"$limit":20}
]

results = coll.aggregate(pipeline)

# print("Auteurs ayant le plus publiés d'articles")
# for auteur in results:
#     #print(auteur)
#     #print(auteur["_id"]["nom"],auteur["_id"]["prenom"],"\nquelques publications :",auteur["titre"][0:4])
#     #print("***********************")


##########################
#2. VISUALISATION
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
    l1 = ' \n'.join((str(n) for n in l1))
    l2.append(auteur["titre"])
    l4.append(auteur["nb_publications"])
    l3.append(l1)
    l3.append(l2[0])
    l3.append(l4[0])
    liste_auteur_publi.append(l3)
# print("Publications de l'auteur ayant publié le plus d'articles :",liste_auteur_publi[0][1])

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

#print(graph)

# On récupère les poids pour les liens entre chaque auteur
weights2=list(weights.values())

plt.figure()
G = nx.Graph(graph)
nx.draw_networkx(G, with_labels=True,font_size=8, node_color=dico_color.values(), width=weights2)

# Légende
def make_proxy(clr, mappable, **kwargs):
    return Line2D([0, 1], [0, 1], color=clr, **kwargs)
clrs = ["red","orange","yellow"]
line = [make_proxy(clr, G, lw=5) for clr in clrs]
labels = [">= 20","> 10", "<=10"]
plt.legend(line, labels, title="Nombre de \npublications", loc="upper right", title_fontsize="small",fontsize="x-small")

plt.title("Liens entre les 20 auteurs de publications \nscientifiques étant les plus prolifiques")
plt.show() 