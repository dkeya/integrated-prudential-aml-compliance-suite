# sacco_core/utils/export.py
from __future__ import annotations
import io
import pandas as pd
import streamlit as st

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def df_to_xlsx_bytes(df: pd.DataFrame, sheet_name: str = "Sheet1") -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        df.to_excel(xw, sheet_name=sheet_name, index=False)
    buf.seek(0)
    return buf.read()

def export_buttons(df: pd.DataFrame, basename: str, height: int = 360):
    st.dataframe(df, use_container_width=True, height=height)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Export CSV",
            df_to_csv_bytes(df),
            file_name=f"{basename}.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"exp_csv_{basename}",
        )
    with col2:
        st.download_button(
            "⬇️ Export XLSX",
            df_to_xlsx_bytes(df),
            file_name=f"{basename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=f"exp_xlsx_{basename}",
        )