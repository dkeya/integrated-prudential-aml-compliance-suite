import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random, os

RNG_SEED = int(os.getenv("AML_SAMPLE_SEED", "20251026"))
random.seed(RNG_SEED); np.random.seed(RNG_SEED)
fake = Faker("en_US")
Faker.seed(RNG_SEED)

# --- Configurable volumes ---
N_MEMBERS = int(os.getenv("AML_SAMPLE_MEMBERS","1200"))
N_TXN_PER_MEMBER_AVG = float(os.getenv("AML_SAMPLE_TXN_AVG","24"))
START_DATE = datetime.now() - relativedelta(months=9)
END_DATE = datetime.now()

BRANCHES = ["Nairobi HQ","Mombasa","Kisumu","Nakuru","Eldoret","Thika","Nyeri"]
PRODUCTS = ["CURRENT","SAVINGS","FIXED","MOBILE","LOAN"]
CHANNELS = ["CASH","MOBILE","TELLER","CARD","AGENT"]
OCCUPATIONS = ["Farmer","Trader","Teacher","Civil Servant","Consultant","Driver","Doctor","Student"]

def _member_id(i): return f"M{100000 + i}"
def _txn_id(i): return f"T{100000000 + i}"

def generate_members(n=N_MEMBERS):
    rows=[]
    for i in range(n):
        fname, lname = fake.first_name(), fake.last_name()
        full = f"{fname} {lname}"
        dob = fake.date_between(start_date="-70y", end_date="-18y")
        id_type = random.choice(["NATIONAL_ID","PASSPORT"])
        id_number = str(fake.random_number(digits=8))
        branch = random.choice(BRANCHES)
        occupation = random.choice(OCCUPATIONS)
        residence_country = random.choice(["KE","UG","TZ","ET","SS","SO","PK","YE"])
        pep_flag = np.random.rand() < 0.03
        onboard_method = random.choice(["BRANCH","ONLINE","AGENT"])
        kyc_complete = np.random.rand() > 0.08
        risk_band = random.choices(["LOW","MEDIUM","HIGH"], weights=[0.6,0.3,0.1])[0]
        created_at = fake.date_time_between(start_date="-2y", end_date="now")
        rows.append([_member_id(i), full, dob, " ".join([fname,lname]), id_type, id_number,
                     branch, occupation, residence_country, pep_flag, onboard_method,
                     kyc_complete, risk_band, created_at])
    return pd.DataFrame(rows, columns=[
        "member_id","full_name","dob","name_parts","id_type","id_number","branch","occupation",
        "residence_country","pep_flag","onboard_method","kyc_complete","risk_band","created_at"
    ])

