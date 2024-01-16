# Projet Scrapper!

Le scrapper, est un projet **Python** qui permet d'aller interroger une base de **MongoDB** pour récupérer une url à scrapper, et une fois que l'url scrappé, la page html obtenu, nous permettra de la sauvegarder dans un collection, isoler quelques données importantes pour les stocker dans des champs séparément, et extraire toutes les url sur laquelle cette même page pointe et en garder que celle qui sont dans le scope       


## Programmes
Le scrapper est divisé en deux parties 

 1.  **initialise_scrapper** : permet d'initialiser la scrapper avec une première **URL** et un **SCOPE** à respecter 
 2. **main** : permet de lancer le scrapper 

## Lancement du scrapper 
il faut suivre un ordre : 
- lancer une permière fois **initialise_scrapper** pour initialiser notre base **mongo**
- lancer autant de fois (sur différents **Terminal**) le programme **main**

### Commandes de lancement : 
```console
	python .\initialise_scrapper.py 'permière_url' 'scope'
	python .\main.py 
```
