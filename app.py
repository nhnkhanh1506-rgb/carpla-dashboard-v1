import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ======================
# 1. PAGE CONFIG
# ======================

st.set_page_config(
    page_title="Dashboard DMS - Đà Nẵng",
    layout="wide"
)

# ======================
# 2. FILE + TARGET
# ======================

DATA_FILE = Path("Lệnh sửa chữa (repair.order)_DN1307.xlsx")

TARGET_RO = 488
TARGET_REVENUE = 1_105_000_000

# ======================
# 3. LOAD DATA
# ======================

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_FILE)

    data = df.copy()

    data = data.rename(columns={
        "Số": "ro",
        "Trạng thái": "trang_thai",
        "Ngày hóa đơn": "ngay_hoa_don",
        "Tổng trước thuế": "doanh_thu_truoc_thue",
        "Tổng tiền": "tong_tien_sau_thue",
        "Hãng xe": "hang_xe",
        "Dòng xe": "dong_xe",
        "Khách hàng": "ten_khach_hang",
        "Khách hàng.1": "khach_hang_chi_tra",
        "Bảo hiểm": "bao_hiem_chi_tra"
    })

    data["ngay_hoa_don"] = pd.to_datetime(data["ngay_hoa_don"], errors="coerce")

    money_cols = [
        "doanh_thu_truoc_thue",
        "tong_tien_sau_thue",
        "khach_hang_chi_tra",
        "bao_hiem_chi_tra"
    ]

    for col in money_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    data["trang_thai"] = data["trang_thai"].astype(str).str.strip()
    data["hang_xe"] = data["hang_xe"].astype(str).str.upper().str.strip()

    data["hang_xe"] = data["hang_xe"].replace({
        "HUYNDAI": "HYUNDAI",
        "HYNDAI": "HYUNDAI",
        "MERCEDES BENZ": "MERCEDES-BENZ",
        "LYNK&CO": "LYNK & CO",
        "LYNK AND CO": "LYNK & CO"
    })

    return data


data_raw = load_data()

# ======================
# 4. TITLE + FILTER
# ======================

st.title("Dashboard DMS - Xưởng Đà Nẵng")

st.sidebar.header("Bộ lọc")

year = st.sidebar.selectbox("Năm", [2026], index=0)
month = st.sidebar.selectbox("Tháng", [7], index=0)

data = data_raw.copy()

# Lọc theo Ngày hóa đơn
data = data[
    (data["ngay_hoa_don"].dt.year == year) &
    (data["ngay_hoa_don"].dt.month == month)
]

exclude_status = [
    "Báo giá",
    "Hủy",
    "Không thực hiện",
    "Không duyệt",
    "Nháp"
]

data = data[~data["trang_thai"].isin(exclude_status)]

# Chỉ lấy dòng có doanh thu trước thuế > 0
data = data[data["doanh_thu_truoc_thue"] > 0]

# ======================
# 5. KPI
# ======================

actual_ro = data["ro"].nunique()
actual_revenue = data["doanh_thu_truoc_thue"].sum()
total_after_tax = data["tong_tien_sau_thue"].sum()

ro_rate = actual_ro / TARGET_RO if TARGET_RO > 0 else 0
revenue_rate = actual_revenue / TARGET_REVENUE if TARGET_REVENUE > 0 else 0
revenue_per_ro = actual_revenue / actual_ro if actual_ro > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric(
    "Lượt xe / RO",
    f"{actual_ro:,.0f}",
    f"Target: {TARGET_RO:,.0f} | {ro_rate:.2%}"
)

kpi2.metric(
    "Doanh thu trước thuế",
    f"{actual_revenue / 1_000_000:,.2f}M",
    f"Target: {TARGET_REVENUE / 1_000_000:,.0f}M | {revenue_rate:.2%}"
)

kpi3.metric(
    "Tổng tiền sau thuế",
    f"{total_after_tax / 1_000_000:,.2f}M"
)

kpi4.metric(
    "DT trước thuế / RO",
    f"{revenue_per_ro / 1_000_000:,.2f}M"
)

st.divider()

# ======================
# 6. SUMMARY TABLE
# ======================

st.subheader("1. Lượt xe và doanh thu: Chỉ tiêu / Thực hiện")

summary_kpi = pd.DataFrame({
    "Chỉ tiêu": ["Lượt xe / RO", "Doanh thu trước thuế"],
    "Target": [
        f"{TARGET_RO:,.0f}",
        f"{TARGET_REVENUE / 1_000_000:,.0f}M"
    ],
    "Thực hiện": [
        f"{actual_ro:,.0f}",
        f"{actual_revenue / 1_000_000:,.2f}M"
    ],
    "% đạt": [
        f"{ro_rate:.2%}",
        f"{revenue_rate:.2%}"
    ]
})

st.dataframe(summary_kpi, use_container_width=True, hide_index=True)

# ======================
# 7. BRAND SUMMARY
# ======================

st.subheader("2. Hãng xe")

