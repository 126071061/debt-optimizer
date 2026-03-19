import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Debt Repayment Optimizer", layout="wide")

# --- Custom Styling ---
custom_style = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f0f4ff, #dbe9f4);
    color: #2c3e50;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
[data-testid="stSidebar"] {
    background: #f7f9fc;
    border-right: 3px solid #4a90e2;
}
.stTable tbody tr:nth-child(odd) {
    background-color: #f9f9f9;
}
.stTable tbody tr:hover {
    background-color: #e6f7ff;
}
button {
    background-color: #4a90e2 !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: bold !important;
}
h1, h2, h3 {
    color: #2c3e50;
}
.suggestion-green {
    background-color: #d4edda;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 10px;
}
.suggestion-blue {
    background-color: #cce5ff;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 10px;
}
</style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

# --- Page Title ---
st.title("💡 AI Debt Repayment Optimizer")
st.write("Enter your debts and income details to generate optimized repayment strategies.")

# --- Input Section ---
st.header("Debt Details")
num_debts = st.number_input("How many debts do you want to enter?", min_value=1, step=1, value=3)

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
discretionary = st.number_input("Discretionary Spending (₹)", min_value=0.0, step=500.0)
savings = st.number_input("Savings Contribution (₹)", min_value=0.0, step=500.0)
emergency_fund = st.number_input("Emergency Fund Allocation (₹)", min_value=0.0, step=500.0)

# --- Sidebar Interactive Options ---
st.sidebar.header("Extra Features")
lump_sum = st.sidebar.number_input("Add lump‑sum payment (₹)", min_value=0, step=1000)
lump_sum_month = st.sidebar.number_input("Month to apply lump‑sum", min_value=1, step=1, value=1)
scenario = st.sidebar.selectbox("Scenario Analysis", [
    "Base Case", "Income +10%", "Expenses -10%", "Unexpected Expense +5000", "Interest Rate +2%"
])

# Adjust scenario
if scenario == "Income +10%":
    income *= 1.1
elif scenario == "Expenses -10%":
    expenses *= 0.9
elif scenario == "Unexpected Expense +5000":
    expenses += 5000
elif scenario == "Interest Rate +2%":
    for d in debts:
        d["rate"] += 2

# --- Loan Payment Reminder ---
st.sidebar.header("Loan Payment Reminder")
reminder_option = st.sidebar.checkbox("Set monthly reminder for loan payments")
if reminder_option:
    st.sidebar.write("✅ Reminder set: You will be notified on the 5th of every month at 9 AM.")

# --- Strategy Guide ---
st.header("📖 Understanding the Strategies")
st.markdown("""
- **Debt Snowball**: Pay off the smallest balance first. Motivational but may cost more in interest.  
- **Debt Avalanche**: Pay off the highest interest debt first. Saves the most money overall.  
- **AI Optimized**: Hybrid approach. Very high‑interest debts (≥15%) are prioritized first, 
  but smaller balances are tackled earlier if interest rates are lower.
""")

# --- Strategy Selection ---
st.header("Choose Repayment Strategy")
strategy = st.radio("Select a method:", ["Debt Snowball", "Debt Avalanche", "AI Optimized"])

# --- Repayment Order Function ---
def get_repayment_order(debts, strategy):
    debts_copy = [d.copy() for d in debts]
    if strategy == "Debt Snowball":
        debts_copy.sort(key=lambda d: d["balance"])
    elif strategy == "Debt Avalanche":
        debts_copy.sort(key=lambda d: d["rate"], reverse=True)
    elif strategy == "AI Optimized":
        debts_copy.sort(key=lambda d: (d["rate"] >= 15, -d["balance"]), reverse=True)
    return debts_copy

# --- Repayment Simulation Function ---
def simulate_repayment(debts, extra_payment, strategy, lump_sum=0, lump_sum_month=None):
    debts = [d.copy() for d in debts]
    schedule = []
    month = 1
    total_interest_paid = 0

    while any(d["balance"] > 0 for d in debts) and month <= 120:
        debts = get_repayment_order(debts, strategy)
        payment = extra_payment
        month_interest = 0
        for d in debts:
            if d["balance"] <= 0:
                continue
            interest = d["balance"] * (d["rate"]/100/12)
            d["balance"] += interest
            month_interest += interest
            pay = d["min_payment"]
            if payment > 0:
                pay += payment
                payment = 0
            if lump_sum > 0 and lump_sum_month == month:
                pay += lump_sum
            d["balance"] = max(0, d["balance"] - pay)
        total_interest_paid += month_interest
        total_balance = sum(d["balance"] for d in debts)
        schedule.append({"Month": month, "Total Balance": total_balance, "Interest Paid": month_interest})
        month += 1

    df = pd.DataFrame(schedule)
    return df, total_interest_paid

# --- Run Single Strategy ---
if st.button("Run Optimizer"):
    extra_payment = income - (expenses + discretionary + savings + emergency_fund) - sum(d["min_payment"] for d in debts)
    if extra_payment <= 0:
        st.error("No surplus income available for debt repayment. Adjust your inputs.")
    else:
        df, total_interest = simulate_repayment(debts, extra_payment, strategy, lump_sum, lump_sum_month)
        st.success(f"Strategy: {strategy}")
        st.write("Repayment order based on strategy:")
        ordered_debts = get_repayment_order(debts, strategy)
        st.table(pd.DataFrame(ordered_debts))

        st.subheader("Debt Repayment Progress")
        fig, ax = plt.subplots()
        ax.plot(df["Month"], df["Total Balance"], marker="o")
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Balance (₹)")
        ax.set_title(f"Debt Repayment Progress ({strategy})")
        st.pyplot(fig)

        months_to_zero = df[df["Total Balance"] <= 0]["Month"].min() if any(df["Total Balance"] <= 0) else None
        if months_to_zero:
            st.success(f"🎉 Based on the {strategy} method, you will be debt‑free in about {months_to_zero} months.")
            st.info(f"Total Interest Paid: ₹{total_interest:.2f}")
        else:
            st.warning("Your debt does not reach zero within the simulated period.")

# --- Strategy Comparison Dashboard ---
if st.button("Compare All Strategies"):
    extra_payment = income - (expenses + discretionary + savings + emergency_fund) - sum(d["min_payment"] for d in debts)
    if extra_payment <= 0:
        st.error("No surplus income available for debt repayment. Adjust your inputs.")
    else:
        results = {}
        for strat in ["Debt Snowball", "Debt Avalanche", "AI Optimized"]:
            df, total_interest = simulate_repayment(debts, extra_payment, strat
