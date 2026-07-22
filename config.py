from pathlib import Path


# ============================================================
# CẤU HÌNH CHI NHÁNH, XƯỞNG VÀ FILE DỮ LIỆU
# ============================================================

WORKSHOP_CONFIG = {
    "Phạm Văn Đồng": {
        "chi_nhanh": "Hà Nội",

        # Doanh thu dịch vụ:
        # Lấy cột "Tổng trước thuế" trong file lệnh sửa chữa
        "service_file": Path(
            "hn_pvd_service_2026_07.xlsx"
        ),

        # Doanh thu phụ tùng:
        # Lấy cột "Doanh thu phụ tùng" tại dòng Tổng cộng
        "parts_file": Path(
            "hn_pvd_parts_2026_07.xlsx"
        ),

        # Xưởng này hiện chưa có file lệnh phụ kiện
        "accessory_file": None,

        # Kỳ dữ liệu của báo cáo phụ tùng
        "parts_year": 2026,
        "parts_month": 7,
    },
}


# ============================================================
# TARGET THEO CHI NHÁNH, XƯỞNG, NĂM, THÁNG
# ============================================================

TARGETS = {
    ("Hà Nội", "Phạm Văn Đồng", 2026, 7): {
        "ro": 714,
        "revenue": 1_429_000_000,
    },
}


# Số ngày làm việc dùng để tính trung bình/ngày
WORKING_DAYS = 25


# Logo trang chủ
LOGO_FILE = Path("carpla_services_logo_hd.png")
