import calendar
from datetime import date

import pandas as pd

# ============================================================
# TRẠNG THÁI KHÔNG ĐƯỢC TÍNH
# ============================================================

EXCLUDED_STATUS = [
    "Báo giá",
    "Hủy",
    "Không thực hiện",
    "Không duyệt",
    "Nháp",
]


# ============================================================
# HÀM CHIA AN TOÀN
# ============================================================

def safe_div(a, b):
    return a / b if b else 0


# ============================================================
# TÍNH TOÀN BỘ KPI DASHBOARD
# ============================================================

def calculate_dashboard_metrics(
    data_raw,
    parts_data,
    accessory_data,
    selected_branch,
    selected_workshop,
    year,
    month,
    targets,
):
    # --------------------------------------------------------
    # 1. LỌC DỮ LIỆU LỆNH SỬA CHỮA
    # --------------------------------------------------------

    data = data_raw[
        (data_raw["chi_nhanh"] == selected_branch)
        & (data_raw["xuong"] == selected_workshop)
        & (data_raw["ngay_hoa_don"].dt.year == year)
        & (data_raw["ngay_hoa_don"].dt.month == month)
    ].copy()

    data = data[
        ~data["trang_thai"].isin(EXCLUDED_STATUS)
    ]

    data = data[
        data["doanh_thu_truoc_thue"] > 0
    ]

    # --------------------------------------------------------
    # 2. DOANH THU DỊCH VỤ
    # --------------------------------------------------------

    service_revenue = data[
        "doanh_thu_truoc_thue"
    ].sum()

    # --------------------------------------------------------
    # 3. DOANH THU PHỤ TÙNG
    # --------------------------------------------------------

    parts_revenue = parts_data.get(
        selected_workshop,
        0,
    )

    # --------------------------------------------------------
    # 4. DOANH THU PHỤ KIỆN
    # --------------------------------------------------------

    accessory_df = accessory_data.get(
        selected_workshop,
        pd.DataFrame(),
    )

    accessory_revenue = 0

    if (
        not accessory_df.empty
        and "ngay_hoa_don" in accessory_df.columns
        and "doanh_thu_truoc_thue" in accessory_df.columns
    ):
        accessory_df = accessory_df.copy()

        accessory_df["ngay_hoa_don"] = pd.to_datetime(
            accessory_df["ngay_hoa_don"],
            errors="coerce",
            dayfirst=True,
        )

        accessory_filtered = accessory_df[
            (accessory_df["ngay_hoa_don"].dt.year == year)
            & (accessory_df["ngay_hoa_don"].dt.month == month)
        ].copy()

        accessory_revenue = accessory_filtered[
            "doanh_thu_truoc_thue"
        ].sum()

    # --------------------------------------------------------
    # 5. TỔNG DOANH THU
    # --------------------------------------------------------

    actual_revenue = (
        service_revenue
        + parts_revenue
        + accessory_revenue
    )

    # --------------------------------------------------------
    # 6. LƯỢT XE / RO
    # --------------------------------------------------------

    actual_ro = data["ro"].nunique()

    # --------------------------------------------------------
    # 7. TỔNG TIỀN SAU THUẾ
    # --------------------------------------------------------

    total_after_tax = data[
        "tong_tien_sau_thue"
    ].sum()

    # --------------------------------------------------------
    # 8. TARGET
    # --------------------------------------------------------

    target_info = targets.get(
        (
            selected_branch,
            selected_workshop,
            year,
            month,
        ),
        {
            "ro": 0,
            "revenue": 0,
        },
    )

    target_ro = target_info["ro"]
    target_revenue = target_info["revenue"]

    # --------------------------------------------------------
    # 9. TỶ LỆ HOÀN THÀNH
    # --------------------------------------------------------

    ro_rate = safe_div(
        actual_ro,
        target_ro,
    )

    revenue_rate = safe_div(
        actual_revenue,
        target_revenue,
    )

    revenue_per_ro = safe_div(
        actual_revenue,
        actual_ro,
    )

    # --------------------------------------------------------
    # 10. TRẢ KẾT QUẢ VỀ APP
    # --------------------------------------------------------

    return {
        "data": data,

        "selected_branch": selected_branch,
        "selected_workshop": selected_workshop,
        "year": year,
        "month": month,

        "actual_ro": actual_ro,

        "service_revenue": service_revenue,
        "parts_revenue": parts_revenue,
        "accessory_revenue": accessory_revenue,
        "actual_revenue": actual_revenue,

        "total_after_tax": total_after_tax,

        "target_ro": target_ro,
        "target_revenue": target_revenue,

        "ro_rate": ro_rate,
        "revenue_rate": revenue_rate,
        "revenue_per_ro": revenue_per_ro,
    }


# ============================================================
# TÍNH NGÀY LÀM VIỆC, KHÔNG BAO GỒM CHỦ NHẬT
# ============================================================

def calculate_working_days(year, month, data):
    """
    Quy ước:
    - Một tháng làm việc tất cả các ngày trừ Chủ nhật.
    - Ngày chốt dữ liệu là ngày hóa đơn mới nhất.
    - Ngày còn lại bắt đầu từ ngày kế tiếp sau ngày chốt dữ liệu.
    """

    days_in_month = calendar.monthrange(
        year,
        month,
    )[1]

    working_dates = [
        date(year, month, day)
        for day in range(1, days_in_month + 1)
        if date(year, month, day).weekday() != 6
    ]

    total_working_days = len(working_dates)

    valid_dates = (
        data["ngay_hoa_don"]
        .dropna()
    )

    if valid_dates.empty:
        data_cutoff_date = date(
            year,
            month,
            1,
        )
    else:
        data_cutoff_date = (
            valid_dates.max().date()
        )

    remaining_working_dates = [
        working_date
        for working_date in working_dates
        if working_date > data_cutoff_date
    ]

    elapsed_working_dates = [
        working_date
        for working_date in working_dates
        if working_date <= data_cutoff_date
    ]

    return {
        "data_cutoff_date": data_cutoff_date,
        "total_working_days": total_working_days,
        "elapsed_working_days": len(
            elapsed_working_dates
        ),
        "remaining_working_days": len(
            remaining_working_dates
        ),
        "remaining_working_dates": (
            remaining_working_dates
        ),
    }


# ============================================================
# TÍNH YÊU CẦU BÌNH QUÂN CHO MỤC TIÊU TƯƠNG TÁC
# ============================================================

def calculate_target_plan(
    actual_value,
    monthly_target,
    desired_percentage,
    remaining_working_days,
):
    desired_value = (
        monthly_target
        * desired_percentage
        / 100
    )

    remaining_required = max(
        desired_value - actual_value,
        0,
    )

    if remaining_working_days > 0:
        average_required = (
            remaining_required
            / remaining_working_days
        )
    else:
        average_required = 0

    already_achieved = (
        actual_value >= desired_value
    )

    return {
        "desired_value": desired_value,
        "remaining_required": remaining_required,
        "average_required": average_required,
        "already_achieved": already_achieved,
    }
