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

# --- Your existing debt input, income/expenses, sidebar, strategy selection, functions ---
# (keep all the code you already have here unchanged)

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
             "Savings vs Snowball (₹)": round(results["Debt Snowball"]["interest"] - res["interest"], 2)
             }
            for strat, res in results.items()
        ])
        st.subheader("📊 Strategy Comparison Summary")
        st.table(summary)

        # Repayment Orders
        st.subheader("Repayment Order by Strategy")
        cols = st.columns(3)
        for i, strat in enumerate(results.keys()):
            with cols[i]:
                st.markdown(f"**{strat}**")
                st.table(pd.DataFrame(results[strat]["order"]))

        # --- Suggestions with badges ---
        st.subheader("💡 Suggestions")
        best_interest = min(results.items(), key=lambda x: x[1]["interest"])
        fastest = min(results.items(), key=lambda x: x[1]["months"] if x[1]["months"] else float("inf"))

        st.markdown(f"""
        <div class="suggestion-green">
        💡 <b>Lowest Interest Paid:</b> {best_interest[0]} strategy (₹{best_interest[1]['interest']:.2f})
        </div>
        <div class="suggestion-blue">
        🚀 <b>Fastest Debt-Free:</b> {fastest[0]} strategy ({fastest[1]['months']} months)
        </div>
        """, unsafe_allow_html=True)
