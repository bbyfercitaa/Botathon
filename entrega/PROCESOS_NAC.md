# Procesos de ingesta NAC en Blue Prism

Estado: **procesos creados y publicados**, con un `MS Excel VBO` corregido para leer **valores reales** (no texto mostrado).

---

## 1. Procesos

| Proceso | Archivo fuente | Salida |
|---|---|---|
| `Ingesta_BaseContratos` | `Nac - Base contratos x mes.xlsx` | `base_contratos.xlsx` |
| `Ingesta_Planificacion` | `Nac - Planificación Asistencial x mes.xlsx` | `dotacion_asistencial.xlsx`, `excepciones.xlsx`, `lop.xlsx` |

Rangos configurados:

- Base: `A2:S3125` (3.123 filas × 19 columnas).
- Plan: `A4:GW475` (471 × 205), `A2:X19` (17 × 24), `A1:C17` (16 × 3).

---

## 2. Corrección del VBO

El `MS Excel VBO` original leía el **texto mostrado** de Excel y lo reescribía, lo que corrompía las fechas.

Se reemplazó el código de `Get Worksheet Range As Collection` para leer `Range.Value` (valores reales) y convertir:

- Fechas → `yyyy-MM-dd`
- Números → representación invariante
- Texto → tal cual

Resultado verificado en Base contratos:

| Columna | Correctas |
|---|---|
| `Periodo` | **3.123 / 3.123** |
| `Fecha de Nacimiento` | **3.123 / 3.123** |
| `Fecha Ingreso Compañía` | **3.123 / 3.123** |

En Planificación, con el generador de respaldo: `Fecha Inicio Contrato` 471/471 y `Fecha Nacimiento` 471/471.

---

## 3. Cómo ejecutar

1. Importar `01_MS_Excel_VBO.xml`, `02_Ingesta_BaseContratos.xml` y `03_Ingesta_Planificacion.xml` con `importar.ps1`.
2. Ajustar las rutas en los Data Items (`vRuta`, `vSalida`, `vSalida1..3`).
3. Con un Resource PC activo:

```powershell
AutomateC.exe /run "Ingesta_BaseContratos" /resource "RECURSO" /user USUARIO CLAVE
AutomateC.exe /run "Ingesta_Planificacion" /resource "RECURSO" /user USUARIO CLAVE
```

Tiempos de referencia: Base ~2,5 min; Planificación ~14 min.

---

## 4. Conversión a CSV

Los procesos dejan XLSX. Para el frontend:

```powershell
python convertir_a_csv.py
```

Si el proceso de Planificación falla por volumen (205 columnas), usar el respaldo:

```powershell
python generar_csv_desde_fuente.py
```

Este lee los Excel originales con pandas/openpyxl y deja los cuatro CSV con fechas correctas.

---

## 5. Limitaciones

1. **Planificación es pesado.** 471 × 205 celdas; en equipos con poca memoria puede fallar en `Write Collection` con un error RPC de Excel. Usar el respaldo Python o un equipo con más RAM.
2. **Salida XLSX.** El VBO no guarda CSV de forma confiable; por eso el conversor.
3. **Requiere Excel instalado** en el Resource PC (COM).
4. **Rutas absolutas.** Hay que ajustarlas en cada PC destino.
5. **Objeto `Util - Excel a CSV`** quedó como intento fallido en el entorno de origen; no se usa.

---

## 6. Verificación

- `Ingesta_BaseContratos` ejecutado con el VBO corregido: **completado**, 3.123 × 19, fechas 100 % correctas.
- `Ingesta_Planificacion`: lógica equivalente; validar en el PC destino por su volumen.
- CSVs de respaldo generados y verificados: 3.123 × 19, 471 × 205, 17 × 24, 16 × 3.
