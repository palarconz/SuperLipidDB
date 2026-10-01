"""
Módulo y herramienta CLI para gestionar la Base de Datos Unificada de Lípidos.
Integra datos y convenciones de:
  - LipidBlast (Fiehn Lab, UC Davis)
  - LIPID MAPS (LMSD)
  - SwissLipids
  - HMDB (Human Metabolome Database)
  - Notación Shorthand / Goslin
"""

from __future__ import annotations

import csv
import json
import re
import sqlite3
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_NAME = "SuperLipidDB_PA"
DB_FILE = Path(__file__).parent / f"{DB_NAME}.sqlite"
CSV_FILE = Path(__file__).parent / f"{DB_NAME}.csv"
JSON_FILE = Path(__file__).parent / f"{DB_NAME}.json"

# Masas de aductos comunes en ESI
MASS_H = 1.007276
MASS_NA = 22.989218
MASS_NH4 = 18.033823
MASS_HCOO = 44.998201
MASS_CH3COO = 59.013851


def normalizar_abreviatura(abrev: str) -> str:
    """Normaliza abreviaturas eliminando espacios redundantes y estandarizando paréntesis."""
    s = abrev.strip()
    # Si viene en formato "PC 34:1", convertir a forma canónica "PC(34:1)"
    m = re.match(r"^([A-Za-z0-9\-]+)[\s_]+([0-9a-zA-Z\:\/_\;]+)$", s)
    if m:
        clase, cadenas = m.group(1), m.group(2)
        return f"{clase}({cadenas})"
    return s


def calcular_aductos(masa_exacta: float, clase: str) -> dict[str, float]:
    """Calcula m/z de los aductos teóricos principales según LipidBlast."""
    aductos = {
        "[M+H]+": round(masa_exacta + MASS_H, 4),
        "[M+Na]+": round(masa_exacta + MASS_NA, 4),
        "[M+NH4]+": round(masa_exacta + MASS_NH4, 4),
        "[M-H]-": round(masa_exacta - MASS_H, 4),
        "[M+HCOO]-": round(masa_exacta + MASS_HCOO, 4),
    }
    return aductos


