"""
data_engine.py — Synthetic Data Generator & Rule Engine
Generates realistic elderly diabetes patient data and evaluates alert rules.

RESEARCH ALIGNMENT:
- RQ1: Taxonomy — 5 clinical domains (glucose, meal, medication, activity, nocturnal)
- RQ2: Unified schema, cross-module clinical insight engine, privacy-by-default
- RQ3: Evidence-grounded evaluation metrics (TIR, adherence, alert precision/recall, latency)

All data is synthetic/simulated — no real patient information used.
Privacy-by-default: no PII stored or displayed without explicit toggle.

Key improvements over previous version:
1. Dynamic seeding from current time — evaluation tests different data each run
2. Cross-module nocturnal risk prediction (Liu et al., 2026 — Gap 4 from SLR)
3. Medication→glucose causal chain (Lanke et al., 2025 — Gap 2 from SLR)
4. Proper alert latency measurement using time.perf_counter (not random.randint)
5. Evidence-grounded metric thresholds (Battelino et al., 2019; ADA 2023; Najafi et al., 2013)
"""

import random
import time
from datetime import datetime, timedelta


# ── Clinical Thresholds (evidence-grounded) ──────────────────────────────────
# Glucose: ADA Standards of Care 2023; Battelino et al. 2019
GLUCOSE_LOW        = 70    # mg/dL  — hypoglycemia (critical)
GLUCOSE_HIGH       = 180   # mg/dL  — hyperglycemia (critical)
GLUCOSE_WARN_LOW   = 80    # mg/dL  — caution low
GLUCOSE_WARN_HIGH  = 160   # mg/dL  — caution high (IDF post-meal guideline)
GLUCOSE_TARGET_LOW = 80    # mg/dL  — TIR lower bound (elderly: 50–180 for complex cases)
GLUCOSE_TARGET_HIGH= 130   # mg/dL  — TIR upper bound

# Activity: Najafi et al. 2013; de Oliveira et al. 2024 meta-analysis (+2131 steps)
STEPS_LOW          = 2000  # steps/day — high sedentary risk (triggers CRITICAL)
STEPS_WARN         = 3500  # steps/day — moderate warning
STEPS_GOAL         = 5000  # steps/day — evidence-based elderly T2D target

# Night: Liu et al. 2026 (NH threshold for elderly T2D)
NIGHT_LOW          = 75    # mg/dL — nocturnal caution threshold
NIGHT_CRITICAL     = GLUCOSE_LOW  # 70 mg/dL — NH critical

# Meal: IDF post-meal glucose guideline
MEAL_SPIKE_LIMIT   = 50    # mg/dL — high spike threshold
MEAL_SPIKE_WARN    = 30    # mg/dL — moderate spike threshold


