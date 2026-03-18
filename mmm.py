import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Debt Repayment Optimizer", layout="wide")

# ---------------- SESSION STATE ----------------
if "step" not in st.session_state:
    st.session_state.step = 1

# ---------------- STEP 1: USER INFO ----------------
if st.session_state.step == 1:
    st.title("💡 AI Debt Repayment Optimizer")
    st.header("Step 1: User Information")

    name = st.text_input("Enter your name")

    if st.button("Next"):
        st.session_state.name = name
        st.session_state.step = 2

# ---------------- STEP 2: DEBTS ----------------
elif st.session_state.step == 2:
    st.header("Step 2: Debt Details")

    num_debts = st.number_input("How many debts?", min_value=1, step=1, value=3)

    debts = []
    for i in range(num_debts):
        st.subheader(f"Debt {i+1}")
        loan_type = st.selectbox(f"Loan Type {i+1}",
                                 ["Credit Card", "Student Loan", "Personal Loan", "Other"],
                                 key=f"type{i}")
        balance = st.number_input(f"Balance ₹ {i+1}", key=f"b{i}")
        rate = st.number_input(f"Interest % {i+1}", key=f"r{i}")
        min_payment = st.number_input(f"Min Payment ₹ {i+1}", key=f"m{i}")

        debts.append({
            "type": loan_type,
            "balance": balance,
            "rate": rate,
            "min_payment": min_payment
        })

    col1, col2 = st.columns(2)
    if col1.button("Back"):
        st.session_state.step = 1
    if col2.button("Next"):
        st.session_state.debts = debts
        st.session_state.step = 3

# ---------------- STEP 3: FINANCIALS ----------------
elif st.session_state.step == 3:
    st.header("Step 3: Income & Expenses")

    income = st.number_input("Income", min_value=0.0)
    expenses = st.number_input("Expenses", min_value=0.0)
    discretionary = st.number_input("Discretionary", min_value=0.0)
    savings = st.number_input("Savings", min_value=0.0)
    emergency = st.number_input("Emergency Fund", min_value=0.0)

    col1, col2 = st.columns(2)
    if col1.button("Back"):
        st.session_state.step = 2
    if col2.button("Next"):
        st.session_state.income = income
        st.session_state.expenses = expenses
        st.session_state.discretionary = discretionary
        st.session_state.savings = savings
        st.session_state.emergency = emergency
        st.session_state.step = 4

# ---------------- STEP 4: RESULTS ----------------
elif st.session_state.step == 4:

    st.title("📊 Results Dashboard")

    debts = st.session_state.debts
    income = st.session_state.income
    expenses = st.session_state.expenses
    discretionary = st.session_state.discretionary
    savings = st.session_state.savings
    emergency = st.session_state.emergency

    strategy = st.radio("Choose Strategy", ["Debt Snowball", "Debt Avalanche", "AI Optimized"])

    lump_sum = st.number_input("Lump Sum", min_value=0)
    lump_month = st.number_input("Lump Sum Month", min_value=1, value=1)

    # ---------------- FIXED SIMULATION ----------------
    def simulate(debts, extra_payment, strategy):
        debts = [d.copy() for d in debts]
        schedule = []
        total_interest = 0
        month = 1

        while any(d["balance"] > 0 for d in debts) and month <= 120:

            # SORT BASED ON STRATEGY
            if strategy == "Debt Snowball":
                debts.sort(key=lambda x: x["balance"])
            elif strategy == "Debt Avalanche":
                debts.sort(key=lambda x: x["rate"], reverse=True)
            else:
                debts.sort(key=lambda x: x["rate"] * x["balance"], reverse=True)

            month_interest = 0

            # APPLY INTEREST
            for d in debts:
                if d["balance"] > 0:
                    interest = d["balance"] * (d["rate"] / 100 / 12)
                    d["balance"] += interest
                    month_interest += interest

            # PAY MINIMUMS
            for d in debts:
                if d["balance"] > 0:
                    d["balance"] -= d["min_payment"]

            # APPLY EXTRA TO PRIORITY DEBT
            for d in debts:
                if d["balance"] > 0:
                    extra = min(extra_payment, d["balance"])
                    d["balance"] -= extra
                    break

            # LUMP SUM
            if month == lump_month:
                for d in debts:
                    if d["balance"] > 0:
                        d["balance"] -= lump_sum
                        break

            total_interest += month_interest
            total_balance = sum(d["balance"] for d in debts)

            schedule.append({
                "Month": month,
                "Balance": total_balance
            })

            month += 1

        return pd.DataFrame(schedule), total_interest

    # ---------------- RUN ----------------
    if st.button("Run Optimizer"):

        extra = income - (expenses + discretionary + savings + emergency) - sum(d["min_payment"] for d in debts)

        if extra <= 0:
            st.error("No surplus income available")
        else:
            df, interest = simulate(debts, extra, strategy)

            st.success(f"{strategy} Selected")

            fig, ax = plt.subplots()
            ax.plot(df["Month"], df["Balance"])
            ax.set_title("Debt Payoff Progress")
            st.pyplot(fig)

            months = df[df["Balance"] <= 0]["Month"].min()
            if months:
                st.success(f"Debt-free in {months} months")
                st.info(f"Total Interest: ₹{round(interest,2)}")

    # ---------------- COMPARE ----------------
    if st.button("Compare All"):
        extra = income - (expenses + discretionary + savings + emergency) - sum(d["min_payment"] for d in debts)

        if extra > 0:
            results = {}
            for strat in ["Debt Snowball", "Debt Avalanche", "AI Optimized"]:
                df, interest = simulate(debts, extra, strat)
                months = df[df["Balance"] <= 0]["Month"].min()
                results[strat] = (months, interest)

            st.table(pd.DataFrame([
                {"Strategy": k, "Months": v[0], "Interest": round(v[1],2)}
                for k,v in results.items()
            ]))

    if st.button("Start Over"):
        st.session_state.step = 1