def inicializar_bd(conexion: Optional[sqlite3.Connection] = None) -> sqlite3.Connection:
    """Crea las tablas e índices si no existen."""
    conn = conexion or sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lipidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                abreviatura TEXT NOT NULL UNIQUE,
                abreviatura_lipidblast TEXT,
                abreviatura_cadenas TEXT,
                nombre_comun TEXT,
                nombre_sistematico TEXT,
                categoria TEXT,
                clase TEXT,
                subclase TEXT,
                formula TEXT,
                masa_exacta REAL,
                aductos_teoricos TEXT,
                lipidmaps_id TEXT,
                swisslipids_id TEXT,
                hmdb_id TEXT,
                chebi_id TEXT,
                pubchem_cid TEXT,
                smiles TEXT,
                inchi_key TEXT,
                fuentes TEXT
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sinonimos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lipido_id INTEGER NOT NULL,
                alias TEXT NOT NULL,
                tipo TEXT,
                FOREIGN KEY (lipido_id) REFERENCES lipidos (id) ON DELETE CASCADE
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lipidos_abrev ON lipidos(abreviatura);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lipidos_abrev_lb ON lipidos(abreviatura_lipidblast);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lipidos_lm_id ON lipidos(lipidmaps_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sinonimos_alias ON sinonimos(alias COLLATE NOCASE);")
    return conn


def insertar_lipido(conn: sqlite3.Connection, datos: dict[str, Any], sinonimos: list[tuple[str, str]] | None = None) -> int:
    """Inserta o actualiza un registro en la base de datos."""
    masa = datos.get("masa_exacta") or 0.0
    clase = datos.get("clase") or ""
    aductos_str = datos.get("aductos_teoricos")
    if not aductos_str and masa > 0:
        aductos_str = json.dumps(calcular_aductos(masa, clase), ensure_ascii=False)

    with conn:
        cursor = conn.execute("""
            INSERT INTO lipidos (
                abreviatura, abreviatura_lipidblast, abreviatura_cadenas,
                nombre_comun, nombre_sistematico, categoria, clase, subclase,
                formula, masa_exacta, aductos_teoricos, lipidmaps_id,
                swisslipids_id, hmdb_id, chebi_id, pubchem_cid, smiles,
                inchi_key, fuentes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(abreviatura) DO UPDATE SET
                abreviatura_lipidblast = excluded.abreviatura_lipidblast,
                abreviatura_cadenas = excluded.abreviatura_cadenas,
                nombre_comun = excluded.nombre_comun,
                nombre_sistematico = excluded.nombre_sistematico,
                categoria = excluded.categoria,
                clase = excluded.clase,
                subclase = excluded.subclase,
                formula = excluded.formula,
                masa_exacta = excluded.masa_exacta,
                aductos_teoricos = excluded.aductos_teoricos,
                lipidmaps_id = excluded.lipidmaps_id,
                swisslipids_id = excluded.swisslipids_id,
                hmdb_id = excluded.hmdb_id,
                chebi_id = excluded.chebi_id,
                pubchem_cid = excluded.pubchem_cid,
                smiles = excluded.smiles,
                inchi_key = excluded.inchi_key,
                fuentes = excluded.fuentes
        """, (
            datos["abreviatura"],
            datos.get("abreviatura_lipidblast"),
            datos.get("abreviatura_cadenas"),
            datos.get("nombre_comun"),
            datos.get("nombre_sistematico"),
            datos.get("categoria"),
            datos.get("clase"),
            datos.get("subclase"),
            datos.get("formula"),
            masa,
            aductos_str,
            datos.get("lipidmaps_id"),
            datos.get("swisslipids_id"),
            datos.get("hmdb_id"),
            datos.get("chebi_id"),
            datos.get("pubchem_cid"),
            datos.get("smiles"),
            datos.get("inchi_key"),
            datos.get("fuentes", "LipidBlast, LIPID MAPS, SwissLipids, HMDB")
        ))
        row = conn.execute("SELECT id FROM lipidos WHERE abreviatura = ?", (datos["abreviatura"],)).fetchone()
        lipido_id = row[0]

        # Insertar alias y variantes por defecto
        aliases = set()
        aliases.add((datos["abreviatura"], "Canonical"))
        if datos.get("abreviatura_lipidblast"):
            aliases.add((datos["abreviatura_lipidblast"], "LipidBlast"))
        if datos.get("abreviatura_cadenas"):
            aliases.add((datos["abreviatura_cadenas"], "MolecularSpecies"))
        if sinonimos:
            for s, t in sinonimos:
                if s:
                    aliases.add((s.strip(), t))

        for alias, tipo in aliases:
            conn.execute("""
                INSERT OR IGNORE INTO sinonimos (lipido_id, alias, tipo)
                VALUES (?, ?, ?)
            """, (lipido_id, alias, tipo))

    return lipido_id


def buscar_lipido(termino: str, conn: Optional[sqlite3.Connection] = None) -> list[dict[str, Any]]:
    """
    Busca lípidos por coincidencia exacta o parcial de abreviatura, alias o ID.
    Soporta formatos tipo 'PC(34:1)', 'PC 34:1', 'LMGP01011732', 'HMDB0007873', etc.
    """
    conexion_propia = conn is None
    if conexion_propia:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row

    termino_limpio = termino.strip()
    termino_norm = normalizar_abreviatura(termino_limpio)
    variantes = [termino_limpio, termino_norm, termino_limpio.replace("(", " ").replace(")", "").strip()]

    # 1. Búsqueda exacta directa o por sinónimo
    query = """
        SELECT DISTINCT l.* FROM lipidos l
        LEFT JOIN sinonimos s ON l.id = s.lipido_id
        WHERE l.abreviatura IN (?, ?, ?)
           OR l.abreviatura_lipidblast IN (?, ?, ?)
           OR l.abreviatura_cadenas IN (?, ?, ?)
           OR l.lipidmaps_id = ?
           OR l.hmdb_id = ?
           OR l.swisslipids_id = ?
           OR s.alias COLLATE NOCASE IN (?, ?, ?)
    """
    params = variantes + variantes + variantes + [termino_limpio, termino_limpio, termino_limpio] + variantes
    cur = conn.execute(query, params)
    resultados = [dict(row) for row in cur.fetchall()]

    # 2. Si no hay resultados exactos, búsqueda parcial (LIKE)
    if not resultados:
        like_term = f"%{termino_limpio}%"
        query_like = """
            SELECT DISTINCT l.* FROM lipidos l
            LEFT JOIN sinonimos s ON l.id = s.lipido_id
            WHERE l.abreviatura LIKE ?
               OR l.abreviatura_lipidblast LIKE ?
               OR l.nombre_comun LIKE ?
               OR l.nombre_sistematico LIKE ?
               OR s.alias LIKE ?
            LIMIT 10
        """
        cur = conn.execute(query_like, (like_term, like_term, like_term, like_term, like_term))
        resultados = [dict(row) for row in cur.fetchall()]

    if conexion_propia:
        conn.close()

    return resultados


def consultar_api_lipidmaps(abreviacion: str) -> Optional[dict[str, Any]]:
    """Consulta la API pública de LIPID MAPS REST para obtener información oficial."""
    term = abreviacion.strip()
    url = f"https://www.lipidmaps.org/rest/compound/abbrev/{urllib.parse.quote(term)}/all"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Antigravity-LipidDB/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode("utf-8"))
            if isinstance(data, dict) and data:
                primera_clave = sorted(data.keys())[0]
                row = data[primera_clave]
                return {
                    "abreviatura": normalizar_abreviatura(term),
                    "abreviatura_lipidblast": row.get("abbrev", term.replace("(", " ").replace(")", "")),
                    "abreviatura_cadenas": row.get("abbrev_chains", row.get("name")),
                    "nombre_comun": row.get("name"),
                    "nombre_sistematico": row.get("sys_name"),
                    "categoria": row.get("core"),
                    "clase": row.get("main_class"),
                    "subclase": row.get("sub_class"),
                    "formula": row.get("formula"),
                    "masa_exacta": float(row.get("exactmass", 0.0)) if row.get("exactmass") else 0.0,
                    "lipidmaps_id": row.get("lm_id"),
                    "chebi_id": row.get("chebi_id"),
                    "pubchem_cid": row.get("pubchem_cid"),
                    "smiles": row.get("smiles"),
                    "inchi_key": row.get("inchi_key"),
                    "fuentes": "LIPID MAPS (LMSD), LipidBlast, SwissLipids"
                }
    except Exception as e:
        return None
    return None


