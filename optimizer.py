import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.markdown(
    """
    <style>

    /* 🌐 FULL APP BACKGROUND */
    .stApp {
        background: linear-gradient(135deg, #1e3c72, #2a5298, #6a11cb);
        color: white;
    }

    /* 🧾 TEXT */
    h1, h2, h3, h4, h5, h6, p, label {
        color: white !important;
    }

    /* 🎯 SIDEBAR (EXTRA FEATURES) */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50, #4ca1af);
        color: white;
        padding: 15px;
        border-right: 2px solid rgba(255,255,255,0.2);
    }

    /* Sidebar text */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: white !important;
    }

    /* 🔘 BUTTONS */
    .stButton>button {
        background: linear-gradient(to right, #00c6ff, #0072ff);
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-size: 16px;
        border: none;
    }

    /* 📥 INPUT BOXES */
    .stTextInput>div>div>input,
    .stNumberInput input,
    .stSelectbox div {
        background-color: rgba(255,255,255,0.9);
        color: black;
        border-radius: 6px;
    }

    /* 📊 TABLES */
    .stDataFrame {
        background-color: rgba(255,255,255,0.1);
        color: white;
    }

    /* 📦 CARD EFFECT (optional nice touch) */
    .css-1d391kg {
        background-color: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)
# --- Page Title ---
st.title("💰AI-Powered Debt Repayment Optimizer")
st.write("Enter your debts and income details to generate optimized repayment strategies.")
# --- User Profile Section ---
st.header("👤 User Profile")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Name")
    age_group = st.selectbox("Age Group", ["18-25", "26-35", "36-50", "50+"])

with col2:
    email = st.text_input("Email (optional)")
    employment = st.selectbox("Employment Type", ["Student", "Salaried", "Self-employed", "Business"])
if name:
    st.success(f"Welcome {name}! Let's optimize your debt smartly 🚀")
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

# --- Strategy Guide BEFORE Selection ---
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
        # Hybrid: prioritize very high interest first, then smaller balances
        debts_copy.sort(
    key=lambda d: (
        -d["rate"] if d["rate"] >= 15 else 0,  # prioritize high interest
        d["balance"]                           # then smallest balance
    )
)
    return debts_copy

# --- Repayment Simulation Function with Interest Tracking ---
def simulate_repayment(debts, extra_payment, strategy, lump_sum=0, lump_sum_month=None):
    debts = [d.copy() for d in debts]
    schedule = []
    month = 1
    total_interest_paid = 0

    while any(d["balance"] > 0 for d in debts) and month <= 120:  # limit to 10 years
        # Choose debt order
        debts = get_repayment_order(debts, strategy)

        payment = extra_payment
        month_interest = 0
        for d in debts:
            if d["balance"] <= 0:
                continue
            # Apply interest
            interest = d["balance"] * (d["rate"]/100/12)
            d["balance"] += interest
            month_interest += interest

            # Apply payments
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
            st.info(f"Total Interest Paid: ₹{total_interest:.2f}")
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
    extra_payment = income - (expenses + discretionary + savings + emergency_fund) - sum(d["min_payment"] for d in debts)
    if extra_payment <= 0:
        st.error("No surplus income available for debt repayment. Adjust your inputs.")
    else:
        results = {}
        for strat in ["Debt Snowball", "Debt Avalanche", "AI Optimized"]:
            df, total_interest = simulate_repayment(debts, extra_payment, strat, lump_sum, lump_sum_month)
            months_to_zero = df[df["Total Balance"] <= 0]["Month"].min() if any(df["Total Balance"] <= 0) else None
            results[strat] = {
                "df": df,
                "months": months_to_zero,
                "interest": total_interest,
                "order": get_repayment_order(debts, strat)
            }

        # 📊 Show summary table
        summary = pd.DataFrame([
            {"Strategy": strat,
             "Debt-Free Months": res["months"],
             "Total Interest Paid (₹)": round(res["interest"], 2),
             "Savings  (₹)": round(results["Debt Snowball"]["interest"] - res["interest"], 2)
             }
            for strat, res in results.items()
        ])
        st.subheader("📊 Strategy Comparison Summary")
        st.table(summary)
# --- Final Recommendation ---
        st.subheader("💡 Best Strategy Recommendation")

        # Find the strategy with minimum interest paid
        best_strategy = summary.loc[summary["Total Interest Paid (₹)"].idxmin()]

        st.success(
            f"Based on your inputs, the **{best_strategy['Strategy']}** method "
            f"is the most cost‑effective option. It will make you debt‑free in about "
            f"{int(best_strategy['Debt-Free Months'])} months with a total interest cost of "
            f"₹{best_strategy['Total Interest Paid (₹)']:.2f}."
        )

        # Suggestions for the user
        st.info(
            "👉 Suggestions:\n"
            "- Stick to the recommended strategy for maximum savings.\n"
            "- If you prefer faster psychological wins, Snowball may still be motivating even if it costs more.\n"
            "- Re‑run the optimizer with different scenarios (income changes, unexpected expenses) to stress‑test your plan.\n"
            "- Consider applying lump‑sum payments earlier to accelerate debt clearance."
        )
