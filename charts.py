import calendar

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from components import (
    fmt_m,
    render_mini_kpi,
)

from styles import (
    PRIMARY_BLUE,
    PRIMARY_BLUE_LIGHT,
    LINE_BLUE,
    LINE_BLUE_SOFT,
    PCT_TEXT_COLOR,
    BAR_LABEL_COLOR,
    DARK_PANEL,
    DARK_GRID,
    WHITE,
    MUTED_BAR_COLORS,
    DONUT_MAIN,
    DONUT_SECOND,
)


# ============================================================
# HÀM CHIA AN TOÀN
# ============================================================

def safe_div(a, b):
    return a / b if b else 0


# ============================================================
# ĐỊNH DẠNG BẢNG
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
                        ("background-color", "#F3F4F6"),
                        ("color", "#6B7280"),
                        ("font-weight", "600"),
                        ("border-color", "#E5E7EB"),
                        ("text-align", "left"),
                    ],
                },
                {
                    "selector": "tbody td",
                    "props": [
                        ("background-color", "#FFFFFF"),
                        ("color", "#1F2937"),
                        ("border-color", "#E5E7EB"),
                    ],
                },
            ],
            overwrite=False,
        )
        .hide(axis="index")
    )


# ============================================================
# CHUẨN BỊ DỮ LIỆU THEO NGÀY
# ============================================================

def prepare_daily_data(
    data,
    year,
    month,
    target_ro,
    target_revenue,
    working_days,
):
    days_in_month = calendar.monthrange(
        year,
        month,
    )[1]

    days = list(
        range(
            1,
            days_in_month + 1,
        )
    )

    daily_source = data.dropna(
        subset=["ngay_hoa_don"]
    ).copy()

    daily_source[
        "doanh_thu_truoc_thue"
    ] = pd.to_numeric(
        daily_source[
            "doanh_thu_truoc_thue"
        ],
        errors="coerce",
    ).fillna(0)

    # CPUS và doanh thu đều chia theo Ngày hóa đơn.
    # Doanh thu Daily chỉ dùng Tổng trước thuế.
    daily = (
        daily_source
        .assign(
            day=lambda dataframe:
            dataframe[
                "ngay_hoa_don"
            ].dt.day
        )
        .groupby("day")
        .agg(
            ro=(
                "ro",
                "nunique",
            ),
            revenue=(
                "doanh_thu_truoc_thue",
                "sum",
            ),
        )
        .reindex(
            days,
            fill_value=0,
        )
        .reset_index()
    )

    daily["revenue_m"] = (
        daily["revenue"]
        / 1_000_000
    )

    daily["cum_ro"] = (
        daily["ro"].cumsum()
    )

    daily["cum_revenue"] = (
        daily["revenue"].cumsum()
    )

    target_ro_day = safe_div(
        target_ro,
        working_days,
    )

    target_revenue_day = safe_div(
        target_revenue,
        working_days,
    )

    daily["target_cum_ro"] = [
        target_ro_day
        * min(day, working_days)
        for day in daily["day"]
    ]

    daily["target_cum_revenue"] = [
        target_revenue_day
        * min(day, working_days)
        for day in daily["day"]
    ]

    daily["cum_ro_pct"] = (
        daily["cum_ro"]
        / daily["target_cum_ro"]
        * 100
    )

    daily["cum_revenue_pct"] = (
        daily["cum_revenue"]
        / daily["target_cum_revenue"]
        * 100
    )

    daily["cum_ro_pct"] = (
        daily["cum_ro_pct"]
        .replace(
            [
                float("inf"),
                -float("inf"),
            ],
            0,
        )
        .fillna(0)
    )

    daily["cum_revenue_pct"] = (
        daily["cum_revenue_pct"]
        .replace(
            [
                float("inf"),
                -float("inf"),
            ],
            0,
        )
        .fillna(0)
    )

    return (
        daily,
        days,
        target_ro_day,
        target_revenue_day,
    )


# ============================================================
# BIỂU ĐỒ LƯỢT XE THEO NGÀY
# ============================================================

