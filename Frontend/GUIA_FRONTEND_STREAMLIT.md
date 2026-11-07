# Guía: crear el frontend del MVP con Streamlit

> Documento de trabajo para el equipo. Describe los pasos generales, sin entrar en el detalle de implementación de cada uno.
> Para leerlo en VS Code: clic derecho sobre el archivo → **Open Preview** (o `Ctrl+Shift+V`).

---

## 0. Objetivo

Construir un dashboard que permita al equipo de planificación central:

- Ver el consolidado nacional de la planificación asistencial.
- Filtrar por instituto, área/especialidad, cargo, tipo de atención, mes y profesional.
- Revisar los indicadores **Meta de Gestión al 90%** y **% FOJA**.
- Consultar el estado de la ingesta (qué archivo procesó Blue Prism, qué errores detectó).
- Demostrar en vivo que un nuevo reporte de BUK cambia la planificación.

**Principio de diseño:** Streamlit es solo la capa visual. No debe contener la lógica de negocio ni depender de que Blue Prism esté corriendo para mostrar datos.

---

## 1. Prerrequisitos

- [ ] Python 3.10 o superior instalado (en la VM hay 3.13).
- [ ] `pip` funcionando.
- [ ] VS Code con las extensiones:
  - **Python** (Microsoft).
  - Opcional: **Markdown All in One** para leer esta guía.
- [ ] Acceso a la VM o al equipo donde correrá el dashboard.
- [ ] Definido con el equipo de backend/bot **dónde se guardan los resultados** (idealmente SQLite u otra base de datos).

---

## 2. Preparar el entorno del proyecto

1. Abrir una terminal en la carpeta `Botathon/Frontend`.
2. Crear un entorno virtual:
   ```bash
   python -m venv .venv
   ```
3. Activarlo en Windows:
   ```bash
   .venv\Scripts\activate
   ```
4. Verificar que el prompt muestre `(.venv)`.
5. Crear el archivo `.gitignore` si se usará Git (incluir `.venv/`, `__pycache__/`, `*.db`, `.streamlit/secrets.toml`).

> Regla: todas las instalaciones se hacen con el entorno virtual activo.

---

## 3. Instalar dependencias

Instalar solo lo necesario para el MVP:

```bash
pip install streamlit pandas openpyxl plotly
```

- `streamlit`: la app.
- `pandas`: lectura y transformación de datos.
- `openpyxl`: leer archivos `.xlsx` (BUK/SIC) si el frontend los necesita directamente.
- `plotly`: gráficos interactivos.

Congelar versiones:

```bash
pip freeze > requirements.txt
```

Dependencias opcionales según el diseño:

| Necesidad | Paquete |
|---|---|
| Base de datos SQLite | `sqlalchemy` o el módulo `sqlite3` incluido |
| Base de datos PostgreSQL | `psycopg2-binary` |
| Formato y fechas | `python-dateutil` |
| Variables de entorno | `python-dotenv` |

---

## 4. Definir la fuente de datos

Antes de programar pantallas, acordar el **contrato de datos** con quien construye el backend/bot.

Opción recomendada para el MVP: **SQLite** (un archivo, sin servidor).

Tablas mínimas sugeridas (ajustar según el modelo real):

| Tabla | Contenido |
|---|---|
| `profesionales` | ID, instituto, cargo, área, tipo de contrato, estado |
| `planificacion` | Profesional, mes, horas contratadas, horas directas/indirectas/NAS, atenciones, meta |
| `parametros` | % por cargo y tramo, minutos estándar, asignaciones, calendario |
| `ejecuciones` | Archivo procesado, fecha, usuario, estado, versión |
| `errores_ingesta` | Archivo, fila, campo, descripción del error |

Reglas:

- El dashboard **lee**, no calcula la planificación.
- Si algún cálculo es solo de presentación (ej. % FOJA), puede hacerse en la consulta o con pandas.
- Los datos que muestra el dashboard deben quedar versionados para poder comparar.

---

## 5. Estructura de carpetas propuesta

