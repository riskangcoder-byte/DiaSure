"""
DiabetesCare Dashboard
A Streamlit-based Diabetes Self-Management App
Based on Executive Summary: Diabetes Self-Management App
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import random
from datetime import datetime, timedelta
import os

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DiabetesCare Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "diabetes_care.db"

# ─────────────────────────────────────────────
# FOOD DATABASE (USDA-style, per 100g)
# ─────────────────────────────────────────────
FOOD_DB = {
    "White Rice (cooked)":      {"calories": 130, "carbs": 28.2, "sugars": 0.1},
    "Brown Rice (cooked)":      {"calories": 111, "carbs": 23.0, "sugars": 0.4},
    "Whole Wheat Bread":        {"calories": 247, "carbs": 41.3, "sugars": 5.6},
    "White Bread":              {"calories": 265, "carbs": 49.0, "sugars": 5.0},
    "Oatmeal (cooked)":         {"calories": 71,  "carbs": 12.0, "sugars": 0.4},
    "Egg (boiled)":             {"calories": 155, "carbs": 1.1,  "sugars": 1.1},
    "Chicken Breast (grilled)": {"calories": 165, "carbs": 0.0,  "sugars": 0.0},
    "Salmon (baked)":           {"calories": 206, "carbs": 0.0,  "sugars": 0.0},
    "Apple":                    {"calories": 52,  "carbs": 13.8, "sugars": 10.4},
    "Banana":                   {"calories": 89,  "carbs": 23.0, "sugars": 12.2},
    "Orange":                   {"calories": 47,  "carbs": 11.8, "sugars": 9.4},
    "Milk (whole)":             {"calories": 61,  "carbs": 4.8,  "sugars": 5.1},
    "Greek Yogurt (plain)":     {"calories": 59,  "carbs": 3.6,  "sugars": 3.2},
    "Lentils (cooked)":         {"calories": 116, "carbs": 20.1, "sugars": 1.8},
    "Broccoli (cooked)":        {"calories": 35,  "carbs": 7.2,  "sugars": 1.7},
    "Spinach (raw)":            {"calories": 23,  "carbs": 3.6,  "sugars": 0.4},
    "Sweet Potato (baked)":     {"calories": 90,  "carbs": 20.7, "sugars": 4.2},
    "Potato (boiled)":          {"calories": 87,  "carbs": 20.1, "sugars": 0.9},
    "Orange Juice":             {"calories": 45,  "carbs": 10.4, "sugars": 8.4},
    "Cola (regular)":           {"calories": 42,  "carbs": 10.6, "sugars": 10.6},
    "Almonds":                  {"calories": 579, "carbs": 21.6, "sugars": 4.4},
    "Peanut Butter":            {"calories": 588, "carbs": 20.0, "sugars": 9.2},
    "Pasta (cooked)":           {"calories": 131, "carbs": 25.1, "sugars": 0.6},
    "Chapati / Roti":           {"calories": 297, "carbs": 52.0, "sugars": 1.0},
    "Dal (cooked)":             {"calories": 116, "carbs": 19.0, "sugars": 2.0},
}

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS food_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, meal_type TEXT, food_name TEXT,
            serving_g REAL, calories REAL, carbs REAL, sugars REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS bg_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT, bg_value REAL, status TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS patient_profile (
            key TEXT PRIMARY KEY, value TEXT
        )
    """)
    conn.commit()
    conn.close()

