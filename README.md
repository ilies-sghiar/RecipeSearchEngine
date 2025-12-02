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

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails

## Contact

Pour toute question, vous pouvez me contacter à `iliesghiar@gmail.com`.