```text
Frontend/
├── app.py                  # Punto de entrada
├── pages/                  # Vistas adicionales (opcional)
│   ├── 1_Resumen_Nacional.py
│   ├── 2_Por_Instituto.py
│   └── 3_Ingesta_y_Errores.py
├── components/             # Funciones reutilizables de UI
│   ├── filtros.py
│   ├── tarjetas.py
│   └── tablas.py
├── data/                   # Acceso a datos (consultas)
│   └── repo.py
├── utils/                  # Formato, cálculos de presentación
│   └── formato.py
├── assets/                 # Logos, íconos
├── .streamlit/
│   └── config.toml         # Tema y configuración
├── requirements.txt
└── README.md
```

> No es obligatorio usar `pages/`; si el MVP es una sola pantalla con pestañas, basta con `app.py` y módulos auxiliares.

---

## 6. Configurar Streamlit

Crear `.streamlit/config.toml` con lo básico:

```toml
[server]
headless = true
port = 8501

[theme]
base = "light"
primaryColor = "#0B2A5B"
```

- `headless = true` evita que intente abrir un navegador en la VM.
- El tema puede ajustarse luego a la identidad visual de Teletón.

Arrancar la app:

```bash
streamlit run app.py
```

---

## 7. Construir el layout

Orden recomendado de trabajo:

1. **Encabezado**: título, período seleccionado y fecha de última actualización.
2. **Barra lateral de filtros**:
   - Instituto (incluir “Nacional”).
   - Área o especialidad.
   - Cargo.
   - Tipo de atención (directa, indirecta, NAS, grupal).
   - Mes o rango de meses.
   - Profesional (solo cuando ya hay un instituto seleccionado).
3. **Tarjetas de indicadores (KPIs)**:
   - Total atenciones planificadas.
   - Meta de Gestión al 90%.
   - % FOJA.
   - Horas semanales totales.
   - N° de profesionales.
4. **Gráficos**:
   - Barras por instituto.
   - Comparación directa / indirecta / NAS.
   - Evolución mensual.
5. **Tabla detallada**:
   - Una fila por profesional o por instituto, según el nivel de filtro.
   - Columnas: instituto, cargo, horas, atenciones, meta, FOJA.
6. **Pestañas o páginas** para separar resumen, detalle e ingesta.

---

## 8. Filtros y estado

- Usar `st.sidebar` para los filtros.
- Los filtros deben ser **en cascada**: al elegir instituto, se reducen las opciones de área, cargo y profesional.
- Guardar selecciones en `st.session_state` para que no se pierdan al recargar.
- Definir un botón **“Limpiar filtros”**.
- Mostrar siempre el contexto activo: “Viendo: Nacional · Todos los institutos · Mayo 2026”.

---

## 9. Indicadores del documento

Implementar como mínimo:

| Indicador | Fórmula |
|---|---|
| Meta de Gestión Asistencial | Atenciones planificadas × 90% |
| % FOJA | Horas mensuales disponibles para atención directa ÷ Horas mensuales contratadas |

Otros útiles:

- Horas directas / indirectas / NAS por instituto.
- Atenciones individuales vs. grupales.
- Cumplimiento real (SIC) vs. planificado, si los datos están disponibles.
- Desviación porcentual y alertas.

> El porcentaje de meta (90%) debe ser un parámetro, no un número fijo en el código.

---

## 10. Tablas y detalle

- Usar `st.dataframe` para tablas ordenables y filtrables.
- Formatear números con separador de miles y horas con dos decimales.
- Permitir **drill-down**: Nacional → Instituto → Área → Profesional.
- Agregar descarga a CSV con `st.download_button` (útil para jefaturas).
- Si la tabla es muy grande, paginar o limitar filas.

---

## 11. Panel de ingesta y estado de Blue Prism

Una sección separada (pestaña o página) que muestre:

