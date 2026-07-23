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
    # 1. LỌC FILE LỆNH SỬA CHỮA THEO NGÀY HÓA ĐƠN
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
            data_raw[
                "ngay_hoa_don"
            ].dt.year
            == year
        )
        & (
            data_raw[
                "ngay_hoa_don"
            ].dt.month
            == month
        )
    ].copy()

    # --------------------------------------------------------
    # 2. LOẠI TRẠNG THÁI KHÔNG HỢP LỆ
    # --------------------------------------------------------

    data = data[
        ~data[
            "trang_thai"
        ].isin(EXCLUDED_STATUS)
    ].copy()

    # Chỉ tính lệnh có doanh thu dương
    data = data[
        data[
            "doanh_thu_truoc_thue"
        ] > 0
    ].copy()

    # Chỉ giữ các dòng có Số lệnh
    data = data[
        data["ro_key"].notna()
    ].copy()

    # Nếu một Số lệnh xuất hiện nhiều dòng,
    # chỉ giữ một dòng để tránh đếm trùng
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
    # 3. TỔNG DOANH THU THEO FILE LỆNH SỬA CHỮA
    # --------------------------------------------------------

    invoice_revenue = data[
        "doanh_thu_truoc_thue"
    ].sum()

    # --------------------------------------------------------
    # 4. GHÉP VỚI FILE BẢNG TỔNG HỢP
    # --------------------------------------------------------

    parts_df = parts_data.get(
        selected_workshop,
        pd.DataFrame(),
    )

    if parts_df is None:
        parts_df = pd.DataFrame()

    if parts_df.empty:
        merged_data = data.copy()

        merged_data[
            "doanh_thu_cong_viec"
        ] = 0

        merged_data[
            "doanh_thu_phu_tung"
        ] = 0

        merged_data[
            "tong_doanh_thu_bang_tong_hop"
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

    # --------------------------------------------------------
    # 5. KIỂM TRA SỐ LỆNH GHÉP ĐƯỢC
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

    # --------------------------------------------------------
    # 6. CHUẨN HÓA CÁC CỘT DOANH THU
    # --------------------------------------------------------

    revenue_columns = [
        "doanh_thu_cong_viec",
        "doanh_thu_phu_tung",
        "tong_doanh_thu_bang_tong_hop",
    ]

    for column in revenue_columns:
        if column not in merged_data.columns:
            merged_data[column] = 0

        merged_data[column] = (
            pd.to_numeric(
                merged_data[column],
                errors="coerce",
            ).fillna(0)
        )

    # --------------------------------------------------------
    # 7. DOANH THU CÔNG VIỆC VÀ PHỤ TÙNG
    # --------------------------------------------------------

    service_revenue = merged_data[
        "doanh_thu_cong_viec"
    ].sum()

    parts_revenue = merged_data[
        "doanh_thu_phu_tung"
    ].sum()

    summary_revenue = merged_data[
        "tong_doanh_thu_bang_tong_hop"
    ].sum()

    # --------------------------------------------------------
    # 8. ĐỐI CHIẾU HAI FILE
    # --------------------------------------------------------

    summary_difference = (
        invoice_revenue
        - summary_revenue
    )

    # Cảnh báo nếu còn lệnh chưa ghép được
    if missing_orders > 0:
        st.warning(
            f"Còn {missing_orders:,} / "
            f"{actual_ro:,} lệnh theo Ngày hóa đơn "
            f"chưa tìm thấy trong file "
            f"Bảng tổng hợp của xưởng "
            f"{selected_workshop}. "
            f"Doanh thu phụ tùng có thể đang bị thiếu."
        )

    # Cảnh báo nếu tổng hai file không khớp
    if (
        missing_orders == 0
        and abs(summary_difference) > 1
    ):
        st.warning(
            f"Tổng doanh thu trong file Lệnh sửa chữa "
            f"và file Bảng tổng hợp đang chênh lệch "
            f"{summary_difference:,.0f} đồng."
        )

    # --------------------------------------------------------
    # 9. DOANH THU PHỤ KIỆN
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
    # 10. TỔNG DOANH THU
    # --------------------------------------------------------
    #
    # Quan trọng:
    # Tổng trước thuế trong file Lệnh sửa chữa
    # đã bằng:
    #
    # Doanh thu công việc + Doanh thu phụ tùng
    #
    # Vì vậy không được cộng phụ tùng thêm lần nữa.
    # --------------------------------------------------------

    actual_revenue = (
        invoice_revenue
        + accessory_revenue
    )

    # --------------------------------------------------------
    # 11. TỔNG TIỀN SAU THUẾ
    # --------------------------------------------------------

    total_after_tax = data[
        "tong_tien_sau_thue"
    ].sum()

    # --------------------------------------------------------
    # 12. TARGET
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
    # 13. TỶ LỆ HOÀN THÀNH
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
    # 14. TRẢ KẾT QUẢ VỀ APP
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

        # Doanh thu chi tiết
        "service_revenue": service_revenue,
        "parts_revenue": parts_revenue,
        "accessory_revenue": accessory_revenue,

        # Tổng theo file Lệnh sửa chữa
        "invoice_revenue": invoice_revenue,

        # Tổng theo file Bảng tổng hợp
        "summary_revenue": summary_revenue,
        "summary_difference": summary_difference,

        # Tổng doanh thu dashboard
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
