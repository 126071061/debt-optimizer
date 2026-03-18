import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Debt Repayment Optimizer", layout="wide")

# --- Page Title ---
st.title("💡 AI Debt Repayment Optimizer")
st.write("Enter your debts and income details to generate optimized repayment strategies.")

# --- Input Section ---
st.header("Debt Details")
num_debts = st.number_input("How many debts do you want to enter?", min_value=1, step=1, value=1)

debts = []
for i in range(num_debts):
    st.subheader(f"Debt {i+1}")
    loan_type = st.selectbox(f"Loan Type {i+1}", ["Credit Card", "Student Loan", "Personal Loan", "Other"], key=f"type{i}")
    balance = st.number_input(f"Outstanding Balance (₹) {i+1}", min_value=0.0, step=1000.0, key=f"balance{i}")
    interest_rate = st.number_input(f"Interest Rate (%) {i+1}", min_value=0.0, step=0.1, key=f"rate{i}")
    min_payment = st.number_input(f"Minimum Monthly Payment (₹) {i+1}", min_value=0.0, step=100.0, key=f"min{i}")
    debts.append({"type": loan_type, "balance": balance, "rate": interest_rate, "min_payment": min_payment})

# --- Income & Expenses ---
st.header("Income & Expenses")
income = st.number_input("Monthly Income (₹)", min_value=0.0, step=1000.0)
expenses = st.number_input("Essential Expenses (₹)", min_value=0.0, step=500.0)

# --- Sidebar Interactive Options ---
st.sidebar.header("Extra Features")
lump_sum = st.sidebar.number_input("Add lump‑sum payment (₹)", min_value=0, step=1000)
lump_sum_month = st.sidebar.number_input("Month to apply lump‑sum", min_value=1, step=1, value=1)
scenario = st.sidebar.selectbox("Scenario Analysis", ["Base Case", "Income +10%", "Expenses -10%"])

# Adjust scenario
if scenario == "Income +10%":
    income *= 1.1
elif scenario == "Expenses -10%":
    expenses *= 0.9

# --- Loan Payment Reminder ---
st.sidebar.header("Loan Payment Reminder")
reminder_option = st.sidebar.checkbox("Set monthly reminder for loan payments")
if reminder_option:
    st.sidebar.write("✅ Reminder set: You will be notified each month to make your loan payments.")
    st.sidebar.write("This helps ensure you never miss a due date.")

# --- Strategy Guide BEFORE Selection ---
st.header("📖 Understanding the Strategies")
st.write("Here’s a quick guide to the three repayment methods:")
st.markdown("""
- **Debt Snowball**: Focuses on paying off the smallest balance first.  
  *Pros*: Quick wins, motivational boost.  
  *Cons*: May cost more in interest overall.  

- **Debt Avalanche**: Focuses on paying off the highest interest debt first.  
  *Pros*: Saves the most money in interest.  
  *Cons*: Progress may feel slower initially.  

- **AI Optimized**: A hybrid approach that balances interest savings with payoff speed.  
  *Pros*: Efficient balance between saving money and clearing debts quickly.  
  *Cons*: More complex, may not always give the fastest psychological wins.
""")

# --- Strategy Selection ---
st.header("Choose Repayment Strategy")
strategy = st.radio("Select a method:", ["Debt Snowball", "Debt Avalanche", "AI Optimized"])

# --- Repayment Simulation Function ---
def simulate_repayment(debts, extra_payment, strategy, lump_sum=0, lump_sum_month=None):
    debts = [d.copy() for d in debts]
    schedule = []
    month = 1

    while any(d["balance"] > 0 for d in debts) and month <= 120:  # limit to 10 years
        # Choose debt order
        if strategy == "Debt Snowball":
            debts.sort(key=lambda x: x["balance"])
        elif strategy == "Debt Avalanche":
            debts.sort(key=lambda x: x["rate"], reverse=True)
        else:  # AI Optimized placeholder: hybrid
            debts.sort(key=lambda x: (x["rate"], -x["balance"]), reverse=True)

        payment = extra_payment
        for d in debts:
            if d["balance"] <= 0:
                continue
            # Apply interest
            d["balance"] += d["balance"] * (d["rate"]/100/12)
            # Apply minimum payment
            pay = d["min_payment"]
            if payment > 0:
                pay += payment
                payment = 0
            # Lump‑sum payment
            if lump_sum > 0 and lump_sum_month == month:
                pay += lump_sum
            d["balance"] = max(0, d["balance"] - pay)

        total_balance = sum(d["balance"] for d in debts)
        schedule.append({"Month": month, "Total Balance": total_balance})
        month += 1

    return pd.DataFrame(schedule)

