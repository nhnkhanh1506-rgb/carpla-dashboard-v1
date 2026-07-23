from pathlib import Path


# ============================================================
# CẤU HÌNH CHI NHÁNH, XƯỞNG VÀ FILE DỮ LIỆU
# ============================================================

WORKSHOP_CONFIG = {
    "Phạm Văn Đồng": {
        "chi_nhanh": "Hà Nội",

        # File lệnh sửa chữa:
        # - Xác định lượt xe theo Số lệnh
        # - Lọc kỳ báo cáo theo Ngày hóa đơn
        # - Lấy doanh thu dịch vụ từ Tổng trước thuế
        "service_file": Path(
            "hn_pvd_service_2026_07.xlsx"
        ),

        # File Bảng tổng hợp lệnh sửa chữa:
        # - Không lọc theo Ngày quyết toán
        # - Ghép với file dịch vụ theo Số lệnh
        # - Lấy Doanh thu phụ tùng của đúng các lệnh
        "parts_file": Path(
            "summary_repair_orders.xlsx"
        ),

        # Chưa có file phụ kiện
        "accessory_file": None,
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


# ============================================================
# CẤU HÌNH CHUNG
# ============================================================

WORKING_DAYS = 27

LOGO_FILE = Path(
    "carpla_services_logo_hd.png"
)
