import streamlit as st
import pandas as pd
from decimal import Decimal, getcontext

getcontext().prec = 28

st.set_page_config(layout="wide")
st.title("🏭 Production Planning (Multi-Factory)")


# =========================================================
# NUMBER FORMATTING
# =========================================================

def format_tr_number(value):
    """
    Format number with Turkish-style thousand separator.

    Examples:
    6600       -> 6.600
    8300       -> 8.300
    1232       -> 1.232
    1232000    -> 1.232.000
    """

    if value is None:
        return ""

    try:
        number = float(value)
        return f"{number:,.0f}".replace(",", ".")
    except:
        return str(value)


def parse_tr_number(value):
    """
    Convert displayed Turkish-style number into Python number.

    Examples:
    6.600       -> 6600
    8.300       -> 8300
    1.232       -> 1232
    1.232.000   -> 1232000
    """

    if value is None:
        return 0.0

    value = str(value).strip()

    if value == "":
        return 0.0

    # Remove thousand separators
    value = value.replace(".", "")

    try:
        return float(value)
    except:
        return 0.0


# =========================================================
# FORMATTED INPUT
# =========================================================

def format_input_value(key):
    """
    Automatically add thousand separators when
    the user changes an input.
    """

    value = st.session_state.get(key, "")

    if value is None:
        return

    value = str(value).strip()

    if value == "":
        return

    try:
        number = parse_tr_number(value)
        st.session_state[key] = format_tr_number(number)
    except:
        pass


def formatted_number_input(label, value, key):

    # Set initial value only once
    if key not in st.session_state:
        st.session_state[key] = format_tr_number(value)

    st.text_input(
        label,
        key=key,
        on_change=format_input_value,
        args=(key,)
    )

    return parse_tr_number(
        st.session_state[key]
    )


# =========================================================
# FACTORY COUNT
# =========================================================

n_factories = st.number_input(
    "Number of Factories",
    min_value=1,
    value=2,
    step=1
)

factories = []


# =========================================================
# FACTORY INPUTS
# =========================================================

st.subheader("Factory Inputs")

cols = st.columns(n_factories)

for i in range(n_factories):

    with cols[i]:

        name = st.text_input(
            f"Factory {i+1} Name",
            value=f"F{i+1}",
            key=f"name_{i}"
        )

        # -------------------------
        # REGULAR COST
        # -------------------------

        reg_cost = formatted_number_input(
            f"{name} Regular Cost(TL/Ton)",
            6600,
            key=f"reg_cost_{i}"
        )

        # -------------------------
        # OVERTIME COST
        # -------------------------

        ot_cost = formatted_number_input(
            f"{name} Overtime Cost(TL/Ton)",
            9900,
            key=f"ot_cost_{i}"
        )

        # -------------------------
        # REGULAR CAPACITY
        # -------------------------

        reg_cap = formatted_number_input(
            f"{name} Regular Capacity(Ton/Ay)",
            510,
            key=f"reg_cap_{i}"
        )

        # -------------------------
        # OVERTIME CAPACITY
        # -------------------------

        ot_cap = formatted_number_input(
            f"{name} Overtime Capacity(Ton/Ay)",
            400,
            key=f"ot_cap_{i}"
        )

        # -------------------------
        # STOCK
        # -------------------------

        stock = formatted_number_input(
            f"{name} Stock(Ton)",
            75,
            key=f"stock_{i}"
        )

        # -------------------------
        # SCRAP
        # -------------------------

        scrap = formatted_number_input(
            f"{name} Scrap (%)",
            5,
            key=f"scrap_{i}"
        ) / 100

        factories.append({
            "name": name,
            "reg_cost": reg_cost,
            "ot_cost": ot_cost,
            "reg_cap": reg_cap,
            "ot_cap": ot_cap,
            "stock": stock,
            "scrap": scrap
        })


# =========================================================
# SUBCONTRACT
# =========================================================

st.subheader("Subcontract")

sub_cost = formatted_number_input(
    "Subcontract Cost(TL/Ton)",
    15000,
    key="sub_cost"
)

sub_cap = formatted_number_input(
    "Subcontract Capacity(Ton/Ay)",
    0,
    key="sub_cap"
)


# =========================================================
# INFLATION
# =========================================================

st.subheader("Inflation")

use_inflation = st.checkbox(
    "Apply Inflation"
)

inflation_input = formatted_number_input(
    "Monthly Inflation (%)",
    2,
    key="inflation_input"
)

inflation_rate = inflation_input / 100


# =========================================================
# DEMAND
# =========================================================

