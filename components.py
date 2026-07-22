from pathlib import Path
import base64

import streamlit as st


# ============================================================
# HÀM FORMAT
# ============================================================

def fmt_m(value):
    return f"{value / 1_000_000:,.2f}M"


def fmt_m0(value):
    return f"{value / 1_000_000:,.0f}M"


# ============================================================
# KPI CARD
# ============================================================

def render_kpi_card(
    title,
    value,
    badge=None,
):
    badge_html = (
        f'<div class="card-badge">{badge}</div>'
        if badge
        else ""
    )

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROGRESS CARD
# ============================================================

def render_progress_card(
    title,
    actual_text,
    target_text,
    rate,
):
    percentage = rate * 100
    percentage_display = max(
        0,
        min(percentage, 100),
    )

    html = f"""
<div class="section-card">
    <div class="progress-title">{title}</div>
    <div class="progress-sub">Thực hiện: {actual_text} / {target_text}</div>
    <div class="progress-track">
        <div class="progress-fill" style="width:{percentage_display}%;"></div>
        <div class="progress-dot" style="left:{percentage_display}%;"></div>
        <div class="progress-label" style="left:{percentage_display}%;">{percentage:.2f}%</div>
    </div>
    <div class="progress-scale">
        <span>0%</span>
        <span>100%</span>
    </div>
</div>
"""

    st.markdown(
        html,
        unsafe_allow_html=True,
    )

# ============================================================
# MINI KPI
# ============================================================