def build_ro_daily_chart(
    daily,
    days,
    workshop,
):
    figure = make_subplots(
        specs=[
            [
                {
                    "secondary_y": True,
                }
            ]
        ]
    )

    figure.add_trace(
        go.Bar(
            x=daily["day"],
            y=daily["ro"],

            marker=dict(
                color=PRIMARY_BLUE,
                line=dict(
                    color=PRIMARY_BLUE_LIGHT,
                    width=1,
                ),
            ),

            name="RO/ngày",

            text=[
                f"{int(value)}"
                if value > 0
                else ""
                for value in daily["ro"]
            ],

            textposition="outside",

            textfont=dict(
                color=BAR_LABEL_COLOR,
                size=14,
            ),

            cliponaxis=False,
        ),
        secondary_y=False,
    )

    figure.add_trace(
        go.Scatter(
            x=daily["day"],
            y=daily["cum_ro_pct"],

            mode="lines+markers+text",

            line=dict(
                color=LINE_BLUE,
                width=2.5,
                dash="dot",
            ),

            marker=dict(
                size=6,
                color=LINE_BLUE_SOFT,
                line=dict(
                    color="#D7EAFE",
                    width=1,
                ),
            ),

            text=[
                f"{value:.0f}%"
                if value > 0
                else ""
                for value in daily[
                    "cum_ro_pct"
                ]
            ],

            textposition="bottom center",

            textfont=dict(
                size=10,
                color=PCT_TEXT_COLOR,
            ),

            name="% đạt lũy kế",
        ),
        secondary_y=True,
    )

    figure.update_layout(
        template="plotly_dark",
        height=370,
        paper_bgcolor=DARK_PANEL,
        plot_bgcolor=DARK_PANEL,

        font=dict(
            color=WHITE,
        ),

        margin=dict(
            l=30,
            r=30,
            t=65,
            b=40,
        ),

        showlegend=False,

        title=dict(
            text=(
                f"CPUS DAILY - "
                f"{workshop.upper()}"
            ),
            x=0.5,
            font=dict(
                size=19,
                color=WHITE,
            ),
        ),
    )

    figure.update_xaxes(
        tickmode="array",
        tickvals=days,
        showgrid=False,
        color="rgba(248,250,252,0.85)",
        linecolor="rgba(255,255,255,0.22)",
    )

    figure.update_yaxes(
        showgrid=True,
        gridcolor=DARK_GRID,
        color="rgba(248,250,252,0.85)",
        zeroline=False,
        secondary_y=False,
    )

    figure.update_yaxes(
        range=[0, 300],
        ticksuffix="%",
        showgrid=False,
        color="rgba(248,250,252,0.85)",
        zeroline=False,
        secondary_y=True,
    )

    return figure


# ============================================================
# BIỂU ĐỒ DOANH THU THEO NGÀY
# ============================================================

def build_revenue_daily_chart(
    daily,
    days,
    workshop,
):
    figure = make_subplots(
        specs=[
            [
                {
                    "secondary_y": True,
                }
            ]
        ]
    )

    figure.add_trace(
        go.Bar(
            x=daily["day"],
            y=daily["revenue_m"],

            marker=dict(
                color=PRIMARY_BLUE,
                line=dict(
                    color=PRIMARY_BLUE_LIGHT,
                    width=1,
                ),
            ),

            name="Doanh thu/ngày",

            text=[
                f"{value:.1f}M"
                if value > 0
                else ""
                for value in daily[
                    "revenue_m"
                ]
            ],

            textposition="outside",

            textfont=dict(
                color=BAR_LABEL_COLOR,
                size=14,
            ),

            cliponaxis=False,
        ),
        secondary_y=False,
    )

    figure.add_trace(
        go.Scatter(
            x=daily["day"],
            y=daily[
                "cum_revenue_pct"
            ],

            mode="lines+markers+text",

            line=dict(
                color=LINE_BLUE,
                width=2.5,
                dash="dot",
            ),

            marker=dict(
                size=6,
                color=LINE_BLUE_SOFT,
                line=dict(
                    color="#D7EAFE",
                    width=1,
                ),
            ),

            text=[
                f"{value:.0f}%"
                if value > 0
                else ""
                for value in daily[
                    "cum_revenue_pct"
                ]
            ],

            textposition="bottom center",

            textfont=dict(
                size=10,
                color=PCT_TEXT_COLOR,
            ),

            name="% đạt lũy kế",
        ),
        secondary_y=True,
    )

    figure.update_layout(
        template="plotly_dark",
        height=370,
        paper_bgcolor=DARK_PANEL,
        plot_bgcolor=DARK_PANEL,

        font=dict(
            color=WHITE,
        ),

        margin=dict(
            l=30,
            r=30,
            t=65,
            b=40,
        ),

        showlegend=False,

        title=dict(
            text=(
                f"DOANH THU DAILY - "
                f"{workshop.upper()}"
            ),
            x=0.5,
            font=dict(
                size=19,
                color=WHITE,
            ),
        ),
    )

    figure.update_xaxes(
        tickmode="array",
        tickvals=days,
        showgrid=False,
        color="rgba(248,250,252,0.85)",
        linecolor="rgba(255,255,255,0.22)",
    )

    figure.update_yaxes(
        showgrid=True,
        gridcolor=DARK_GRID,
        color="rgba(248,250,252,0.85)",
        zeroline=False,
        secondary_y=False,
    )

    figure.update_yaxes(
        range=[0, 300],
        ticksuffix="%",
        showgrid=False,
        color="rgba(248,250,252,0.85)",
        zeroline=False,
        secondary_y=True,
    )

    return figure