st.subheader("Demand")

default = pd.DataFrame({
    "Period": [
        "Ocak",
        "Şubat",
        "Mart",
        "Nisan",
        "Mayıs",
        "Haziran",
        "Temmuz",
        "Ağustos",
        "Eylül",
        "Ekim",
        "Kasım",
        "Aralık"
    ],

    "Demand": [
        "1.500",
        "1.578",
        "1.670",
        "1.358",
        "1.587",
        "1.581",
        "1.854",
        "3.607",
        "2.066",
        "1.710",
        "1.686",
        "1.794"
    ]
})


# =========================================================
# DEMAND FORMAT CALLBACK
# =========================================================

def format_demand_table():

    if "demand_editor" not in st.session_state:
        return

    data = st.session_state["demand_editor"]

    if isinstance(data, pd.DataFrame):

        data = data.copy()

        if "Demand" in data.columns:

            formatted_values = []

            for value in data["Demand"]:

                if value is None or str(value).strip() == "":
                    formatted_values.append("")
                    continue

                try:
                    number = parse_tr_number(value)
                    formatted_values.append(
                        format_tr_number(number)
                    )
                except:
                    formatted_values.append(value)

            data["Demand"] = formatted_values

            st.session_state["demand_editor"] = data


# =========================================================
# DEMAND TABLE
# =========================================================

df = st.data_editor(
    default,
    num_rows="dynamic",
    width="stretch",
    key="demand_editor",
    on_change=format_demand_table
)


# =========================================================
# BACKORDER
# =========================================================

bo_flags = []

for i in range(len(df)):

    period_name = str(
        df.loc[i, "Period"]
    )

    if period_name.strip() == "":

        bo_flags.append(False)

    else:

        flag = st.checkbox(
            f"{period_name} → carry over",
            key=f"bo_{i}"
        )

        bo_flags.append(flag)


# =========================================================
# MODEL
# =========================================================

