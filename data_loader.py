from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# ĐỌC FILE LỆNH SỬA CHỮA
# ============================================================

def read_service_file(
    file_path: Path,
    workshop_name: str,
    branch_name: str,
):
    if not file_path.exists():
        st.error(
            f"Không tìm thấy file lệnh sửa chữa: {file_path.name}"
        )
        st.stop()

    data = pd.read_excel(file_path)

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
        "Bảo hiểm": "bao_hiem_chi_tra",
    })

    required_columns = [
        "ro",
        "trang_thai",
        "ngay_hoa_don",
        "doanh_thu_truoc_thue",
        "tong_tien_sau_thue",
        "hang_xe",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        st.error(
            f"File {file_path.name} thiếu các cột: "
            + ", ".join(missing_columns)
        )
        st.stop()

    data["chi_nhanh"] = branch_name
    data["xuong"] = workshop_name

    data["ngay_hoa_don"] = pd.to_datetime(
        data["ngay_hoa_don"],
        errors="coerce",
        dayfirst=True,
    )

    money_columns = [
        "doanh_thu_truoc_thue",
        "tong_tien_sau_thue",
        "khach_hang_chi_tra",
        "bao_hiem_chi_tra",
    ]

    for column in money_columns:
        if column not in data.columns:
            data[column] = 0

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        ).fillna(0)

    data["trang_thai"] = (
        data["trang_thai"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    data["hang_xe"] = (
        data["hang_xe"]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    data["hang_xe"] = data["hang_xe"].replace({
        "HUYNDAI": "HYUNDAI",
        "HYNDAI": "HYUNDAI",
        "MERCEDES BENZ": "MERCEDES-BENZ",
        "LYNK&CO": "LYNK & CO",
        "LYNK AND CO": "LYNK & CO",
    })

    return data


# ============================================================
# ĐỌC TỔNG DOANH THU PHỤ TÙNG
# ============================================================

def read_parts_total(file_path: Path):
    if file_path is None:
        return 0

    if not file_path.exists():
        st.error(
            f"Không tìm thấy file phụ tùng: {file_path.name}"
        )
        st.stop()

    data = pd.read_excel(
        file_path,
        sheet_name="Báo cáo",
        header=3,
    )

    required_columns = [
        "Số lệnh sửa chữa",
        "Doanh thu phụ tùng",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        st.error(
            f"File {file_path.name} thiếu các cột: "
            + ", ".join(missing_columns)
        )
        st.stop()

    total_row = data[
        data["Số lệnh sửa chữa"]
        .fillna("")
        .astype(str)
        .str.contains(
            "Tổng cộng",
            case=False,
            na=False,
        )
    ]

    if total_row.empty:
        st.error(
            f"Không tìm thấy dòng Tổng cộng "
            f"trong file {file_path.name}"
        )
        st.stop()

    parts_revenue = pd.to_numeric(
        total_row["Doanh thu phụ tùng"],
        errors="coerce",
    ).sum()

    return parts_revenue


# ============================================================
# ĐỌC FILE LỆNH PHỤ KIỆN
# ============================================================

def read_accessory_file(file_path: Path | None):
    if file_path is None:
        return pd.DataFrame()

    if not file_path.exists():
        return pd.DataFrame()

    data = pd.read_excel(file_path)

    data = data.rename(columns={
        "Ngày hóa đơn": "ngay_hoa_don",
        "Tổng trước thuế": "doanh_thu_truoc_thue",
    })

    if "ngay_hoa_don" not in data.columns:
        return pd.DataFrame()

    if "doanh_thu_truoc_thue" not in data.columns:
        return pd.DataFrame()

    data["ngay_hoa_don"] = pd.to_datetime(
        data["ngay_hoa_don"],
        errors="coerce",
        dayfirst=True,
    )

    data["doanh_thu_truoc_thue"] = pd.to_numeric(
        data["doanh_thu_truoc_thue"],
        errors="coerce",
    ).fillna(0)

    return data


# ============================================================
# LOAD TOÀN BỘ DỮ LIỆU
# ============================================================

@st.cache_data
def load_all_data(workshop_config):
    service_frames = []
    parts_data = {}
    accessory_data = {}

    for workshop_name, config in workshop_config.items():
        branch_name = config["chi_nhanh"]

        service_df = read_service_file(
            file_path=config["service_file"],
            workshop_name=workshop_name,
            branch_name=branch_name,
        )

        service_frames.append(service_df)

        parts_data[workshop_name] = read_parts_total(
            config["parts_file"]
        )

        accessory_data[workshop_name] = read_accessory_file(
            config["accessory_file"]
        )

    if not service_frames:
        st.error("Không có dữ liệu lệnh sửa chữa để hiển thị.")
        st.stop()

    data_raw = pd.concat(
        service_frames,
        ignore_index=True,
    )

    return data_raw, parts_data, accessory_data
