import calendar
from datetime import date

import pandas as pd
import streamlit as st


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
    # 1. LỌC LỆNH THEO NGÀY HÓA ĐƠN
    # --------------------------------------------------------

    data = data_raw[
        (
            data_raw["chi_nhanh"]
            == selected_branch
        )
        & (
            data_raw["xuong"]
            == selected_workshop
        )
        & (
            data_raw["ngay_hoa_don"].dt.year
            == year
        )
        & (
            data_raw["ngay_hoa_don"].dt.month
            == month
        )
    ].copy()

    # Loại trạng thái không hợp lệ
    data = data[
        ~data["trang_thai"].isin(
            EXCLUDED_STATUS
        )
    ].copy()

    # Chỉ lấy lệnh có doanh thu dương
    data = data[
        data["doanh_thu_truoc_thue"] > 0
    ].copy()

    # Chỉ lấy dòng có số lệnh
    data = data[
        data["ro_key"].notna()
    ].copy()

    # Mỗi số lệnh chỉ giữ một dòng
    data = (
        data.sort_values(
            "ngay_hoa_don"
        )
        .drop_duplicates(
            subset=["ro_key"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # 2. DOANH THU DỊCH VỤ
    # --------------------------------------------------------
    #
    # Lấy Tổng trước thuế trong file
    # hn_pvd_service_2026_07.xlsx
    # --------------------------------------------------------

    service_revenue = data[
        "doanh_thu_truoc_thue"
    ].sum()

    # --------------------------------------------------------
    # 3. GHÉP DOANH THU PHỤ TÙNG THEO SỐ LỆNH
    # --------------------------------------------------------

    parts_df = parts_data.get(
        selected_workshop,
        pd.DataFrame(),
    )

    if (
        parts_df is None
        or parts_df.empty
    ):
        merged_data = data.copy()

        merged_data[
            "doanh_thu_phu_tung"
        ] = 0

        merged_data[
            "tim_thay_trong_bang_tong_hop"
        ] = False

    else:
        merged_data = data.merge(
            parts_df,
            on="ro_key",
            how="left",
            indicator=True,
        )

        merged_data[
            "tim_thay_trong_bang_tong_hop"
        ] = (
            merged_data["_merge"]
            == "both"
        )

        merged_data = merged_data.drop(
            columns=["_merge"]
        )

    merged_data[
        "doanh_thu_phu_tung"
    ] = pd.to_numeric(
        merged_data[
            "doanh_thu_phu_tung"
        ],
        errors="coerce",
    ).fillna(0)

    # --------------------------------------------------------
    # 4. KIỂM TRA SỐ LỆNH GHÉP
    # --------------------------------------------------------

    actual_ro = data[
        "ro_key"
    ].nunique()

    matched_orders = int(
        merged_data[
            "tim_thay_trong_bang_tong_hop"
        ].sum()
    )

    missing_orders = (
        actual_ro
        - matched_orders
    )

    if missing_orders > 0:
        st.warning(
            f"Còn {missing_orders:,}/{actual_ro:,} "
            f"lệnh theo Ngày hóa đơn chưa tìm thấy "
            f"trong file Bảng tổng hợp. "
            f"Doanh thu phụ tùng có thể bị thiếu."
        )

    # --------------------------------------------------------
    # 5. DOANH THU PHỤ TÙNG
    # --------------------------------------------------------
    #
    # Chỉ cộng doanh thu phụ tùng của đúng các lệnh
    # trong file dịch vụ đã lọc theo Ngày hóa đơn.
    # --------------------------------------------------------

    parts_revenue = merged_data[
        "doanh_thu_phu_tung"
    ].sum()

    # --------------------------------------------------------
    # 6. DOANH THU PHỤ KIỆN
    # --------------------------------------------------------

    accessory_df = accessory_data.get(
        selected_workshop,
        pd.DataFrame(),
    )

    accessory_revenue = 0

    if (
        accessory_df is not None
        and not accessory_df.empty
        and "ngay_hoa_don"
        in accessory_df.columns
        and "doanh_thu_truoc_thue"
        in accessory_df.columns
    ):
        accessory_df = (
            accessory_df.copy()
        )

        accessory_df[
            "ngay_hoa_don"
        ] = pd.to_datetime(
            accessory_df[
                "ngay_hoa_don"
            ],
            errors="coerce",
            dayfirst=True,
        )

        accessory_filtered = accessory_df[
            (
                accessory_df[
                    "ngay_hoa_don"
                ].dt.year
                == year
            )
            & (
                accessory_df[
                    "ngay_hoa_don"
                ].dt.month
                == month
            )
        ].copy()

        accessory_revenue = (
            accessory_filtered[
                "doanh_thu_truoc_thue"
            ].sum()
        )

    # --------------------------------------------------------
    # 7. TỔNG DOANH THU
    # --------------------------------------------------------
    #
    # Tổng doanh thu =
    # Tổng trước thuế file dịch vụ
    # + Doanh thu phụ tùng của các lệnh match
    # + Doanh thu phụ kiện
    # --------------------------------------------------------

    actual_revenue = (
        service_revenue
        + parts_revenue
        + accessory_revenue
    )

    # --------------------------------------------------------
    # 8. TỔNG TIỀN SAU THUẾ
    # --------------------------------------------------------

    total_after_tax = data[
        "tong_tien_sau_thue"
    ].sum()

    # --------------------------------------------------------
    # 9. TARGET
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
    target_revenue = (
        target_info["revenue"]
    )

    # --------------------------------------------------------
    # 10. TỶ LỆ HOÀN THÀNH
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
    # 11. TRẢ KẾT QUẢ VỀ APP
    # --------------------------------------------------------

    return {
        "data": data,
        "merged_data": merged_data,

        "selected_branch": selected_branch,
        "selected_workshop": selected_workshop,
        "year": year,
        "month": month,

        "actual_ro": actual_ro,
        "matched_orders": matched_orders,
        "missing_orders": missing_orders,

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

def calculate_working_days(
    year,
    month,
    data,
):
    """
    Quy ước:
    - Làm việc tất cả các ngày trừ Chủ nhật.
    - Ngày chốt dữ liệu là Ngày hóa đơn mới nhất.
    - Ngày còn lại bắt đầu từ ngày kế tiếp.
    """

    days_in_month = calendar.monthrange(
        year,
        month,
    )[1]

    working_dates = [
        date(
            year,
            month,
            day,
        )
        for day in range(
            1,
            days_in_month + 1,
        )
        if date(
            year,
            month,
            day,
        ).weekday() != 6
    ]

    total_working_days = len(
        working_dates
    )

    valid_dates = data[
        "ngay_hoa_don"
    ].dropna()

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
        "data_cutoff_date": (
            data_cutoff_date
        ),
        "total_working_days": (
            total_working_days
        ),
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
        "remaining_required": (
            remaining_required
        ),
        "average_required": (
            average_required
        ),
        "already_achieved": (
            already_achieved
        ),
    }