brand_summary = (
    data.groupby("hang_xe")
    .agg(
        so_ro=("ro", "nunique"),
        doanh_thu=("doanh_thu_truoc_thue", "sum")
    )
    .reset_index()
    .sort_values("doanh_thu", ascending=False)
)

total_ro_brand = brand_summary["so_ro"].sum()
total_revenue_brand = brand_summary["doanh_thu"].sum()

brand_summary["ty_trong_ro"] = brand_summary["so_ro"] / total_ro_brand
brand_summary["ty_trong_doanh_thu"] = brand_summary["doanh_thu"] / total_revenue_brand

brand_display = brand_summary.copy()

brand_display["doanh_thu"] = brand_display["doanh_thu"].map(
    lambda x: f"{x / 1_000_000:,.2f}M"
)

brand_display["ty_trong_ro"] = brand_display["ty_trong_ro"].map(
    lambda x: f"{x:.2%}"
)

brand_display["ty_trong_doanh_thu"] = brand_display["ty_trong_doanh_thu"].map(
    lambda x: f"{x:.2%}"
)

brand_display = brand_display.rename(columns={
    "hang_xe": "Hãng xe",
    "so_ro": "Số RO",
    "doanh_thu": "Doanh thu trước thuế",
    "ty_trong_ro": "Tỷ trọng RO",
    "ty_trong_doanh_thu": "Tỷ trọng doanh thu"
})

total_brand_row = pd.DataFrame({
    "Hãng xe": ["TỔNG"],
    "Số RO": [total_ro_brand],
    "Doanh thu trước thuế": [f"{total_revenue_brand / 1_000_000:,.2f}M"],
    "Tỷ trọng RO": ["100.00%"],
    "Tỷ trọng doanh thu": ["100.00%"]
})

brand_display = pd.concat(
    [brand_display, total_brand_row],
    ignore_index=True
)

left, right = st.columns([1.2, 1])

with left:
    st.dataframe(brand_display, use_container_width=True, hide_index=True)

with right:
    brand_chart = brand_summary.head(10).copy()
    brand_chart["doanh_thu_M"] = brand_chart["doanh_thu"] / 1_000_000

    fig_brand = px.bar(
        brand_chart,
        x="hang_xe",
        y="doanh_thu_M",
        text="doanh_thu_M",
        title="Top hãng xe theo doanh thu"
    )

    fig_brand.update_traces(
        texttemplate="%{text:.1f}M",
        textposition="outside"
    )

    fig_brand.update_layout(
        xaxis_title="Hãng xe",
        yaxis_title="Doanh thu trước thuế (M)",
        height=420
    )

    st.plotly_chart(fig_brand, use_container_width=True)

# ======================
# 8. PAYMENT STRUCTURE
# ======================

st.subheader("3. Cơ cấu nguồn thanh toán")

bao_hiem_value = data["bao_hiem_chi_tra"].sum()
khach_hang_value = data["khach_hang_chi_tra"].sum()

payment_structure = pd.DataFrame({
    "Nguồn thanh toán": [
        "Bảo hiểm chi trả",
        "Khách hàng chi trả"
    ],
    "Giá trị": [
        bao_hiem_value,
        khach_hang_value
    ]
})

total_payment = payment_structure["Giá trị"].sum()

payment_structure["Tỷ trọng"] = payment_structure["Giá trị"] / total_payment

payment_display = payment_structure.copy()

payment_display["Giá trị"] = payment_display["Giá trị"].map(
    lambda x: f"{x / 1_000_000:,.2f}M"
)

payment_display["Tỷ trọng"] = payment_display["Tỷ trọng"].map(
    lambda x: f"{x:.2%}"
)

total_payment_row = pd.DataFrame({
    "Nguồn thanh toán": ["TỔNG"],
    "Giá trị": [f"{total_payment / 1_000_000:,.2f}M"],
    "Tỷ trọng": ["100.00%"]
})

payment_display = pd.concat(
    [payment_display, total_payment_row],
    ignore_index=True
)

left, right = st.columns([1, 1])

with left:
    st.dataframe(payment_display, use_container_width=True, hide_index=True)

with right:
    fig_payment = px.pie(
        payment_structure,
        names="Nguồn thanh toán",
        values="Giá trị",
        title="Tỷ trọng nguồn thanh toán"
    )

    st.plotly_chart(fig_payment, use_container_width=True)

# ======================
# 9. CHECK TOTAL
# ======================

with st.expander("Kiểm tra đối chiếu tổng"):
    st.write(
        "Tổng doanh thu trước thuế:",
        f"{actual_revenue / 1_000_000:,.2f}M"
    )

    st.write(
        "Tổng tiền sau thuế:",
        f"{total_after_tax / 1_000_000:,.2f}M"
    )

    st.write(
        "Tổng cơ cấu nguồn thanh toán:",
        f"{total_payment / 1_000_000:,.2f}M"
    )

    st.write(
        "Chênh Tổng tiền sau thuế - Cơ cấu:",
        f"{(total_after_tax - total_payment) / 1_000_000:,.2f}M"
    )

# ======================
# 10. RAW DATA
# ======================

with st.expander("Xem dữ liệu chi tiết"):
    st.dataframe(data, use_container_width=True)