def render_mini_kpi(
    title,
    value,
    badge=None,
):
    badge_html = (
        f'<div class="mini-kpi-badge">{badge}</div>'
        if badge
        else ""
    )

    st.markdown(
        f"""
        <div class="mini-kpi">
            <div class="mini-kpi-title">{title}</div>
            <div class="mini-kpi-value">{value}</div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR FILTER
# ============================================================

def render_sidebar(
    data_raw,
):
    if "show_dashboard" not in st.session_state:
        st.session_state.show_dashboard = False

    st.sidebar.markdown("## Bộ lọc")

    branch_options = sorted(
        data_raw["chi_nhanh"]
        .dropna()
        .unique()
    )

    selected_branch_input = st.sidebar.selectbox(
        "Chi nhánh",
        branch_options,
        key="sidebar_branch",
    )

    branch_data = data_raw[
        data_raw["chi_nhanh"]
        == selected_branch_input
    ].copy()

    workshop_options = sorted(
        branch_data["xuong"]
        .dropna()
        .unique()
    )

    selected_workshop_input = st.sidebar.selectbox(
        "Xưởng",
        workshop_options,
        key="sidebar_workshop",
    )

    workshop_data = branch_data[
        branch_data["xuong"]
        == selected_workshop_input
    ].copy()

    year_options = sorted(
        workshop_data["ngay_hoa_don"]
        .dropna()
        .dt.year
        .unique(),
        reverse=True,
    )

    selected_year_input = st.sidebar.selectbox(
        "Năm",
        year_options,
        key="sidebar_year",
    )

    month_options = sorted(
        workshop_data.loc[
            workshop_data[
                "ngay_hoa_don"
            ].dt.year
            == selected_year_input,
            "ngay_hoa_don",
        ]
        .dropna()
        .dt.month
        .unique()
    )

    selected_month_input = st.sidebar.selectbox(
        "Tháng",
        month_options,
        format_func=lambda value: (
            f"Tháng {int(value)}"
        ),
        key="sidebar_month",
    )

    if st.sidebar.button(
        "XEM DASHBOARD",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.selected_branch = (
            selected_branch_input
        )

        st.session_state.selected_workshop = (
            selected_workshop_input
        )

        st.session_state.selected_year = int(
            selected_year_input
        )

        st.session_state.selected_month = int(
            selected_month_input
        )

        st.session_state.show_dashboard = True
        st.rerun()

    if st.session_state.show_dashboard:
        if st.sidebar.button(
            "← TRANG CHỦ",
            use_container_width=True,
        ):
            st.session_state.show_dashboard = False
            st.rerun()

    return {
        "show_dashboard": (
            st.session_state.show_dashboard
        ),

        "branch": st.session_state.get(
            "selected_branch",
            selected_branch_input,
        ),

        "workshop": st.session_state.get(
            "selected_workshop",
            selected_workshop_input,
        ),

        "year": int(
            st.session_state.get(
                "selected_year",
                selected_year_input,
            )
        ),

        "month": int(
            st.session_state.get(
                "selected_month",
                selected_month_input,
            )
        ),
    }


# ============================================================
# HOMEPAGE
# ============================================================

def render_homepage(
    logo_path: Path,
):
    st.markdown(
        "<div style='height:55px;'></div>",
        unsafe_allow_html=True,
    )

    if logo_path.exists():
        logo_base64 = base64.b64encode(
            logo_path.read_bytes()
        ).decode("utf-8")

        logo_html = (
            '<img '
            f'src="data:image/png;base64,{logo_base64}" '
            'style="'
            'width:360px;'
            'max-width:72%;'
            'height:auto;'
            'display:block;'
            'margin:0 auto;'
            '">'
        )

    else:
        logo_html = """
        <div
            style="
                font-size:42px;
                font-weight:900;
                color:#172554;
            "
        >
            CARPLA SERVICES
        </div>
        """

    st.markdown(
        f"""
        <div
            style="
                max-width:900px;
                margin:0 auto;
                text-align:center;
                padding:36px 28px 42px 28px;
            "
        >
            {logo_html}

            <div
                style="
                    font-size:38px;
                    line-height:1.2;
                    font-weight:900;
                    color:#172554;
                    margin-top:28px;
                    margin-bottom:18px;
                "
            >
                DASHBOARD QUẢN TRỊ DMS
            </div>

            <div
                style="
                    max-width:790px;
                    margin:0 auto;
                    font-size:18px;
                    line-height:1.75;
                    color:#64748B;
                "
            >
                Nền tảng dashboard tập trung giúp theo dõi,
                phân tích và đánh giá hiệu quả hoạt động của
                các xưởng trong toàn hệ thống Carpla Services,
                bao gồm lượt xe, doanh thu, cơ cấu hãng xe,
                nguồn thanh toán và các chỉ số vận hành liên quan.
            </div>

            <div
                style="
                    margin-top:26px;
                    font-size:15px;
                    font-weight:700;
                    color:#475569;
                "
            >
                Vui lòng chọn Chi nhánh, Xưởng, Năm và Tháng
                tại bộ lọc bên trái, sau đó nhấn
                “XEM DASHBOARD”.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO DASHBOARD
# ============================================================

def render_dashboard_header(
    branch,
    workshop,
    year,
    month,
):
    html = f"""
<div class="hero-box">
    <div class="hero-title">Dashboard DMS - Xưởng {workshop}</div>
    <div class="hero-subtitle">Chi nhánh {branch} | Theo dõi hiệu quả hoạt động tháng {month}/{year}: lượt xe, doanh thu, cơ cấu hãng xe và nguồn thanh toán</div>
</div>
"""

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ============================================================
# TOP KPI SECTION
# ============================================================

def render_top_kpis(metrics):
    actual_ro = metrics["actual_ro"]
    actual_revenue = metrics["actual_revenue"]
    total_after_tax = metrics["total_after_tax"]
    revenue_per_ro = metrics["revenue_per_ro"]

    target_ro = metrics["target_ro"]
    target_revenue = metrics["target_revenue"]

    ro_rate = metrics["ro_rate"]
    revenue_rate = metrics["revenue_rate"]

    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:
        render_kpi_card(
            "Lượt xe / RO",
            f"{actual_ro:,.0f}",
            (
                f"Target: {target_ro:,.0f} | "
                f"Đạt: {ro_rate:.2%}"
            ),
        )

    with column_2:
        render_kpi_card(
            "Tổng doanh thu",
            fmt_m(actual_revenue),
            (
                f"Target: "
                f"{target_revenue / 1_000_000:,.0f}M | "
                f"Đạt: {revenue_rate:.2%}"
            ),
        )

    with column_3:
        render_kpi_card(
            "Tổng tiền sau thuế",
            fmt_m(total_after_tax),
        )

    with column_4:
        render_kpi_card(
            "Doanh thu / RO",
            fmt_m(revenue_per_ro),
        )

    st.markdown(
        "<div style='height:18px;'></div>",
        unsafe_allow_html=True,
    )
