# DAX Measures — HR Attrition & Workforce Analytics

Create these in Power BI: **Model view (or Report view) → right-click
Fact_Employee → New Measure**. Paste each formula exactly, then press Enter.

Do these in order — later measures reference earlier ones.

---

## Core KPIs

```dax
Total Employees = COUNTROWS(Fact_Employee)
```

```dax
Total Attritions =
CALCULATE(
    COUNTROWS(Fact_Employee),
    Fact_Employee[Attrition] = "Yes"
)
```

```dax
Active Employees = [Total Employees] - [Total Attritions]
```

```dax
Attrition Rate =
DIVIDE([Total Attritions], [Total Employees], 0)
```

```dax
Avg Monthly Income = AVERAGE(Fact_Employee[MonthlyIncome])
```

```dax
Avg Tenure (Years) = AVERAGE(Fact_Employee[YearsAtCompany])
```

```dax
Avg Job Satisfaction = AVERAGE(Fact_Employee[JobSatisfaction])
```

---

## Segmented attrition rates (for driver analysis charts)

```dax
Attrition Rate - OverTime =
CALCULATE([Attrition Rate], Fact_Employee[OverTime] = "Yes")
```

```dax
Attrition Rate - No OverTime =
CALCULATE([Attrition Rate], Fact_Employee[OverTime] = "No")
```

```dax
Attrition Rate - New Hires (<2yr) =
CALCULATE([Attrition Rate], Fact_Employee[YearsAtCompany] < 2)
```

---

## Time intelligence (this is the part that needs USERELATIONSHIP)

Fact_Employee has **two** date columns pointing at Dim_Date
(`HireDateKey` and `AttritionDateKey`), but Power BI only allows one
**active** relationship per pair of tables. So:

1. In **Model view**, you'll have already made `HireDateKey → Dim_Date[DateKey]`
   the ACTIVE relationship (solid line).
2. Make `AttritionDateKey → Dim_Date[DateKey]` an INACTIVE relationship
   (dashed line) — Power BI does this automatically for the second
   relationship between the same two tables.
3. To actually use that inactive relationship in a measure, you activate
   it temporarily with `USERELATIONSHIP`:

```dax
Attritions by Exit Date =
CALCULATE(
    [Total Attritions],
    USERELATIONSHIP(Fact_Employee[AttritionDateKey], Dim_Date[DateKey])
)
```

Use **this** measure (not `Total Attritions`) on any visual where the
X-axis is `Dim_Date` and you want to see *when people left* rather than
*when people were hired*. This is the single most "I actually understand
data modeling" thing in this whole project — be ready to explain it in
an interview.

```dax
YoY Attrition Change =
VAR CurrentPeriod = [Attritions by Exit Date]
VAR PriorPeriod =
    CALCULATE(
        [Attritions by Exit Date],
        USERELATIONSHIP(Fact_Employee[AttritionDateKey], Dim_Date[DateKey]),
        SAMEPERIODLASTYEAR(Dim_Date[Date])
    )
RETURN
    CurrentPeriod - PriorPeriod
```

---

## Optional calculated column (flag, not a measure)

Add this as a **New Column** on Fact_Employee (not a measure) to build a
"who's at risk right now" table/visual:

```dax
Flight Risk =
IF(
    Fact_Employee[Attrition] = "No" &&
    Fact_Employee[OverTime] = "Yes" &&
    Fact_Employee[JobSatisfaction] <= 2 &&
    Fact_Employee[YearsAtCompany] < 3,
    "High Risk",
    "Normal"
)
```
