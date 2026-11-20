#!/usr/bin/env bash
# Comprueba que el hosting sirve el .pmtiles con peticiones por rango.
#
# PMTiles lee pedazos del archivo con la cabecera Range. Si el servidor
# responde 200 en vez de 206, el mapa descarga el archivo entero o no carga.
#
# Uso:  ./scripts/verificar_rangos.sh https://quebradacamelia.com/mapa-rutas/cr.pmtiles
set -euo pipefail

URL="${1:-}"
if [ -z "$URL" ]; then
  echo "Uso: $0 <URL del archivo cr.pmtiles>" >&2
  exit 1
fi

echo "Probando: $URL"
echo

CODIGO=$(curl -s -o /dev/null -w '%{http_code}' -r 0-99 "$URL")

case "$CODIGO" in
  206)
    echo "OK (HTTP 206): el servidor admite peticiones por rango. PMTiles va a funcionar."
    ;;
  200)
    echo "PROBLEMA (HTTP 200): el servidor ignora la cabecera Range y manda el archivo completo."
    echo
    echo "En SiteGround suele venir de un proxy o de la capa de caché. Opciones:"
    echo "  1. Pedir a soporte de SiteGround que habilite byte-range en esa carpeta."
    echo "  2. Excluir la carpeta del caché dinámico desde Site Tools."
    echo "  3. Servir el .pmtiles desde almacenamiento de objetos (Cloudflare R2, S3)"
    echo "     y dejar solo el HTML en SiteGround."
    ;;
  404)
    echo "No encontrado (HTTP 404): revisá que cr.pmtiles esté subido en esa ruta."
    ;;
  *)
    echo "Respuesta inesperada: HTTP $CODIGO"
    ;;
esac

echo
echo "Cabeceras completas:"
curl -s -D - -o /dev/null -r 0-99 "$URL" | sed 's/^/  /'
