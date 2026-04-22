import streamlit as st
import pandas as pd
from decimal import Decimal, getcontext

getcontext().prec = 28

st.set_page_config(layout="wide")
st.title("🏭 Production Planning (Multi-Factory)")

# -----------------------------
# FACTORY COUNT
# -----------------------------
n_factories = st.number_input("Number of Factories", min_value=1, value=2, step=1)

factories = []

# -----------------------------
# FACTORY INPUTS
# -----------------------------
st.subheader("Factory Inputs")
cols = st.columns(n_factories)

for i in range(n_factories):
    with cols[i]:
        name = st.text_input(f"Factory {i+1} Name", value=f"F{i+1}", key=f"name_{i}")

        reg_cost = st.number_input(f"{name} Regular Cost(TL/Ton)", value=6600.0, key=f"reg_cost_{i}")
        ot_cost = st.number_input(f"{name} Overtime Cost(TL/Ton)", value=9900.0, key=f"ot_cost_{i}")

        reg_cap = st.number_input(f"{name} Regular Capacity(Ton/Ay)", value=510.0, key=f"reg_cap_{i}")
        ot_cap = st.number_input(f"{name} Overtime Capacity(Ton/Ay)", value=400.0, key=f"ot_cap_{i}")

        stock = st.number_input(f"{name} Stock(Ton)", value=75.0, key=f"stock_{i}")

        scrap = st.number_input(f"{name} Scrap (%)", value=5.0, key=f"scrap_{i}") / 100

        factories.append({
            "name": name,
            "reg_cost": reg_cost,
            "ot_cost": ot_cost,
            "reg_cap": reg_cap,
            "ot_cap": ot_cap,
            "stock": stock,
            "scrap": scrap
        })

# -----------------------------
# SUBCONTRACT
# -----------------------------
st.subheader("Subcontract")
sub_cost = st.number_input("Subcontract Cost(TL/Ton)", value=1500.0)
sub_cap = st.number_input("Subcontract Capacity(Ton/Ay)", value=0.0)

# -----------------------------
# INFLATION
# -----------------------------
st.subheader("Inflation")

use_inflation = st.checkbox("Apply Inflation")
inflation_input = st.number_input("Monthly Inflation (%)", value=2.0)
inflation_rate = inflation_input / 100

# -----------------------------
# DEMAND
# -----------------------------
st.subheader("Demand")

default = pd.DataFrame({
    "Period": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
    "Demand": [1500, 1578, 1670, 1358, 1587, 1581, 1854, 3607, 2066, 1710, 1686, 1794]
})

df = st.data_editor(default, num_rows="dynamic", width="stretch")

# -----------------------------
# BACKORDER
# -----------------------------
bo_flags = []
for i in range(len(df)):
    period_name = str(df.loc[i, "Period"])
    if period_name.strip() == "":
        bo_flags.append(False)
    else:
        flag = st.checkbox(f"{period_name} → carry over", key=f"bo_{i}")
        bo_flags.append(flag)

# -----------------------------
# MODEL
# -----------------------------
def run_model(df_input, scenario):

    df = df_input.copy()

    # 🔥 TYPE FIX
    df["Demand"] = pd.to_numeric(df["Demand"], errors="coerce")
    df = df.dropna(subset=["Demand"]).reset_index(drop=True)

    # 🔥 INDEX SAFE LOOP
    for idx in range(len(df)):
        if pd.isna(df.loc[idx, "Demand"]):
            continue

        if scenario == "decrease":
            df.loc[idx, "Demand"] *= (0.9 ** idx)
        elif scenario == "increase":
            df.loc[idx, "Demand"] *= (1.1 ** idx)

    carry = 0
    rows = []
    total_cost = Decimal(0)
    factory_states = [f.copy() for f in factories]

    for i in range(len(df)):

        period = str(df.loc[i, "Period"])
        if period.strip() == "":
            continue

        demand = float(df.loc[i, "Demand"]) + carry

        avg_scrap = sum([f["scrap"] for f in factory_states]) / len(factory_states)
        adjusted_demand = demand / (1 - avg_scrap) if avg_scrap < 1 else demand

        remaining = adjusted_demand

        infl = Decimal(1)
        if use_inflation:
            infl = (Decimal(1) + Decimal(str(inflation_rate))) ** Decimal(i)

        for f in factory_states:
            f["reg_cost_i"] = Decimal(str(f["reg_cost"])) * infl
            f["ot_cost_i"] = Decimal(str(f["ot_cost"])) * infl

        used_stock = {}
        for f in sorted(factory_states, key=lambda x: x["reg_cost_i"]):
            used = min(f["stock"], remaining)
            used_stock[f["name"]] = used
            f["stock"] -= used
            remaining -= used
            if remaining <= 0:
                break

        used_reg = {}
        for f in sorted(factory_states, key=lambda x: x["reg_cost_i"]):
            used = min(f["reg_cap"], remaining)
            used_reg[f["name"]] = used
            remaining -= used
            if remaining <= 0:
                break

        used_ot = {}
        for f in sorted(factory_states, key=lambda x: x["ot_cost_i"]):
            used = min(f["ot_cap"], remaining)
            used_ot[f["name"]] = used
            remaining -= used
            if remaining <= 0:
                break

        sub_used = min(sub_cap, remaining)
        remaining -= sub_used

        shortage = max(0, remaining)

        if i < len(df)-1 and bo_flags[i]:
            carry = shortage
            shortage = 0
        else:
            carry = 0

        total_prod = sum(used_stock.values()) + sum(used_reg.values()) + sum(used_ot.values()) + sub_used

        period_cost = Decimal(0)

        for f in factory_states:
            name = f["name"]
            period_cost += Decimal(str(used_stock.get(name, 0))) * f["reg_cost_i"]
            period_cost += Decimal(str(used_reg.get(name, 0))) * f["reg_cost_i"]
            period_cost += Decimal(str(used_ot.get(name, 0))) * f["ot_cost_i"]

        period_cost += Decimal(str(sub_used)) * Decimal(str(sub_cost)) * infl
        total_cost += period_cost

        row = {
            "Period": period,
            "Net Demand": demand,
            "Gross Production Need": adjusted_demand,
            "Subcontract": sub_used,
            "Shortage": shortage,
            "Total Production": total_prod,
            "Cost": float(period_cost)
        }

        rows.append(row)

    return pd.DataFrame(rows), float(total_cost)

# -----------------------------
# RESULTS
# -----------------------------
st.divider()
st.header("Results")

tab1, tab2, tab3 = st.tabs([
    "Base Scenario",
    "Demand Decreasing (-10%)",
    "Demand Increasing (+10%)"
])

for tab, scenario, title in [
    (tab1, "normal", "Base Scenario"),
    (tab2, "decrease", "Demand Decreasing"),
    (tab3, "increase", "Demand Increasing")
]:

    with tab:
        st.subheader(title)

        result, total_cost = run_model(df, scenario)

        st.metric("Total Cost", f"{total_cost:,.0f}")

        st.dataframe(result, width="stretch")

