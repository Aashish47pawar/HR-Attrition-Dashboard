"""
generate_hr_data.py
--------------------
Generates a realistic synthetic HR Attrition dataset, structured as a
proper STAR SCHEMA (fact + dimension tables) instead of one flat file --
on purpose, so you build real relationships in Power BI's Model view
instead of just importing a single table.

Loosely modeled on the well-known "IBM HR Analytics Employee Attrition"
dataset structure (same kind of columns recruiters/interviewers recognize),
but generated fresh with realistic correlations baked in:
    - OverTime + low JobSatisfaction + low WorkLifeBalance -> higher attrition
    - Higher MonthlyIncome + longer tenure -> lower attrition
    - Frequent business travel + long commute -> higher attrition
    - New hires (<2 years) leave more often than veterans

Output (in data/):
    dim_department.csv
    dim_jobrole.csv
    dim_date.csv
    fact_employee.csv
"""

import random
import csv
import os
from datetime import date, timedelta

random.seed(42)
N_EMPLOYEES = 1500
TODAY = date(2026, 9, 26)
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ---------------------------------------------------------------------------
# DIMENSION: Department
# ---------------------------------------------------------------------------
departments = [
    (1, "Sales"),
    (2, "Research & Development"),
    (3, "Human Resources"),
]

# ---------------------------------------------------------------------------
# DIMENSION: Job Role (linked to a department)
# ---------------------------------------------------------------------------
job_roles = [
    (1, "Sales Executive", 1),
    (2, "Sales Representative", 1),
    (3, "Manager - Sales", 1),
    (4, "Research Scientist", 2),
    (5, "Laboratory Technician", 2),
    (6, "Manufacturing Director", 2),
    (7, "Healthcare Representative", 2),
    (8, "Manager - R&D", 2),
    (9, "Human Resources Executive", 3),
    (10, "HR Business Partner", 3),
]

EDUCATION_FIELDS = ["Life Sciences", "Medical", "Marketing", "Technical Degree", "Human Resources", "Other"]
BUSINESS_TRAVEL = ["Non-Travel", "Travel_Rarely", "Travel_Frequently"]
MARITAL_STATUS = ["Single", "Married", "Divorced"]


def random_hire_date():
    """Hire dates spread over the last 15 years."""
    days_back = random.randint(30, 15 * 365)
    return TODAY - timedelta(days=days_back)


def build_dim_date(start_year=2011, end_year=2026):
    """One row per day is overkill for this dataset; use one row per month
    (common, practical choice for HR/attrition-style reporting)."""
    rows = []
    date_key_set = set()
    d = date(start_year, 1, 1)
    while d <= date(end_year, 12, 31):
        date_key = int(d.strftime("%Y%m%d"))
        rows.append({
            "DateKey": date_key,
            "Date": d.isoformat(),
            "Year": d.year,
            "Quarter": f"Q{(d.month - 1)//3 + 1}",
            "MonthNumber": d.month,
            "MonthName": d.strftime("%B"),
            "YearMonth": d.strftime("%Y-%m"),
        })
        date_key_set.add(date_key)
        # advance by 1 month
        if d.month == 12:
            d = date(d.year + 1, 1, 1)
        else:
            d = date(d.year, d.month + 1, 1)
    return rows


def to_month_date_key(d: date) -> int:
    """Snap any date down to the 1st of its month, matching Dim_Date's grain."""
    return int(d.replace(day=1).strftime("%Y%m%d"))