# ============================================================
# HIỂN THỊ BIỂU ĐỒ THEO NGÀY
# ============================================================

def render_daily_charts(
    data,
    year,
    month,
    workshop,
    target_ro,
    target_revenue,
    working_days,
):
    st.markdown(
        "## 2. Lượt xe & Doanh thu theo ngày"
    )

    (
        daily,
        days,
        target_ro_day,
        target_revenue_day,
    ) = prepare_daily_data(
        data=data,
        year=year,
        month=month,
        target_ro=target_ro,
        target_revenue=target_revenue,
        working_days=working_days,
    )

    total_ro = daily[
        "ro"
    ].sum()

    total_revenue = daily[
        "revenue"
    ].sum()

    actual_ro_average = safe_div(
        total_ro,
        working_days,
    )

    actual_revenue_average = safe_div(
        total_revenue,
        working_days,
    )

    revenue_per_cpus = safe_div(
        total_revenue,
        total_ro,
    )

    # HÀNG 1: CPUS DAILY
    ro_chart_column, ro_kpi_column = (
        st.columns(
            [4.6, 1.25]
        )
    )

    with ro_chart_column:
        ro_figure = build_ro_daily_chart(
            daily=daily,
            days=days,
            workshop=workshop,
        )

        st.plotly_chart(
            ro_figure,
            use_container_width=True,
        )

    with ro_kpi_column:
        render_mini_kpi(
            "CPUS TB/NGÀY",
            f"{actual_ro_average:.0f}",
        )

        render_mini_kpi(
            "CPUS/NGÀY TARGET",
            f"{target_ro_day:.0f}",
        )

    # HÀNG 2: DOANH THU DAILY
    revenue_chart_column, revenue_kpi_column = (
        st.columns(
            [4.6, 1.25]
        )
    )

    with revenue_chart_column:
        revenue_figure = (
            build_revenue_daily_chart(
                daily=daily,
                days=days,
                workshop=workshop,
            )
        )

        st.plotly_chart(
            revenue_figure,
            use_container_width=True,
        )

    with revenue_kpi_column:
        render_mini_kpi(
            "DT TB/CPUS",
            fmt_m(
                revenue_per_cpus
            ),
        )

        render_mini_kpi(
            "DT TB/NGÀY",
            fmt_m(
                actual_revenue_average
            ),
        )

        render_mini_kpi(
            "DT TB/NGÀY TARGET",
            fmt_m(
                target_revenue_day
            ),
        )

# ============================================================
# HÃNG XE
# ============================================================

