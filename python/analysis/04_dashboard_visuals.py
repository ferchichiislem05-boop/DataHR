"""
HR Analytics — Dashboard Visuals (all 5 pages)
Generates professional PNG exports to powerbi/visuals/
Run from the project root.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import os, warnings
warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA     = r"C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\processed\hr_cleaned.csv"
TREND    = r"C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\exports\dim_hiring_trend.csv"
MANAGERS = r"C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\exports\dim_manager_scoreboard.csv"
OUT_DIR  = r"C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\powerbi\visuals"
os.makedirs(OUT_DIR, exist_ok=True)

df      = pd.read_csv(DATA)
trend   = pd.read_csv(TREND, parse_dates=["date"])
mgr_df  = pd.read_csv(MANAGERS)

# ── Colour palette ─────────────────────────────────────────────────────────────
BG        = "#F8F9FA"
PANEL     = "#FFFFFF"
DARK      = "#1A1A2E"
BLUE      = "#2980B9"
TEAL      = "#16A085"
RED       = "#C0392B"
ORANGE    = "#E67E22"
GREEN     = "#27AE60"
PURPLE    = "#8E44AD"
GREY      = "#95A5A6"
ACCENT    = "#2C3E50"
PALETTE   = [BLUE, TEAL, ORANGE, RED, PURPLE, GREEN, GREY]

plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "axes.facecolor":   PANEL,
    "figure.facecolor": BG,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.edgecolor":   "#CCCCCC",
    "axes.labelcolor":  DARK,
    "xtick.color":      DARK,
    "ytick.color":      DARK,
    "text.color":       DARK,
    "axes.titleweight": "bold",
    "axes.titlesize":   11,
    "axes.labelsize":   9,
    "xtick.labelsize":  8,
    "ytick.labelsize":  8,
})

# ── Helpers ────────────────────────────────────────────────────────────────────
def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  Saved: {name}")

def attrition_color(rate):
    if rate >= 40: return RED
    if rate >= 25: return ORANGE
    return GREEN

def add_page_title(fig, title, subtitle="HR Analytics Dashboard"):
    fig.text(0.5, 0.98, title, ha="center", va="top",
             fontsize=18, fontweight="bold", color=DARK)
    fig.text(0.5, 0.955, subtitle, ha="center", va="top",
             fontsize=10, color=GREY)

def kpi_card(ax, value, label, color=BLUE, fmt="{:.0f}"):
    ax.set_facecolor(color)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.58, fmt.format(value), ha="center", va="center",
            fontsize=22, fontweight="bold", color="white")
    ax.text(0.5, 0.22, label, ha="center", va="center",
            fontsize=8.5, color="white", alpha=0.9)

# ── Pre-compute KPIs ───────────────────────────────────────────────────────────
total      = len(df)
active     = int((df["is_attrition"] == 0).sum())
attrited   = int(df["is_attrition"].sum())
attr_rate  = round(df["is_attrition"].mean() * 100, 1)
ret_rate   = round(100 - attr_rate, 1)
avg_tenure = round(df["tenure_years"].mean(), 1)
avg_exp    = round(df["total_experience"].mean(), 1)

dept_attr = (df.groupby("department")["is_attrition"]
             .agg(headcount="count", attritions="sum", rate="mean")
             .assign(rate=lambda x: (x["rate"]*100).round(1))
             .sort_values("rate", ascending=False))

grade_attr = (df.groupby("grade")["is_attrition"]
              .agg(headcount="count", attritions="sum", rate="mean")
              .assign(rate=lambda x: (x["rate"]*100).round(1))
              .sort_values("rate", ascending=False))

tenure_attr = (df.groupby("tenure_band")["is_attrition"]
               .agg(headcount="count", attritions="sum", rate="mean")
               .assign(rate=lambda x: (x["rate"]*100).round(1)))

age_attr = (df.groupby("age_group")["is_attrition"]
             .agg(headcount="count", attritions="sum", rate="mean")
             .assign(rate=lambda x: (x["rate"]*100).round(1)))

visa_attr = (df.groupby("visa_type")["is_attrition"]
              .agg(headcount="count", attritions="sum", rate="mean")
              .assign(rate=lambda x: (x["rate"]*100).round(1))
              .sort_values("rate", ascending=False))

marital_attr = (df.groupby("marital_status")["is_attrition"]
                .agg(headcount="count", attritions="sum", rate="mean")
                .assign(rate=lambda x: (x["rate"]*100).round(1)))

dept_hc = df["department"].value_counts()
gender  = df["gender"].value_counts()
marital = df["marital_status"].value_counts()

stab_order = ["5+ Years","4+ Years","3+ Years","2+ Years","1+ Years","<1 Year"]
stability  = df["stability"].value_counts().reindex(stab_order).fillna(0)

tenure_order = ["<1yr","1yr","2yr","3yr","4yr","5yr","6+yr"]
age_order    = ["<25","25-29","30-34","35-39","40-49"]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("Building Page 1: Executive Summary...")

fig = plt.figure(figsize=(18, 11), facecolor=BG)
add_page_title(fig, "Executive Summary", "HR Analytics Dashboard  |  May 2026")

gs = gridspec.GridSpec(3, 6, figure=fig,
                        top=0.92, bottom=0.05,
                        left=0.04, right=0.98,
                        hspace=0.5, wspace=0.35)

# Row 0 — 6 KPI cards
cards = [
    (total,     "Total Headcount",     DARK,   "{:.0f}"),
    (active,    "Active Employees",    GREEN,  "{:.0f}"),
    (attrited,  "Total Attritions",    RED,    "{:.0f}"),
    (attr_rate, "Attrition Rate",      ORANGE, "{:.1f}%"),
    (ret_rate,  "Retention Rate",      TEAL,   "{:.1f}%"),
    (avg_tenure,"Avg Tenure (yrs)",    BLUE,   "{:.1f}"),
]
for i, (val, lbl, col, fmt) in enumerate(cards):
    ax = fig.add_subplot(gs[0, i])
    kpi_card(ax, val, lbl, col, fmt)

# Row 1 left — Dept headcount bar
ax_dept = fig.add_subplot(gs[1:, :3])
colors_dept = [PALETTE[i % len(PALETTE)] for i in range(len(dept_hc))]
bars = ax_dept.barh(dept_hc.index[::-1], dept_hc.values[::-1],
                     color=colors_dept[::-1], edgecolor="none", height=0.6)
for bar, val in zip(bars, dept_hc.values[::-1]):
    ax_dept.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                 str(val), va="center", fontsize=9, fontweight="bold", color=DARK)
ax_dept.set_title("Headcount by Department", pad=10)
ax_dept.set_xlabel("Employees")
ax_dept.set_xlim(0, dept_hc.max() * 1.18)
ax_dept.tick_params(left=False)

# Row 1 mid — Gender donut
ax_g = fig.add_subplot(gs[1, 3:5])
wedges, texts, autotexts = ax_g.pie(
    gender.values, labels=gender.index,
    colors=[BLUE, RED], autopct="%1.1f%%",
    startangle=90, wedgeprops=dict(width=0.55, edgecolor="white"))
for t in autotexts: t.set_fontsize(9); t.set_color("white"); t.set_fontweight("bold")
ax_g.set_title("Gender Distribution", pad=8)

# Row 1 right — Marital donut
ax_m = fig.add_subplot(gs[1, 5])
wedges2, texts2, autotexts2 = ax_m.pie(
    marital.values, labels=marital.index,
    colors=[TEAL, PURPLE], autopct="%1.1f%%",
    startangle=90, wedgeprops=dict(width=0.55, edgecolor="white"))
for t in autotexts2: t.set_fontsize(9); t.set_color("white"); t.set_fontweight("bold")
ax_m.set_title("Marital Status", pad=8)

# Row 2 mid/right — Experience histogram
ax_exp = fig.add_subplot(gs[2, 3:])
ax_exp.hist(df["total_experience"].dropna(), bins=15,
            color=BLUE, edgecolor="white", alpha=0.85)
ax_exp.axvline(avg_exp, color=RED, linestyle="--", linewidth=1.5, label=f"Avg {avg_exp}yr")
ax_exp.set_title("Experience Distribution", pad=10)
ax_exp.set_xlabel("Years of Experience")
ax_exp.set_ylabel("Employees")
ax_exp.legend(fontsize=8)

save(fig, "page1_executive_summary.png")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ATTRITION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
print("Building Page 2: Attrition Analysis...")

fig = plt.figure(figsize=(18, 12), facecolor=BG)
add_page_title(fig, "Attrition Analysis", "HR Analytics Dashboard  |  May 2026")

gs = gridspec.GridSpec(2, 3, figure=fig,
                        top=0.90, bottom=0.06,
                        left=0.04, right=0.98,
                        hspace=0.55, wspace=0.35)

# Attrition by Department
ax1 = fig.add_subplot(gs[0, 0])
dept_colors = [attrition_color(r) for r in dept_attr["rate"]]
bars = ax1.barh(dept_attr.index[::-1], dept_attr["rate"][::-1],
                color=dept_colors[::-1], edgecolor="none", height=0.6)
for bar, val in zip(bars, dept_attr["rate"][::-1]):
    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
             f"{val:.1f}%", va="center", fontsize=8.5, fontweight="bold",
             color=attrition_color(val))
ax1.set_title("Attrition Rate by Department")
ax1.set_xlabel("Attrition Rate (%)")
ax1.axvline(attr_rate, color=GREY, linestyle="--", linewidth=1, alpha=0.7)
ax1.text(attr_rate + 0.3, -0.7, f"Avg {attr_rate}%", fontsize=7.5, color=GREY)
ax1.set_xlim(0, dept_attr["rate"].max() * 1.22)

# Attrition by Grade
ax2 = fig.add_subplot(gs[0, 1])
grade_colors = [attrition_color(r) for r in grade_attr["rate"]]
bars2 = ax2.bar(grade_attr.index, grade_attr["rate"],
                color=grade_colors, edgecolor="none", width=0.55)
for bar, val in zip(bars2, grade_attr["rate"]):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{val:.1f}%", ha="center", fontsize=9, fontweight="bold",
             color=attrition_color(val))
ax2.set_title("Attrition Rate by Grade")
ax2.set_ylabel("Attrition Rate (%)")
ax2.axhline(attr_rate, color=GREY, linestyle="--", linewidth=1, alpha=0.7)
ax2.set_ylim(0, grade_attr["rate"].max() * 1.22)

# Attrition by Marital Status & Gender
ax3 = fig.add_subplot(gs[0, 2])
gender_attr = (df.groupby("gender")["is_attrition"]
               .agg(headcount="count", rate="mean")
               .assign(rate=lambda x: (x["rate"]*100).round(1)))
categories = ["Marital: Single", "Marital: Married", "Gender: Male", "Gender: Female"]
rates = [
    marital_attr.loc["Single","rate"] if "Single" in marital_attr.index else 0,
    marital_attr.loc["Married","rate"] if "Married" in marital_attr.index else 0,
    gender_attr.loc["Male","rate"] if "Male" in gender_attr.index else 0,
    gender_attr.loc["Female","rate"] if "Female" in gender_attr.index else 0,
]
colors3 = [attrition_color(r) for r in rates]
bars3 = ax3.barh(categories, rates, color=colors3, edgecolor="none", height=0.5)
for bar, val in zip(bars3, rates):
    ax3.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             f"{val:.1f}%", va="center", fontsize=9, fontweight="bold",
             color=attrition_color(val))
ax3.set_title("Attrition by Gender & Marital Status")
ax3.set_xlabel("Attrition Rate (%)")
ax3.set_xlim(0, max(rates) * 1.25)

# Attrition by Tenure Band
ax4 = fig.add_subplot(gs[1, 0])
tb = tenure_attr.reindex(tenure_order).dropna()
tb_colors = [attrition_color(r) for r in tb["rate"]]
bars4 = ax4.bar(tb.index, tb["rate"], color=tb_colors, edgecolor="none", width=0.6)
for bar, val in zip(bars4, tb["rate"]):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{val:.0f}%", ha="center", fontsize=8.5, fontweight="bold",
             color=attrition_color(val))
ax4.set_title("Attrition Rate by Tenure Band")
ax4.set_ylabel("Attrition Rate (%)")
ax4.axhline(attr_rate, color=GREY, linestyle="--", linewidth=1, alpha=0.7)
ax4.set_ylim(0, tb["rate"].max() * 1.22)

# Attrition by Age Group
ax5 = fig.add_subplot(gs[1, 1])
ag = age_attr.reindex(age_order).dropna()
ag_colors = [attrition_color(r) for r in ag["rate"]]
bars5 = ax5.bar(ag.index, ag["rate"], color=ag_colors, edgecolor="none", width=0.55)
for bar, val in zip(bars5, ag["rate"]):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{val:.0f}%", ha="center", fontsize=8.5, fontweight="bold",
             color=attrition_color(val))
ax5.set_title("Attrition Rate by Age Group")
ax5.set_ylabel("Attrition Rate (%)")
ax5.axhline(attr_rate, color=GREY, linestyle="--", linewidth=1, alpha=0.7)
ax5.set_ylim(0, ag["rate"].max() * 1.22)

# Attrition by Visa Type
ax6 = fig.add_subplot(gs[1, 2])
v_colors = [attrition_color(r) for r in visa_attr["rate"]]
bars6 = ax6.barh(visa_attr.index[::-1], visa_attr["rate"][::-1],
                  color=v_colors[::-1], edgecolor="none", height=0.5)
for bar, val in zip(bars6, visa_attr["rate"][::-1]):
    ax6.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             f"{val:.1f}%", va="center", fontsize=9, fontweight="bold",
             color=attrition_color(val))
ax6.set_title("Attrition Rate by Visa Type")
ax6.set_xlabel("Attrition Rate (%)")
ax6.set_xlim(0, visa_attr["rate"].max() * 1.25)

# Legend
legend_patches = [
    mpatches.Patch(color=RED,    label="High Risk (>=40%)"),
    mpatches.Patch(color=ORANGE, label="Medium Risk (25-39%)"),
    mpatches.Patch(color=GREEN,  label="Low Risk (<25%)"),
]
fig.legend(handles=legend_patches, loc="lower center",
           ncol=3, fontsize=9, frameon=True,
           bbox_to_anchor=(0.5, 0.0))

save(fig, "page2_attrition_analysis.png")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — WORKFORCE PROFILE
# ══════════════════════════════════════════════════════════════════════════════
print("Building Page 3: Workforce Profile...")

fig = plt.figure(figsize=(18, 12), facecolor=BG)
add_page_title(fig, "Workforce Profile", "HR Analytics Dashboard  |  May 2026")

gs = gridspec.GridSpec(2, 3, figure=fig,
                        top=0.90, bottom=0.06,
                        left=0.04, right=0.98,
                        hspace=0.52, wspace=0.35)

# Age Group Distribution
ax1 = fig.add_subplot(gs[0, 0])
ag_hc = df["age_group"].value_counts().reindex(age_order).fillna(0)
ag_c  = [PALETTE[i] for i in range(len(ag_hc))]
bars1 = ax1.bar(ag_hc.index, ag_hc.values, color=ag_c, edgecolor="none", width=0.6)
for bar, val in zip(bars1, ag_hc.values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             int(val), ha="center", fontsize=9, fontweight="bold", color=DARK)
ax1.set_title("Age Group Distribution (Estimated)")
ax1.set_ylabel("Employees")
ax1.set_ylim(0, ag_hc.max() * 1.18)

# Tenure Band Distribution
ax2 = fig.add_subplot(gs[0, 1])
tb_hc = df["tenure_band"].value_counts().reindex(tenure_order).fillna(0)
bars2 = ax2.bar(tb_hc.index, tb_hc.values,
                color=[BLUE if i < 2 else TEAL if i < 4 else ORANGE
                       for i in range(len(tb_hc))],
                edgecolor="none", width=0.6)
for bar, val in zip(bars2, tb_hc.values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             int(val), ha="center", fontsize=9, fontweight="bold", color=DARK)
ax2.set_title("Tenure Band Distribution")
ax2.set_ylabel("Employees")
ax2.set_ylim(0, tb_hc.max() * 1.18)

# Stability Distribution
ax3 = fig.add_subplot(gs[0, 2])
stability_vals = stability.values
stab_colors = [GREEN, TEAL, BLUE, ORANGE, RED, GREY]
bars3 = ax3.barh(stability.index[::-1], stability_vals[::-1],
                  color=stab_colors[::-1], edgecolor="none", height=0.55)
for bar, val in zip(bars3, stability_vals[::-1]):
    ax3.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             int(val), va="center", fontsize=9, fontweight="bold", color=DARK)
ax3.set_title("Employee Stability Distribution")
ax3.set_xlabel("Employees")
ax3.set_xlim(0, stability.max() * 1.18)

# Gender × Department stacked bar
ax4 = fig.add_subplot(gs[1, :2])
dept_gender = (df.groupby(["department", "gender"])
               .size().unstack(fill_value=0))
if "Male" in dept_gender.columns and "Female" in dept_gender.columns:
    dept_gender = dept_gender.sort_values("Male", ascending=True)
    ax4.barh(dept_gender.index, dept_gender["Male"],
             color=BLUE, label="Male", edgecolor="none", height=0.55)
    ax4.barh(dept_gender.index, dept_gender["Female"],
             left=dept_gender["Male"], color=RED, label="Female",
             edgecolor="none", height=0.55)
    for i, (idx, row) in enumerate(dept_gender.iterrows()):
        total_row = row.sum()
        ax4.text(total_row + 0.3, i, int(total_row),
                 va="center", fontsize=8.5, fontweight="bold", color=DARK)
    ax4.set_title("Headcount by Department & Gender")
    ax4.set_xlabel("Employees")
    ax4.set_xlim(0, dept_gender.sum(axis=1).max() * 1.15)
    ax4.legend(loc="lower right", fontsize=9)

# Grade × Status donut-style breakdown
ax5 = fig.add_subplot(gs[1, 2])
grade_status = (df.groupby(["grade", "employee_status"])
                .size().unstack(fill_value=0))
grade_order_chart = ["Trainees", "Professional", "Management", "Contract"]
grade_status = grade_status.reindex(
    [g for g in grade_order_chart if g in grade_status.index])

status_colors = {"On-Board": GREEN, "Attrition": RED, "Transfer": ORANGE}
bottom = np.zeros(len(grade_status))
for status_val in grade_status.columns:
    vals = grade_status[status_val].values
    color = status_colors.get(status_val, GREY)
    bars5 = ax5.bar(grade_status.index, vals, bottom=bottom,
                    color=color, label=status_val, edgecolor="white", width=0.55)
    for bar, val, bot in zip(bars5, vals, bottom):
        if val > 0:
            ax5.text(bar.get_x() + bar.get_width()/2,
                     bot + val/2, int(val),
                     ha="center", va="center", fontsize=8,
                     fontweight="bold", color="white")
    bottom += vals
ax5.set_title("Grade × Employee Status")
ax5.set_ylabel("Employees")
ax5.legend(loc="upper right", fontsize=8)

save(fig, "page3_workforce_profile.png")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — HIRING TREND
# ══════════════════════════════════════════════════════════════════════════════
print("Building Page 4: Hiring Trend...")

fig = plt.figure(figsize=(18, 11), facecolor=BG)
add_page_title(fig, "Hiring Trend (2020 – 2025)", "HR Analytics Dashboard  |  May 2026")

gs = gridspec.GridSpec(2, 2, figure=fig,
                        top=0.90, bottom=0.07,
                        left=0.06, right=0.98,
                        hspace=0.52, wspace=0.3)

# Annual hiring line chart
ax1 = fig.add_subplot(gs[0, :])
annual = trend.groupby("hire_year")["new_hires"].sum().reset_index()
ax1.plot(annual["hire_year"], annual["new_hires"],
         color=BLUE, linewidth=2.5, marker="o", markersize=8,
         markerfacecolor="white", markeredgewidth=2, markeredgecolor=BLUE)
ax1.fill_between(annual["hire_year"], annual["new_hires"],
                  alpha=0.12, color=BLUE)
for _, row in annual.iterrows():
    ax1.annotate(f'{int(row["new_hires"])}',
                 xy=(row["hire_year"], row["new_hires"]),
                 xytext=(0, 10), textcoords="offset points",
                 ha="center", fontsize=10, fontweight="bold", color=BLUE)
ax1.set_title("Annual New Hires (2020–2025)", pad=12)
ax1.set_xlabel("Year")
ax1.set_ylabel("New Hires")
ax1.set_xticks(annual["hire_year"])
ax1.set_ylim(0, annual["new_hires"].max() * 1.25)
ax1.grid(axis="y", alpha=0.3, linestyle="--")

# Monthly hiring heatmap
ax2 = fig.add_subplot(gs[1, 0])
pivot = trend.pivot_table(index="hire_year", columns="hire_month",
                            values="new_hires", aggfunc="sum", fill_value=0)
month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"]
im = ax2.imshow(pivot.values, cmap="Blues", aspect="auto")
ax2.set_xticks(range(len(pivot.columns)))
ax2.set_xticklabels([month_labels[m-1] for m in pivot.columns], fontsize=8)
ax2.set_yticks(range(len(pivot.index)))
ax2.set_yticklabels(pivot.index.astype(int), fontsize=8)
ax2.set_title("Hiring Heatmap (Year × Month)")
for i in range(pivot.shape[0]):
    for j in range(pivot.shape[1]):
        val = pivot.values[i, j]
        if val > 0:
            ax2.text(j, i, int(val), ha="center", va="center",
                     fontsize=7.5, color="white" if val > 5 else DARK)
plt.colorbar(im, ax=ax2, shrink=0.8, label="Hires")

# Monthly totals bar chart
ax3 = fig.add_subplot(gs[1, 1])
monthly_total = trend.groupby("hire_month")["new_hires"].sum().reindex(range(1,13), fill_value=0)
bar_colors = [TEAL if v == monthly_total.max() else BLUE for v in monthly_total.values]
bars3 = ax3.bar(range(1, 13), monthly_total.values,
                color=bar_colors, edgecolor="none", width=0.65)
for bar, val in zip(bars3, monthly_total.values):
    if val > 0:
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                 int(val), ha="center", fontsize=8, fontweight="bold", color=DARK)
ax3.set_xticks(range(1, 13))
ax3.set_xticklabels(month_labels, fontsize=8)
ax3.set_title("Total Hires by Month (All Years)")
ax3.set_ylabel("Total New Hires")
ax3.set_ylim(0, monthly_total.max() * 1.2)

save(fig, "page4_hiring_trend.png")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — MANAGER SCOREBOARD
# ══════════════════════════════════════════════════════════════════════════════
print("Building Page 5: Manager Scoreboard...")

fig = plt.figure(figsize=(18, 10), facecolor=BG)
add_page_title(fig, "Manager Scoreboard", "HR Analytics Dashboard  |  May 2026")

gs = gridspec.GridSpec(1, 2, figure=fig,
                        top=0.88, bottom=0.08,
                        left=0.04, right=0.98,
                        hspace=0.4, wspace=0.35)

mgr_sorted = mgr_df.sort_values("attrition_rate_pct", ascending=True)

# Attrition rate by manager (bar)
ax1 = fig.add_subplot(gs[0, 0])
mgr_colors = [attrition_color(r) for r in mgr_sorted["attrition_rate_pct"]]
bars1 = ax1.barh(mgr_sorted["reporting_manager"],
                  mgr_sorted["attrition_rate_pct"],
                  color=mgr_colors, edgecolor="none", height=0.55)
for bar, val in zip(bars1, mgr_sorted["attrition_rate_pct"]):
    ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             f"{val:.1f}%", va="center", fontsize=10, fontweight="bold",
             color=attrition_color(val))
ax1.axvline(attr_rate, color=GREY, linestyle="--", linewidth=1.5, alpha=0.8)
ax1.text(attr_rate + 0.3, -0.7, f"Company avg\n{attr_rate}%",
         fontsize=7.5, color=GREY, va="top")
ax1.set_title("Attrition Rate by Reporting Manager", pad=12)
ax1.set_xlabel("Attrition Rate (%)")
ax1.set_xlim(0, mgr_sorted["attrition_rate_pct"].max() * 1.25)

# Bubble chart: team size vs attrition rate
ax2 = fig.add_subplot(gs[0, 1])
bubble_colors = [attrition_color(r) for r in mgr_df["attrition_rate_pct"]]
sc = ax2.scatter(mgr_df["headcount"],
                  mgr_df["attrition_rate_pct"],
                  s=mgr_df["attritions"] * 60,
                  c=mgr_df["attrition_rate_pct"],
                  cmap="RdYlGn_r", vmin=10, vmax=50,
                  alpha=0.85, edgecolors="white", linewidth=1.5)
for _, row in mgr_df.iterrows():
    ax2.annotate(
        row["reporting_manager"].split()[-1],
        xy=(row["headcount"], row["attrition_rate_pct"]),
        xytext=(5, 4), textcoords="offset points",
        fontsize=8, color=DARK, fontweight="bold"
    )
ax2.axhline(attr_rate, color=GREY, linestyle="--", linewidth=1, alpha=0.7)
ax2.text(mgr_df["headcount"].max() * 0.75, attr_rate + 0.5,
         f"Company avg {attr_rate}%", fontsize=7.5, color=GREY)
ax2.set_title("Team Size vs Attrition Rate\n(bubble size = attritions)", pad=10)
ax2.set_xlabel("Team Size (headcount)")
ax2.set_ylabel("Attrition Rate (%)")
plt.colorbar(sc, ax=ax2, label="Attrition %", shrink=0.8)

save(fig, "page5_manager_scoreboard.png")

# ── Final summary ──────────────────────────────────────────────────────────────
print("\nAll 5 dashboard pages saved to:")
print(f"  {OUT_DIR}")
files = sorted(os.listdir(OUT_DIR))
for f in files:
    size_kb = os.path.getsize(os.path.join(OUT_DIR, f)) // 1024
    print(f"  {f}  ({size_kb} KB)")
