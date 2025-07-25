from sqlalchemy.orm import Session
from app.core.models import Phim, TrangThaiGhe, LichChieu, Ghe, Ve
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type
from app.core.database import get_session
from typing import List, Type
from sqlalchemy import func

# 4. TOOL KIỂM TRA GHẾ TRỐNG CỦA MỘT SUẤT CHIẾU
# ==============================================================================
class PhimConSuatTrongInput(BaseModel):
    """Input cho công cụ liệt kê các suất còn trống của một hoặc nhiều phim."""
    danh_sach_ten_phim: List[str] = Field(
        description="Danh sách tên các bộ phim cần kiểm tra."
    )

# --- Tool đã được sửa đổi ---
class PhimConSuatTrongTool(BaseTool):
    """Liệt kê TẤT CẢ các suất chiếu (ngày, giờ) CÒN GHẾ TRỐNG của một hoặc nhiều bộ phim."""
    name: str = "phim_con_suat_trong"
    description: str = (
        "Sử dụng khi người dùng hỏi về lịch chiếu của một hoặc nhiều phim cụ thể "
        "(ví dụ: 'lịch chiếu phim X', 'phim X và Y còn suất nào không?') mà không chỉ định rõ ngày giờ."
    )
    args_schema: Type[BaseModel] = PhimConSuatTrongInput

    def _run(self, danh_sach_ten_phim: List[str]) -> List[str]:
        """Thực thi công cụ để kiểm tra suất chiếu cho danh sách phim."""
        session: Session = get_session()
        ket_qua_tong_hop = []
        try:
            for ten_phim in danh_sach_ten_phim:
                # Tìm tất cả suất chiếu của phim hiện tại trong vòng lặp
                cac_suat = (
                    session.query(LichChieu)
                    .join(Phim)
                    .filter(Phim.ten_phim == ten_phim)
                    .all()
                )

                if not cac_suat:
                    ket_qua_tong_hop.append(f"Không tìm thấy suất chiếu nào cho phim '{ten_phim}'.")
                    continue  # Chuyển sang phim tiếp theo

                # Danh sách chứa kết quả cho phim hiện tại
                ket_qua_phim_hien_tai = []

                for suat in cac_suat:
                    # Lấy danh sách tất cả ghế trong phòng chiếu
                    tong_ghe = (
                        session.query(func.count(Ghe.ma_ghe))
                        .join(TrangThaiGhe, Ghe.ma_ghe == TrangThaiGhe.ma_ghe)
                        .filter(TrangThaiGhe.ma_phong == suat.ma_phong)
                        .scalar()
                    )

                    # Đếm số vé đã đặt cho suất chiếu
                    ghe_da_dat = (
                        session.query(func.count(Ve.ma_ve))
                        .filter(Ve.ma_lich_chieu == suat.ma_lich_chieu)
                        .scalar()
                    )

                    so_ghe_trong = tong_ghe - (ghe_da_dat or 0)

                    if so_ghe_trong > 0:
                        ket_qua_phim_hien_tai.append(
                            f"- Ngày {suat.ngay.strftime('%d/%m/%Y')} lúc {suat.gio.strftime('%H:%M')} còn {so_ghe_trong} ghế"
                        )

                # Thêm kết quả của phim hiện tại vào kết quả tổng hợp
                if not ket_qua_phim_hien_tai:
                    ket_qua_tong_hop.append(f"Tất cả suất chiếu của phim '{ten_phim}' đều đã hết ghế.")
                else:
                    ket_qua_tong_hop.append(f"Các suất chiếu còn trống của phim '{ten_phim}':")
                    ket_qua_tong_hop.extend(ket_qua_phim_hien_tai)
            
            if not ket_qua_tong_hop:
                 return ["Không tìm thấy thông tin cho bất kỳ phim nào được yêu cầu."]

            return ket_qua_tong_hop

        finally:
            session.close()
