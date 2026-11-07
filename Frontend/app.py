# AQUÍ SE EDITA EL DASHBOARD
# ============================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN DE LA PÁGINA
# ============================================================

# Path: permite construir rutas de archivos de forma segura.
# pandas: se usa para leer los CSV y agrupar/sumar datos.
# streamlit: se usa para construir toda la interfaz.
from pathlib import Path

import pandas as pd
import streamlit as st

# set_page_config debe ser el primer comando de Streamlit.
# page_title: texto de la pestaña del navegador.
# page_icon: ícono de la pestaña.
# layout="wide": usa todo el ancho disponible en pantalla.
st.set_page_config(
    page_title="Planificación Asistencial",
    page_icon="📊",
    layout="wide",
)

# Carpeta donde están los CSV. __file__ es la ruta de app.py,
# .parent es la carpeta Frontend, y / "data" agrega la subcarpeta.
DATA_DIR = Path(__file__).resolve().parent / "data"


# ============================================================
# 2. CARGA DE DATOS
# ============================================================

# @st.cache_data guarda el resultado durante 60 segundos.
# Así Streamlit no vuelve a leer los CSV en cada clic o cambio de filtro.
@st.cache_data(ttl=60)
def cargar_datos():
    # Función interna: lee un CSV y devuelve un DataFrame.
    # Si el archivo no existe o está vacío, devuelve un DataFrame vacío
    # para que la aplicación no se caiga.
    def leer(nombre):
        ruta = DATA_DIR / nombre
        if not ruta.exists() or ruta.stat().st_size == 0:
            return pd.DataFrame()
        return pd.read_csv(ruta)

    # Se cargan las cuatro tablas del contrato de datos.
    return (
        leer("planificacion.csv"),
        leer("profesionales.csv"),
        leer("parametros.csv"),
        leer("errores_ingesta.csv"),
    )


# Se guardan las cuatro tablas en variables separadas.
plan, profesionales, parametros, errores = cargar_datos()

# Si la tabla principal está vacía, no tiene sentido seguir:
# se muestra un error y se detiene la ejecución de esta página.
if plan.empty:
    st.error("No hay datos de planificación. Revisa data/planificacion.csv.")
    st.stop()


# ============================================================
# 3. FUNCIONES AUXILIARES
# ============================================================

# Formatea un número con separador de miles chileno.
# Ejemplo: 2850 se muestra como "2.850".
def fmt(numero):
    return f"{numero:,.0f}".replace(",", ".")


# Devuelve la lista de opciones para un filtro.
# Agrega "Todos" al inicio y elimina valores repetidos.
# Ejemplo: ["Todos", "Arica", "Santiago", ...]
def opciones(df, columna):
    valores = sorted(df[columna].dropna().astype(str).unique().tolist())
    return ["Todos"] + valores


# ============================================================
# 4. ENCABEZADO
# ============================================================

# st.title muestra el título principal.
# st.caption muestra un texto pequeño debajo del título.
st.title("Planificación Asistencial Teletón")
st.caption("MVP Botathon 2026 · Datos ficticios de prueba")


# ============================================================
# 5. BARRA LATERAL: FILTROS EN CASCADA
# ============================================================

# with st.sidebar: agrupa todos los controles en la barra izquierda.
with st.sidebar:
    st.header("Filtros")

    # Botón para limpiar la caché y volver a leer los CSV.
    # st.rerun() vuelve a ejecutar la página desde el inicio.
    if st.button("Recargar datos"):
        st.cache_data.clear()
        st.rerun()

    # ---- Filtro por instituto ----
    # st.selectbox crea una lista desplegable.
    instituto = st.selectbox("Instituto", opciones(plan, "instituto"))

    # Si se eligió "Todos", se usa la tabla completa.
    # Si se eligió un instituto, se filtra la tabla.
    base = plan if instituto == "Todos" else plan[plan["instituto"] == instituto]

    # ---- Filtro por área ----
    # Las opciones se calculan sobre "base", por eso es en cascada:
    # solo aparecen áreas que existen en el instituto elegido.
    area = st.selectbox("Área", opciones(base, "area"))
    base = base if area == "Todos" else base[base["area"] == area]

    # ---- Filtro por cargo ----
    # Se vuelve a reducir la tabla antes de calcular las opciones.
    cargo = st.selectbox("Cargo", opciones(base, "cargo"))
    base = base if cargo == "Todos" else base[base["cargo"] == cargo]

    # ---- Filtro por mes ----
    mes = st.selectbox("Mes", opciones(base, "mes"))
    base = base if mes == "Todos" else base[base["mes"] == mes]

    # ---- Filtro por profesional ----
    # Al final queda la tabla "filtrado" con todas las selecciones aplicadas.
    profesional = st.selectbox("Profesional", opciones(base, "profesional_id"))
    filtrado = base if profesional == "Todos" else base[base["profesional_id"] == profesional]

    # Línea divisoria y contador de registros seleccionados.
    st.divider()
    st.caption(f"{len(filtrado)} registros seleccionados")

