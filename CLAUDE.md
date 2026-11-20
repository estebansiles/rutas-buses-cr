# Contexto del proyecto para Claude Code

Dashboard y mapa interactivo de las líneas de autobús de Costa Rica, a partir de
datos abiertos de ARESEP. Todo es HTML estático: no hay backend.

## Estructura

```
data/analisis_lineas_buses_cr_2026.csv   Fuente de tarifas y kilómetros (ARESEP)
templates/dashboard.html                 Plantilla del dashboard (marcador __DATA__)
templates/mapa.html                      Plantilla del mapa (marcador __DATA__)
scripts/build.py                         Parsea el CSV e incrusta los datos en las plantillas
scripts/generar_teselas.sh               Extrae dist/cr.pmtiles (fondo del mapa)
scripts/verificar_rangos.sh              Comprueba HTTP 206 en el hosting
dist/                                    Salida generada (no versionada)
```

`make build` regenera `dist/`. Las plantillas se editan a mano; `dist/` nunca.

## Reglas duras

**Nunca apuntar el mapa a `tile.openstreetmap.org` ni a otro servidor público de
OSM.** El proyecto ya fue bloqueado con HTTP 403 por la política de uso de
teselas. OSM espera que una app con tráfico tenga teselas propias o un proveedor.
El fondo se sirve desde `cr.pmtiles` alojado junto a la página.

Consecuencias que hay que mantener:

- El crédito `© OpenStreetMap contributors` va visible en el mapa, sin esconderlo.
- Nada de descarga anticipada de teselas ni funciones de uso sin conexión.
- Si alguna vez se usa un servicio de teselas de terceros, hay que revisar sus
  términos antes de conectarlo.

**El costo por tramo está fuera de alcance.** Se decidió no incluirlo en ninguna
parte del proyecto. El CSV solo trae un costo por línea (tarifa máxima del
recorrido completo), no un desglose.

## Formato del CSV

Export de hoja de cálculo en español. Al parsearlo:

- Delimitador `;`, codificación `utf-8-sig`.
- La fila de encabezado se busca por el texto `Código CTP`; antes hay título y notas.
- Punto = separador de miles, coma = decimal, `₡` como prefijo. `'₡3.360'` → `3360.0`.
- Columna `Visible` = `1` marca las filas del análisis; se excluyen los permisos.
- `Km máx` = ramal más largo. `Tarifa máx` = recorrido completo.
- 69 líneas no tienen tarifa; quedan fuera del gráfico y de la regresión.

Cifras de referencia del estado actual (si cambian tras editar el parser, algo se rompió):

| Dato | Valor |
|---|---|
| Filas | 361 |
| Con tarifa | 292 |
| Regresión tarifa ~ km | a = 396,09 · b = 12,687 |
| Correlación | r = 0,8506 · R² = 0,7235 |

## Capa geográfica (WFS de ARESEP)

```
Servicio: https://mapas.aresep.go.cr/server/services/I_Transporte_Externo_PII/
          I_Transporte_Externo_PII/MapServer/WFSServer
Capa:     I_Transporte_Externo_PII_I_Transporte_Externo_PII:PR05_Vista_BusRamales
```

- Proyección **EPSG:5367** (CRTM05). Se convierte a WGS84 con proj4 en el navegador.
- Geometría en el campo `SHAPE`, tipo `gml:MultiCurvePropertyType`.
- Campos útiles: `CODCTP2019`, `OPERADOR`, `CANTONINICIO`, `CANTONFINAL`,
  `KM_ARESEP`, `DISTANCIA`, `PENDIENTE`, `PAVIMENTADO`, `AÑORAMAL`.
- **El servicio solo entrega GML3 / `text/xml`.** No ofrece GeoJSON ni shape-zip,
  por eso el mapa trae su propio parser de GML en vez de usar `fetch` + JSON.

La unión con el CSV es `CODCTP2019` ↔ `Código CTP`. Primero coincidencia exacta;
después, para códigos múltiples tipo `44-45-47`, se indexan los tokens numéricos
sueltos. Los ramales sin línea en el CSV se dibujan en gris.

## Colores por provincia

Definidos por el cliente, no cambiar sin pedirlo:

| Provincia | Color |
|---|---|
| San José | `#1F4E79` |
| Alajuela | `#C00000` |
| Cartago | `#7030A0` |
| Heredia | `#ED7D31` |
| Guanacaste | `#FFC000` |
| Puntarenas | `#00B050` |
| Limón | `#00B0F0` |

Guanacaste y Limón llevan texto oscuro encima; el resto, blanco.

## Pendiente de verificar

Nada de esto se probó con datos reales todavía. Al retomar, conviene empezar aquí:

1. **Orden de ejes del WFS.** `toLatLngs()` asume que si `x > y` los valores
   vienen como (norte, este) y los invierte, porque en Costa Rica el norte ronda
   1.100.000 y el este 500.000. Hay que confirmarlo contra el mapa real.
2. **CORS del WFS.** No se sabe si ARESEP permite el `fetch` desde el navegador.
   La página tiene un respaldo: cargar un `.gml` descargado a mano.
3. **Peticiones por rango en SiteGround.** `make verificar` lo comprueba.
4. **Cobertura de la unión.** El panel lateral muestra cuántas líneas del CSV
   quedaron sin trazado; ese número todavía no se ha revisado.

## Al desarrollar

- El mapa **no funciona abierto con `file://`**: PMTiles y el WFS necesitan HTTP.
  Usar `make servir`.
- Las librerías (MapLibre, pmtiles, proj4, basemaps) se cargan desde unpkg con
  versión fija. Si se cambia una versión, revisar que la API siga igual: el
  paquete de estilos cambió de `protomaps-themes-base` a `@protomaps/basemaps`
  en su versión 5 y la llamada es distinta.
