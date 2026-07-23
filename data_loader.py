from pathlib import Path
import re
import unicodedata

import pandas as pd
import streamlit as st


# ============================================================
# HÀM CHUẨN HÓA CHUỖI
# ============================================================

def normalize_text(value):
    """
    Chuẩn hóa chuỗi để nhận diện tên cột:
    - Bỏ dấu tiếng Việt
    - Chuyển thành chữ thường
    - Thay ký tự đặc biệt bằng dấu _
    """
    value = str(value).strip()

    value = unicodedata.normalize(
        "NFD",
        value,
    )

    value = "".join(
        character
        for character in value
        if unicodedata.category(character) != "Mn"
    )

    value = value.lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "_",
        value,
    )

    return value.strip("_")


# ============================================================
# CHUẨN HÓA SỐ LỆNH
# ============================================================

def normalize_order_number(series):
    """
    Chuẩn hóa Số lệnh để ghép giữa hai file.
    """
    return (
        series.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(
            r"\s+",
            " ",
            regex=True,
        )
        .replace({
            "": pd.NA,
            "NAN": pd.NA,
            "NONE": pd.NA,
        })
    )


# ============================================================
# CHUYỂN CỘT TIỀN VỀ DẠNG SỐ
# ============================================================

def parse_money(series):
    """
    Chuyển dữ liệu tiền về dạng số.
    """
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(
            ",",
            "",
            regex=False,
        )
        .str.replace(
            " ",
            "",
            regex=False,
        )
        .str.replace(
            r"[^\d\-.]",
            "",
            regex=True,
        )
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce",
    ).fillna(0)


# ============================================================
# TÌM TÊN CỘT
# ============================================================

def find_column(
    data,
    possible_names,
    file_name,
    required=True,
):
    """
    Tìm tên cột thực tế dựa trên nhiều tên có thể có.
    """
    normalized_columns = {
        normalize_text(column): column
        for column in data.columns
    }

    for possible_name in possible_names:
        normalized_name = normalize_text(
            possible_name
        )

        if normalized_name in normalized_columns:
            return normalized_columns[
                normalized_name
            ]

    if required:
        st.error(
            f"Không tìm thấy cột cần thiết trong "
            f"file {file_name}.\n\n"
            f"Các tên đang tìm: "
            f"{', '.join(possible_names)}"
        )
        st.stop()

    return None


# ============================================================
# ĐỌC EXCEL VÀ TỰ TÌM DÒNG TIÊU ĐỀ
# ============================================================

