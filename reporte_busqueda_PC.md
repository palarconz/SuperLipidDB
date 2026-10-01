# Reporte de Búsqueda: Fosfatidilcolinas (`PC`) en `SuperLipidDB_PA`

## 1. Resumen de la Búsqueda

- **Término consultado**: `PC`
- **Base de datos consultada**: [`SuperLipidDB_PA.sqlite`](file:///Users/pedrofelipe/proyectos/antigravity-test/SuperLipidDB_PA.sqlite)
- **Coincidencia directa exacta**: Clase **`PC`** (Fosfatidilcolinas / Phosphatidylcholines, ID LMSD: `GP0101`).
- **Total de registros de la familia GP01 (`Glycerophosphocholines`)**: **16 registros**:
  - **10 especies moleculares intactas (Diacil-PC)**: `PC(32:0)`, `PC(34:1)`, `PC(34:2)`, `PC(36:1)`, `PC(36:2)`, `PC(36:4)`, `PC(38:4)`, `PC(38:5)`, `PC(38:6)`, `PC(40:6)`.
  - **3 especies liso-fosfatidilcolinas (LPC)**: `LPC(16:0)`, `LPC(18:0)`, `LPC(18:1)`.
  - **3 clases y subclases generales**: `PC` (diacil), `LPC` (monoacil), `LPC O-` (alquil).

---

## 2. Ficha Técnica de la Clase Principal (`PC`)

| Campo | Detalle en Base de Datos |
| :--- | :--- |
| **Abreviatura Estándar** | `PC` |
| **Abreviatura Shorthand (LipidBlast)** | `PC` |
| **Estructura / Cadenas** | `1,2-diacyl-sn-glycero-3-phosphocholine` |
| **Nombre Común** | Fosfatidilcolinas (Phosphatidylcholines / Lecitinas) |
| **Nombre Sistemático** | 1,2-diacyl-sn-glycero-3-phosphocholine |
| **Categoría LMSD** | `Glycerophospholipids [GP]` |
| **Clase LMSD** | `Glycerophosphocholines [GP01]` |
| **Subclase LMSD** | `Diacylglycerophosphocholines [GP0101]` |
| **Fórmula General** | Variable (`CnH2n-2xNO8P`) |
| **LIPID MAPS ID** | `GP0101` |
| **SwissLipids ID** | `SLM:PC` |
| **HMDB ID** | `HMDB0007873` |
| **Sinónimos Registrados** | `Lecithin`, `Phosphatidylcholine`, `Fosfatidilcolina`, `1,2-diacyl-sn-glycero-3-phosphocholine` |

---

## 3. Inventario de Especies de Fosfatidilcolina en `SuperLipidDB_PA`

A continuación se detalla la caracterización química y espectrométrica de las 13 especies moleculares concretas:

### A. Especies Diacil-PC (Intactas)

| Abreviatura | Especie Molecular | Nombre Común | Fórmula | Masa Neutra (Da) | Ad. [M+H]⁺ | Ad. [M+Na]⁺ | Ad. [M+HCOO]⁻ |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **`PC(32:0)`** | PC 16:0/16:0 | DPPC (Dipalmitoil) | C₄₀H₈₀NO₈P | 733.5622 | 734.5695 | 756.5514 | 778.5604 |
| **`PC(34:2)`** | PC 16:0/18:2 | PLPC (Palmitoil-linoleoil) | C₄₂H₈₀NO₈P | 757.5622 | 758.5695 | 780.5514 | 802.5604 |
| **`PC(34:1)`** | PC 16:0/18:1 | POPC (Palmitoil-oleoil) | C₄₂H₈₂NO₈P | 759.5778 | 760.5851 | 782.5670 | 804.5760 |
| **`PC(36:4)`** | PC 16:0/20:4 | PAPC (Palmitoil-araquidonoil) | C₄₄H₇₈NO₈P | 781.5465 | 782.5538 | 804.5357 | 826.5447 |
| **`PC(36:2)`** | PC 18:1/18:1 | DOPC (Dioleoil) | C₄₄H₈₄NO₈P | 785.5935 | 786.6008 | 808.5827 | 830.5917 |
| **`PC(36:1)`** | PC 18:0/18:1 | SOPC (Estearoil-oleoil) | C₄₄H₈₆NO₈P | 787.6091 | 788.6164 | 810.5983 | 832.6073 |
| **`PC(38:6)`** | PC 16:0/22:6 | PDPC (Palmitoil-docosahexaenoil) | C₄₆H₇₈NO₈P | 805.5465 | 806.5538 | 828.5357 | 850.5447 |
| **`PC(38:5)`** | PC 18:0/20:5 | Estearoil-eicosapentaenoil | C₄₆H₈₀NO₈P | 807.5622 | 808.5695 | 830.5514 | 852.5604 |
| **`PC(38:4)`** | PC 18:0/20:4 | SAPC (Estearoil-araquidonoil) | C₄₆H₈₂NO₈P | 809.5778 | 810.5851 | 832.5670 | 854.5760 |
| **`PC(40:6)`** | PC 18:0/22:6 | SDPC (Estearoil-docosahexaenoil) | C₄₈H₈₄NO₈P | 833.5935 | 834.6008 | 856.5827 | 878.5917 |

### B. Especies Liso-Fosfatidilcolina (LPC)

| Abreviatura | Especie Molecular | Nombre Común | Fórmula | Masa Neutra (Da) | Ad. [M+H]⁺ | Ad. [M+Na]⁺ | Ad. [M+HCOO]⁻ |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **`LPC(16:0)`** | LPC 16:0 | 1-palmitoil-sn-glicero-3-fosfocolina | C₂₄H₅₀NO₇P | 495.3325 | 496.3398 | 518.3217 | 540.3307 |
| **`LPC(18:1)`** | LPC 18:1(9Z) | 1-oleoil-sn-glicero-3-fosfocolina | C₂₆H₅₂NO₇P | 521.3481 | 522.3554 | 544.3373 | 566.3463 |
| **`LPC(18:0)`** | LPC 18:0 | 1-estearoil-sn-glicero-3-fosfocolina | C₂₆H₅₄NO₇P | 523.3638 | 524.3711 | 546.3530 | 568.3620 |

---

## 4. Identificadores Cruzados en Repositorios Internacionales

| Especie | LIPID MAPS ID | SwissLipids ID | HMDB ID | ChEBI ID | PubChem CID |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`PC(32:0)`** | `LMGP01010002` | `SLM:000000557` | `HMDB0000564` | `CHEBI:16127` | `443015` |
| **`PC(34:1)`** | `LMGP01010001` | `SLM:000000571` | `HMDB0007873` | `CHEBI:72986` | `52922943` |
| **`PC(34:2)`** | `LMGP01010005` | `SLM:000000572` | `HMDB0007874` | `CHEBI:73010` | `52922944` |
| **`PC(36:1)`** | `LMGP01010006` | `SLM:000000589` | `HMDB0007886` | `CHEBI:73024` | `52922949` |
| **`PC(36:2)`** | `LMGP01010003` | `SLM:000000590` | `HMDB0000574` | `CHEBI:73026` | `52922950` |
| **`PC(36:4)`** | `LMGP01010008` | `SLM:000000592` | `HMDB0007888` | `CHEBI:73030` | `52922952` |
| **`PC(38:4)`** | `LMGP01010010` | `SLM:000000609` | `HMDB0007901` | `CHEBI:73041` | `52922956` |
| **`PC(38:5)`** | `LMGP01010011` | `SLM:000000610` | `HMDB0007902` | `CHEBI:73042` | `52922957` |
| **`PC(38:6)`** | `LMGP01010012` | `SLM:000000611` | `HMDB0007903` | `CHEBI:73043` | `52922958` |
| **`PC(40:6)`** | `LMGP01010821` | `SLM:000000628` | `HMDB0007917` | `CHEBI:73049` | `52922960` |
| **`LPC(16:0)`**| `LMGP01050001` | `SLM:000001001` | `HMDB0010382` | `CHEBI:34159` | `46173873` |
| **`LPC(18:0)`**| `LMGP01050002` | `SLM:000001012` | `HMDB0010384` | `CHEBI:34160` | `46173875` |
| **`LPC(18:1)`**| `LMGP01050003` | `SLM:000001013` | `HMDB0010385` | `CHEBI:34161` | `46173876` |

---

## 5. Correlación con el Dataset Experimental (`datos_lipidomica.csv`)

Todas las variables cuantificadas en el ensayo experimental [`datos_lipidomica.csv`](file:///Users/pedrofelipe/proyectos/antigravity-test/datos_lipidomica.csv) corresponden a especies de esta familia:

| Lípido Experimental | Media Control | Media Tratamiento | Variación (Tratamiento vs Control) | Tendencia Biológica |
| :--- | :---: | :---: | :---: | :--- |
| **`PC(32:0)`** | 144.49 | 165.94 | +14.8% | Inducción moderada |
| **`PC(34:1)`** | 320.00 | 290.75 | -9.1% | Disminución leve |
| **`PC(36:2)`** | 206.90 | 270.19 | +30.6% | **Inducción significativa** |
| **`PC(38:4)`** | 87.11 | 124.54 | +43.0% | **Fuerte incremento** |
| **`PC(40:6)`** | 40.45 | 30.41 | -24.8% | **Disminución marcada** |