def seed_data():
    """Seed 30 days of synthetic data on first run."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM bg_logs")
    if c.fetchone()[0] > 0:
        conn.close()
        return  # already seeded

    today = datetime.now().date()
    foods_list = list(FOOD_DB.keys())
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]

    for day_offset in range(29, -1, -1):
        day = today - timedelta(days=day_offset)

        # 3–4 BG readings per day
        for hour in [7, 12, 18, 22]:
            # Mix of normal and elevated readings
            if random.random() < 0.65:
                bg = random.uniform(90, 175)
            elif random.random() < 0.55:
                bg = random.uniform(175, 260)
            else:
                bg = random.uniform(55, 320)
            bg = round(bg, 1)
            status = classify_bg(bg)
            dt_str = f"{day} {hour:02d}:{random.randint(0,59):02d}"
            c.execute("INSERT INTO bg_logs (datetime, bg_value, status) VALUES (?,?,?)",
                      (dt_str, bg, status))

        # 3–4 meals per day
        for meal in random.sample(meal_types, k=random.randint(3, 4)):
            food = random.choice(foods_list)
            serving = random.choice([100, 150, 200, 250, 80])
            info = FOOD_DB[food]
            cal  = round(info["calories"]  * serving / 100, 1)
            carb = round(info["carbs"]     * serving / 100, 1)
            sug  = round(info["sugars"]    * serving / 100, 1)
            c.execute(
                "INSERT INTO food_logs (date, meal_type, food_name, serving_g, calories, carbs, sugars) VALUES (?,?,?,?,?,?,?)",
                (str(day), meal, food, serving, cal, carb, sug)
            )

    # Default profile
    defaults = {
        "name": "Patient", "age": "45", "weight_kg": "75",
        "diabetes_type": "T2", "calorie_target": "2000", "carb_target": "130"
    }
    for k, v in defaults.items():
        c.execute("INSERT OR IGNORE INTO patient_profile (key, value) VALUES (?,?)", (k, v))

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def classify_bg(bg):
    if bg < 70:   return "Hypoglycemia"
    if bg < 180:  return "Normal"
    if bg < 240:  return "Mild Hyperglycemia"
    if bg < 300:  return "Check Ketones"
    return "Severe Hyperglycemia"

def bg_color(status):
    return {
        "Hypoglycemia":       "#3B82F6",
        "Normal":             "#22C55E",
        "Mild Hyperglycemia": "#EAB308",
        "Check Ketones":      "#F97316",
        "Severe Hyperglycemia": "#EF4444",
    }.get(status, "#6B7280")

def get_profile():
    conn = get_conn()
    rows = conn.execute("SELECT key, value FROM patient_profile").fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}

def save_profile(data: dict):
    conn = get_conn()
    for k, v in data.items():
        conn.execute("INSERT OR REPLACE INTO patient_profile (key, value) VALUES (?,?)", (k, v))
    conn.commit()
    conn.close()

def get_food_logs(days=1):
    cutoff = (datetime.now().date() - timedelta(days=days - 1)).isoformat()
    conn = get_conn()
    df = pd.read_sql(
        "SELECT * FROM food_logs WHERE date >= ? ORDER BY date, id", conn, params=(cutoff,))
    conn.close()
    return df

def get_bg_logs(days=1):
    cutoff = (datetime.now() - timedelta(days=days - 1)).strftime("%Y-%m-%d 00:00")
    conn = get_conn()
    df = pd.read_sql(
        "SELECT * FROM bg_logs WHERE datetime >= ? ORDER BY datetime", conn, params=(cutoff,))
    conn.close()
    return df

def add_food_log(date, meal_type, food_name, serving_g, cal, carb, sug):
    conn = get_conn()
    conn.execute(
        "INSERT INTO food_logs (date, meal_type, food_name, serving_g, calories, carbs, sugars) VALUES (?,?,?,?,?,?,?)",
        (date, meal_type, food_name, serving_g, cal, carb, sug))
    conn.commit()
    conn.close()

def add_bg_log(dt_str, bg, status):
    conn = get_conn()
    conn.execute("INSERT INTO bg_logs (datetime, bg_value, status) VALUES (?,?,?)",
                 (dt_str, bg, status))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────

def page_dashboard():
    st.title("🩺 DiabetesCare Dashboard")
    profile = get_profile()
    name = profile.get("name", "Patient")
    cal_target  = float(profile.get("calorie_target", 2000))
    carb_target = float(profile.get("carb_target", 130))

    st.markdown(f"### Welcome, **{name}** | {datetime.now().strftime('%A, %d %B %Y')}")
    st.divider()

    today_food = get_food_logs(days=1)
    today_bg   = get_bg_logs(days=1)

    total_cal  = today_food["calories"].sum() if not today_food.empty else 0
    total_carb = today_food["carbs"].sum()    if not today_food.empty else 0
    rem_cal    = max(cal_target - total_cal, 0)
    rem_carb   = max(carb_target - total_carb, 0)
    latest_bg  = today_bg["bg_value"].iloc[-1] if not today_bg.empty else None
    latest_status = today_bg["status"].iloc[-1] if not today_bg.empty else "—"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔥 Calories Today", f"{total_cal:.0f} kcal", f"Remaining: {rem_cal:.0f} kcal")
    col2.metric("🍞 Carbs Today",    f"{total_carb:.1f} g",   f"Remaining: {rem_carb:.1f} g")
    col3.metric("🩸 Latest BG",      f"{latest_bg:.0f} mg/dL" if latest_bg else "No data", latest_status)
    col4.metric("🎯 Carb Target",    f"{carb_target:.0f} g",  f"Cal Target: {cal_target:.0f} kcal")

    st.divider()

    # Gauge charts
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_cal = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=total_cal,
            delta={"reference": cal_target},
            title={"text": "Calories Consumed (kcal)"},
            gauge={
                "axis": {"range": [0, cal_target * 1.3]},
                "bar":  {"color": "#3B82F6"},
                "steps": [
                    {"range": [0, cal_target * 0.5],  "color": "#DCFCE7"},
                    {"range": [cal_target * 0.5, cal_target], "color": "#FEF9C3"},
                    {"range": [cal_target, cal_target * 1.3], "color": "#FEE2E2"},
                ],
                "threshold": {"line": {"color": "red", "width": 3}, "value": cal_target},
            }
        ))
        fig_cal.update_layout(height=250, margin=dict(t=30, b=0, l=20, r=20))
        st.plotly_chart(fig_cal, use_container_width=True)

    with col_g2:
        fig_carb = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=total_carb,
            delta={"reference": carb_target},
            title={"text": "Carbs Consumed (g)"},
            gauge={
                "axis": {"range": [0, carb_target * 1.5]},
                "bar":  {"color": "#F97316"},
                "steps": [
                    {"range": [0, carb_target * 0.6],  "color": "#DCFCE7"},
                    {"range": [carb_target * 0.6, carb_target], "color": "#FEF9C3"},
                    {"range": [carb_target, carb_target * 1.5], "color": "#FEE2E2"},
                ],
                "threshold": {"line": {"color": "red", "width": 3}, "value": carb_target},
            }
        ))
        fig_carb.update_layout(height=250, margin=dict(t=30, b=0, l=20, r=20))
        st.plotly_chart(fig_carb, use_container_width=True)

    # Active alerts
    if not today_bg.empty:
        st.subheader("🚨 Active Alerts")
        alert_rows = today_bg[today_bg["status"] != "Normal"]
        if alert_rows.empty:
            st.success("✅ All BG readings today are within normal range.")
        else:
            for _, row in alert_rows.tail(3).iterrows():
                show_alert(row["status"], row["bg_value"], row["datetime"])


def show_alert(status, bg, dt_str=""):
    messages = {
        "Hypoglycemia":
            "🔵 **Hypoglycemia** — Take 15g of fast-acting carbohydrates immediately (e.g., glucose tablet, juice). Re-check in 15 min.",
        "Mild Hyperglycemia":
            "🟡 **Mild Hyperglycemia** — Monitor closely. Avoid additional carb intake. Hydrate well.",
        "Check Ketones":
            "🟠 **Check Ketones** — Test urine/blood ketones now. Avoid exercise. Contact physician if persistent.",
        "Severe Hyperglycemia":
            "🔴 **Severe Hyperglycemia / DKA Risk** — Emergency: test ketones immediately, contact your doctor or call emergency services.",
    }
    fns = {
        "Hypoglycemia": st.info,
        "Mild Hyperglycemia": st.warning,
        "Check Ketones": st.warning,
        "Severe Hyperglycemia": st.error,
    }
    msg = messages.get(status, "")
    fn  = fns.get(status, st.info)
    if msg:
        fn(f"{msg}  \n*BG: {bg:.0f} mg/dL  •  {dt_str}*")


def page_food_log():
    st.title("🍽️ Food Log")
    profile = get_profile()
    carb_target = float(profile.get("carb_target", 130))
    cal_target  = float(profile.get("calorie_target", 2000))

    with st.form("food_form"):
        st.subheader("Log a Meal")
        col1, col2 = st.columns(2)
        food_name  = col1.selectbox("Food Item", sorted(FOOD_DB.keys()))
        meal_type  = col2.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        serving_g  = st.slider("Serving Size (g)", 10, 500, 100, 10)
        submitted  = st.form_submit_button("➕ Add to Log", type="primary")

    if submitted:
        info  = FOOD_DB[food_name]
        cal   = round(info["calories"] * serving_g / 100, 1)
        carb  = round(info["carbs"]    * serving_g / 100, 1)
        sug   = round(info["sugars"]   * serving_g / 100, 1)
        today = datetime.now().date().isoformat()
        add_food_log(today, meal_type, food_name, serving_g, cal, carb, sug)
        st.success(f"✅ Logged: **{food_name}** ({serving_g}g) — {cal} kcal | {carb}g carbs | {sug}g sugars")

    # Today's log
    st.divider()
    st.subheader("📋 Today's Food Log")
    df = get_food_logs(days=1)
    if df.empty:
        st.info("No meals logged today yet.")
    else:
        display = df[["meal_type", "food_name", "serving_g", "calories", "carbs", "sugars"]].copy()
        display.columns = ["Meal", "Food", "Serving (g)", "Calories (kcal)", "Carbs (g)", "Sugars (g)"]
        st.dataframe(display, use_container_width=True, hide_index=True)

        total_cal  = df["calories"].sum()
        total_carb = df["carbs"].sum()

        c1, c2 = st.columns(2)
        c1.metric("Total Calories", f"{total_cal:.0f} kcal",
                  f"{'Over' if total_cal > cal_target else 'Under'} target by {abs(total_cal - cal_target):.0f} kcal")
        c2.metric("Total Carbs", f"{total_carb:.1f} g",
                  f"{'Over' if total_carb > carb_target else 'Under'} target by {abs(total_carb - carb_target):.1f} g")

        # Breakdown bar
        fig = px.bar(
            display, x="Meal", y=["Calories (kcal)", "Carbs (g)", "Sugars (g)"],
            barmode="group", title="Today's Nutrient Breakdown by Meal",
            color_discrete_sequence=["#3B82F6", "#F97316", "#EAB308"]
        )
        st.plotly_chart(fig, use_container_width=True)


def page_bg_log():
    st.title("🩸 Blood Glucose Log")

    with st.form("bg_form"):
        st.subheader("Log a BG Reading")
        bg_val  = st.number_input("Blood Glucose (mg/dL)", min_value=20.0, max_value=600.0,
                                   value=120.0, step=1.0)
        bg_time = st.time_input("Time of Reading", value=datetime.now().time())
        sub     = st.form_submit_button("➕ Log Reading", type="primary")

    if sub:
        dt_str = f"{datetime.now().date()} {bg_time}"
        status = classify_bg(bg_val)
        add_bg_log(dt_str, bg_val, status)
        st.success(f"✅ BG logged: **{bg_val:.0f} mg/dL** — Status: **{status}**")
        if status != "Normal":
            show_alert(status, bg_val, dt_str)

    st.divider()
    st.subheader("📋 Today's BG Readings")
    df = get_bg_logs(days=1)
    if df.empty:
        st.info("No BG readings logged today.")
    else:
        df["Color"] = df["status"].map(bg_color)
        display = df[["datetime", "bg_value", "status"]].copy()
        display.columns = ["Date/Time", "BG (mg/dL)", "Status"]
        st.dataframe(display, use_container_width=True, hide_index=True)

        fig = px.line(df, x="datetime", y="bg_value", markers=True,
                      title="Today's BG Trend",
                      labels={"datetime": "Time", "bg_value": "BG (mg/dL)"},
                      color_discrete_sequence=["#3B82F6"])
        fig.add_hline(y=70,  line_dash="dot", line_color="#3B82F6",  annotation_text="Hypo <70")
        fig.add_hline(y=180, line_dash="dot", line_color="#EAB308",  annotation_text="Hyper >180")
        fig.add_hline(y=240, line_dash="dot", line_color="#F97316",  annotation_text="Check Ketones >240")
        fig.add_hline(y=300, line_dash="dot", line_color="#EF4444",  annotation_text="Severe >300")
        st.plotly_chart(fig, use_container_width=True)


def page_analytics():
    st.title("📊 Analytics & Charts")

    tab1, tab2 = st.tabs(["📅 Weekly View (7 Days)", "🗓️ Monthly View (30 Days)"])

    with tab1:
        render_period_charts(days=7, label="Weekly")

    with tab2:
        render_period_charts(days=30, label="Monthly")


def render_period_charts(days: int, label: str):
    bg_df   = get_bg_logs(days=days)
    food_df = get_food_logs(days=days)

    st.subheader(f"🩸 {label} Blood Glucose Trend")
    if bg_df.empty:
        st.info("No BG data available.")
    else:
        bg_df["date"] = pd.to_datetime(bg_df["datetime"]).dt.date
        daily_bg = bg_df.groupby("date")["bg_value"].mean().reset_index()
        daily_bg.columns = ["Date", "Avg BG (mg/dL)"]

        fig_bg = px.line(daily_bg, x="Date", y="Avg BG (mg/dL)", markers=True,
                         title=f"{label} Average Daily Blood Glucose",
                         color_discrete_sequence=["#3B82F6"])
        fig_bg.add_hrect(y0=0,   y1=70,  fillcolor="#BFDBFE", opacity=0.2, annotation_text="Hypo Zone")
        fig_bg.add_hrect(y0=70,  y1=180, fillcolor="#DCFCE7", opacity=0.2, annotation_text="Normal Zone")
        fig_bg.add_hrect(y0=180, y1=240, fillcolor="#FEF9C3", opacity=0.2, annotation_text="Mild Hyper")
        fig_bg.add_hrect(y0=240, y1=300, fillcolor="#FFEDD5", opacity=0.2, annotation_text="Check Ketones")
        fig_bg.add_hrect(y0=300, y1=600, fillcolor="#FEE2E2", opacity=0.2, annotation_text="Severe")
        fig_bg.update_layout(xaxis_title="Date", yaxis_title="Avg BG (mg/dL)")
        st.plotly_chart(fig_bg, use_container_width=True)

    st.divider()
    st.subheader(f"🍽️ {label} Calorie & Carb Intake")
    if food_df.empty:
        st.info("No food data available.")
    else:
        daily_food = food_df.groupby("date")[["calories", "carbs"]].sum().reset_index()
        daily_food.columns = ["Date", "Calories (kcal)", "Carbs (g)"]

        fig_food = px.bar(daily_food, x="Date",
                          y=["Calories (kcal)", "Carbs (g)"],
                          barmode="group",
                          title=f"{label} Daily Calorie & Carb Intake",
                          color_discrete_sequence=["#3B82F6", "#F97316"])
        st.plotly_chart(fig_food, use_container_width=True)

    st.divider()
    st.subheader(f"🥧 {label} Diabetes Status Distribution")
    if bg_df.empty:
        st.info("No BG status data available.")
    else:
        status_counts = bg_df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        color_map = {
            "Hypoglycemia":       "#3B82F6",
            "Normal":             "#22C55E",
            "Mild Hyperglycemia": "#EAB308",
            "Check Ketones":      "#F97316",
            "Severe Hyperglycemia": "#EF4444",
        }
        colors = [color_map.get(s, "#6B7280") for s in status_counts["Status"]]

        fig_pie = px.pie(
            status_counts, values="Count", names="Status",
            title=f"{label} BG Status Distribution",
            hole=0.45,
            color="Status",
            color_discrete_map=color_map,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

        # Summary table
        total = status_counts["Count"].sum()
        status_counts["Percentage"] = (status_counts["Count"] / total * 100).round(1).astype(str) + "%"
        st.dataframe(status_counts, use_container_width=True, hide_index=True)


def page_alerts():
    st.title("🚨 Alerts & Clinical Guidance")

    df = get_bg_logs(days=1)
    alerts = df[df["status"] != "Normal"] if not df.empty else pd.DataFrame()

    if alerts.empty:
        st.success("✅ No active alerts today. All readings are within normal range.")
    else:
        st.warning(f"⚠️ {len(alerts)} alert(s) detected today.")
        for _, row in alerts.iterrows():
            show_alert(row["status"], row["bg_value"], row["datetime"])

    st.divider()
    st.subheader("📖 Clinical Reference — Alert Thresholds (ADA/NICE Guidelines)")

    thresholds = [
        ("🔵 Hypoglycemia",        "< 70 mg/dL",    "Take 15g fast-acting carbs. Re-check in 15 min."),
        ("🟢 Normal (Fasting)",    "80–130 mg/dL",  "ADA target for most non-pregnant adults."),
        ("🟢 Normal (Post-meal)",  "< 180 mg/dL",   "ADA 1–2 hour postprandial target."),
        ("🟡 Mild Hyperglycemia",  "180–239 mg/dL", "Above target. Monitor closely. Avoid extra carbs. Hydrate."),
        ("🟠 Check Ketones",       "240–299 mg/dL", "ADA: Test urine ketones. Do not exercise. Consult physician."),
        ("🔴 Severe Hyperglycemia","≥ 300 mg/dL",   "DKA risk. Test ketones immediately. Contact doctor or ER."),
    ]

    for icon_label, range_str, action in thresholds:
        with st.expander(f"{icon_label}  —  {range_str}"):
            st.write(f"**Action:** {action}")

    st.divider()
    st.subheader("💊 Medication Guidance (Non-Prescriptive)")
    with st.expander("Basal Insulin Titration (ADA Guidelines)"):
        st.markdown("""
