from pathlib import Path


# ============================================================
# CẤU HÌNH CHI NHÁNH, XƯỞNG VÀ FILE DỮ LIỆU
# ============================================================

WORKSHOP_CONFIG = {
    "Phạm Văn Đồng": {
        "chi_nhanh": "Hà Nội",

        # File lệnh sửa chữa:
        # - Dùng Ngày hóa đơn để xác định kỳ báo cáo
        # - Dùng Số lệnh để xác định lượt xe
        # - Dùng Tổng trước thuế để đối chiếu tổng doanh thu
        "service_file": Path(
            "hn_pvd_service_2026_07.xlsx"
        ),

        # File Bảng tổng hợp lệnh sửa chữa mới:
        # - Có dữ liệu từ 01/06/2026 đến 15/07/2026
        # - Không lọc theo Ngày quyết toán trong dashboard
        # - Ghép với file lệnh sửa chữa theo Số lệnh
        # - Lấy Doanh thu công việc và Doanh thu phụ tùng
        "parts_file": Path(
            "summary_repair_orders.xlsx"
        ),

        # Hiện tại xưởng chưa có file doanh thu phụ kiện
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

# Số ngày làm việc tiêu chuẩn
WORKING_DAYS = 25

# Logo trang chủ
LOGO_FILE = Path(
    "carpla_services_logo_hd.png"
)
