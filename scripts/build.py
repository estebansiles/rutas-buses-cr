#!/usr/bin/env python3
"""Genera el dashboard y el mapa a partir del CSV de ARESEP.

Lee data/analisis_lineas_buses_cr_2026.csv, incrusta los datos en las
plantillas de templates/ y escribe los HTML finales en dist/.

Uso:  python3 scripts/build.py
"""
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "analisis_lineas_buses_cr_2026.csv"
DIST = ROOT / "dist"
SALIDAS = [
    (ROOT / "templates" / "dashboard.html", DIST / "dashboard.html"),
    (ROOT / "templates" / "mapa.html", DIST / "index.html"),
]
PROVS = ["San José", "Alajuela", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"]


def origen_destino(ruta):
    """'SAN JOSE-PAVAS-LOMAS DEL RIO' -> ('San Jose', 'Lomas Del Rio')

    'CIUDAD QUESADA – FORTUNA POR SAN JOSECITO' -> ('Ciudad Quesada', 'Fortuna')
    Corta el destino en 'POR' o 'X' para quedarse con el destino principal.
    """
    partes = [p.strip() for p in re.split(r"\s*[-–]\s*", ruta) if p.strip()]
    if len(partes) < 2:
        return ruta, ruta
    destino = re.split(r"\s+(?:POR|X)\s+|\s*\(", partes[-1])[0].strip()
    return partes[0].title(), destino.title()


def num(s):
    """Formato del CSV: '₡3.360' -> 3360.0 ; '268,7' -> 268.7 ; '' -> None

    Punto = separador de miles, coma = separador decimal.
    """
    s = s.strip().replace("₡", "")
    if s == "":
        return None
    return float(s.replace(".", "").replace(",", "."))


def leer_lineas():
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter=";"))

    hdr = next(i for i, r in enumerate(rows) if r and r[0].strip() == "Código CTP")

    data, excluidas, incoherentes = [], [], []
    for lineno, r in enumerate(rows[hdr + 1:], start=hdr + 2):
        if not r or not r[0].strip():
            continue
        r = r + [""] * (14 - len(r))
        code, clave, op, ruta, prov = (x.strip() for x in r[:5])
        # La fuente excluye los permisos; la columna 'Visible' marca las filas del análisis
        if "PERMISO" in (code + clave + ruta).upper() or r[13].strip() != "1":
            excluidas.append(lineno)
            continue
        km = num(r[6])
        tar = num(r[10])
        kml = num(r[11])
        con = r[12].strip() == "Sí"
        if km is None:
            raise SystemExit(f"Línea {lineno} sin km máx")
        if con != (tar is not None):
            incoherentes.append(lineno)
        if tar is not None and kml is None:
            kml = tar / km
        origen, destino = origen_destino(ruta)
        data.append({
            "id": len(data), "code": code, "op": op, "ruta": ruta, "prov": prov,
            "origen": origen, "destino": destino,
            "tramos": [p.strip().title() for p in re.split(r"\s*[-–]\s*", ruta) if p.strip()],
            "ramales": int(r[5]) if r[5].strip().isdigit() else None,
            "kmp": num(r[7]),
            "km": km, "pend": r[9].strip(), "tar": tar,
            "kml": kml if tar is not None else None,
        })

    desconocidas = sorted({d["prov"] for d in data} - set(PROVS))
    if desconocidas:
        raise SystemExit(f"Provincias no reconocidas: {desconocidas}")
    return data, excluidas, incoherentes


def regresion(T):
    """Mínimos cuadrados de tarifa sobre km. Devuelve (a, b, r)."""
    n = len(T)
    mx = sum(d["km"] for d in T) / n
    my = sum(d["tar"] for d in T) / n
    sxx = sum((d["km"] - mx) ** 2 for d in T)
    syy = sum((d["tar"] - my) ** 2 for d in T)
    sxy = sum((d["km"] - mx) * (d["tar"] - my) for d in T)
    b = sxy / sxx
    return my - b * mx, b, sxy / math.sqrt(sxx * syy)


def main():
    data, excluidas, incoherentes = leer_lineas()
    T = [d for d in data if d["tar"] is not None]
    a, b, r = regresion(T)

    print(f"Filas: {len(data)} | excluidas: {len(excluidas)} | incoherencias 'Con tarifa': {incoherentes}")
    print(f"Con tarifa: {len(T)} | Sin tarifa: {len(data) - len(T)}")
    print("Por provincia:", dict(Counter(d["prov"] for d in data)))
    print("Km máx: min %.1f, max %.1f" % (min(d["km"] for d in data), max(d["km"] for d in data)))
    print("Tarifa: min %.0f, max %.0f, promedio %.1f"
          % (min(d["tar"] for d in T), max(d["tar"] for d in T), sum(d["tar"] for d in T) / len(T)))
    print("Regresión: a = %.2f  b = %.3f  r = %.4f  R² = %.4f" % (a, b, r, r * r))
    print("₡/km promedio por línea: %.2f" % (sum(d["kml"] for d in T) / len(T)))

    payload = json.dumps(data, ensure_ascii=False)
    DIST.mkdir(exist_ok=True)
    for tpl, out in SALIDAS:
        html = tpl.read_text(encoding="utf-8")
        if "__DATA__" not in html:
            raise SystemExit(f"{tpl.name} no contiene el marcador __DATA__")
        out.write_text(html.replace("__DATA__", payload), encoding="utf-8")
        print(f"Escrito: {out.relative_to(ROOT)} ({len(html) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