# Si los filtros no dejan ningún registro, se avisa y se detiene la página.
if filtrado.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()


# ============================================================
# 6. INDICADORES PRINCIPALES (KPIs)
# ============================================================

# Todas las sumas se calculan sobre "filtrado",
# por lo que las tarjetas cambian al mover los filtros.
total_atenciones = int(filtrado["atenciones_totales"].sum())
meta = int(filtrado["meta_gestion"].sum())

horas_directas = float(filtrado["horas_directas"].sum())
horas_contratadas = float(filtrado["horas_contratadas"].sum())

# % FOJA = horas disponibles para atención directa / horas contratadas.
# Se multiplica por 100 para mostrarlo como porcentaje.
foja = (horas_directas / horas_contratadas * 100) if horas_contratadas else 0.0

# nunique() cuenta profesionales distintos, sin repetir si aparecen en varios meses.
n_profesionales = int(filtrado["profesional_id"].nunique())

# st.columns(4) divide el ancho en cuatro columnas iguales.
c1, c2, c3, c4 = st.columns(4)

# st.metric crea una tarjeta con etiqueta y valor grande.
c1.metric("Atenciones planificadas", fmt(total_atenciones))
c2.metric("Meta de Gestión (90%)", fmt(meta))
c3.metric("% FOJA", f"{foja:.1f}%")
c4.metric("Profesionales", fmt(n_profesionales))

st.caption(
    f"{len(filtrado)} registros · {n_profesionales} profesionales · "
    "Los valores son de prueba y se validarán contra el Excel real."
)


# ============================================================
# 7. PESTAÑAS DEL DASHBOARD
# ============================================================

# st.tabs crea pestañas; cada bloque "with tab_..." llena una pestaña.
tab_resumen, tab_detalle, tab_ingesta = st.tabs(["Resumen", "Detalle", "Ingesta"])


# ---- Pestaña Resumen ----
with tab_resumen:
    st.subheader("Atenciones por instituto")

    # groupby("instituto") agrupa las filas por instituto.
    # [["atenciones_totales", "meta_gestion"]].sum() suma esas columnas.
    # as_index=False deja "instituto" como columna normal.
    # sort_values ordena de mayor a menor para que el gráfico se lea mejor.
    por_instituto = (
        filtrado.groupby("instituto", as_index=False)[["atenciones_totales", "meta_gestion"]]
        .sum()
        .sort_values("atenciones_totales", ascending=False)
    )

    # st.bar_chart dibuja un gráfico de barras con los datos agrupados.
    st.bar_chart(por_instituto, x="instituto", y="atenciones_totales")

    # st.dataframe muestra la misma información en formato tabla.
    # hide_index=True oculta la columna de índice (0, 1, 2...).
    st.dataframe(por_instituto, hide_index=True)


# ---- Pestaña Detalle ----
with tab_detalle:
    st.subheader("Detalle por profesional y mes")

    # Lista de columnas que se quieren mostrar.
    # Mantener el orden hace que la tabla sea más fácil de leer.
    columnas = [
        "profesional_id",
        "instituto",
        "cargo",
        "area",
        "mes",
        "estado_mes",
        "horas_contratadas",
        "horas_directas",
        "horas_indirectas",
        "horas_nas",
        "atenciones_directas",
        "atenciones_grupales",
        "atenciones_indirectas",
        "atenciones_totales",
        "meta_gestion",
    ]

    # Se muestra solo el subconjunto de columnas elegido.
    st.dataframe(filtrado[columnas], hide_index=True)


# ---- Pestaña Ingesta ----
with tab_ingesta:
    st.subheader("Errores de ingesta")

    # Si la tabla de errores está vacía, se muestra un mensaje de éxito.
    if errores.empty:
        st.success("No hay errores registrados.")
    else:
        # Si hay errores, se muestran en una tabla.
        st.dataframe(errores, hide_index=True)

        # value_counts() cuenta cuántos errores hay por severidad.
        # to_dict() lo convierte en un diccionario para mostrarlo en el texto.
        conteo = errores["severidad"].value_counts().to_dict()
        st.caption(f"{len(errores)} registros · {conteo}")
