# AML/CFT Compliance System (Dev Scaffold)

## Quick Start
1) `python build_aml_cft_structure_and_data.py`  (this script)
2) `python data/sample_data_generator.py`         (creates CSVs under `data/samples/`)
3) `python scripts/setup_database.py`
4) `python scripts/load_sample_data.py`
5) `streamlit run app.py`

### Config
- Edit `configs/aml_config.yml` (KES 1.9M CTR, STR=2 days, sanctions=24h, 7-year retention).
- Env vars in `.env.example`.

### Data Volumes
- Override via env: `AML_SAMPLE_MEMBERS`, `AML_SAMPLE_TXN_AVG`, `AML_SAMPLE_SEED`.
