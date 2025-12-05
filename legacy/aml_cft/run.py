import os, subprocess, sys
os.environ.setdefault("AML_DB_PATH","./data/aml_database.duckdb")
cmds = [
    [sys.executable,"data/sample_data_generator.py"],
    [sys.executable,"scripts/setup_database.py"],
    [sys.executable,"scripts/load_sample_data.py"],
    ["streamlit","run","app.py"]
]
for c in cmds:
    print("→", " ".join(c))
    subprocess.run(c, check=True)
