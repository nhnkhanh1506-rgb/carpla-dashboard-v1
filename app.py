import pandas as pd
import streamlit as st

from calculations import (
    calculate_dashboard_metrics,
    calculate_target_plan,
    calculate_working_days,
)

from charts import (
    render_brand_section,
    render_daily_charts,
    render_payment_section,
)

from components import (
    fmt_m,
    fmt_m0,
    render_dashboard_header,
    render_homepage,
    render_interactive_target_planner,
    render_sidebar,
    render_top_kpis,
)

from config import (
    LOGO_FILE,
    TARGETS,
    WORKING_DAYS,
    WORKSHOP_CONFIG,
)

from data_loader import load_all_data
from styles import apply_global_style


# ============================================================
# HÀM ĐỊNH DẠNG BẢNG
# HEADER XÁM NHẠT, DÒNG DỮ LIỆU TRẮNG
# ============================================================

def style_white_table(dataframe):
    return (
        dataframe.style
        .set_properties(
            **{
                "background-color": "#FFFFFF",
                "color": "#1F2937",
                "border-color": "#E5E7EB",
                "font-weight": "500",
            }
        )
        .set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [
                        (
                            "background-color",
                            "#F3F4F6",
                        ),
                        (
                            "color",
                            "#6B7280",
                        ),
                        (
                            "font-weight",
                            "600",
                        ),
                        (
                            "border-color",
                            "#E5E7EB",
                        ),
                        (
                            "text-align",
                            "left",
                        ),
                    ],
                },
                {
                    "selector": "tbody td",
                    "props": [
                        (
                            "background-color",
                            "#FFFFFF",
                        ),
                        (
                            "color",
                            "#1F2937",
                        ),
                        (
                            "border-color",
                            "#E5E7EB",
                        ),
                    ],
                },
            ],
            overwrite=False,
        )
        .hide(axis="index")
    )


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dashboard DMS - Carpla Service",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. GLOBAL STYLE
# ============================================================

apply_global_style()


# ============================================================
# 3. LOAD DATA
# ============================================================

data_raw, parts_data, accessory_data = load_all_data(
    WORKSHOP_CONFIG
)


# ============================================================
# 4. SIDEBAR FILTER
# ============================================================

selection = _sidebar(
    data_raw=data_raw
)


# ============================================================
# 5. HOME PAGE
# ============================================================

if not selection["show_dashboard"]:
    _homepage(
        logo_path=LOGO_FILE
    )

    st.stop()


# ============================================================
# 6. SELECTED FILTERS
# ============================================================

selected_branch = selection["branch"]
selected_workshop = selection["workshop"]
year = int(selection["year"])
month = int(selection["month"])


# ============================================================
# 7. CALCULATE METRICS
# ============================================================

metrics = calculate_dashboard_metrics(
    data_raw=data_raw,
    parts_data=parts_data,
    accessory_data=accessory_data,
    selected_branch=selected_branch,
    selected_workshop=selected_workshop,
    year=year,
    month=month,
    targets=TARGETS,
)

data = metrics["data"]

actual_ro = metrics["actual_ro"]

service_revenue = metrics["service_revenue"]
parts_revenue = metrics["parts_revenue"]
accessory_revenue = metrics["accessory_revenue"]
actual_revenue = metrics["actual_revenue"]

total_after_tax = metrics["total_after_tax"]

target_ro = metrics["target_ro"]
target_revenue = metrics["target_revenue"]

ro_rate = metrics["ro_rate"]
revenue_rate = metrics["revenue_rate"]


# ============================================================
# 8. WARNING IF TARGET IS MISSING
# ============================================================

if target_ro == 0 and target_revenue == 0:
    st.warning(
        f"Chưa thiết lập target cho Chi nhánh "
        f"{selected_branch}, Xưởng {selected_workshop}, "
        f"tháng {month}/{year}."
    )


# ============================================================
# 9. DASHBOARD HEADER
# ============================================================

_dashboard_header(
    branch=selected_branch,
    workshop=selected_workshop,
    year=year,
    month=month,
)


# ============================================================
# 10. TOP KPI CARDS
# ============================================================

_top_kpis(
    metrics
)


# ============================================================
# 11. INTERACTIVE TARGET PLANNER
# ============================================================

working_day_info = calculate_working_days(
    year=year,
    month=month,
    data=data,
)