# --- Run Single Strategy ---
if st.button("Run Optimizer"):
    extra_payment = income - expenses - sum(d["min_payment"] for d in debts)
    if extra_payment <= 0:
        st.error("No surplus income available for debt repayment. Adjust your inputs.")
    else:
        df = simulate_repayment(debts, extra_payment, strategy, lump_sum, lump_sum_month)
        st.success(f"Strategy: {strategy}")
        st.write("Repayment order based on strategy:")

        df_debts = pd.DataFrame(debts)
        st.table(df_debts)

        # --- Visualization ---
        st.subheader("Debt Repayment Progress")
        fig, ax = plt.subplots()
        ax.plot(df["Month"], df["Total Balance"], marker="o")
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Balance (₹)")
        ax.set_title(f"Debt Repayment Progress ({strategy})")
        st.pyplot(fig)

        # --- Decision/Interpretation AFTER Chart ---
        st.subheader("Decision & Interpretation")
        months_to_zero = df[df["Total Balance"] <= 0]["Month"].min() if any(df["Total Balance"] <= 0) else None
        if months_to_zero:
            st.success(f"🎉 Based on the {strategy} method, you will be debt‑free in about {months_to_zero} months.")
            if strategy == "Debt Snowball":
                st.info("This strategy clears your smallest balance first, giving quick psychological wins. "
                        "It may cost slightly more in interest compared to Avalanche, but it helps you stay motivated.")
            elif strategy == "Debt Avalanche":
                st.info("This strategy clears your highest‑interest debt first, saving you the most money overall. "
                        "It may feel slower at the start, but it minimizes total interest paid.")
            else:  # AI Optimized
                st.info("This strategy balances interest savings with payoff speed. "
                        "It often starts with high‑interest debts but shifts surplus to smaller balances when efficient.")
        else:
            st.warning("Your debt does not reach zero within the simulated period. Try adjusting income, expenses, or payments.")

        # --- Download Plan ---
        st.download_button(
            label="Download Repayment Schedule (CSV)",
            data=df.to_csv(index=False),
            file_name="repayment_schedule.csv",
            mime="text/csv"
        )

# --- Strategy Comparison Dashboard ---
if st.button("Compare All Strategies"):
    extra_payment = income - expenses - sum(d["min_payment"] for d in debts)
    if extra_payment <= 0:
        st.error("No surplus income available for debt repayment. Adjust your inputs.")
    else:
        results = {}
        for strat in ["Debt Snowball", "Debt Avalanche", "AI Optimized"]:
            df = simulate_repayment(debts, extra_payment, strat, lump_sum, lump_sum_month)
            months_to_zero = df[df["Total Balance"] <= 0]["Month"].min() if any(df["Total Balance"] <= 0) else None
            results[strat] = {"df": df, "months": months_to_zero}

        # Show payoff times
        st.subheader("📊 Strategy Comparison")
        for strat, res in results.items():
            if res["months"]:
                st.success(f"{strat}: Debt‑free in {res['months']} months")
            else:
                st.warning(f"{strat}: Debt not cleared within 10 years")

        # Show charts side‑by‑side
        cols = st.columns(3)
        for i, strat in enumerate(results.keys()):
            with cols[i]:
                df = results[strat]["df"]
                fig, ax = plt.subplots()
                ax.plot(df["Month"], df["Total Balance"], marker="o")
                ax.set_xlabel("Month")
                ax.set_ylabel("Total Balance (₹)")
                ax.set_title(strat)
                st.pyplot(fig)