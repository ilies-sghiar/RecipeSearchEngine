# Recipe Search Engine

Ce projet implémente une API permettant de rechercher, de manière sémantique, des recettes de cuisine stockées dans une base Elasticsearch grâce à des embeddings vectoriels issus de modèles de langage.

Un script dédié permet l’indexation des données dans Elasticsearch.

À terme, un frontend sera ajouté pour offrir une expérience de recherche complète.

<p align="center">
  <img src="https://marketplace.canva.com/EAF_asJtgSY/2/0/566w/canva-white-minimalist-food-recipe-magazine-a4-Cln80zeGmm0.jpg" alt="Recipe Image" height="250"/>
</p>

**Disclaimer :** Le projet a été initialement développé sous Linux. Il devrait fonctionner également sur Windows, mais cela n’est pas garanti à 100 %.

---

## Installation

Clonez le dépôt :

```bash
git clone https://github.com/ilies-sghiar/RecipeSearchEngine.git
cd RecipeSearchEngine
```

Lancez les services Elasticsearch containerisés (nécessaires pour stocker les données) grâce au Makefile :

```bash
make
```

Quelques commandes utiles du Makefile :

- `make elasticsearch` : Démarre les services Docker Elasticsearch
- `make elasticsearch-stop` : Arrête les services Docker Elasticsearch
- `make clean` : Supprime les services Docker Elasticsearch

Vérifiez que les services sont actifs en accédant aux adresses suivantes :

- [http://localhost:5601/](http://localhost:5601/) : Kibana (visualisation des données)
- [http://localhost:9200/](http://localhost:9200/) : Elasticsearch (stockage des données, vide au démarrage)

Installez l’environnement Python pour l’indexation des données et le lancement de l’API :

- Pour un environnement complet (avec les outils de test) :
```bash
poetry install --with dev
```

- Pour l’environnement de production uniquement :
```bash
poetry install --without dev
```

---

## Utilisation

### Indexation des données

Pour indexer le fichier `src/recipes.json` dans Elasticsearch :

```bash
poetry run index-recipes
```

Cette commande crée un index contenant les champs des recettes (nom, ingrédients, temps…) ainsi qu’un champ spécial contenant l’embedding vectoriel de l’ensemble des champs, calculé avec le modèle `all-MiniLM-L6-v2`.

Pour supprimer l’index créé :

```bash
curl -X DELETE "http://localhost:9200/index_with_schema_combined"
```

### Lancement de l’API

#### Sous Linux :

```bash
poetry run uvicorn searchengine.api:app --reload &
```

#### Sous Windows :

```bash
Start-Process poetry -ArgumentList "run uvicorn searchengine.api:app --reload"
```

Sinon, cette commande fonctionne sur les deux systèmes, mais l'API n'est pas en arrière plan:

```bash
poetry run uvicorn searchengine.api:app --reload
```

### Requêter l’API

Pour interroger l’API :

```bash
curl -X POST "http://127.0.0.1:8000/search-names/"
-H "Content-Type: application/json"
-d '{"query": "Entrer votre recherche ici"}'
```

Exemple :

```bash
curl -X POST "http://127.0.0.1:8000/search-names/"
-H "Content-Type: application/json"
-d '{"query": "Smoothie"}'
```

Réponse :

```json
{
"names": [
"Summer Breeze Smoothie",
"Green Pineapple Power Smoothie",
"Tangy Fruit Salad",
"Cantaloupe Crush",
"Mango Shake",
"Mai Tai",
"Piña Colada",
"Any Berry Sauce",
"Multigrain Apple Muffins",
"Apple Banana Salad with Peanuts"
]
}
```

### Arrêt de l’API

#### Sous Linux :

```bash
pkill -f uvicorn
```

#### Sous Windows :

```bash
Get-Process uvicorn | Stop-Process
```

---

## Tests

Pour exécuter les tests (mode développement requis : `poetry install --with dev`) :

```bash
poetry run pytest -v
```

---

## Packaging

Pour créer les fichiers de distribution (`.whl` et `.tar.gz`) :

```bash
poetry build
```

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails

## Contact

Pour toute question, vous pouvez me contacter à `iliesghiar@gmail.com`.