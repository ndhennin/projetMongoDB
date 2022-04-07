# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 20:23:31 2022

@author: leclerc
"""
import pymongo

############
#MONGODB
############

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/?tls=true&tlsAllowInvalidCertificates=true"
client = pymongo.MongoClient(db_uri)

db=client["publications"]
#print(db.list_collection_names())

coll = db["hal_irisa_2021"]
#print(coll.index_information())

#On récupère les 20 auteurs ayant le + publiés d'articles 

pipeline = [ 
    {"$unwind" : "$authors"},
    {"$group":{"_id" : {"nom": "$authors.name", 
    "prenom":"$authors.firstname"},                                                                                                                                                                                                                                         
    "nb_publications" : {"$sum":1}}},
    {"$sort":{"nb_publications":pymongo.DESCENDING}},
    {"$limit":20}
]

results = coll.aggregate(pipeline)
print("Auteurs ayant le plus publiés d'articles")
for auteur in results:
    #print(auteur)
    print(auteur["_id"]["nom"],auteur["_id"]["prenom"])

#On veut récupérer la liste de chacune des publications de ces auteurs

# pipeline = [ 
#     {"$unwind" : "$authors"},
#     {"$group":{"_id" : {"nom": "$authors.name", 
#     "prenom":"$authors.firstname"},                                                                                                                                                                                                                                         
#     "nb_publications" : {"$sum":1}}},
#     {"$sort":{"nb_publications":pymongo.DESCENDING}},
#     {"$limit":20},
#     {"$group":{"_id":{"publications":"$_id.title"}}}
# ]

# results = coll.aggregate(pipeline)
# print("Auteurs ayant le plus publiés d'articles")
# for publi in results:
#     print(publi)



##########################
#2. VISUALISATION
##########################


