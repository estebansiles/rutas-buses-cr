# Rutas de autobús de Costa Rica

Dashboard y mapa interactivo de las líneas de autobús del país, construidos sobre
datos abiertos de ARESEP. Son páginas estáticas: se suben a cualquier hosting y
funcionan sin backend ni base de datos.

**Dashboard** — dispersión de kilómetros contra tarifa máxima, con una línea de
tendencia cuyos `r` y `R²` se recalculan al filtrar, un Top 15 por kilometraje e
indicadores resumidos. Filtros por provincia, rango de kilómetros, relieve y
tarifa.

**Mapa** — el trazado real de cada ramal sobre un mapa base, coloreado por
provincia y cruzado con las tarifas del dashboard.

## Requisitos

| Para | Necesitás |
|---|---|
| Generar los HTML | Python 3.9 o superior (solo biblioteca estándar) |
| Generar el fondo del mapa | La herramienta [`pmtiles`](https://github.com/protomaps/go-pmtiles/releases) · en macOS: `brew install pmtiles` |
| Ver el resultado | Un navegador y conexión a internet |

## Inicio rápido

```bash
git clone https://github.com/estebansiles/rutas-buses-cr.git
cd rutas-buses-cr

make build        # genera dist/dashboard.html y dist/index.html
make servir       # abre http://localhost:8000
```

El dashboard ya funciona con eso. El mapa además necesita su fondo:

```bash
make teselas BUILD=20250709   # genera dist/cr.pmtiles (~1 vez)
```

`BUILD` es la fecha de una build diaria de Protomaps, en formato `AAAAMMDD`.
Buscá una vigente en [maps.protomaps.com](https://maps.protomaps.com); si la
fecha no existe, el comando falla al descargar y conviene probar otra.

> El mapa no funciona si abrís el HTML con doble clic (`file://`). PMTiles y el
> servicio de ARESEP necesitan que la página se sirva por HTTP. Por eso existe
> `make servir`.

## Publicar en un hosting

Subí a una misma carpeta del servidor, por ejemplo `public_html/mapa-rutas/`:

```
index.html        (el mapa)
dashboard.html    (el dashboard)
cr.pmtiles        (el fondo del mapa)
```

Después comprobá que el servidor sirve el `.pmtiles` por partes:

```bash
make verificar URL=https://tu-dominio.com/mapa-rutas/cr.pmtiles
```

Tiene que responder **HTTP 206**. Si responde 200, el servidor ignora la cabecera
`Range` y el mapa no va a cargar bien; el propio script explica las salidas.

## Por qué el fondo es propio

Una versión anterior usaba los servidores públicos de teselas de OpenStreetMap y
fue bloqueada con un error 403. Esos servidores los sostienen voluntarios con
donaciones, y su política pide que las aplicaciones con tráfico usen teselas
propias o un proveedor. Por eso el mapa sirve su propio archivo `cr.pmtiles`.

Si alguien retoma el proyecto: no vuelvas a apuntar a `tile.openstreetmap.org`.
Hay más contexto en [`CLAUDE.md`](CLAUDE.md).

## Fuentes y créditos

| Dato | Fuente |
|---|---|
| Tarifas y kilómetros por línea | ARESEP, [datos abiertos de rutas de autobuses](https://aresep.go.cr/datos-abiertos/rutas-autobuses/) |
| Trazado de los ramales | ARESEP, capa `PR05_Vista_BusRamales` (servicio WFS) |
| Mapa base | OpenStreetMap vía [Protomaps](https://protomaps.com) |

El mapa base deriva de OpenStreetMap, bajo licencia ODbL. El crédito
`© OpenStreetMap contributors` debe quedar visible: la página ya lo muestra en la
esquina del mapa, y no hay que taparlo ni moverlo fuera de la vista.

## Estructura

```
data/        CSV de origen
templates/   Plantillas HTML con el marcador __DATA__
scripts/     build.py y utilidades de despliegue
dist/        Salida generada (no se versiona)
```

Las plantillas se editan a mano y `make build` las rellena con los datos del CSV.
Nunca edités `dist/`: se sobrescribe en cada build.
