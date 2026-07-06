import pandas as pd

# ── Load karo ──────────────────────────────
df = pd.read_csv("Nassau _Candy1.csv")
df["Order Date"] = pd.to_datetime(df["Order Date"])

print(f"Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# ── 1. Cost & Sales Validation ─────────────
df = df[df["Sales"] > 0]
df = df[df["Cost"] > 0]
df = df[df["Cost"] <= df["Sales"]]

# ── 2. Invalid Profit Records ──────────────
df = df[df["Gross Profit"] > 0]

# ── 3. Missing Units ───────────────────────
df = df[df["Units"] > 0]
df = df[df["Units"].notnull()]

# ── 4. Label Standardization ───────────────
df["Product Name"] = df["Product Name"].str.strip()
df["Division"]     = df["Division"].str.strip()
df["Region"]       = df["Region"].str.strip()

df["Product Name"] = df["Product Name"].str.replace(
    "Wonka Bar -Scrumdiddlyumptious",
    "Wonka Bar - Scrumdiddlyumptious",
    regex=False
)

# ── 6. Save karo ───────────────────────────
df.to_csv("Nassau_Candy_Validated.csv", index=False)

print(f"Clean file saved: {df.shape[0]} rows × {df.shape[1]} columns")
print("File: Nassau_Candy_Validated.csv")