def build_fact_employee():
    rows = []
    for emp_id in range(1, N_EMPLOYEES + 1):
        job_role_id, role_name, dept_id = random.choice(job_roles)

        age = random.randint(21, 60)
        gender = random.choice(["Male", "Female"])
        marital_status = random.choice(MARITAL_STATUS)
        education_field = random.choice(EDUCATION_FIELDS)
        education_level = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 40, 30, 10])[0]

        hire_date = random_hire_date()
        years_at_company = round((TODAY - hire_date).days / 365, 1)
        total_working_years = round(years_at_company + random.uniform(0, 8), 1)
        years_in_current_role = round(min(years_at_company, random.uniform(0, years_at_company)), 1)
        years_since_last_promotion = round(min(years_at_company, random.uniform(0, years_at_company)), 1)
        years_with_curr_manager = round(min(years_at_company, random.uniform(0, years_at_company)), 1)
        num_companies_worked = random.randint(0, 6)

        business_travel = random.choices(BUSINESS_TRAVEL, weights=[15, 60, 25])[0]
        distance_from_home = random.randint(1, 30)
        overtime = random.choices(["Yes", "No"], weights=[30, 70])[0]

        job_level = random.choices([1, 2, 3, 4, 5], weights=[35, 30, 20, 10, 5])[0]
        base_income = {1: 3200, 2: 5500, 3: 8500, 4: 13000, 5: 19000}[job_level]
        monthly_income = round(max(2000, random.gauss(base_income, base_income * 0.18)), -1)
        percent_salary_hike = random.randint(11, 25)
        stock_option_level = random.choices([0, 1, 2, 3], weights=[45, 30, 15, 10])[0]

        job_involvement = random.choices([1, 2, 3, 4], weights=[8, 25, 50, 17])[0]
        job_satisfaction = random.choices([1, 2, 3, 4], weights=[15, 20, 30, 35])[0]
        environment_satisfaction = random.choices([1, 2, 3, 4], weights=[15, 20, 30, 35])[0]
        work_life_balance = random.choices([1, 2, 3, 4], weights=[10, 25, 45, 20])[0]
        relationship_satisfaction = random.choices([1, 2, 3, 4], weights=[12, 22, 36, 30])[0]
        performance_rating = random.choices([3, 4], weights=[85, 15])[0]
        training_times_last_year = random.randint(0, 6)

        # --- Attrition probability model (weighted score -> probability) ---
        score = 0.12  # base attrition rate
        if overtime == "Yes":
            score += 0.16
        if job_satisfaction <= 2:
            score += 0.10
        if work_life_balance <= 2:
            score += 0.08
        if business_travel == "Travel_Frequently":
            score += 0.07
        if distance_from_home > 20:
            score += 0.05
        if years_at_company < 2:
            score += 0.12
        if num_companies_worked >= 4:
            score += 0.05
        if monthly_income < base_income * 0.75:
            score += 0.06
        if stock_option_level == 0:
            score += 0.03
        if job_level >= 4:
            score -= 0.08
        if years_at_company > 10:
            score -= 0.10
        score = max(0.02, min(0.85, score))

        attrition = "Yes" if random.random() < score else "No"

        attrition_date = None
        if attrition == "Yes":
            # left sometime between hire date and today
            max_days = (TODAY - hire_date).days
            leave_offset = random.randint(30, max(31, max_days))
            attrition_date = hire_date + timedelta(days=leave_offset)
            if attrition_date > TODAY:
                attrition_date = TODAY

        rows.append({
            "EmployeeID": emp_id,
            "DepartmentID": dept_id,
            "JobRoleID": job_role_id,
            "HireDateKey": to_month_date_key(hire_date),
            "AttritionDateKey": to_month_date_key(attrition_date) if attrition_date else None,
            "Age": age,
            "Gender": gender,
            "MaritalStatus": marital_status,
            "EducationLevel": education_level,
            "EducationField": education_field,
            "BusinessTravel": business_travel,
            "DistanceFromHome": distance_from_home,
            "JobLevel": job_level,
            "MonthlyIncome": int(monthly_income),
            "PercentSalaryHike": percent_salary_hike,
            "StockOptionLevel": stock_option_level,
            "OverTime": overtime,
            "JobInvolvement": job_involvement,
            "JobSatisfaction": job_satisfaction,
            "EnvironmentSatisfaction": environment_satisfaction,
            "WorkLifeBalance": work_life_balance,
            "RelationshipSatisfaction": relationship_satisfaction,
            "PerformanceRating": performance_rating,
            "NumCompaniesWorked": num_companies_worked,
            "TotalWorkingYears": total_working_years,
            "YearsAtCompany": years_at_company,
            "YearsInCurrentRole": years_in_current_role,
            "YearsSinceLastPromotion": years_since_last_promotion,
            "YearsWithCurrManager": years_with_curr_manager,
            "TrainingTimesLastYear": training_times_last_year,
            "Attrition": attrition,
        })
    return rows


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows -> {path}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    write_csv(
        os.path.join(OUT_DIR, "dim_department.csv"),
        [{"DepartmentID": d[0], "DepartmentName": d[1]} for d in departments],
        ["DepartmentID", "DepartmentName"],
    )

    write_csv(
        os.path.join(OUT_DIR, "dim_jobrole.csv"),
        [{"JobRoleID": r[0], "JobRoleName": r[1], "DepartmentID": r[2]} for r in job_roles],
        ["JobRoleID", "JobRoleName", "DepartmentID"],
    )

    dim_date_rows = build_dim_date()
    write_csv(
        os.path.join(OUT_DIR, "dim_date.csv"),
        dim_date_rows,
        ["DateKey", "Date", "Year", "Quarter", "MonthNumber", "MonthName", "YearMonth"],
    )

    fact_rows = build_fact_employee()
    fact_fieldnames = list(fact_rows[0].keys())
    write_csv(os.path.join(OUT_DIR, "fact_employee.csv"), fact_rows, fact_fieldnames)

    n_attrition = sum(1 for r in fact_rows if r["Attrition"] == "Yes")
    print(f"\nOverall attrition rate: {n_attrition/len(fact_rows)*100:.1f}% "
          f"({n_attrition} of {len(fact_rows)} employees)")


if __name__ == "__main__":
    main()
