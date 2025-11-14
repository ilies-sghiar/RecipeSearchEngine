# Makefile pour automatiser le lancement des services Docker Elasticsearch

# Variables
DOCKER_COMPOSE = docker-compose.yml
ELASTIC_DIR = elasticsearch
OS := $(shell uname -s)

# Targets	
.PHONY: all help setup-dirs elasticsearch elasticsearch-stop clean

# Default target
all: elasticsearch 

help:
	@echo "Commandes disponibles:"
	@echo "  make elasticsearch       - Lance les services Docker Elasticsearch"
	@echo "  make elasticsearch-stop  - Arrête les services Docker Elasticsearch"
	@echo "  make clean               - Supprime les services Docker Elasticsearch"
	
setup-dirs:
ifeq ($(OS),Linux)
	@echo "Linux détecté"
	@echo "Création des répertoires de données..."
	@mkdir -p ./$(ELASTIC_DIR)/es_data ./$(ELASTIC_DIR)/kb_data
	@echo "Configuration des permissions (UID 1000)..."
	@sudo chown -R 1000:1000 ./$(ELASTIC_DIR)/es_data ./$(ELASTIC_DIR)/kb_data
	@sudo chmod -R 770 ./$(ELASTIC_DIR)/es_data ./$(ELASTIC_DIR)/kb_data
endif
	@echo "Répertoires configurés"
	
elasticsearch: setup-dirs
	@echo "Démarrage d'Elasticsearch et Kibana..."
	@cd $(ELASTIC_DIR) && docker-compose -f $(DOCKER_COMPOSE) up -d
	@echo "Services démarrés"
	
elasticsearch-stop:
	@echo "Arrêt des services..."
	@cd $(ELASTIC_DIR) && docker-compose -f $(DOCKER_COMPOSE) stop
	@echo "Services arrêtés"
	
clean:
	@echo "Suppression des conteneurs..."
	@cd $(ELASTIC_DIR) && docker-compose -f $(DOCKER_COMPOSE) down -v
	@echo "Nettoyage terminé"
