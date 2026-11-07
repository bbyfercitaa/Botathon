"""Convierte las salidas XLSX de Blue Prism a CSV UTF-8.

Uso:
    python convertir_a_csv.py
    python convertir_a_csv.py --data "C:\ruta\Frontend\data"
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

NOMBRES = ["base_contratos", "dotacion_asistencial", "excepciones", "lop"]


def normalizar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def main() -> None:
    raiz = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=str(raiz.parent.parent / "Frontend" / "data"))
    args = parser.parse_args()

    data = Path(args.data)
    for nombre in NOMBRES:
        origen = data / f"{nombre}.xlsx"
        destino = data / f"{nombre}.csv"
        if not origen.exists():
            print(f"OMITIDO: no existe {origen}")
            continue
        df = normalizar(pd.read_excel(origen))
        df.to_csv(destino, index=False, encoding="utf-8-sig")
        print(f"{origen.name} -> {destino.name} ({df.shape[0]} x {df.shape[1]})")


if __name__ == "__main__":
    main()
