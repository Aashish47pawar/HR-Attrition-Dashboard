# HR Attrition & Workforce Analytics Dashboard (Power BI)

Identifies which employee segments are leaving at the highest rates and
why — using a proper star-schema data model instead of one flat table.

---

## Files in this project

```
hr-attrition-dashboard/
├── data/
│   ├── fact_employee.csv       # 1,500 employees, one row each
│   ├── dim_department.csv      # 3 departments
│   ├── dim_jobrole.csv         # 10 job roles, linked to a department
│   └── dim_date.csv            # Monthly calendar, 2011–2026
├── src/
│   └── generate_hr_data.py     # Regenerates the dataset if you want to tweak it
├── DAX_measures.md             # Every DAX formula you need, ready to paste
└── README.md                   # This file
```

---

## The data model (star schema)

```
        Dim_Department
              │
              │ (DepartmentID)
              ▼
        Dim_JobRole ──(JobRoleID)──▶ Fact_Employee ◀──(HireDateKey)── Dim_Date
                                          │                              ▲
                                          └────(AttritionDateKey)────────┘
                                               (inactive relationship)
```

- **Fact_Employee** — one row per employee, with all the numeric/categorical
  attributes (income, satisfaction scores, tenure, attrition flag, etc.)
- **Dim_Department**, **Dim_JobRole** — lookup tables for clean slicers and
  readable labels instead of raw IDs
- **Dim_Date** — a proper calendar table, linked TWICE to Fact_Employee
  (once for hire date, once for attrition date) — this is what lets you
  correctly answer both "how many people were hired each year" and "how
  many people left each year" from the same date table, which is exactly
  what real HR reporting needs.

---

## Step-by-step build in Power BI Desktop

### Step 1 — Install Power BI Desktop
Download free from https://powerbi.microsoft.com/desktop (Microsoft
account required, no paid license needed for this).

### Step 2 — Import the 4 CSVs
Home → Get Data → Text/CSV → select `fact_employee.csv`. Repeat for the
other 3 files. Click **Load** (not "Transform Data") for each — the data
is already clean.

### Step 3 — Build the relationships (Model view)
Click the **Model** icon on the left sidebar (looks like connected boxes).
Drag to connect:
- `Fact_Employee[DepartmentID]` → `Dim_Department[DepartmentID]`
- `Fact_Employee[JobRoleID]` → `Dim_JobRole[JobRoleID]`
- `Fact_Employee[HireDateKey]` → `Dim_Date[DateKey]`
- `Fact_Employee[AttritionDateKey]` → `Dim_Date[DateKey]`

For each, double-click the line and confirm: **Cardinality = Many to one
(*:1)**, **Cross filter direction = Single**. The 4th relationship
(AttritionDateKey) will automatically show as a **dashed line** — that's
correct, it means "inactive," and `DAX_measures.md` shows you exactly how
to use it anyway with `USERELATIONSHIP`.

### Step 4 — Mark Dim_Date as an actual Date Table
Click on `Dim_Date` table → in the ribbon, **Table tools → Mark as Date
Table** → pick the `Date` column. This unlocks proper time-intelligence
functions (`SAMEPERIODLASTYEAR`, etc.).

### Step 5 — Add all the DAX measures
Open `DAX_measures.md` and add each measure exactly as shown, in order,
via Report view → right-click `Fact_Employee` in the Fields pane → **New
Measure**.

### Step 6 — Build the report pages

**Page 1 — Executive Overview**
- 4 KPI Cards: `Total Employees`, `Attrition Rate`, `Avg Tenure (Years)`, `Avg Monthly Income`
- Line chart: `Dim_Date[YearMonth]` (X-axis) vs `Attritions by Exit Date` (Y-axis) — shows attrition trend over time
- Donut chart: `Attrition Rate` by `Dim_Department[DepartmentName]`

**Page 2 — Attrition Drivers**
- Clustered bar chart: `Attrition Rate - OverTime` vs `Attrition Rate - No OverTime` side by side
- Bar chart: `Attrition Rate` by `Fact_Employee[JobSatisfaction]` (1–4)
- Scatter chart: `MonthlyIncome` (X) vs `YearsAtCompany` (Y), colored by `Attrition` — visually separates who's leaving
- Table: `Fact_Employee[Flight Risk]` = "High Risk" filtered view, showing names/IDs of at-risk current employees (add the `Flight Risk` calculated column from `DAX_measures.md` first)

**Page 3 — Department & Role Deep-Dive**
- Slicer: `Dim_Department[DepartmentName]`
- Table: `Dim_JobRole[JobRoleName]` × `Attrition Rate` × `Avg Monthly Income`
- Bar chart: headcount by `JobRoleName`

### Step 7 — Polish
- Consistent color: pick ONE color for "Attrition = Yes" (e.g., red/orange)
  and use it consistently across every chart on every page — this is the
  single biggest visual-polish win in Power BI.
- Add a title text box and your name/date at the top of Page 1.
- File → Export → Export to PDF (gives you something to attach/share
  even if the person viewing doesn't have Power BI installed).

### Step 8 — (Optional) Publish
Home → Publish → sign in with a free Power BI account → publish to your
own workspace. This gives you a shareable web link, similar to what we
did with the Streamlit dashboard.

---

## Talking points for interviews / resume bullet

- **Data modeling:** designed a star schema (1 fact table, 3 dimension
  tables) instead of a single denormalized sheet — the standard
  professional pattern in Power BI/Tableau, not just "one big Excel table."
- **Advanced DAX:** used `USERELATIONSHIP` to activate a second date
  relationship for exit-date reporting, and `SAMEPERIODLASTYEAR` for
  year-over-year attrition comparison — genuinely intermediate/advanced
  DAX, not just `SUM()`.
- **Business insight, not just charts:** the dashboard directly answers
  "who's about to leave and why" (the Flight Risk table) — the kind of
  actionable output an HR/People Ops team would actually use.

## Next steps to make this even stronger
- Swap in the real IBM HR Analytics Employee Attrition dataset from
  Kaggle (same general column structure) for extra "real data" credibility.
- Add a "what-if" parameter (Power BI's What-If parameter feature) to
  simulate "if we reduced overtime by X%, attrition rate would change by Y%."
- Add row-level security (RLS) by department as a bonus advanced feature
  to mention in interviews, even if you don't fully implement it.
