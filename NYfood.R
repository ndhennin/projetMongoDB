library(mongolite)
library(rAmCharts)
library(tidyverse)
library(htmlwidgets)
library(R3port)

# Connexion à la base NYfood

url="mongodb://etudiant:ur2@clusterm1-shard-00-00.0rm7t.mongodb.net:27017,clusterm1-shard-00-01.0rm7t.mongodb.net:27017,clusterm1-shard-00-02.0rm7t.mongodb.net:27017/?ssl=true&replicaSet=atlas-l4xi61-shard-0"
mdb = mongo(collection="NYfood", db="food",
            url=url,
            verbose=TRUE)

# Requête MongoDB

q = '[
        {"$unwind": "$grades"},
        {"$match": {"cuisine":"French"}},
        {"$group":{"_id":{"grade" : "$grades.grade",
                      "borough" : "$borough"}, "nb_notes": {"$sum":1}}}
]          
    '
dataset <- mdb$aggregate(pipeline = q)

# Barplot

dataset <- data.frame(as.matrix(dataset))
colnames(dataset) <- c("Grade", "Borough", "Nb")

# Différentes notes présentes
grades <- levels(as.factor(dataset$Grade))

# Dataframe final
final_dataset <- data.frame(c(rep(0,5)))

for(i in grades){
  final_dataset[i] <- c(rep(0,5))
}

final_dataset <- final_dataset[-c(1)]

rownames(final_dataset) <- levels(as.factor(dataset$Borough))

for(i in seq(nrow(dataset))){
  final_dataset[dataset[i,"Borough"],dataset[i,"Grade"]] <- as.numeric(dataset[i,"Nb"])
}

# On ajoute une colonne de la somme des notes
final_dataset$sum <- apply(final_dataset,1,function(x) sum(x))
final_dataset <- final_dataset[order(-final_dataset$sum),]
# Mise en forme du dataset

barplot <- amBarplot(y = c("A", "B", "C", "Not Yet Graded", "P", "Z"), data = final_dataset, stack_type = "regular")  %>% 
  amOptions(legend = TRUE, main = "Nombre de notes des restaurants français par quartier")

html_plot(amBarplot(y = c("A", "B", "C", "Not Yet Graded", "P", "Z"), data = final_dataset, stack_type = "regular")  %>% 
            amOptions(legend = TRUE, main = "Nombre de notes des restaurants français par quartier")
          , out="barplot.html")





