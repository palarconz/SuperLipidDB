# Auditoría y Diagnóstico de la Base de Datos de Lípidos (`SuperLipidDB_PA`)

## 1. Resumen Ejecutivo

Se realizó una revisión integral de la base de datos de lípidos, compuesta por:
- Base de datos relacional: [`SuperLipidDB_PA.sqlite`](file:///Users/pedrofelipe/proyectos/antigravity-test/SuperLipidDB_PA.sqlite)
- Exportaciones tabulares: [`SuperLipidDB_PA.csv`](file:///Users/pedrofelipe/proyectos/antigravity-test/SuperLipidDB_PA.csv) y [`SuperLipidDB_PA.json`](file:///Users/pedrofelipe/proyectos/antigravity-test/SuperLipidDB_PA.json)
- Scripts de gestión y población: [`gestor_lipidos.py`](file:///Users/pedrofelipe/proyectos/antigravity-test/gestor_lipidos.py) y [`poblar_base_datos.py`](file:///Users/pedrofelipe/proyectos/antigravity-test/poblar_base_datos.py)
- Datos experimentales asociados: [`datos_lipidomica.csv`](file:///Users/pedrofelipe/proyectos/antigravity-test/datos_lipidomica.csv) y [`datos_lipidomica_anotado.csv`](file:///Users/pedrofelipe/proyectos/antigravity-test/datos_lipidomica_anotado.csv)

### Estado General
- **Total de registros principales (`lipidos`)**: 66 especies y clases lipídicas integradas.
- **Total de alias/sinónimos (`sinonimos`)**: 713 registros en base de datos (de los cuales solo **316 son únicos**).
- **Integridad referencial**: Sin claves foráneas huérfanas (`PRAGMA foreign_key_check` limpio).
- **Sincronización multi-formato**: SQLite, CSV y JSON contienen exactamente los mismos 66 registros principales.

---

## 2. Hallazgos Críticos Detectados

### ⚠️ A. Discrepancias Químicas en Fórmulas Moleculares y Masas Exactas (5 especies)
Al contrastar las fórmulas químicas con sus masas monoisotópicas neutras reales (calculadas con masas atómicas monoisotópicas IUPAC y validadas contra la API de LIPID MAPS), se identificaron discrepancias en **5 especies**:

| Lípido | Parámetro | Valor Actual en BD | Valor Químico Real (LIPID MAPS) | Diagnóstico del Error |
| :--- | :--- | :--- | :--- | :--- |
| **`PC(36:4)`** | Fórmula<br>Masa Exacta | `C44H78NO8P`<br>`781.5465` Da | **`C44H80NO8P`**<br>**`781.5622`** Da | Faltan 2 hidrógenos en la fórmula (16:0/20:4 posee 4 insaturaciones = 80 H). La masa estaba desfasada en ~0.0156 Da. |
| **`PC(38:4)`** | Fórmula<br>Masa Exacta | `C46H82NO8P`<br>`809.5778` Da | **`C46H84NO8P`**<br>**`809.5935`** Da | Faltan 2 hidrógenos (18:0/20:4 posee 4 insaturaciones = 84 H). **Afecta a [`datos_lipidomica_anotado.csv`](file:///Users/pedrofelipe/proyectos/antigravity-test/datos_lipidomica_anotado.csv)**. |
| **`PC(38:5)`** | Fórmula<br>Masa Exacta | `C46H80NO8P`<br>`807.5622` Da | **`C46H82NO8P`**<br>**`807.5778`** Da | Faltan 2 hidrógenos (18:0/20:5 posee 5 insaturaciones = 82 H). |
| **`PC(38:6)`** | Fórmula<br>Masa Exacta | `C46H78NO8P`<br>`805.5465` Da | **`C46H80NO8P`**<br>**`805.5622`** Da | Faltan 2 hidrógenos (16:0/22:6 posee 6 insaturaciones = 80 H). |
| **`PS(36:1)`** | Fórmula<br>Masa Exacta | `C42H82NO10P`<br>`789.5520` Da | **`C42H80NO10P`**<br>`789.5520` Da | La masa en BD era correcta, pero la fórmula tenía 2 hidrógenos sobrantes (debe ser H80 para 18:0/18:1). |

---

### ⚠️ B. Duplicación Masiva en la Tabla `sinonimos` (397 registros redundantes)
- **Problema**: La tabla `sinonimos` posee 713 registros para representar 316 alias únicos. Hay sinónimos triplicados y cuadruplicados (ej. `LPC 16:0` aparece 4 veces para el id 11).
- **Causa en el código**: En [`gestor_lipidos.py`](file:///Users/pedrofelipe/proyectos/antigravity-test/gestor_lipidos.py#L89-L96), la tabla fue definida sin restricción de unicidad:
  ```sql
  CREATE TABLE IF NOT EXISTS sinonimos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      lipido_id INTEGER NOT NULL,
      alias TEXT NOT NULL,
      tipo TEXT,
      FOREIGN KEY (lipido_id) REFERENCES lipidos (id) ON DELETE CASCADE
  );
  ```
  La sentencia `INSERT OR IGNORE INTO sinonimos (lipido_id, alias, tipo)` no previene duplicados porque SQLite requiere un índice o constraint `UNIQUE(lipido_id, alias)` para activar la cláusula `IGNORE`. Cada ejecución de [`poblar_base_datos.py`](file:///Users/pedrofelipe/proyectos/antigravity-test/poblar_base_datos.py) reinserta los sinónimos sin deduplicarlos.

---

### ⚠️ C. Inconsistencias Taxonómicas (Categorías y Clases LIPID MAPS)
1. **Discrepancia en FA01 (Fatty Acyls)**:
   - `FA(16:0)`, `FA(18:1)`, `FA(20:4)`, `FA(22:6)` utilizan: `Fatty Acids and Conjugates [FA01]`
   - `CAR` (Acilcarnitinas) utiliza: `Fatty acid conjugates [FA01]`
   - *Efecto*: Las agrupaciones (`GROUP BY categoria, clase`) parten FA01 en dos grupos distintos por diferencia de mayúsculas ("Acids" vs "acid").
2. **Discrepancia en Subclases de Diacilgliceroles**:
   - `DG(34:1)` y `DG(36:2)` usan: `Diacylglycerols [GL0201]`
   - `DG` (genérico) usa: `1,2-Diacylglycerols [GL0201]`

---

### ⚠️ D. Coexistencia de Especies Moleculares y Clases Abstractas
La tabla `lipidos` combina dos niveles ontológicos sin diferenciación explícita:
- **38 especies moleculares concretas**: Tienen masa exacta, aductos, fórmula, SMILES e InChIKey completos.
- **28 clases y subclases genéricas** (`PC`, `PE`, `SM`, `TG`, `CAR`, `NAE`, `BA`, etc.):
  - Poseen `masa_exacta = 0.0`.
  - Poseen `aductos_teoricos = NULL` (porque [`gestor_lipidos.py`](file:///Users/pedrofelipe/proyectos/antigravity-test/gestor_lipidos.py#L109) condiciona el cálculo a `masa > 0`).
  - Poseen `formula = 'Variable (...)'`.
  - Poseen `smiles = NULL` e `inchi_key = NULL`.

> [!NOTE]
> Aunque es común en bases de lípidos dar soporte a clases generales (para búsquedas como `"PC"` o `"DG"`), no disponer de una columna `tipo_registro` (`'especie'` vs `'clase'`) dificulta consultas cuantitativas donde se asume que todo registro tiene masa monoisotópica válida.

---

### ⚠️ E. Falta de Índice en Clave Foránea (`sinonimos.lipido_id`)
Actualmente existe un índice en `sinonimos(alias COLLATE NOCASE)` y en campos de `lipidos`, pero **no** en `sinonimos(lipido_id)`.
- Esto impacta negativamente el rendimiento de las consultas `LEFT JOIN` en [`gestor_lipidos.py`](file:///Users/pedrofelipe/proyectos/antigravity-test/gestor_lipidos.py#L201-L210) y las eliminaciones en cascada.

---

## 3. Comportamiento Espectrométrico de Aductos Teóricos

La función [`calcular_aductos`](file:///Users/pedrofelipe/proyectos/antigravity-test/gestor_lipidos.py#L47-L56) asigna los mismos 5 aductos teóricos de forma universal:
`[M+H]+`, `[M+Na]+`, `[M+NH4]+`, `[M-H]-`, `[M+HCOO]-`.

En espectrometría de masas (ESI-MS/MS):
- **PC y SM**: Se detectan como `[M+H]+` en modo positivo, pero en modo negativo casi **nunca** forman `[M-H]-` estable (requieren aductos de acetato o formiato `[M+HCOO]-`).
- **TG y CE**: Son moléculas neutras apolares. No ionizan en modo negativo y en modo positivo forman predominantemente aductos de amonio `[M+NH4]+` y sodio `[M+Na]+`, rara vez `[M+H]+`.
- **FA (Ácidos grasos)**: Ionizan prácticamente en exclusiva en modo negativo como `[M-H]-`.

---

## 4. Plan de Acción Recomendado

1. **Corregir [`poblar_base_datos.py`](file:///Users/pedrofelipe/proyectos/antigravity-test/poblar_base_datos.py)**:
   - Corregir fórmulas y masas de `PC(36:4)`, `PC(38:4)`, `PC(38:5)`, `PC(38:6)` y `PS(36:1)`.
   - Estandarizar la clase de `CAR` a `Fatty Acids and Conjugates [FA01]`.
   - Estandarizar la subclase de `DG` a `1,2-Diacylglycerols [GL0201]`.
2. **Mejorar el Esquema en [`gestor_lipidos.py`](file:///Users/pedrofelipe/proyectos/antigravity-test/gestor_lipidos.py)**:
   - Añadir `UNIQUE(lipido_id, alias)` en la tabla `sinonimos`.
   - Añadir `CREATE INDEX IF NOT EXISTS idx_sinonimos_lipido_id ON sinonimos(lipido_id);`.
   - Opcionalmente añadir columna `tipo_entidad` (`'especie'` / `'clase'`).
3. **Regenerar la Base y Archivos Derivados**:
   - Limpiar y repoblar [`SuperLipidDB_PA.sqlite`](file:///Users/pedrofelipe/proyectos/antigravity-test/SuperLipidDB_PA.sqlite).
   - Reexportar [`SuperLipidDB_PA.csv`](file:///Users/pedrofelipe/proyectos/antigravity-test/SuperLipidDB_PA.csv) y [`SuperLipidDB_PA.json`](file:///Users/pedrofelipe/proyectos/antigravity-test/SuperLipidDB_PA.json).
   - Reanotar [`datos_lipidomica_anotado.csv`](file:///Users/pedrofelipe/proyectos/antigravity-test/datos_lipidomica_anotado.csv) para que `PC(38:4)` quede con masa `809.5935 Da` y fórmula `C46H84NO8P`.