- Último archivo procesado y fecha/hora.
- Estado: exitoso, con errores, en proceso.
- N° de registros leídos, creados, modificados y rechazados.
- Lista de errores de validación con fila y motivo.
- Versión de la planificación generada.
- Opcional: estado de la sesión de Blue Prism (`session_status`) y últimos logs.

Reglas:

- El dashboard **no debe depender** de Blue Prism para mostrar la planificación.
- La consulta a Blue Prism es solo para monitoreo.
- Si se agrega un botón para ejecutar el bot, debe quedar claro que requiere permisos y un Resource PC disponible.

---

## 12. Rendimiento

- Usar `@st.cache_data` en las consultas de lectura.
- Evitar recalcular todo en cada interacción.
- Hacer las agregaciones en SQL cuando sea posible.
- No cargar tablas completas si solo se muestran totales.
- Probar con un volumen similar al real (600+ profesionales).

---

## 13. Validación

- [ ] Los totales del dashboard coinciden con el Excel de referencia.
- [ ] Los filtros no alteran los totales nacionales.
- [ ] La meta al 90% se recalcula al cambiar el parámetro.
- [ ] El % FOJA coincide con la definición del documento.
- [ ] Los meses de enero–abril usan 44 h y mayo–diciembre 42 h.
- [ ] Los errores de ingesta se muestran sin romper la app.
- [ ] La app funciona sin conexión a internet.

---

## 14. Ejecución en la VM

1. Activar el entorno virtual.
2. Ejecutar:
   ```bash
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```
3. Dentro de la VM: abrir `http://localhost:8501`.
4. Desde otro equipo: abrir `http://IP_DE_LA_VM:8501` y permitir el puerto 8501 en el firewall de Windows.
5. Si la VM está detrás de NAT, configurar redirección de puertos.

Notas:

- `--server.address 0.0.0.0` expone la app a la red; no usarlo sin control de acceso.
- Para la demo, preferir `localhost` salvo que el jurado necesite conectarse.
- Tener un `.bat` que active el entorno y levante la app:
  ```bat
  @echo off
  cd /d "%~dp0"
  call .venv\Scripts\activate
  streamlit run app.py
  pause
  ```

---

## 15. Seguridad y datos personales

- Mostrar el **mínimo de datos personales** necesario (idealmente solo ID o iniciales).
- No exponer RUT, nombres completos ni datos clínicos en el dashboard.
- Si se publica en red, agregar autenticación o restringir por IP.
- No incluir credenciales en el código; usar variables de entorno o `secrets.toml`.
- Registrar quién consulta y qué versión de la planificación ve, si el tiempo lo permite.

---

## 16. Checklist para la demo

- [ ] La app arranca en menos de 10 segundos.
- [ ] Se ve correctamente en la resolución del proyector.
- [ ] El flujo “llega archivo → Blue Prism procesa → dashboard se actualiza” se puede mostrar en vivo.
- [ ] Hay datos de respaldo por si falla la carga.
- [ ] Se muestran los filtros nacional, por instituto y por profesional.
- [ ] Se ven la Meta al 90% y el % FOJA.
- [ ] Hay una vista de errores de ingesta.
- [ ] Capturas o video de respaldo.
- [ ] El pitch explica qué hace Blue Prism y qué hace el dashboard.

---

## 17. Orden de trabajo sugerido

1. Entorno y “hola mundo” en Streamlit.
2. Conexión a la fuente de datos y primera tabla.
3. Filtros en cascada.
4. KPIs y gráficos.
5. Drill-down y detalle por profesional.
6. Panel de ingesta y errores.
7. Validación contra el Excel.
8. Estética, accesibilidad y demo.
9. Despliegue en la VM y ensayo cronometrado.

---

## 18. Próximos pasos

Cuando el equipo confirme la fuente de datos y el modelo, profundizar en:

- Esquema exacto de la base de datos.
- Consultas y agregaciones.
- Diseño visual y accesibilidad.
- Integración con Blue Prism.
- Guion de la demo.

> Este documento es una guía general. Cualquier cambio en el código o en otros archivos se hará solo cuando se solicite explícitamente.
