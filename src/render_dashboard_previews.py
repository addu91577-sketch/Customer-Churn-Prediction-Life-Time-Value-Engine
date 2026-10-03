"""
Customer Churn & LTV Engine - Power BI Dashboard Visual Layout Generator
Renders publication-grade 16:9 executive dashboard visual mockups for Pages 1, 2, and 3.
Author: Adarsh Kumar Pandey
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'


def render_page1_executive(df):
    fig = plt.figure(figsize=(16, 9), facecolor='#F8F9FA')
    gs = gridspec.GridSpec(3, 4, figure=fig, height_ratios=[0.8, 2.2, 2.2], wspace=0.3, hspace=0.35)
    
    # Header Banner
    ax_title = fig.add_axes([0.05, 0.92, 0.90, 0.06])
    ax_title.set_facecolor('#002050')
    ax_title.text(0.02, 0.5, "TELCO CUSTOMER CHURN & LTV ENGINE | EXECUTIVE OVERVIEW", 
                  fontsize=16, weight='bold', color='white', va='center')
    ax_title.text(0.98, 0.5, "Page 1 of 3 | Live Power BI Report", 
                  fontsize=11, color='#CBD5E1', va='center', ha='right')
    ax_title.axis('off')
    
    # 4 Top KPI Cards
    kpis = [
        ("Total Subscribers", f"{len(df):,}", "#1E293B", "#F1F5F9"),
        ("Churn Rate", f"{(df['Churn']=='Yes').mean():.1%}", "#DC2626", "#FEE2E2"),
        ("Monthly Revenue (MRR)", f"${df['MonthlyCharges'].sum()/1000:,.1f}K", "#0284C7", "#E0F2FE"),
        ("Annual Revenue At Risk", f"${df['Annual_Revenue_At_Risk'].sum()/1000000:,.2f}M", "#D97706", "#FEF3C7")
    ]
    
    for i, (title, val, text_c, bg_c) in enumerate(kpis):
        ax = fig.add_subplot(gs[0, i])
        ax.set_facecolor(bg_c)
        ax.text(0.5, 0.65, title.upper(), fontsize=10, weight='bold', color='#475569', ha='center', va='center')
        ax.text(0.5, 0.30, val, fontsize=20, weight='bold', color=text_c, ha='center', va='center')
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('#CBD5E1')
            spine.set_linewidth(1.2)
            
    # Chart 1: Churn by Contract Type (Horizontal Bar)
    ax_contract = fig.add_subplot(gs[1, 0:2])
    contract_churn = df.groupby('Contract')['Churn'].apply(lambda x: (x == 'Yes').mean() * 100).sort_values()
    colors = ['#10B981', '#3B82F6', '#EF4444']
    bars = ax_contract.barh(contract_churn.index, contract_churn.values, color=colors, height=0.55, edgecolor='#334155')
    ax_contract.set_title("Churn Rate by Contract Type (%)", fontsize=12, weight='bold', pad=10)
    ax_contract.set_xlabel("Churn Rate (%)", fontsize=10)
    ax_contract.set_xlim(0, 50)
    for bar in bars:
        ax_contract.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f"{bar.get_width():.1f}%", 
                         va='center', fontsize=10, weight='bold')
        
    # Chart 2: Risk Tier Distribution (Donut Chart)
    ax_donut = fig.add_subplot(gs[1, 2:4])
    risk_counts = df['Risk_Tier'].value_counts()[['Low Risk', 'Medium Risk', 'High Risk']]
    donut_colors = ['#10B981', '#F59E0B', '#EF4444']
    wedges, texts, autotexts = ax_donut.pie(
        risk_counts, labels=risk_counts.index, colors=donut_colors, autopct='%1.1f%%',
        startangle=140, pctdistance=0.75, wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
    )
    for at in autotexts:
        at.set_color('white')
        at.set_weight('bold')
    ax_donut.set_title("Customer Risk Tier Segmentation", fontsize=12, weight='bold', pad=10)
    
    # Chart 3: Churn Rate Across Tenure Cohorts
    ax_tenure = fig.add_subplot(gs[2, 0:4])
    cohort_order = ['0-12 Months', '13-24 Months', '25-36 Months', '37-48 Months', '49-60 Months', '61-72 Months']
    tenure_stats = df.groupby('Tenure_Cohort', observed=False).agg(
        total=('customerID', 'count'),
        churn_rate=('Churn', lambda x: (x == 'Yes').mean() * 100)
    ).reindex(cohort_order)
    
    x = np.arange(len(cohort_order))
    bars = ax_tenure.bar(x, tenure_stats['churn_rate'], color='#3B82F6', width=0.5, edgecolor='#1E3A8A', alpha=0.9)
    # Highlight highest cohort
    bars[0].set_color('#EF4444')
    ax_tenure.set_title("Early-Tenure Cliff: Churn Rate by Customer Lifecycle Stage (%)", fontsize=12, weight='bold', pad=10)
    ax_tenure.set_xticks(x)
    ax_tenure.set_xticklabels(cohort_order, fontsize=10, weight='bold')
    ax_tenure.set_ylabel("Churn Rate (%)", fontsize=10)
    ax_tenure.set_ylim(0, 55)
    for bar in bars:
        ax_tenure.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.2, f"{bar.get_height():.1f}%",
                       ha='center', fontsize=9, weight='bold')
        
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.92])
    os.makedirs('visuals', exist_ok=True)
    plt.savefig('visuals/powerbi_dashboard_page1_executive.png', dpi=200)
    plt.close()
    print("Saved visuals/powerbi_dashboard_page1_executive.png")


def render_page2_diagnostics(df):
    fig = plt.figure(figsize=(16, 9), facecolor='#F8F9FA')
    gs = gridspec.GridSpec(2, 2, figure=fig, height_ratios=[1, 1], wspace=0.25, hspace=0.35)
    
    # Header Banner
    ax_title = fig.add_axes([0.05, 0.92, 0.90, 0.06])
    ax_title.set_facecolor('#0F172A')
    ax_title.text(0.02, 0.5, "TELCO CHURN ENGINE | ROOT-CAUSE RISK DIAGNOSTICS", 
                  fontsize=16, weight='bold', color='white', va='center')
    ax_title.text(0.98, 0.5, "Page 2 of 3 | Diagnostic Deep-Dive", 
                  fontsize=11, color='#CBD5E1', va='center', ha='right')
    ax_title.axis('off')
    
    # 1. Internet Service & Tech Support Matrix
    ax1 = fig.add_subplot(gs[0, 0])
    sub_df = df[df['InternetService'] != 'No']
    sns.barplot(data=sub_df, x='InternetService', y=df['Churn']=='Yes', hue='TechSupport', 
                palette=['#EF4444', '#10B981'], ax=ax1, errorbar=None, edgecolor='black')
    ax1.set_title("Internet Service vs Tech Support Churn Rate", fontsize=12, weight='bold')
    ax1.set_ylabel("Churn Proportion", fontsize=10)
    ax1.set_ylim(0, 0.6)
    
    # 2. Payment Method Impact
    ax2 = fig.add_subplot(gs[0, 1])
    pm_churn = df.groupby('PaymentMethod')['Churn'].apply(lambda x: (x == 'Yes').mean() * 100).sort_values(ascending=False)
    colors = ['#EF4444' if 'Electronic' in pm else '#64748B' for pm in pm_churn.index]
    ax2.barh(pm_churn.index, pm_churn.values, color=colors, height=0.55, edgecolor='black')
    ax2.set_title("Payment Method Friction: Churn Rate (%)", fontsize=12, weight='bold')
    ax2.set_xlabel("Churn Rate (%)", fontsize=10)
    
    # 3. Monthly Charges vs Churn Probability Scatter
    ax3 = fig.add_subplot(gs[1, 0])
    sample_df = df.sample(n=1000, random_state=42)
    sns.scatterplot(
        data=sample_df, x='MonthlyCharges', y='Churn_Probability', hue='InternetService',
        palette={'DSL': '#3B82F6', 'Fiber optic': '#EF4444', 'No': '#10B981'},
        alpha=0.65, ax=ax3, s=40
    )
    ax3.set_title("Price Fatigue: Monthly Charges vs Predicted Churn Probability", fontsize=12, weight='bold')
    ax3.set_xlabel("Monthly Charges ($)", fontsize=10)
    ax3.set_ylabel("Predicted Churn Probability", fontsize=10)
    
    # 4. Service Add-on Protection Index
    ax4 = fig.add_subplot(gs[1, 1])
    services = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport']
    rates_no = [ (df[df[s] == 'No']['Churn'] == 'Yes').mean() * 100 for s in services ]
    rates_yes = [ (df[df[s] == 'Yes']['Churn'] == 'Yes').mean() * 100 for s in services ]
    
    y_pos = np.arange(len(services))
    width = 0.35
    ax4.barh(y_pos - width/2, rates_no, width, label='Without Service (High Churn)', color='#EF4444', edgecolor='black')
    ax4.barh(y_pos + width/2, rates_yes, width, label='With Service (Protected)', color='#10B981', edgecolor='black')
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(services, fontsize=10, weight='bold')
    ax4.set_title("Add-on Service Protection Effect on Churn (%)", fontsize=12, weight='bold')
    ax4.set_xlabel("Churn Rate (%)", fontsize=10)
    ax4.legend(loc='lower right', fontsize=9)
    
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.92])
    plt.savefig('visuals/powerbi_dashboard_page2_diagnostics.png', dpi=200)
    plt.close()
    print("Saved visuals/powerbi_dashboard_page2_diagnostics.png")


def render_page3_ltv_engine(df):
    fig = plt.figure(figsize=(16, 9), facecolor='#F8F9FA')
    gs = gridspec.GridSpec(2, 2, figure=fig, height_ratios=[1, 1], wspace=0.25, hspace=0.35)
    
    # Header Banner
    ax_title = fig.add_axes([0.05, 0.92, 0.90, 0.06])
    ax_title.set_facecolor('#064E3B')
    ax_title.text(0.02, 0.5, "TELCO CHURN ENGINE | CUSTOMER LTV & PROACTIVE RETENTION TARGETING", 
                  fontsize=16, weight='bold', color='white', va='center')
    ax_title.text(0.98, 0.5, "Page 3 of 3 | Value Preservation Engine", 
                  fontsize=11, color='#A7F3D0', va='center', ha='right')
    ax_title.axis('off')
    
    # 1. LTV by Contract Type
    ax1 = fig.add_subplot(gs[0, 0])
    sns.boxplot(data=df, x='Contract', y='Customer_LTV', palette=['#EF4444', '#F59E0B', '#10B981'], ax=ax1, width=0.5)
    ax1.set_title("Customer Lifetime Value (LTV) Distribution by Contract", fontsize=12, weight='bold')
    ax1.set_ylabel("Projected Customer LTV ($)", fontsize=10)
    ax1.set_xlabel("Contract Type", fontsize=10)
    
    # 2. Value at Risk by Recommended Retention Action
    ax2 = fig.add_subplot(gs[0, 1])
    action_var = df.groupby('Recommended_Retention_Action')['Annual_Revenue_At_Risk'].sum().sort_values()
    colors = sns.color_palette("rocket", len(action_var))
    bars = ax2.barh(action_var.index, action_var.values / 1000, color=colors, height=0.55, edgecolor='black')
    ax2.set_title("Prescriptive Retention Queue: Annual Revenue at Risk ($K)", fontsize=12, weight='bold')
    ax2.set_xlabel("Annual Revenue at Risk ($ in Thousands)", fontsize=10)
    
    # 3. LTV vs Churn Probability Quadrant
    ax3 = fig.add_subplot(gs[1, 0])
    sample_df = df.sample(n=800, random_state=42)
    sns.scatterplot(
        data=sample_df, x='Customer_LTV', y='Churn_Probability', hue='Risk_Tier',
        palette={'High Risk': '#EF4444', 'Medium Risk': '#F59E0B', 'Low Risk': '#10B981'},
        alpha=0.6, ax=ax3, s=45
    )
    # Add quadrant reference lines
    ax3.axhline(0.6, color='red', linestyle='--', alpha=0.5)
    ax3.axvline(3500, color='blue', linestyle='--', alpha=0.5)
    ax3.text(5000, 0.85, "HIGH VALUE / HIGH RISK\n(TOP PRIORITY RETENTION)", 
             fontsize=9, weight='bold', color='#DC2626', bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))
    ax3.set_title("Strategic Quadrant: Customer LTV vs Churn Probability", fontsize=12, weight='bold')
    ax3.set_xlabel("Customer LTV ($)", fontsize=10)
    ax3.set_ylabel("Churn Probability", fontsize=10)
    
    # 4. Projected Retention Campaign Economics
    ax4 = fig.add_subplot(gs[1, 1])
    categories = ['Total High-Risk Revenue Exposure', 'Projected Saved ARR (25% Save)', 'Estimated Campaign Cost', 'Net Projected Value Added']
    values = [2448.75, 612.18, 79.06, 533.12]
    colors = ['#EF4444', '#3B82F6', '#64748B', '#10B981']
    bars = ax4.bar(categories, values, color=colors, width=0.45, edgecolor='black')
    ax4.set_title("Proactive Campaign Economics & Financial Return ($ in Thousands)", fontsize=12, weight='bold')
    ax4.set_ylabel("Amount ($K)", fontsize=10)
    ax4.set_xticklabels(categories, rotation=15, ha='right', fontsize=9, weight='bold')
    for bar in bars:
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20, f"${bar.get_height():,.0f}K",
                 ha='center', fontsize=9, weight='bold')
        
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.92])
    plt.savefig('visuals/powerbi_dashboard_page3_ltv_engine.png', dpi=200)
    plt.close()
    print("Saved visuals/powerbi_dashboard_page3_ltv_engine.png")


def main():
    df = pd.read_csv('data/telco_churn_powerbi_dataset.csv')
    render_page1_executive(df)
    render_page2_diagnostics(df)
    render_page3_ltv_engine(df)
    print("All Power BI dashboard previews rendered successfully!")


if __name__ == '__main__':
    main()