def render_brand_section(data):
    st.markdown(
        "## 3. Hãng xe"
    )

    required_columns = [
        "ro",
        "hang_xe",
        "doanh_thu_truoc_thue",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        st.error(
            "Dữ liệu phần Hãng xe thiếu các cột: "
            + ", ".join(missing_columns)
        )
        st.stop()

    brand_data = data.copy()

    brand_data[
        "doanh_thu_truoc_thue"
    ] = pd.to_numeric(
        brand_data[
            "doanh_thu_truoc_thue"
        ],
        errors="coerce",
    ).fillna(0)

    brand_data[
        "hang_xe"
    ] = (
        brand_data[
            "hang_xe"
        ]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .str.strip()
    )

    # Danh sách lệnh và hãng lấy từ file Lệnh sửa chữa.
    # Doanh thu theo hãng dùng Tổng trước thuế.
    brand_summary = (
        brand_data
        .groupby(
            "hang_xe"
        )
        .agg(
            so_ro=(
                "ro",
                "nunique",
            ),
            doanh_thu=(
                "doanh_thu_truoc_thue",
                "sum",
            ),
        )
        .reset_index()
        .sort_values(
            "doanh_thu",
            ascending=False,
        )
    )

    total_ro_brand = (
        brand_summary[
            "so_ro"
        ].sum()
    )

    total_revenue_brand = (
        brand_summary[
            "doanh_thu"
        ].sum()
    )

    brand_summary[
        "ty_trong_ro"
    ] = (
        brand_summary["so_ro"]
        / total_ro_brand
        if total_ro_brand
        else 0
    )

    brand_summary[
        "ty_trong_doanh_thu"
    ] = (
        brand_summary["doanh_thu"]
        / total_revenue_brand
        if total_revenue_brand
        else 0
    )

    brand_display = (
        brand_summary.copy()
    )

    brand_display[
        "doanh_thu"
    ] = (
        brand_display[
            "doanh_thu"
        ].map(fmt_m)
    )

    brand_display[
        "ty_trong_ro"
    ] = (
        brand_display[
            "ty_trong_ro"
        ]
        .map(
            lambda value:
            f"{value:.0%}"
        )
    )

    brand_display[
        "ty_trong_doanh_thu"
    ] = (
        brand_display[
            "ty_trong_doanh_thu"
        ]
        .map(
            lambda value:
            f"{value:.0%}"
        )
    )

    brand_display = (
        brand_display.rename(
            columns={
                "hang_xe": "Hãng xe",
                "so_ro": "Số RO",
                "doanh_thu": (
                    "Doanh thu trước thuế"
                ),
                "ty_trong_ro": (
                    "Tỷ trọng RO"
                ),
                "ty_trong_doanh_thu": (
                    "Tỷ trọng doanh thu"
                ),
            }
        )
    )

    total_row = pd.DataFrame(
        {
            "Hãng xe": [
                "TỔNG"
            ],
            "Số RO": [
                total_ro_brand
            ],
            "Doanh thu trước thuế": [
                fmt_m(
                    total_revenue_brand
                )
            ],
            "Tỷ trọng RO": [
                "100%"
            ],
            "Tỷ trọng doanh thu": [
                "100%"
            ],
        }
    )

    brand_display = pd.concat(
        [
            brand_display,
            total_row,
        ],
        ignore_index=True,
    )

    left_column, right_column = (
        st.columns(
            [1.35, 1]
        )
    )

    # ========================================================
    # BẢNG CHI TIẾT
    # ========================================================

    with left_column:
        st.markdown(
            '<div class="section-label">'
            'Bảng chi tiết theo hãng xe'
            '</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(
            style_white_table(
                brand_display
            ),
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # BIỂU ĐỒ TOP HÃNG XE
    # ========================================================

    with right_column:
        st.markdown(
            '<div class="section-label">'
            'Top hãng xe theo doanh thu'
            '</div>',
            unsafe_allow_html=True,
        )

        brand_chart = (
            brand_summary
            .head(10)
            .sort_values(
                "doanh_thu",
                ascending=True,
            )
            .copy()
        )

        brand_chart[
            "doanh_thu_m"
        ] = (
            brand_chart[
                "doanh_thu"
            ]
            / 1_000_000
        )

        color_list = (
            MUTED_BAR_COLORS[
                :len(brand_chart)
            ]
        )

        figure = go.Figure()

        figure.add_trace(
            go.Bar(
                x=brand_chart[
                    "doanh_thu_m"
                ],
                y=brand_chart[
                    "hang_xe"
                ],

                orientation="h",

                marker=dict(
                    color=color_list,
                    line=dict(
                        color="#E5ECF6",
                        width=0.5,
                    ),
                ),

                text=[
                    f"{value:.1f}M"
                    for value
                    in brand_chart[
                        "doanh_thu_m"
                    ]
                ],

                textposition="outside",

                textfont=dict(
                    color="#667085",
                    size=12,
                ),

                cliponaxis=False,

                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Doanh thu trước thuế: "
                    "%{x:.1f}M"
                    "<extra></extra>"
                ),
            )
        )

        figure.update_layout(
            template="simple_white",

            # Chỉ giảm chiều cao để cân với bảng.
            height=405,

            margin=dict(
                 l=24,
        r=62,
        t=18,
        b=42,
    ),

            xaxis_title=(
                "Doanh thu trước thuế (M)"
            ),

            yaxis_title="",

            paper_bgcolor="white",
            plot_bgcolor="white",

            font=dict(
                color="#475467",
            ),

            showlegend=False,
        )

        figure.update_xaxes(
            showgrid=True,
            gridcolor="#E5E7EB",
            zeroline=False,

            title_font=dict(
                color="#667085",
            ),

            tickfont=dict(
                color="#667085",
            ),
        )

        figure.update_yaxes(
            showgrid=False,

            tickfont=dict(
                color="#667085",
            ),
        )

        # Container chỉ dùng để bo góc ô graph này.
        chart_card = st.container(
            key="brand_revenue_chart_card"
        )

        with chart_card:
            st.plotly_chart(
                figure,
                use_container_width=True,
            )


# ============================================================
# CƠ CẤU NGUỒN THANH TOÁN
# ============================================================

def render_payment_section(data):
    st.markdown(
        "## 4. Cơ cấu nguồn thanh toán"
    )

    required_columns = [
        "khach_hang_chi_tra",
        "bao_hiem_chi_tra",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        st.error(
            "Thiếu cột nguồn thanh toán: "
            + ", ".join(missing_columns)
        )
        return 0

    # ========================================================
    # LẤY TRỰC TIẾP TỪ FILE LỆNH SỬA CHỮA
    # ========================================================

    customer_value = pd.to_numeric(
        data["khach_hang_chi_tra"],
        errors="coerce",
    ).fillna(0).sum()

    insurance_value = pd.to_numeric(
        data["bao_hiem_chi_tra"],
        errors="coerce",
    ).fillna(0).sum()

    total_payment = (
        customer_value
        + insurance_value
    )

    # ========================================================
    # DỮ LIỆU BẢNG
    # ========================================================

    payment_structure = pd.DataFrame(
        {
            "Nguồn thanh toán": [
                "Bảo hiểm chi trả",
                "Khách hàng chi trả",
            ],

            "Giá trị": [
                insurance_value,
                customer_value,
            ],
        }
    )

    payment_structure[
        "Tỷ trọng"
    ] = payment_structure[
        "Giá trị"
    ].apply(
        lambda value:
        safe_div(
            value,
            total_payment,
        )
    )

    payment_display = (
        payment_structure.copy()
    )

    payment_display[
        "Giá trị"
    ] = payment_display[
        "Giá trị"
    ].map(
        fmt_m
    )

    payment_display[
        "Tỷ trọng"
    ] = payment_display[
        "Tỷ trọng"
    ].map(
        lambda value:
        f"{value:.2%}"
    )

    total_row = pd.DataFrame(
        {
            "Nguồn thanh toán": [
                "TỔNG"
            ],

            "Giá trị": [
                fmt_m(
                    total_payment
                )
            ],

            "Tỷ trọng": [
                "100.00%"
            ],
        }
    )

    payment_display = pd.concat(
        [
            payment_display,
            total_row,
        ],
        ignore_index=True,
    )

    # ========================================================
    # LAYOUT
    # ========================================================

    left_column, right_column = (
        st.columns(
            [1, 1]
        )
    )

    # ========================================================
    # BẢNG CƠ CẤU NGUỒN THANH TOÁN
    # ========================================================

    with left_column:
        st.markdown(
            '<div class="section-label">'
            'Bảng cơ cấu nguồn thanh toán'
            '</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(
            style_white_table(
                payment_display
            ),
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # BIỂU ĐỒ DONUT
    # ========================================================

    with right_column:
        st.markdown(
            '<div class="section-label">'
            'Tỷ trọng nguồn thanh toán'
            '</div>',
            unsafe_allow_html=True,
        )

        figure = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        "Khách hàng chi trả",
                        "Bảo hiểm chi trả",
                    ],

                    values=[
                        customer_value,
                        insurance_value,
                    ],

                    hole=0.58,

                    marker=dict(
                        colors=[
                            DONUT_MAIN,
                            DONUT_SECOND,
                        ]
                    ),

                    textinfo="percent",

                    texttemplate=(
                        "%{percent:.0%}"
                    ),

                    textfont=dict(
                        size=15,
                        color="white",
                    ),

                    domain=dict(
                        x=[0.08, 0.78],
                        y=[0.10, 0.90],
                    ),

                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Giá trị: %{value:,.0f}<br>"
                        "Tỷ trọng: %{percent:.2%}"
                        "<extra></extra>"
                    ),
                )
            ]
        )

        figure.update_layout(
            template="simple_white",
            height=410,

            margin=dict(
                l=10,
                r=20,
                t=10,
                b=10,
            ),

            legend=dict(
                orientation="v",
                y=0.5,
                yanchor="middle",
                x=0.82,
                xanchor="left",

                font=dict(
                    color="#475467",
                ),
            ),

            paper_bgcolor="white",
            plot_bgcolor="white",

            font=dict(
                color="#475467",
            ),
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    return total_payment
