.PHONY: help build teselas servir verificar limpiar

BUILD   ?= 20250709
BBOX    ?= -86.1,7.9,-82.5,11.3
MAXZOOM ?= 14
PUERTO  ?= 8000
URL     ?= https://quebradacamelia.com/mapa-rutas/cr.pmtiles

help:
	@echo "Objetivos disponibles:"
	@echo "  make build                 Genera dist/dashboard.html y dist/index.html desde el CSV"
	@echo "  make teselas BUILD=AAAAMMDD  Extrae dist/cr.pmtiles de la build de Protomaps"
	@echo "  make servir                Levanta un servidor local en http://localhost:$(PUERTO)"
	@echo "  make verificar URL=...     Comprueba que el hosting admite peticiones por rango"
	@echo "  make limpiar               Borra dist/"

build:
	python3 scripts/build.py

teselas:
	BUILD=$(BUILD) BBOX=$(BBOX) MAXZOOM=$(MAXZOOM) ./scripts/generar_teselas.sh

# El mapa necesita servirse por HTTP: abrirlo con file:// rompe PMTiles y el WFS.
servir: build
	@echo "Abre http://localhost:$(PUERTO)/ para el mapa y /dashboard.html para el dashboard"
	cd dist && python3 -m http.server $(PUERTO)

verificar:
	./scripts/verificar_rangos.sh $(URL)

limpiar:
	rm -rf dist