- Initiate basal insulin at ~0.1–0.2 U/kg body weight.
- If fasting BG is consistently above **130 mg/dL** over 3–5 days, consider increasing basal dose by **2 units**.
- If fasting BG falls below ~100 mg/dL, reduce dose similarly.
- Once basal dose reaches ~0.5 U/kg without reaching A1C goal, consult physician about adding prandial insulin.
- **Always review medication changes with your healthcare provider.**
        """)
    with st.expander("DKA Emergency Escalation Flow"):
        st.markdown("""
1. **BG > 300 mg/dL** → Test ketones immediately.
2. **Ketones negative** → Take prescribed corrective insulin, hydrate, re-test BG in 1 hour.
3. **Ketones positive** → 🔴 DKA Risk — Contact diabetes team or call emergency services.
4. **Symptoms** (nausea, vomiting, abdominal pain): seek hospital care immediately.
        """)


def page_profile():
    st.title("👤 Patient Profile")
    profile = get_profile()

    with st.form("profile_form"):
        name    = st.text_input("Full Name",        value=profile.get("name", ""))
        age     = st.number_input("Age",            value=int(profile.get("age", 40)), min_value=1, max_value=120)
        weight  = st.number_input("Weight (kg)",    value=float(profile.get("weight_kg", 70)), min_value=10.0, max_value=300.0)
        dtype   = st.selectbox("Diabetes Type",     ["T1", "T2", "Gestational", "Pre-diabetes"],
                               index=["T1", "T2", "Gestational", "Pre-diabetes"].index(
                                   profile.get("diabetes_type", "T2")))
        cal_t   = st.number_input("Daily Calorie Target (kcal)", value=int(profile.get("calorie_target", 2000)), min_value=500, max_value=5000)
        carb_t  = st.number_input("Daily Carb Target (g)",       value=int(profile.get("carb_target", 130)),    min_value=20,  max_value=500)
        saved   = st.form_submit_button("💾 Save Profile", type="primary")

    if saved:
        save_profile({
            "name": name, "age": str(age), "weight_kg": str(weight),
            "diabetes_type": dtype, "calorie_target": str(cal_t), "carb_target": str(carb_t)
        })
        st.success("✅ Profile saved successfully!")
        st.rerun()

    st.divider()
    st.subheader("Current Profile")
    p = get_profile()
    col1, col2 = st.columns(2)
    col1.info(f"**Name:** {p.get('name','—')}  \n**Age:** {p.get('age','—')}  \n**Weight:** {p.get('weight_kg','—')} kg")
    col2.info(f"**Diabetes Type:** {p.get('diabetes_type','—')}  \n**Calorie Target:** {p.get('calorie_target','—')} kcal  \n**Carb Target:** {p.get('carb_target','—')} g")


# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
def main():
    init_db()
    seed_data()

    with st.sidebar:
        st.image("https://img.icons8.com/color/96/diabetes.png", width=60)
        st.title("DiabetesCare")
        st.caption("Self-Management Dashboard")
        st.divider()

        pages = {
            "🏠 Dashboard":          page_dashboard,
            "🍽️ Food Log":           page_food_log,
            "🩸 Blood Glucose Log":  page_bg_log,
            "📊 Analytics & Charts": page_analytics,
            "🚨 Alerts & Guidance":  page_alerts,
            "👤 Patient Profile":    page_profile,
        }

        choice = st.radio("Navigate", list(pages.keys()), label_visibility="collapsed")
        st.divider()
        st.caption("📌 Data stored locally in SQLite")

    pages[choice]()

    # Footer
    st.divider()
    st.caption(
        "⚕️ *Disclaimer: This app is for informational purposes only. "
        "Always consult your healthcare provider before making any medical decisions. "
        "Not a substitute for professional medical advice, diagnosis, or treatment.*"
    )


if __name__ == "__main__":
    main()
