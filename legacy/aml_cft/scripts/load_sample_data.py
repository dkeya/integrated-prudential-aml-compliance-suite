import os, pandas as pd
import sys
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sacco_core.db import get_connection
from sacco_core.utils import validate_data

SAMPLES = Path("./data/samples")

def load_df(name): 
    return pd.read_csv(SAMPLES / name)

if __name__ == "__main__":
    con = get_connection()
    cur = con.cursor()

    members = load_df("members.csv")
    txns = load_df("transactions.csv")
    pep = load_df("pep_list.csv")
    sanc = load_df("sanctions_list.csv")
    training = load_df("training.csv")

    miss = validate_data(members, ["member_id","full_name","dob","id_type","id_number","branch"])
    if miss: 
        raise SystemExit(f"members missing: {miss}")

    # Truncate tables
    cur.execute("DELETE FROM members")
    cur.execute("DELETE FROM transactions")
    cur.execute("DELETE FROM pep_list")
    cur.execute("DELETE FROM sanctions_list")
    cur.execute("DELETE FROM training")

    # Load data
    cur.executemany("""
        INSERT INTO members 
        (member_id, full_name, dob, id_type, id_number, branch, occupation, residence_country, 
         pep_flag, onboard_method, kyc_complete, risk_band, created_at, name_parts)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, members[[
        "member_id","full_name","dob","id_type","id_number","branch","occupation","residence_country",
        "pep_flag","onboard_method","kyc_complete","risk_band","created_at","name_parts"
    ]].values.tolist())

    cur.executemany("""
        INSERT INTO transactions 
        (txn_id, member_id, ts, amount, channel, product, counterparty, geo, narrative, branch, device_id)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, txns.values.tolist())

    cur.executemany("""
        INSERT INTO pep_list (name, position, country) VALUES (?,?,?)
    """, pep.values.tolist())

    cur.executemany("""
        INSERT INTO sanctions_list (name, list, program, country) VALUES (?,?,?,?)
    """, sanc.values.tolist())

    cur.executemany("""
        INSERT INTO training (staff_id, module, completed_on, score, expiry_on) VALUES (?,?,?,?,?)
    """, training.values.tolist())

    con.commit()
    con.close()
    print("✅ Loaded samples into DuckDB.")
