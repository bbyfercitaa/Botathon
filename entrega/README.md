# Entrega Blue Prism — Ingesta NAC

Paquete portable de los procesos de ingesta de los dos Excel de dotación/planificación.

## Contenido

| Archivo | Qué es |
|---|---|
| `01_MS_Excel_VBO.xml` | Objeto `MS Excel VBO` **corregido**: lee valores reales (no texto mostrado) y escribe fechas como `yyyy-MM-dd`. |
| `02_Ingesta_BaseContratos.xml` | Proceso que lee `Dotacion_2026` y genera `base_contratos.xlsx`. |
| `03_Ingesta_Planificacion.xml` | Proceso que lee `Dotacion_Asistencial`, `Excepciones` y `LOP`, y genera tres XLSX. |
| `importar.ps1` | Importa y publica los tres elementos con AutomateC. |
| `convertir_a_csv.py` | Convierte los XLSX a CSV UTF-8 para el frontend. |
| `generar_csv_desde_fuente.py` | Respaldo: genera los CSV correctos directamente desde los Excel originales (fechas preservadas). |
| `PROCESOS_NAC.md` | Detalle técnico y limitaciones. |

## Requisitos en el PC destino

- Blue Prism 7.x con `AutomateC.exe`.
- **Microsoft Excel instalado** (el VBO usa COM).
- Un Resource PC disponible.
- Los dos Excel de origen en una ruta local.

## 1. Importar

```powershell
cd .\entrega
.\importar.ps1 -User "tu_usuario" -Password "tu_clave"
```

Opcional: `-DbConName "NombreConexion"` y `-AutomateC "ruta\AutomateC.exe"`.

El script importa en orden:

1. `MS Excel VBO` (con `/overwrite`).
2. `Ingesta_BaseContratos`.
3. `Ingesta_Planificacion`.

Luego publica los dos procesos.

> Si en el PC destino ya existe un objeto llamado `MS Excel VBO` distinto, el import puede pedir resolución. **Usa el VBO incluido**: es el que corrige las fechas.

## 2. Ajustar rutas

Los procesos traen rutas absolutas de ejemplo. Después de importar, edítalas en **Process Studio → Data Items**:

### `Ingesta_BaseContratos`

| Data Item | Valor esperado |
|---|---|
| `vRuta` | Ruta al `Nac - Base contratos x mes.xlsx` |
| `vSalida` | Ruta al `base_contratos.xlsx` de salida |

### `Ingesta_Planificacion`

| Data Item | Valor esperado |
|---|---|
| `vRuta` | Ruta al `Nac - Planificación Asistencial x mes.xlsx` |
| `vSalida1` | `dotacion_asistencial.xlsx` |
| `vSalida2` | `excepciones.xlsx` |
| `vSalida3` | `lop.xlsx` |

Los rangos ya vienen configurados:

- Base: `A2:S3125`
- Plan: `A4:GW475`, `A2:X19`, `A1:C17`

## 3. Ejecutar

Con un Resource PC activo, desde Control Room o por consola:

```powershell
AutomateC.exe /run "Ingesta_BaseContratos" /resource "NOMBRE_RECURSO" /user USUARIO CLAVE
AutomateC.exe /run "Ingesta_Planificacion" /resource "NOMBRE_RECURSO" /user USUARIO CLAVE
```

Tiempos de referencia:

- Base: ~2,5 minutos.
- Planificación: ~14 minutos (205 columnas).

## 4. Convertir a CSV

```powershell
python convertir_a_csv.py
```

Genera `base_contratos.csv`, `dotacion_asistencial.csv`, `excepciones.csv` y `lop.csv` en UTF-8 con BOM.

## 5. Respaldo si el Plan falla

`Ingesta_Planificacion` es pesado (471 × 205 celdas). En equipos con poca memoria puede fallar en `Write Collection` con un error RPC de Excel.

En ese caso:

```powershell
python generar_csv_desde_fuente.py
```

Lee los Excel originales con pandas/openpyxl (fechas reales) y deja los CSV correctos en `Frontend/data`.

## Limitaciones

- El VBO es una versión antigua del `MS Excel VBO`; funciona por COM y requiere Excel.
- La salida de Blue Prism es XLSX (el VBO no guarda CSV de forma confiable).
- El proceso de planificación es intensivo; si el PC destino tiene poca RAM, usa el respaldo Python.
- Las fechas ya no se corrompen con el VBO incluido (verificado en Base: 3.123/3.123).

## Verificación

- `Ingesta_BaseContratos` ejecutado con el VBO corregido: 3.123 filas × 19 columnas, fechas 100 % correctas.
- `Ingesta_Planificacion` queda incluido; validar en el PC destino por su volumen.