planner_result = _interactive_target_planner(
    actual_ro=actual_ro,
    target_ro=target_ro,
    actual_revenue=actual_revenue,
    target_revenue=target_revenue,
    working_day_info=working_day_info,
    calculate_target_plan_function=(
        calculate_target_plan
    ),
)


# ============================================================
# 11.1 SUMMARY TABLE
# ============================================================

summary_kpi = pd.DataFrame(
    {
        "Hạng mục": [
            "Lượt xe / RO",
            "Tổng Doanh thu",
        ],

        "Thực hiện": [
            f"{actual_ro:,.0f}",
            fmt_m(actual_revenue),
        ],

        "Chỉ tiêu": [
            f"{target_ro:,.0f}",
            fmt_m(target_revenue),
        ],

        "% đạt": [
            f"{ro_rate:.0%}",
            f"{revenue_rate:.0%}",
        ],
    }
)

st.dataframe(
    style_white_table(
        summary_kpi
    ),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# 12. REVENUE BREAKDOWN
# ============================================================

st.markdown(
    "## Cơ cấu tổng doanh thu"
)

revenue_breakdown = pd.DataFrame(
    {
        "Nguồn doanh thu": [
            "Doanh thu dịch vụ",
            "Doanh thu phụ tùng",
            "Doanh thu phụ kiện",
            "TỔNG DOANH THU",
        ],

        "Giá trị": [
            service_revenue,
            parts_revenue,
            accessory_revenue,
            actual_revenue,
        ],
    }
)

revenue_breakdown[
    "Giá trị hiển thị"
] = (
    revenue_breakdown["Giá trị"]
    .map(fmt_m)
)

revenue_breakdown["Tỷ trọng"] = [
    (
        service_revenue / actual_revenue
        if actual_revenue
        else 0
    ),

    (
        parts_revenue / actual_revenue
        if actual_revenue
        else 0
    ),

    (
        accessory_revenue / actual_revenue
        if actual_revenue
        else 0
    ),

    (
        1
        if actual_revenue
        else 0
    ),
]

revenue_breakdown[
    "Tỷ trọng"
] = (
    revenue_breakdown["Tỷ trọng"]
    .map(
        lambda value:
        f"{value:.0%}"
    )
)

revenue_breakdown_display = (
    revenue_breakdown[
        [
            "Nguồn doanh thu",
            "Giá trị hiển thị",
            "Tỷ trọng",
        ]
    ]
    .rename(
        columns={
            "Giá trị hiển thị":
                "Giá trị",
        }
    )
)

st.dataframe(
    style_white_table(
        revenue_breakdown_display
    ),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# 13. DAILY CHARTS
# ============================================================

render_daily_charts(
    data=merged_data,
    year=year,
    month=month,
    workshop=selected_workshop,
    target_ro=target_ro,
    target_revenue=target_revenue,
    working_days=WORKING_DAYS,
)


# ============================================================
# 14. BRAND SECTION
# ============================================================

render_brand_section(
    data=data
)


# ============================================================
# 15. PAYMENT STRUCTURE
# ============================================================

total_payment = render_payment_section(
    data=data
)


# ============================================================
# 16. CHECK TOTAL
# ============================================================

with st.expander(
    "Kiểm tra đối chiếu tổng"
):
    st.write(
        "Doanh thu dịch vụ:",
        fmt_m(service_revenue),
    )

    st.write(
        "Doanh thu phụ tùng:",
        fmt_m(parts_revenue),
    )

    st.write(
        "Doanh thu phụ kiện:",
        fmt_m(accessory_revenue),
    )

    st.write(
        "Tổng doanh thu:",
        fmt_m(actual_revenue),
    )

    st.write(
        "Tổng tiền sau thuế từ lệnh sửa chữa:",
        fmt_m(total_after_tax),
    )

    st.write(
        "Tổng cơ cấu nguồn thanh toán:",
        fmt_m(total_payment),
    )

    st.write(
        "Chênh lệch cơ cấu thanh toán:",
        fmt_m(
            total_after_tax
            - total_payment
        ),
    )


# ============================================================
# 17. RAW DATA
# ============================================================

with st.expander(
    "Xem dữ liệu lệnh sửa chữa"
):
    st.dataframe(
        data,
        use_container_width=True,
    )
