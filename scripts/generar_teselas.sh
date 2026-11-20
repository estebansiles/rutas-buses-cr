#!/usr/bin/env bash
# Extrae las teselas de Costa Rica desde una build diaria de Protomaps.
#
# Se corre UNA SOLA VEZ (o cuando quieras datos más frescos). El archivo
# resultante, dist/cr.pmtiles, es el fondo del mapa y se sube al hosting.
#
# Uso:  BUILD=20250709 ./scripts/generar_teselas.sh
#
# Requiere la herramienta pmtiles:
#   macOS:  brew install pmtiles
#   otros:  https://github.com/protomaps/go-pmtiles/releases
set -euo pipefail

BUILD="${BUILD:-}"
BBOX="${BBOX:--86.1,7.9,-82.5,11.3}"   # Costa Rica continental; no incluye Isla del Coco
MAXZOOM="${MAXZOOM:-14}"               # 14 ~ calles; 15 pesa bastante más
DEST="$(cd "$(dirname "$0")/.." && pwd)/dist/cr.pmtiles"

if ! command -v pmtiles >/dev/null 2>&1; then
  echo "ERROR: falta la herramienta 'pmtiles'." >&2
  echo "       macOS: brew install pmtiles" >&2
  echo "       otros: https://github.com/protomaps/go-pmtiles/releases" >&2
  exit 1
fi

if [ -z "$BUILD" ]; then
  cat >&2 <<'MSG'
ERROR: falta la fecha de la build de Protomaps.

Las builds son diarias y tienen el formato AAAAMMDD. Busca una build vigente en
https://maps.protomaps.com (o en https://docs.protomaps.com/guide/getting-started)
y vuelve a correr, por ejemplo:

    BUILD=20250709 ./scripts/generar_teselas.sh

Si la fecha no existe, pmtiles devuelve un error de descarga: probá otra.
MSG
  exit 1
fi

FUENTE="https://build.protomaps.com/${BUILD}.pmtiles"
mkdir -p "$(dirname "$DEST")"

echo "Fuente : $FUENTE"
echo "Recorte: bbox=$BBOX  maxzoom=$MAXZOOM"
echo "Destino: $DEST"
echo

pmtiles extract "$FUENTE" "$DEST" --bbox="$BBOX" --maxzoom="$MAXZOOM"

echo
echo "Listo. Tamaño:"
ls -lh "$DEST" | awk '{print "  " $5 "  " $9}'
echo
echo "Los datos son de OpenStreetMap (ODbL): el crédito debe quedar visible en el mapa."
echo "La página ya lo muestra en la esquina inferior."
