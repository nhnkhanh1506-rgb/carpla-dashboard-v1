import streamlit as st


# ============================================================
# MÀU SẮC CHUNG
# ============================================================

BG_COLOR = "#EEF3F9"
TEXT_DARK = "#1F2937"
TEXT_MUTED = "#64748B"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#DBE3EE"

PRIMARY_BLUE = "#3B6FD8"
PRIMARY_BLUE_DARK = "#2F5FBE"
PRIMARY_BLUE_LIGHT = "#7FA7E6"

LINE_BLUE = "#8EC5FF"
LINE_BLUE_SOFT = "#A8D3FF"
PCT_TEXT_COLOR = "#DCEEFF"
BAR_LABEL_COLOR = "#FF8A80"

RED_MAIN = "#E45858"
RED_DARK = "#D64545"

DARK_PANEL = "#0B1530"
DARK_GRID = "rgba(255,255,255,0.10)"
WHITE = "#F8FAFC"

MUTED_BAR_COLORS = [
    "#335C99",
    "#426AA4",
    "#5278AF",
    "#6185BA",
    "#7193C4",
    "#80A0CE",
    "#90ADD7",
    "#9FB9DF",
    "#AFC6E7",
    "#BED2EE",
]

DONUT_MAIN = "#3C64A6"
DONUT_SECOND = "#9CC0DF"


# ============================================================
# ÁP DỤNG CSS CHO TOÀN BỘ APP
# ============================================================

def apply_global_style():
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {BG_COLOR};
            }}

            .block-container {{
                padding-top: 1.2rem;
                padding-bottom: 2rem;
                max-width: 1500px;
            }}

            [data-testid="stSidebar"] {{
                background:
                    linear-gradient(
                        180deg,
                        #1F2937 0%,
                        #111827 100%
                    );
            }}

            [data-testid="stSidebar"] * {{
                color: white !important;
            }}

            h1, h2, h3 {{
                color: {TEXT_DARK};
                font-weight: 800 !important;
            }}

            .hero-box {{
                background:
                    linear-gradient(
                        135deg,
                        #22314D 0%,
                        #2F456D 55%,
                        #496B9E 100%
                    );

                border-radius: 24px;
                padding: 28px 32px;
                color: white;
                margin-bottom: 24px;

                box-shadow:
                    0 10px 30px
                    rgba(31, 41, 55, 0.18);
            }}

            .hero-title {{
                font-size: 42px;
                font-weight: 900;
                line-height: 1.1;
                margin-bottom: 8px;
            }}

            .hero-subtitle {{
                font-size: 15px;
                color: #DBEAFE;
            }}

            .card {{
                background: {CARD_BG};
                border-radius: 22px;
                padding: 22px 24px;
                border: 1px solid {CARD_BORDER};

                box-shadow:
                    0 8px 24px
                    rgba(15, 23, 42, 0.06);

                min-height: 170px;
            }}

            .card-title {{
                font-size: 15px;
                font-weight: 700;
                color: {TEXT_MUTED};
                margin-bottom: 16px;
            }}

            .card-value {{
                font-size: 48px;
                font-weight: 900;
                color: #0F172A;
                line-height: 1;
                margin-bottom: 18px;
            }}

            .card-badge {{
                display: inline-block;
                padding: 8px 14px;
                border-radius: 999px;
                background: #E8F0FF;
                color: #1D4ED8;
                font-size: 13px;
                font-weight: 700;
            }}

            .section-card {{
                background: {CARD_BG};
                border-radius: 22px;
                padding: 22px 22px 18px 22px;
                border: 1px solid {CARD_BORDER};

                box-shadow:
                    0 8px 24px
                    rgba(15, 23, 42, 0.05);

                min-height: 170px;
                margin-bottom: 22px;
            }}

            .progress-title {{
                font-size: 16px;
                font-weight: 800;
                color: {TEXT_DARK};
                margin-bottom: 14px;
            }}

            .progress-sub {{
                font-size: 15px;
                color: #475569;
                margin-bottom: 8px;
                font-weight: 600;
            }}

            .progress-track {{
                position: relative;
                width: 100%;
                height: 10px;
                background: #E5E7EB;
                border-radius: 999px;
                margin-top: 38px;
            }}

            .progress-fill {{
                height: 10px;

                background:
                    linear-gradient(
                        90deg,
                        {RED_DARK},
                        {RED_MAIN}
                    );

                border-radius: 999px;
            }}

            .progress-dot {{
                position: absolute;
                top: -7px;
                width: 24px;
                height: 24px;
                background: {RED_MAIN};
                border: 4px solid white;
                border-radius: 50%;
                transform: translateX(-50%);

                box-shadow:
                    0 6px 16px
                    rgba(239, 68, 68, 0.22);
            }}

            .progress-label {{
                position: absolute;
                top: -34px;
                transform: translateX(-50%);
                font-size: 14px;
                font-weight: 800;
                color: {RED_MAIN};
                white-space: nowrap;
            }}

            .progress-scale {{
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                font-weight: 700;
                color: {TEXT_MUTED};
                margin-top: 10px;
            }}

            .mini-kpi {{
                background: {CARD_BG};
                border-radius: 18px;
                padding: 18px;
                border: 1px solid {CARD_BORDER};

                box-shadow:
                    0 8px 22px
                    rgba(15, 23, 42, 0.05);

                margin-bottom: 14px;
            }}

            .mini-kpi-title {{
                font-size: 13px;
                font-weight: 800;
                color: {TEXT_MUTED};
                text-transform: uppercase;
                margin-bottom: 8px;
            }}

            .mini-kpi-value {{
                font-size: 30px;
                font-weight: 900;
                color: #0F172A;
                margin-bottom: 10px;
            }}

            .mini-kpi-badge {{
                display: inline-block;
                padding: 6px 10px;
                border-radius: 999px;
                background: #ECFEFF;
                color: #0F766E;
                font-size: 12px;
                font-weight: 700;
            }}

            .section-label {{
                font-size: 17px;
                font-weight: 800;
                color: {TEXT_DARK};
                margin-bottom: 12px;
            }}

            div[data-testid="stDataFrame"] {{
                border-radius: 18px;
                overflow: hidden;
            }}

            .landing-shell {{
                max-width: 980px;
                margin: 3.5rem auto 0 auto;
                padding: 48px 52px;
                background: rgba(255,255,255,0.96);
                border: 1px solid #DBE3EE;
                border-radius: 28px;

                box-shadow:
                    0 18px 50px
                    rgba(15, 23, 42, 0.10);

                text-align: center;
            }}

            .landing-title {{
                margin-top: 10px;
                font-size: 38px;
                line-height: 1.15;
                font-weight: 900;
                color: #172554;
            }}

            .landing-description {{
                max-width: 760px;
                margin: 14px auto 30px auto;
                font-size: 17px;
                line-height: 1.7;
                color: #64748B;
            }}

            .landing-filter-title {{
                margin-top: 8px;
                margin-bottom: 10px;
                font-size: 16px;
                font-weight: 800;
                color: #334155;
            }}

            div.stButton > button {{
                min-height: 48px;
                border-radius: 14px;
                font-weight: 800;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