def read_excel_with_header_detection(
    file_path: Path,
    expected_columns,
    preferred_sheet=None,
):
    """
    Tự tìm dòng tiêu đề trong file Excel.

    Phù hợp với file Bảng tổng hợp có vài dòng
    mô tả nằm phía trên bảng dữ liệu.
    """
    if not file_path.exists():
        st.error(
            f"Không tìm thấy file: "
            f"{file_path.name}"
        )
        st.stop()

    excel_file = pd.ExcelFile(
        file_path
    )

    if (
        preferred_sheet
        and preferred_sheet in excel_file.sheet_names
    ):
        sheet_name = preferred_sheet
    else:
        sheet_name = excel_file.sheet_names[0]

    preview = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=None,
        nrows=30,
    )

    normalized_expected = {
        normalize_text(column)
        for column in expected_columns
    }

    header_row = None

    for row_index in range(len(preview)):
        row_values = {
            normalize_text(value)
            for value in preview.iloc[
                row_index
            ].dropna()
        }

        if normalized_expected.issubset(
            row_values
        ):
            header_row = row_index
            break

    if header_row is None:
        st.error(
            f"Không xác định được dòng tiêu đề "
            f"trong file {file_path.name}."
        )
        st.stop()

    data = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=header_row,
    )

    data = data.dropna(
        how="all"
    ).copy()

    data.columns = [
        str(column).strip()
        for column in data.columns
    ]

    return data


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
            f"Không tìm thấy file lệnh sửa chữa: "
            f"{file_path.name}"
        )
        st.stop()

    data = pd.read_excel(
        file_path
    )

    data.columns = [
        str(column).strip()
        for column in data.columns
    ]

    data = data.rename(columns={
        "Số": "ro",
        "Trạng thái": "trang_thai",
        "Ngày hóa đơn": "ngay_hoa_don",
        "Ngày hoá đơn": "ngay_hoa_don",
        "Tổng trước thuế": (
            "doanh_thu_truoc_thue"
        ),
        "Tổng tiền": "tong_tien_sau_thue",
        "Hãng xe": "hang_xe",
        "Dòng xe": "dong_xe",
        "Khách hàng": "ten_khach_hang",
        "Khách hàng.1": (
            "khach_hang_chi_tra"
        ),
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

    # Thông tin chi nhánh và xưởng
    data["chi_nhanh"] = branch_name
    data["xuong"] = workshop_name

    # Chuẩn hóa số lệnh
    data["ro_key"] = normalize_order_number(
        data["ro"]
    )

    # Chuẩn hóa ngày hóa đơn
    data["ngay_hoa_don"] = pd.to_datetime(
        data["ngay_hoa_don"],
        errors="coerce",
        dayfirst=True,
    )

    # Chuẩn hóa các cột tiền
    money_columns = [
        "doanh_thu_truoc_thue",
        "tong_tien_sau_thue",
        "khach_hang_chi_tra",
        "bao_hiem_chi_tra",
    ]

    for column in money_columns:
        if column not in data.columns:
            data[column] = 0

        data[column] = parse_money(
            data[column]
        )

    # Chuẩn hóa trạng thái
    data["trang_thai"] = (
        data["trang_thai"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Chuẩn hóa hãng xe
    data["hang_xe"] = (
        data["hang_xe"]
        .fillna("KHÔNG XÁC ĐỊNH")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    data["hang_xe"] = data[
        "hang_xe"
    ].replace({
        "HUYNDAI": "HYUNDAI",
        "HYNDAI": "HYUNDAI",
        "MERCEDES BENZ": "MERCEDES-BENZ",
        "LYNK&CO": "LYNK & CO",
        "LYNK AND CO": "LYNK & CO",
    })

    return data


# ============================================================
# ĐỌC FILE BẢNG TỔNG HỢP LỆNH SỬA CHỮA
# ============================================================

def read_parts_file(
    file_path: Path | None,
):
    """
    Đọc Doanh thu phụ tùng theo từng Số lệnh.

    Không lấy dòng Tổng cộng.
    Không lọc theo Ngày quyết toán.
    """
    empty_result = pd.DataFrame(
        columns=[
            "ro_key",
            "doanh_thu_phu_tung",
        ]
    )

    if file_path is None:
        return empty_result

    if not file_path.exists():
        st.error(
            f"Không tìm thấy file Bảng tổng hợp: "
            f"{file_path.name}"
        )
        st.stop()

    data = read_excel_with_header_detection(
        file_path=file_path,
        expected_columns=[
            "Số lệnh sửa chữa",
            "Doanh thu phụ tùng",
        ],
        preferred_sheet="Báo cáo",
    )

    order_column = find_column(
        data,
        [
            "Số lệnh sửa chữa",
            "Số lệnh",
            "Số",
            "Mã lệnh sửa chữa",
        ],
        file_path.name,
    )

    parts_revenue_column = find_column(
        data,
        [
            "Doanh thu phụ tùng",
            "Doanh thu vật tư phụ tùng",
            "Tiền phụ tùng",
            "Phụ tùng",
        ],
        file_path.name,
    )

    # Loại dòng Tổng cộng trước khi chuẩn hóa
    total_row_mask = (
        data[order_column]
        .fillna("")
        .astype(str)
        .str.contains(
            "Tổng cộng",
            case=False,
            na=False,
        )
    )

    data = data[
        ~total_row_mask
    ].copy()

    # Chuẩn hóa số lệnh
    data["ro_key"] = normalize_order_number(
        data[order_column]
    )

    data = data[
        data["ro_key"].notna()
    ].copy()

    # Chuẩn hóa doanh thu phụ tùng
    data["doanh_thu_phu_tung"] = (
        parse_money(
            data[parts_revenue_column]
        )
    )

    # Nếu một lệnh có nhiều dòng thì cộng lại
    parts_by_order = (
        data.groupby(
            "ro_key",
            as_index=False,
        )
        .agg(
            doanh_thu_phu_tung=(
                "doanh_thu_phu_tung",
                "sum",
            )
        )
    )

    return parts_by_order


# ============================================================
# ĐỌC FILE LỆNH PHỤ KIỆN
# ============================================================

def read_accessory_file(
    file_path: Path | None,
):
    if file_path is None:
        return pd.DataFrame()

    if not file_path.exists():
        return pd.DataFrame()

    data = pd.read_excel(
        file_path
    )

    data.columns = [
        str(column).strip()
        for column in data.columns
    ]

    data = data.rename(columns={
        "Ngày hóa đơn": "ngay_hoa_don",
        "Ngày hoá đơn": "ngay_hoa_don",
        "Tổng trước thuế": (
            "doanh_thu_truoc_thue"
        ),
    })

    required_columns = [
        "ngay_hoa_don",
        "doanh_thu_truoc_thue",
    ]

    if any(
        column not in data.columns
        for column in required_columns
    ):
        return pd.DataFrame()

    data["ngay_hoa_don"] = pd.to_datetime(
        data["ngay_hoa_don"],
        errors="coerce",
        dayfirst=True,
    )

    data["doanh_thu_truoc_thue"] = (
        parse_money(
            data["doanh_thu_truoc_thue"]
        )
    )

    return data


# ============================================================
# LOAD TOÀN BỘ DỮ LIỆU
# ============================================================

@st.cache_data
def load_all_data(
    workshop_config,
):
    service_frames = []
    parts_data = {}
    accessory_data = {}

    for (
        workshop_name,
        config,
    ) in workshop_config.items():
        branch_name = config[
            "chi_nhanh"
        ]

        service_df = read_service_file(
            file_path=config["service_file"],
            workshop_name=workshop_name,
            branch_name=branch_name,
        )

        service_frames.append(
            service_df
        )

        parts_data[
            workshop_name
        ] = read_parts_file(
            config.get("parts_file")
        )

        accessory_data[
            workshop_name
        ] = read_accessory_file(
            config.get("accessory_file")
        )

    if not service_frames:
        st.error(
            "Không có dữ liệu lệnh sửa chữa "
            "để hiển thị."
        )
        st.stop()

    data_raw = pd.concat(
        service_frames,
        ignore_index=True,
    )

    return (
        data_raw,
        parts_data,
        accessory_data,
    )