def _dynamic_seed():
    """
    Return a seed that changes every 5 minutes.
    This ensures each evaluation run sees different data values,
    making evaluation metrics non-trivial (fixes static seed=42 issue).
    """
    return int(time.time() // 300)  # changes every 5 minutes


# ── Glucose Data Generator ───────────────────────────────────────────────────
def generate_glucose_series(hours=24, seed=None):
    """
    Generate realistic 24-hour glucose readings every 30 minutes.
    Simulates: dawn effect, post-meal spikes, nocturnal dip.
    If a medication dose was missed, glucose is elevated accordingly
    (implements medication→glucose causal chain from Gap 2).
    """
    if seed is None:
        seed = _dynamic_seed()
    rng = random.Random(seed)

    readings = []
    base = rng.uniform(108, 125)  # inter-patient variability
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(hours=hours)

    # Simulate whether evening insulin was missed (affects overnight + morning glucose)
    evening_dose_missed = rng.random() < 0.35  # ~35% chance missed (realistic non-adherence rate)

    for i in range(hours * 2):
        t = start + timedelta(minutes=30 * i)
        hour = t.hour

        # Physiological patterns
        dawn_effect     = rng.uniform(8, 14) if 4 <= hour <= 8 else 0
        post_meal_spike = 0
        if hour in [8, 9]:   post_meal_spike = rng.uniform(15, 40)   # breakfast
        if hour in [13, 14]: post_meal_spike = rng.uniform(20, 50)   # lunch
        if hour in [19, 20]: post_meal_spike = rng.uniform(10, 35)   # dinner
        night_dip       = rng.uniform(-18, -8) if 1 <= hour <= 4 else 0

        # Medication→glucose causal chain (Gap 2 from SLR)
        # Missed evening insulin → elevated overnight and morning glucose
        medication_effect = 0
        if evening_dose_missed:
            if 21 <= hour <= 23 or 0 <= hour <= 6:
                medication_effect = rng.uniform(15, 35)  # overnight hyperglycemia
            elif 7 <= hour <= 10:
                medication_effect = rng.uniform(8, 20)   # elevated fasting morning

        noise   = rng.gauss(0, 5)
        glucose = base + dawn_effect + post_meal_spike + night_dip + medication_effect + noise
        glucose = max(60, min(215, glucose))

        readings.append({
            "time":              t.strftime("%H:%M"),
            "timestamp":         t,
            "glucose":           round(glucose, 1),
            "medication_effect": round(medication_effect, 1)
        })

    return readings, evening_dose_missed


def generate_weekly_glucose(seed=None):
    """7-day daily average glucose with realistic variability."""
    if seed is None:
        seed = _dynamic_seed()
    rng = random.Random(seed + 1)
    days = []
    base = rng.uniform(112, 130)
    for i in range(7):
        d = datetime.now() - timedelta(days=6 - i)
        avg = base + rng.gauss(0, 10)
        days.append({
            "day":         d.strftime("%a"),
            "avg_glucose": round(max(85, min(185, avg)), 1)
        })
    return days


# ── Meal Data Generator ──────────────────────────────────────────────────────
def generate_meal_log(seed=None):
    """
    Generate today's meal log with pre/post glucose comparison.
    Willis et al. (2025) — meal-glucose feedback loop.
    Joshi et al. (2025) — post-prandial glucose as CV risk predictor.
    """
    if seed is None:
        seed = _dynamic_seed()
    rng = random.Random(seed + 2)

    meals = [
        {
            "meal":     "Breakfast",
            "time":     "08:15 AM",
            "type":     rng.choice(["Oatmeal + Fruit", "Toast + Eggs", "Cereal + Milk"]),
            "category": "Low GI",
            "before":   round(rng.uniform(95, 115), 1),
        },
        {
            "meal":     "Lunch",
            "time":     "01:10 PM",
            "type":     rng.choice(["Rice + Vegetables", "Sandwich + Salad", "Pasta + Protein"]),
            "category": "Balanced",
            "before":   round(rng.uniform(110, 130), 1),
        },
        {
            "meal":     "Snack",
            "time":     "04:00 PM",
            "type":     rng.choice(["Biscuits + Tea", "Fruit + Nuts", "Yoghurt"]),
            "category": "Moderate GI",
            "before":   round(rng.uniform(115, 135), 1),
        },
    ]
    for m in meals:
        rise    = rng.uniform(15, 65)
        m["after"]  = round(m["before"] + rise, 1)
        m["impact"] = round(rise, 1)
        m["status"] = (
            "High Spike"  if m["impact"] > MEAL_SPIKE_LIMIT else
            "Moderate"    if m["impact"] > MEAL_SPIKE_WARN else
            "Normal"
        )
    return meals


# ── Medication Data Generator ────────────────────────────────────────────────
def generate_medication_log(seed=None):
    """
    Generate medication schedule with realistic adherence (~67–100%).
    Lanke et al. (2025): dose logging + reminders are the 2 highest-impact adherence features.
    Faisal et al. (2023): caregiver notification for missed doses is essential.
    """
    if seed is None:
        seed = _dynamic_seed()
    rng = random.Random(seed + 3)

    # Randomly determine today's adherence pattern
    taken_morning = rng.random() < 0.92   # Morning Metformin — high adherence
    taken_lunch   = rng.random() < 0.85   # Lunchtime dose — moderate adherence
    taken_evening = rng.random() < 0.68   # Evening insulin — lower adherence (realistic)

    schedule = [
        {
            "time":        "08:00 AM",
            "med":         "Metformin 500mg",
            "taken":       taken_morning,
            "actual_time": "08:05 AM" if taken_morning else None,
        },
        {
            "time":        "01:00 PM",
            "med":         "Metformin 500mg",
            "taken":       taken_lunch,
            "actual_time": "01:12 PM" if taken_lunch else None,
        },
        {
            "time":        "08:00 PM",
            "med":         "Insulin Glargine",
            "taken":       taken_evening,
            "actual_time": "08:03 PM" if taken_evening else None,
        },
    ]

    taken     = sum(1 for d in schedule if d["taken"])
    total     = len(schedule)
    adherence = round((taken / total) * 100, 1)

    weekly = []
    rng2 = random.Random(seed + 31)
    for i in range(7):
        d       = datetime.now() - timedelta(days=6 - i)
        taken_w = rng2.randint(1, 3)
        weekly.append({
            "day":   d.strftime("%a"),
            "taken": taken_w,
            "total": 3,
            "rate":  round((taken_w / 3) * 100, 1)
        })
    return schedule, adherence, weekly


# ── Activity Data Generator ──────────────────────────────────────────────────
def generate_activity_data(seed=None):
    """
    Generate daily activity metrics.
    Najafi et al. (2013): validated activity metrics for elderly T2D.
    de Oliveira et al. (2024): +2131 steps/day from wearable interventions.
    Nature Communications (2024): mortality associations with activity levels.
    """
    if seed is None:
        seed = _dynamic_seed()
    rng = random.Random(seed + 4)

    today_steps = rng.randint(1500, 7200)   # realistic range for elderly T2D
    active_mins = rng.randint(20, 70)
    calories    = round(today_steps * 0.045, 0)

    weekly = []
    rng2 = random.Random(seed + 41)
    for i in range(7):
        d     = datetime.now() - timedelta(days=6 - i)
        steps = rng2.randint(1800, 7500)
        weekly.append({
            "day":        d.strftime("%a"),
            "steps":      steps,
            "active_min": rng2.randint(15, 75)
        })

    hourly = []
    for h in range(6, 22):
        steps = (
            rng.randint(400, 1200) if h in [9, 10, 12, 13, 17, 18]
            else rng.randint(0, 500)
        )
        hourly.append({"hour": f"{h:02d}:00", "steps": steps})

    return {
        "today_steps": today_steps,
        "active_mins": active_mins,
        "calories":    int(calories),
        "weekly":      weekly,
        "hourly":      hourly,
        "goal":        STEPS_GOAL
    }


# ── Night Monitoring Data Generator ─────────────────────────────────────────
def generate_night_data(seed=None):
    """
    Generate overnight glucose trace (10 PM – 6 AM).
    Liu et al. (2026): 25–40% NH prevalence in elderly T2D — NH is common, not rare.
    """
    if seed is None:
        seed = _dynamic_seed()
    rng = random.Random(seed + 5)

    readings = []
    base = rng.uniform(100, 120)

    for i in range(17):  # 10 PM to 6 AM every 30 min
        t_hour = 22 + (i * 0.5)
        if t_hour >= 24:
            t_hour -= 24
        h = int(t_hour)
        m = int((t_hour % 1) * 60)
        label = f"{h:02d}:{m:02d}"

        dip   = rng.uniform(-20, -8) if 1 <= h <= 4 else 0
        noise = rng.gauss(0, 5)
        g     = base + dip + noise
        g     = max(58, min(150, g))
        readings.append({"time": label, "glucose": round(g, 1)})

    lowest  = min(r["glucose"] for r in readings)
    highest = max(r["glucose"] for r in readings)
    alerts  = [r for r in readings if r["glucose"] < NIGHT_LOW]

    return {
        "readings":          readings,
        "lowest":            lowest,
        "highest":           highest,
        "alerts_triggered":  len(alerts),
        "hypo_risk":         (
            "HIGH"     if lowest < NIGHT_CRITICAL else
            "MODERATE" if lowest < NIGHT_LOW      else
            "LOW"
        ),
        "sleep_status": (
            "UNSAFE"  if lowest < NIGHT_CRITICAL else
            "CAUTION" if lowest < NIGHT_LOW      else
            "SAFE"
        )
    }


# ── Pre-Sleep Nocturnal Risk Prediction ─────────────────────────────────────
def compute_presleep_risk(glucose_series, activity, medication_schedule, night_data):
    """
    Pre-emptive nocturnal risk assessment generated from DAYTIME data.

    This is the key novel contribution from Gap 4 in the SLR:
    Liu et al. (2026) demonstrated that nocturnal hypoglycaemia is predictable
    from daytime CGM patterns, activity levels, and medication adherence —
    meaning caregivers can take preventive action BEFORE sleep, not just
    react to overnight alerts.

    Risk factors assessed:
    1. Evening dose missed (direct predictor of nocturnal hyperglycaemia)
    2. High daytime activity (can deplete glycogen → nocturnal hypo)
    3. Low afternoon glucose trend (trending toward hypoglycaemia)
    4. High glucose variability (coefficient of variation)
    """
    risk_score = 0
    risk_factors = []

    # Unpack glucose series (may be tuple from updated generate_glucose_series)
    if isinstance(glucose_series, tuple):
        series, evening_missed = glucose_series
    else:
        series, evening_missed = glucose_series, False

    # Factor 1: Missed evening insulin (strongest predictor — Liu et al., 2026)
    missed_insulin = any(
        not d["taken"] and "Insulin" in d["med"]
        for d in medication_schedule
    )
    if missed_insulin:
        risk_score += 35
        risk_factors.append("⚠️ Evening insulin dose missed — nocturnal hyperglycaemia risk elevated")

    # Factor 2: Very high daytime activity (glycogen depletion → nocturnal hypo)
    if activity["today_steps"] > 7000:
        risk_score += 20
        risk_factors.append("ℹ️ High daytime activity (>7,000 steps) — monitor for nocturnal hypoglycaemia")
    elif activity["today_steps"] < STEPS_LOW:
        risk_score += 10
        risk_factors.append("ℹ️ Low activity today — insulin resistance may be elevated overnight")

    # Factor 3: Afternoon glucose trend (last 4 readings = last 2 hours)
    if len(series) >= 4:
        recent = [r["glucose"] for r in series[-4:]]
        afternoon_avg = sum(recent) / len(recent)
        if afternoon_avg < 90:
            risk_score += 25
            risk_factors.append(f"⚠️ Afternoon glucose averaging {round(afternoon_avg,1)} mg/dL — trending low pre-sleep")
        elif afternoon_avg > 160:
            risk_score += 15
            risk_factors.append(f"ℹ️ Afternoon glucose elevated ({round(afternoon_avg,1)} mg/dL) — review pre-sleep dose")

    # Factor 4: Glucose variability (coefficient of variation)
    if len(series) >= 10:
        glucose_vals = [r["glucose"] for r in series]
        mean_g = sum(glucose_vals) / len(glucose_vals)
        std_g  = (sum((g - mean_g)**2 for g in glucose_vals) / len(glucose_vals)) ** 0.5
        cv     = (std_g / mean_g) * 100 if mean_g > 0 else 0
        if cv > 36:  # ADA high variability threshold
            risk_score += 20
            risk_factors.append(f"⚠️ High glucose variability (CV={round(cv,1)}%) — unpredictable overnight pattern")

    # Classify risk
    if risk_score >= 50:
        risk_level    = "HIGH"
        recommendation = "Consider a pre-sleep snack (15–20g carbohydrate). Caregiver check-in advised."
    elif risk_score >= 25:
        risk_level    = "MODERATE"
        recommendation = "Monitor closely overnight. Set CGM alerts to caution threshold."
    else:
        risk_level    = "LOW"
        recommendation = "No specific pre-sleep action required. Continue standard management."

    return {
        "risk_score":     min(100, risk_score),
        "risk_level":     risk_level,
        "risk_factors":   risk_factors if risk_factors else ["✅ No significant nocturnal risk factors identified today"],
        "recommendation": recommendation
    }


# ── Alert / Rule Engine ───────────────────────────────────────────────────────
def evaluate_alerts(glucose_series, activity, medication_schedule, night_data):
    """
    Rule-based alert engine with severity tiers.
    Hasan & Ahmed (2024): device→gateway→caregiver escalation pattern.
    Hernández et al. (2018): alert fatigue mitigation through severity tiering.
    """
    alerts = []
    now    = datetime.now()

    # Unpack glucose series
    if isinstance(glucose_series, tuple):
        series, _ = glucose_series
    else:
        series = glucose_series

    latest_g = series[-1]["glucose"] if series else 120

    # ── Glucose alerts ──────────────────────────────────────────────────────
    if latest_g < GLUCOSE_LOW:
        alerts.append({"level": "CRITICAL", "module": "Glucose",
                        "message": f"Hypoglycemia detected — glucose {latest_g} mg/dL (< {GLUCOSE_LOW})",
                        "time": now.strftime("%H:%M"), "icon": "🚨"})
    elif latest_g > GLUCOSE_HIGH:
        alerts.append({"level": "CRITICAL", "module": "Glucose",
                        "message": f"Hyperglycemia detected — glucose {latest_g} mg/dL (> {GLUCOSE_HIGH})",
                        "time": now.strftime("%H:%M"), "icon": "🚨"})
    elif latest_g < GLUCOSE_WARN_LOW:
        alerts.append({"level": "WARNING", "module": "Glucose",
                        "message": f"Low glucose caution — {latest_g} mg/dL approaching threshold",
                        "time": now.strftime("%H:%M"), "icon": "⚠️"})
    elif latest_g > GLUCOSE_WARN_HIGH:
        alerts.append({"level": "WARNING", "module": "Glucose",
                        "message": f"Elevated glucose — {latest_g} mg/dL, monitor closely",
                        "time": now.strftime("%H:%M"), "icon": "⚠️"})
    else:
        alerts.append({"level": "OK", "module": "Glucose",
                        "message": f"Glucose stable at {latest_g} mg/dL — within target range",
                        "time": now.strftime("%H:%M"), "icon": "✅"})

    # ── Medication alerts ───────────────────────────────────────────────────
    for dose in medication_schedule:
        if not dose["taken"]:
            is_insulin = "Insulin" in dose["med"]
            alerts.append({
                "level":   "CRITICAL" if is_insulin else "WARNING",
                "module":  "Medication",
                "message": f"Missed dose — {dose['med']} scheduled {dose['time']}"
                           + (" · Nocturnal glucose risk elevated" if is_insulin else ""),
                "time":    now.strftime("%H:%M"),
                "icon":    "🚨" if is_insulin else "⚠️"
            })

    # ── Activity alerts ─────────────────────────────────────────────────────
    if activity["today_steps"] < STEPS_LOW:
        alerts.append({"level": "WARNING", "module": "Activity",
                        "message": f"Very low activity — {activity['today_steps']:,} steps "
                                   f"(critical threshold: {STEPS_LOW:,})",
                        "time": now.strftime("%H:%M"), "icon": "⚠️"})
    elif activity["today_steps"] < STEPS_WARN:
        alerts.append({"level": "INFO", "module": "Activity",
                        "message": f"Below goal — {activity['today_steps']:,} steps "
                                   f"(target: {STEPS_GOAL:,})",
                        "time": now.strftime("%H:%M"), "icon": "ℹ️"})
    else:
        alerts.append({"level": "OK", "module": "Activity",
                        "message": f"Good activity — {activity['today_steps']:,} steps today",
                        "time": now.strftime("%H:%M"), "icon": "✅"})

    # ── Nocturnal alerts ────────────────────────────────────────────────────
    if night_data["hypo_risk"] == "HIGH":
        alerts.append({"level": "CRITICAL", "module": "Night",
                        "message": f"Nocturnal hypoglycemia — lowest reading {night_data['lowest']} mg/dL",
                        "time": "Last Night", "icon": "🚨"})
    elif night_data["hypo_risk"] == "MODERATE":
        alerts.append({"level": "WARNING", "module": "Night",
                        "message": f"Night glucose dipped to {night_data['lowest']} mg/dL — "
                                   f"monitor closely tonight",
                        "time": "Last Night", "icon": "⚠️"})
    else:
        alerts.append({"level": "OK", "module": "Night",
                        "message": f"Night stable — lowest {night_data['lowest']} mg/dL, "
                                   f"no hypoglycemia",
                        "time": "Last Night", "icon": "✅"})

    return alerts


# ── Evaluation Metrics (RQ3) ─────────────────────────────────────────────────
def compute_evaluation_metrics(alerts, glucose_series, activity,
                                medication_schedule, weekly_med):
    """
    Compute system evaluation metrics to answer RQ3.

    Metrics are evidence-grounded:
    - TIR: Battelino et al. (2019), ADA Standards of Care 2023
    - Adherence: Lanke et al. (2025) target ≥90%
    - Activity: Najafi et al. (2013), de Oliveira et al. (2024) 5000-step target
    - Alert latency: measured with perf_counter, not simulated random
    """
    # Unpack glucose series if needed
    if isinstance(glucose_series, tuple):
        series, _ = glucose_series
    else:
        series = glucose_series

    total_alerts = len(alerts)
    critical  = sum(1 for a in alerts if a["level"] == "CRITICAL")
    warnings  = sum(1 for a in alerts if a["level"] == "WARNING")
    ok_count  = sum(1 for a in alerts if a["level"] == "OK")
    info_count = sum(1 for a in alerts if a["level"] == "INFO")

    # Alert precision: proportion of alerts that are actionable (not OK/INFO)
    actionable = critical + warnings
    precision  = round((actionable / total_alerts) * 100, 1) if total_alerts > 0 else 0

    # Recall: of the ground-truth events (CRITICAL conditions present), how many were caught
    # Ground truth: count of clinical conditions that should have generated an alert
    ground_truth_events = sum([
        1 if series and (series[-1]["glucose"] < GLUCOSE_LOW or series[-1]["glucose"] > GLUCOSE_HIGH) else 0,
        sum(1 for d in medication_schedule if not d["taken"]),
        1 if activity["today_steps"] < STEPS_LOW else 0,
        1 if activity["today_steps"] < STEPS_WARN else 0,
    ])
    recall = round((critical / max(ground_truth_events, 1)) * 100, 1)

    # Glucose time-in-range (TIR)
    in_range = [r for r in series if GLUCOSE_TARGET_LOW <= r["glucose"] <= GLUCOSE_TARGET_HIGH]
    tir       = round(len(in_range) / len(series) * 100, 1) if series else 0
    tir_met   = tir >= 70  # ADA target

    # Medication adherence
    taken     = sum(1 for d in medication_schedule if d["taken"])
    adherence = round((taken / len(medication_schedule)) * 100, 1)
    adherence_met = adherence >= 90  # Lanke et al. 2025 target

    # Weekly adherence
    weekly_avg = round(sum(d["rate"] for d in weekly_med) / len(weekly_med), 1)

    # Activity goal
    activity_score = min(100, round((activity["today_steps"] / STEPS_GOAL) * 100, 1))
    activity_met   = activity["today_steps"] >= STEPS_GOAL

    # Alert latency — measured with actual timer, not random
    t0              = time.perf_counter()
    _ = evaluate_alerts(series, activity, medication_schedule,
                        {"lowest": 80, "highest": 120, "hypo_risk": "LOW",
                         "sleep_status": "SAFE", "alerts_triggered": 0,
                         "readings": []})
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)

    # Stream coverage: % of expected 30-min slots that have data
    expected_slots = 48  # 24 hours × 2 readings/hour
    actual_slots   = len(series)
    stream_coverage = round(min(100, (actual_slots / expected_slots) * 100), 1)

    return {
        "total_alerts":        total_alerts,
        "critical":            critical,
        "warnings":            warnings,
        "ok_count":            ok_count,
        "info_count":          info_count,
        "alert_precision":     precision,
        "alert_recall":        recall,
        "time_in_range":       tir,
        "tir_met":             tir_met,
        "medication_adherence": adherence,
        "adherence_met":       adherence_met,
        "weekly_adherence":    weekly_avg,
        "activity_score":      activity_score,
        "activity_met":        activity_met,
        "latency_ms":          latency_ms,
        "stream_coverage":     stream_coverage,
    }