def inject_structuring(txn_df, ctr_threshold_kes=1900000, unit=150000):
    # create staircase bursts totaling near CTR within window
    by_member = txn_df["member_id"].unique()[:max(10, len(txn_df)//5000)]
    for m in by_member:
        base_day = fake.date_time_between_dates(datetime_start=START_DATE, datetime_end=END_DATE - timedelta(days=7))
        parts = [unit+random.randint(-10000, 8000) for _ in range(random.randint(5,9))]
        times = [base_day + timedelta(hours=random.randint(0,160)) for _ in parts]
        add = pd.DataFrame({
            "txn_id":[f"S{random.randint(10**8,10**9-1)}" for _ in parts],
            "member_id":m, "ts":times, "amount":parts,
            "channel":"CASH", "product":"CURRENT","counterparty":"N/A",
            "geo":"KE-NRB","narrative":"cash deposits","branch":"Nairobi HQ","device_id":"dev-cash-01"
        })
        txn_df = pd.concat([txn_df, add], ignore_index=True)
    return txn_df

def inject_rapid_movement(txn_df):
    # create inflow then outflow within 5 days ≥80% of inflow
    choose = txn_df["member_id"].sample(min(20, txn_df["member_id"].nunique()), random_state=RNG_SEED)
    for m in choose:
        t0 = fake.date_time_between_dates(datetime_start=START_DATE, datetime_end=END_DATE - timedelta(days=5))
        inflow = random.randint(800000, 2500000)
        outflow = int(inflow * random.uniform(0.8,0.98))
        a = dict(txn_id=_txn_id(random.randint(1,10**7)), member_id=m, ts=t0,
                 amount=inflow, channel="CASH", product="CURRENT",
                 counterparty="N/A", geo="KE-NRB", narrative="cash inflow",
                 branch=random.choice(BRANCHES), device_id="dev-cash-02")
        b = dict(txn_id=_txn_id(random.randint(1,10**7)), member_id=m, ts=t0+timedelta(days=3),
                 amount=-outflow, channel="TELLER", product="CURRENT",
                 counterparty="External", geo="KE-NRB", narrative="cash withdrawal",
                 branch=random.choice(BRANCHES), device_id="dev-teller-07")
        txn_df = pd.concat([txn_df, pd.DataFrame([a,b])], ignore_index=True)
    return txn_df

def inject_dormant_to_active(txn_df, members_df):
    # pick KYC-complete members with long silence then spike
    candidates = members_df[members_df["kyc_complete"]].sample(15, random_state=RNG_SEED, replace=True)["member_id"]
    for m in candidates:
        t0 = START_DATE + timedelta(days=random.randint(0, 60))
        spike_day = t0 + timedelta(days=random.randint(80, 140))
        spike_amts = [random.randint(200000,800000) for _ in range(5)]
        add = pd.DataFrame({
            "txn_id":[_txn_id(random.randint(1,10**7)) for _ in spike_amts],
            "member_id":m, "ts":[spike_day + timedelta(hours=i*3) for i in range(5)],
            "amount":spike_amts, "channel":"MOBILE","product":"MOBILE","counterparty":"N/A",
            "geo":"KE-NRB","narrative":"mobile inflow cluster","branch":"Nairobi HQ","device_id":"phone-xyz"
        })
        txn_df = pd.concat([txn_df, add], ignore_index=True)
    return txn_df

def inject_odd_hours(txn_df):
    sel = txn_df.sample(frac=0.02, random_state=RNG_SEED).index
    txn_df.loc[sel, "ts"] = txn_df.loc[sel, "ts"] - pd.to_timedelta(np.random.randint(1,5,len(sel)), unit="h")
    txn_df.loc[sel, "narrative"] = "overnight activity"
    return txn_df

def generate_transactions(members_df):
    rows=[]
    txn_counter=0
    for _, m in members_df.iterrows():
        k = np.random.poisson(N_TXN_PER_MEMBER_AVG)
        for _ in range(k):
            ts = fake.date_time_between_dates(datetime_start=START_DATE, datetime_end=END_DATE)
            amt = np.round(np.random.lognormal(mean=12.2, sigma=0.8),0)  # skewed
            if np.random.rand() < 0.35: amt = -amt  # outflow
            rows.append([
                _txn_id(txn_counter), m["member_id"], ts, float(amt),
                random.choice(CHANNELS), random.choice(PRODUCTS),
                fake.company(), "KE-"+random.choice(["NRB","MSA","KSM","NKR","EDL","THK","NYR"]),
                fake.sentence(nb_words=5), random.choice(BRANCHES), "dev-"+fake.pystr(min_chars=6,max_chars=8)
            ])
            txn_counter += 1
    df = pd.DataFrame(rows, columns=["txn_id","member_id","ts","amount","channel","product","counterparty","geo","narrative","branch","device_id"])
    # Anomalies
    df = inject_structuring(df)
    df = inject_rapid_movement(df)
    df = inject_dormant_to_active(df, members_df)
    df = inject_odd_hours(df)
    return df

def generate_pep_list(n=120):
    rows=[]
    for _ in range(n):
        rows.append([fake.name(), random.choice(["Minister","MP","Ambassador","General"]), random.choice(["KE","UG","TZ","ET","SS"])])
    return pd.DataFrame(rows, columns=["name","position","country"])

def generate_sanctions_list(n=100):
    rows=[]
    for _ in range(n):
        rows.append([fake.name(), random.choice(["OFAC","UN","EU","FRC"]), random.choice(["TFS","CTF","WMD"]), random.choice(["IR","KP","AF","YE"])])
    return pd.DataFrame(rows, columns=["name","list","program","country"])

def generate_training(n=200):
    rows=[]
    for _ in range(n):
        start = fake.date_between(start_date="-18mo", end_date="today")
        expiry = start + timedelta(days=365)
        rows.append([fake.uuid4()[:8], random.choice(["AML Basics","CDD/EDD","TFS","goAML Filing"]), start, random.randint(60,100), expiry])
    return pd.DataFrame(rows, columns=["staff_id","module","completed_on","score","expiry_on"])

def generate_branches_products():
    b = pd.DataFrame({"branch": BRANCHES})
    p = pd.DataFrame({"product": PRODUCTS})
    return b, p

def generate_alert_seeds():
    # Minimal seed for UI lists (will be replaced by rules engine in-app)
    return pd.DataFrame([
        {"alert_id":"A001","type":"Structuring","severity":"HIGH","status":"OPEN"},
        {"alert_id":"A002","type":"Rapid Movement","severity":"MEDIUM","status":"OPEN"}
    ])

def main(out_dir="./data/samples"):
    os.makedirs(out_dir, exist_ok=True)
    members = generate_members()
    txns = generate_transactions(members)
    pep = generate_pep_list()
    sanc = generate_sanctions_list()
    training = generate_training()
    branches, products = generate_branches_products()
    alerts = generate_alert_seeds()

    members.to_csv(f"{out_dir}/members.csv", index=False)
    txns.to_csv(f"{out_dir}/transactions.csv", index=False)
    pep.to_csv(f"{out_dir}/pep_list.csv", index=False)
    sanc.to_csv(f"{out_dir}/sanctions_list.csv", index=False)
    training.to_csv(f"{out_dir}/training.csv", index=False)
    branches.to_csv(f"{out_dir}/branches.csv", index=False)
    products.to_csv(f"{out_dir}/products.csv", index=False)
    alerts.to_csv(f"{out_dir}/alerts_seed.csv", index=False)
    print("✅ Sample datasets created under", out_dir)

if __name__ == "__main__":
    main()
