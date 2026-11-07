"""Genera los CSV correctos directamente desde los Excel originales.

Respaldo para cuando Blue Prism no puede procesar el libro de planificación
(205 columnas) o cuando se necesita una fuente con fechas 100 % fieles.

Uso:
    python generar_csv_desde_fuente.py
    python generar_csv_desde_fuente.py --base "..." --plan "..." --out "..."
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def normalizar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def main() -> None:
    raiz = Path(__file__).resolve().parent
    proyecto = raiz.parent.parent

    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=str(proyecto / "Recursos" / "Nac - Base contratos x mes.xlsx"))
    parser.add_argument("--plan", default=str(proyecto / "Recursos" / "Nac - Planificación Asistencial x mes.xlsx"))
    parser.add_argument("--out", default=str(proyecto / "Frontend" / "data"))
    args = parser.parse_args()

    salida = Path(args.out)
    salida.mkdir(parents=True, exist_ok=True)

    # --- Base contratos ---
    base = pd.read_excel(args.base, sheet_name="Dotacion_2026", header=1, usecols="A:S")
    base = base.dropna(how="all")
    normalizar(base).to_csv(salida / "base_contratos.csv", index=False, encoding="utf-8-sig")
    print(f"base_contratos.csv ({base.shape[0]} x {base.shape[1]})")

    # --- Planificación ---
    dot = pd.read_excel(args.plan, sheet_name="Dotacion_Asistencial", header=3, usecols="A:GW")
    dot = dot[dot["IT"].astype(str).str.strip() != "Total"]
    dot = dot.dropna(subset=["PersonaId"])
    normalizar(dot).to_csv(salida / "dotacion_asistencial.csv", index=False, encoding="utf-8-sig")
    print(f"dotacion_asistencial.csv ({dot.shape[0]} x {dot.shape[1]})")

    exc = pd.read_excel(args.plan, sheet_name="Excepciones", header=1, usecols="A:X")
    exc = exc.dropna(how="all")
    normalizar(exc).to_csv(salida / "excepciones.csv", index=False, encoding="utf-8-sig")
    print(f"excepciones.csv ({exc.shape[0]} x {exc.shape[1]})")

    lop = pd.read_excel(args.plan, sheet_name="LOP", header=0, usecols="A:C")
    lop = lop[lop["IT"].notna()]
    normalizar(lop).to_csv(salida / "lop.csv", index=False, encoding="utf-8-sig")
    print(f"lop.csv ({lop.shape[0]} x {lop.shape[1]})")


if __name__ == "__main__":
    main()