def run_model(df_input, scenario):

    df = df_input.copy()

    # Convert Turkish formatted Demand
    df["Demand"] = df["Demand"].apply(
        parse_tr_number
    )

    df = df.dropna(
        subset=["Demand"]
    ).reset_index(drop=True)

    # -------------------------
    # DEMAND SCENARIOS
    # -------------------------

    if scenario == "decrease":

        df["Demand"] = (
            df["Demand"]
            * (
                0.9
                ** pd.Series(
                    range(len(df))
                )
            )
        )

    elif scenario == "increase":

        df["Demand"] = (
            df["Demand"]
            * (
                1.1
                ** pd.Series(
                    range(len(df))
                )
            )
        )

    # -------------------------
    # INITIAL VALUES
    # -------------------------

    carry = 0

    rows = []

    total_cost = Decimal(0)

    factory_states = [
        f.copy()
        for f in factories
    ]

    # =====================================================
    # PERIOD LOOP
    # =====================================================

    for i in range(len(df)):

        period = str(
            df.loc[i, "Period"]
        )

        if period.strip() == "":
            continue

        raw_demand = df.loc[i, "Demand"]

        if pd.isna(raw_demand):
            continue

        demand = float(raw_demand)

        demand += carry

        # -------------------------
        # SCRAP
        # -------------------------

        avg_scrap = (
            sum(
                f["scrap"]
                for f in factory_states
            )
            / len(factory_states)
        )

        adjusted_demand = (
            demand / (1 - avg_scrap)
            if avg_scrap < 1
            else demand
        )

        remaining = adjusted_demand

        # -------------------------
        # INFLATION
        # -------------------------

        infl = Decimal(1)

        if use_inflation:

            infl = (
                Decimal(1)
                + Decimal(
                    str(inflation_rate)
                )
            ) ** Decimal(i)

        # -------------------------
        # INFLATED COSTS
        # -------------------------

        for f in factory_states:

            f["reg_cost_i"] = (
                Decimal(
                    str(f["reg_cost"])
                )
                * infl
            )

            f["ot_cost_i"] = (
                Decimal(
                    str(f["ot_cost"])
                )
                * infl
            )

        # =================================================
        # STOCK
        # =================================================

        stock_order = sorted(
            factory_states,
            key=lambda x: x["reg_cost_i"]
        )

        used_stock = {}

        for f in stock_order:

            used = min(
                f["stock"],
                remaining
            )

            used_stock[f["name"]] = used

            f["stock"] -= used

            remaining -= used

            if remaining <= 0:
                break

        # =================================================
        # REGULAR PRODUCTION
        # =================================================

        reg_order = sorted(
            factory_states,
            key=lambda x: x["reg_cost_i"]
        )

        used_reg = {}

        for f in reg_order:

            used = min(
                f["reg_cap"],
                remaining
            )

            used_reg[f["name"]] = used

            remaining -= used

            if remaining <= 0:
                break

        # =================================================
        # OVERTIME
        # =================================================

        ot_order = sorted(
            factory_states,
            key=lambda x: x["ot_cost_i"]
        )

        used_ot = {}

        for f in ot_order:

            used = min(
                f["ot_cap"],
                remaining
            )

            used_ot[f["name"]] = used

            remaining -= used

            if remaining <= 0:
                break

        # =================================================
        # SUBCONTRACT
        # =================================================

        sub_used = min(
            sub_cap,
            remaining
        )

        remaining -= sub_used

        # -------------------------
        # SHORTAGE
        # -------------------------

        shortage = max(
            0,
            remaining
        )

        # =================================================
        # BACKORDER
        # =================================================

        if (
            i < len(df) - 1
            and bo_flags[i]
        ):

            carry = shortage

            shortage = 0

        else:

            carry = 0

        # =================================================
        # TOTAL PRODUCTION
        # =================================================

        total_prod = (
            sum(used_stock.values())
            + sum(used_reg.values())
            + sum(used_ot.values())
            + sub_used
        )

        # =================================================
        # COST
        # =================================================

        period_cost = Decimal(0)

        for f in factory_states:

            name = f["name"]

            # Stock cost
            period_cost += (
                Decimal(
                    str(
                        used_stock.get(
                            name,
                            0
                        )
                    )
                )
                * f["reg_cost_i"]
            )

            # Regular cost
            period_cost += (
                Decimal(
                    str(
                        used_reg.get(
                            name,
                            0
                        )
                    )
                )
                * f["reg_cost_i"]
            )

            # Overtime cost
            period_cost += (
                Decimal(
                    str(
                        used_ot.get(
                            name,
                            0
                        )
                    )
                )
                * f["ot_cost_i"]
            )

        # Subcontract cost
        period_cost += (
            Decimal(
                str(sub_used)
            )
            * Decimal(
                str(sub_cost)
            )
            * infl
        )

        total_cost += period_cost

        # =================================================
        # RESULT ROW
        # =================================================

        row = {
            "Period": period,
            "Net Demand": demand,
            "Gross Production Need": adjusted_demand
        }

        # Stock
        for f in stock_order:

            row[
                f"{f['name']}_Stock"
            ] = used_stock.get(
                f["name"],
                0
            )

        # Regular
        for f in reg_order:

            row[
                f"{f['name']}_Reg"
            ] = used_reg.get(
                f["name"],
                0
            )

        # Overtime
        for f in ot_order:

            row[
                f"{f['name']}_OT"
            ] = used_ot.get(
                f["name"],
                0
            )

        row["Subcontract"] = sub_used

        row["Shortage"] = shortage

        row["Total Production"] = total_prod

        row["Cost"] = float(
            period_cost
        )

        rows.append(row)

    return (
        pd.DataFrame(rows),
        float(total_cost)
    )


# =========================================================
# RESULTS
# =========================================================

st.divider()

st.header("Results")

tab1, tab2, tab3 = st.tabs([
    "Base Scenario",
    "Demand Decreasing (-10%)",
    "Demand Increasing (+10%)"
])


# =========================================================
# SCENARIOS
# =========================================================

for tab, scenario, title in [

    (
        tab1,
        "normal",
        "Base Scenario"
    ),

    (
        tab2,
        "decrease",
        "Demand Decreasing"
    ),

    (
        tab3,
        "increase",
        "Demand Increasing"
    )

]:

    with tab:

        st.subheader(title)

        result, total_cost = run_model(
            df,
            scenario
        )

        # =================================================
        # TOTAL COST
        # =================================================

        st.metric(
            "Total Cost",
            format_tr_number(
                total_cost
            )
        )

        # =================================================
        # RESULT TABLE
        # =================================================

        numeric_cols = (
            result
            .select_dtypes(
                include="number"
            )
            .columns
        )

        styled = result.style.format({

            col: lambda x:
                format_tr_number(x)

            for col in numeric_cols

        })

        # =================================================
        # BOLD COLUMNS
        # =================================================

        for col in [
            "Total Production",
            "Cost"
        ]:

            if col in result.columns:

                styled = styled.map(
                    lambda x:
                        "font-weight:bold",
                    subset=[col]
                )

        st.dataframe(
            styled,
            width="stretch"
        )
