import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Debt Optimizer", layout="wide")

# ---------------- SESSION ----------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "debts_data" not in st.session_state:
    st.session_state.debts_data = []

# ---------------- STEP 1 ----------------
if st.session_state.step == 1:
    st.title("💡 AI Debt Repayment Optimizer")
    st.subheader("Step 1: User Info")

    st.text_input("Enter your name", key="name")

    if st.button("Next"):
        st.session_state.step = 2

# ---------------- STEP 2 ----------------
elif st.session_state.step == 2:
    st.subheader("Step 2: Debt Details")

    num_debts = st.number_input("Number of Debts", min_value=1, max_value=10, key="num_debts")

    loan_types = [
        "Credit Card", "Student Loan", "Personal Loan",
        "Home Loan", "Car Loan", "Business Loan",
        "Gold Loan", "Other"
    ]

    debts = []

    for i in range(num_debts):
        st.markdown(f"### Debt {i+1}")
        col1, col2 = st.columns(2)

        with col1:
            loan = st.selectbox("Loan Type", loan_types, key=f"type_{i}")
            balance = st.number_input("Balance ₹", min_value=0.0, key=f"bal_{i}")

        with col2:
            rate = st.number_input("Interest %", min_value=0.0, key=f"rate_{i}")
            min_pay = st.number_input("Min Payment ₹", min_value=0.0, key=f"min_{i}")

        debts.append({
            "type": loan,
            "balance": balance,
            "rate": rate,
            "min_payment": min_pay
        })

    col1, col2 = st.columns(2)
    if col1.button("Back"):
        st.session_state.step = 1

    if col2.button("Next"):
        st.session_state.debts_data = debts
        st.session_state.step = 3

# ---------------- STEP 3 ----------------
elif st.session_state.step == 3:
    st.subheader("Step 3: Financial Details")

    st.number_input("Income", key="income")
    st.number_input("Expenses", key="expenses")
    st.number_input("Discretionary Spending", key="disc")
    st.number_input("Savings", key="sav")
    st.number_input("Emergency Fund", key="emer")

    col1, col2 = st.columns(2)
    if col1.button("Back"):
        st.session_state.step = 2

    if col2.button("Next"):
        st.session_state.step = 4

# ---------------- STEP 4 ----------------
elif st.session_state.step == 4:

    st.title(f"📊 Dashboard - {st.session_state.name}")

    debts = st.session_state.debts_data
    income = st.session_state.income
    expenses = st.session_state.expenses
    disc = st.session_state.disc
    sav = st.session_state.sav
    emer = st.session_state.emer

    strategy = st.radio("Choose Strategy", ["Debt Snowball", "Debt Avalanche", "AI Optimized"])

    lump_sum = st.number_input("Lump Sum Payment", value=0)
    lump_month = st.number_input("Apply in Month", value=1)

    # -------- SIMULATION ENGINE --------
    def simulate(debts, extra, strategy):
        debts = [d.copy() for d in debts]
        schedule = []
        total_interest = 0
        month = 1

        while any(d["balance"] > 0 for d in debts) and month <= 120:

            if strategy == "Debt Snowball":
                debts.sort(key=lambda x: x["balance"])
            elif strategy == "Debt Avalanche":
                debts.sort(key=lambda x: x["rate"], reverse=True)
            else:
                debts.sort(key=lambda x: (x["rate"] * x["balance"]), reverse=True)

            month_interest = 0

            # Interest
            for d in debts:
                if d["balance"] > 0:
                    interest = d["balance"] * (d["rate"]/100/12)
                    d["balance"] += interest
                    month_interest += interest

            # Minimum payments
            for d in debts:
                if d["balance"] > 0:
                    pay = min(d["min_payment"], d["balance"])
                    d["balance"] -= pay

            # Extra payment (correct distribution)
            remaining = extra
            for d in debts:
                if d["balance"] > 0 and remaining > 0:
                    pay = min(remaining, d["balance"])
                    d["balance"] -= pay
                    remaining -= pay

            # Lump sum
            if month == lump_month:
                for d in debts:
                    if d["balance"] > 0:
                        d["balance"] -= min(lump_sum, d["balance"])
                        break

            total_interest += month_interest

            schedule.append({
                "Month": month,
                "Balance": sum(d["balance"] for d in debts)
            })

            month += 1

        return pd.DataFrame(schedule), total_interest

    # -------- EXTRA CALC --------
    extra = income - (expenses + disc + sav + emer) - sum(d["min_payment"] for d in debts)

    if extra <= 0:
        st.error("No surplus income available")
    else:

        if st.button("Run Optimizer"):

            df, interest = simulate(debts, extra, strategy)

            months = df[df["Balance"] <= 0]["Month"].min()

            # KPIs
            col1, col2, col3 = st.columns(3)
            col1.metric("Months to Debt-Free", months)
            col2.metric("Total Interest Paid", f"₹{round(interest,2)}")
            col3.metric("Monthly Extra Payment", f"₹{round(extra,2)}")

            # Graph
            fig, ax = plt.subplots()
            ax.plot(df["Month"], df["Balance"])
            ax.set_title("Debt Reduction Over Time")
            ax.set_xlabel("Month")
            ax.set_ylabel("Balance ₹")
            st.pyplot(fig)

            # Download
            st.download_button("Download Plan", df.to_csv(index=False), "plan.csv")

        # -------- COMPARE --------
        if st.button("Compare Strategies"):

            results = {}

            for strat in ["Debt Snowball", "Debt Avalanche", "AI Optimized"]:
                df, interest = simulate(debts, extra, strat)
                months = df[df["Balance"] <= 0]["Month"].min()
                results[strat] = {"months": months, "interest": interest}

            df_res = pd.DataFrame([
                {
                    "Strategy": k,
                    "Months": v["months"],
                    "Interest ₹": round(v["interest"], 2)
                }
                for k, v in results.items()
            ])

            st.table(df_res)

            # AI Recommendation
            best = min(results.items(), key=lambda x: x[1]["interest"])
            st.success(f"💡 Recommended: {best[0]} (Lowest Interest)")

    if st.button("Restart"):
        st.session_state.clear()