def exportar_archivos(conn: Optional[sqlite3.Connection] = None):
    """Exporta el contenido de SQLite a CSV y JSON legibles."""
    cerrar = False
    if conn is None:
        conn = sqlite3.connect(DB_FILE)
        cerrar = True
    conn.row_factory = sqlite3.Row

    filas = [dict(r) for r in conn.execute("SELECT * FROM lipidos ORDER BY categoria, clase, abreviatura").fetchall()]

    # Exportar JSON
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(filas, f, indent=2, ensure_ascii=False)

    # Exportar CSV
    if filas:
        campos = [
            "abreviatura", "abreviatura_lipidblast", "abreviatura_cadenas",
            "nombre_comun", "nombre_sistematico", "categoria", "clase", "subclase",
            "formula", "masa_exacta", "lipidmaps_id", "swisslipids_id", "hmdb_id",
            "chebi_id", "pubchem_cid", "fuentes"
        ]
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
            writer.writeheader()
            for fila in filas:
                writer.writerow(fila)

    if cerrar:
        conn.close()


def anotar_archivo_csv(archivo_csv: str | Path, salida_csv: Optional[str | Path] = None) -> list[dict[str, Any]]:
    """
    Identifica columnas de lípidos en un archivo CSV y genera una tabla de anotación de metadatos.
    """
    archivo = Path(archivo_csv)
    if not archivo.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {archivo}")

    with open(archivo, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columnas = reader.fieldnames or []

    # Filtrar columnas identificadas como lípidos
    anotaciones = []
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row

    for col in columnas:
        if col.lower() in ("muestra", "sample", "condicion", "condition", "grupo", "group", "id"):
            continue
        resultados = buscar_lipido(col, conn)
        if resultados:
            anotaciones.append(resultados[0])
        else:
            # Intentar consultar la API si no está en la BD
            datos_api = consultar_api_lipidmaps(col)
            if datos_api:
                insertar_lipido(conn, datos_api)
                anotaciones.append(datos_api)
            else:
                anotaciones.append({
                    "abreviatura": col,
                    "nombre_comun": "No identificado en bases conjuntas",
                    "nombre_sistematico": "-",
                    "formula": "-",
                    "masa_exacta": 0.0,
                    "lipidmaps_id": "-",
                    "swisslipids_id": "-",
                    "hmdb_id": "-",
                })
    conn.close()

    if salida_csv:
        with open(salida_csv, mode="w", newline="", encoding="utf-8") as f:
            campos = ["abreviatura", "abreviatura_lipidblast", "nombre_comun", "nombre_sistematico", "formula", "masa_exacta", "lipidmaps_id", "swisslipids_id", "hmdb_id"]
            writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(anotaciones)

    return anotaciones


def formatear_ficha_lipido(lip: dict[str, Any]) -> str:
    """Genera una ficha legible en texto de un lípido."""
    aductos_dict = {}
    if lip.get("aductos_teoricos"):
        try:
            aductos_dict = json.loads(lip["aductos_teoricos"])
        except Exception:
            pass

    lineas = [
        f"🏷️  Abreviatura Estándar:      {lip.get('abreviatura')}",
        f"🧬 LipidBlast ID/Shorthand:    {lip.get('abreviatura_lipidblast') or '-'}",
        f"🔗 Cadenas / Especie Molecular:{lip.get('abreviatura_cadenas') or '-'}",
        f"📖 Nombre Común:              {lip.get('nombre_comun') or '-'}",
        f"🔬 Nombre Sistemático (IUPAC): {lip.get('nombre_sistematico') or '-'}",
        f"📂 Categoría / Clase:         {lip.get('categoria') or '-'} -> {lip.get('clase') or '-'}",
        f"🧪 Fórmula Molecular:         {lip.get('formula') or '-'}",
        f"⚖️  Masa Exacta Neutra:        {lip.get('masa_exacta') or '-'} Da",
        f"🆔 LIPID MAPS ID:             {lip.get('lipidmaps_id') or '-'}",
        f"🆔 SwissLipids ID:            {lip.get('swisslipids_id') or '-'}",
        f"🆔 HMDB ID:                   {lip.get('hmdb_id') or '-'}",
        f"🆔 ChEBI / PubChem:           {lip.get('chebi_id') or '-'} / {lip.get('pubchem_cid') or '-'}",
        f"🌐 Fuentes Integradas:        {lip.get('fuentes') or '-'}",
    ]
    if aductos_dict:
        lineas.append("⚡ Aductos MS/MS (LipidBlast):")
        for ad, mz in aductos_dict.items():
            lineas.append(f"     • {ad:<10} m/z {mz:.4f}")
    return "\n".join(lineas)


def listar_resumen():
    """Muestra un resumen de las clases y especies presentes en la base de datos."""
    if not DB_FILE.exists():
        print(f"❌ La base de datos no existe aún. Ejecuta 'python3 poblar_base_datos.py'.")
        return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    total = cur.execute("SELECT COUNT(*) FROM lipidos").fetchone()[0]
    sinonimos_totales = cur.execute("SELECT COUNT(*) FROM sinonimos").fetchone()[0]

    print("\n" + "=" * 70)
    print(f"🗄️  {DB_NAME} (Total: {total} especies | {sinonimos_totales} alias/sinónimos)")
    print("=" * 70)

    cur.execute("""
        SELECT categoria, clase, COUNT(*) as cnt
        FROM lipidos
        GROUP BY categoria, clase
        ORDER BY categoria, clase
    """)
    for cat, cla, cnt in cur.fetchall():
        print(f"• {cat} -> {cla}: {cnt} especies")

    print("=" * 70)
    conn.close()


def main():
    if len(sys.argv) < 2:
        print(f"""
=== {DB_NAME} ===
Base de Datos Conjunta de Lípidos (LipidBlast, LIPID MAPS, SwissLipids, HMDB)

Uso: python3 gestor_lipidos.py <comando> [argumentos]

Comandos disponibles:
  buscar <abreviacion_o_id>   Busca un lípido por abreviatura (PC(34:1), PC 34:1, SM d18:1/16:0, etc.) o ID
  anotar <archivo.csv>        Anota las columnas de lípidos de un archivo CSV con nombres completos y metadatos
  listar                      Muestra un resumen de especies y clases registradas en {DB_NAME}
  agregar <abreviacion>       Consulta la API de LIPID MAPS y añade un nuevo lípido a {DB_NAME}
  exportar                    Regenera los archivos {DB_NAME}.csv y {DB_NAME}.json
        """)

        return

    comando = sys.argv[1].lower()

    if comando == "buscar":
        if len(sys.argv) < 3:
            print("❌ Debes especificar un término o abreviatura a buscar. Ejemplo: python3 gestor_lipidos.py buscar 'PC(34:1)'")
            return
        termino = " ".join(sys.argv[2:])
        resultados = buscar_lipido(termino)
        if not resultados:
            print(f"🔍 No se encontró '{termino}' en la base local. Consultando LIPID MAPS en línea...")
            encontrado_api = consultar_api_lipidmaps(termino)
            if encontrado_api:
                conn = sqlite3.connect(DB_FILE)
                insertar_lipido(conn, encontrado_api)
                exportar_archivos(conn)
                conn.close()
                print("✨ Encontrado e incorporado automáticamente a la base interna:\n")
                print(formatear_ficha_lipido(encontrado_api))
            else:
                print(f"❌ No se encontró ningún resultado para '{termino}'.")
        else:
            print(f"\n✅ Se encontraron {len(resultados)} resultado(s) para '{termino}':\n")
            for i, r in enumerate(resultados, 1):
                print(f"--- [Resultado {i}] ---")
                print(formatear_ficha_lipido(r))
                print()

    elif comando == "anotar":
        if len(sys.argv) < 3:
            print("❌ Especifica el archivo CSV. Ejemplo: python3 gestor_lipidos.py anotar datos_lipidomica.csv")
            return
        archivo_in = Path(sys.argv[2])
        archivo_out = archivo_in.with_name(f"{archivo_in.stem}_anotado.csv")
        anotaciones = anotar_archivo_csv(archivo_in, archivo_out)

        print("\n" + "=" * 80)
        print(f"📋 ANOTACIÓN DE LÍPIDOS PARA: {archivo_in.name}")
        print("=" * 80)
        for a in anotaciones:
            abrev = a.get("abreviatura")
            nom = a.get("nombre_comun") or a.get("nombre_sistematico") or "-"
            formula = a.get("formula") or "-"
            masa = a.get("masa_exacta") or 0.0
            lm_id = a.get("lipidmaps_id") or "-"
            hmdb = a.get("hmdb_id") or "-"
            print(f"• {abrev:<10} | {nom[:35]:<35} | {formula:<12} | {masa:>8.4f} Da | LM: {lm_id:<12} | HMDB: {hmdb}")
        print("=" * 80)
        print(f"💾 Archivo de anotación guardado en: {archivo_out.name}\n")

    elif comando == "listar":
        listar_resumen()

    elif comando == "exportar":
        exportar_archivos()
        print("✅ Archivos CSV y JSON actualizados exitosamente.")

    elif comando == "agregar":
        if len(sys.argv) < 3:
            print("❌ Especifica la abreviatura. Ejemplo: python3 gestor_lipidos.py agregar 'PE(34:1)'")
            return
        abrev = " ".join(sys.argv[2:])
        print(f"Consultando información para '{abrev}'...")
        datos = consultar_api_lipidmaps(abrev)
        if datos:
            conn = sqlite3.connect(DB_FILE)
            insertar_lipido(conn, datos)
            exportar_archivos(conn)
            conn.close()
            print("✅ Lípido agregado con éxito:")
            print(formatear_ficha_lipido(datos))
        else:
            print(f"❌ No se pudo encontrar datos para '{abrev}'.")
    else:
        print(f"Comando desconocido: '{comando}'")


if __name__ == "__main__":
    main()

