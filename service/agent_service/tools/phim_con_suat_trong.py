from sqlalchemy.orm import Session
from app.core.models import Phim, TrangThaiGhe, LichChieu, Ghe, Ve
from sqlalchemy import func
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type, List
from app.core.database import get_session

# 5. TOOL LIỆT KÊ CÁC SUẤT CÒN TRỐNG CỦA MỘT PHIM
# ==============================================================================

class PhimConSuatTrongInput(BaseModel):
    """Input cho công cụ liệt kê các suất còn trống của phim."""
    ten_phim: str = Field(description="Tên bộ phim cần kiểm tra.")

class PhimConSuatTrongTool(BaseTool):
    """Liệt kê TẤT CẢ các suất chiếu (ngày, giờ) CÒN GHẾ TRỐNG của một bộ phim."""
    name: str = "phim_con_suat_trong"
    description: str = (
        "Sử dụng khi người dùng hỏi một phim cụ thể 'còn suất nào không?' mà không chỉ định rõ ngày giờ."
    )
    args_schema: Type[BaseModel] = PhimConSuatTrongInput

    def _run(self, ten_phim: str) -> List[str]:
        session: Session = get_session()
        try:
            # Tìm tất cả suất chiếu của phim
            cac_suat = (
                session.query(LichChieu)
                .join(Phim)
                .filter(Phim.ten_phim == ten_phim)
                .all()
            )

            if not cac_suat:
                return [f"Không tìm thấy suất chiếu nào cho phim '{ten_phim}'"]

            ket_qua = []

            for suat in cac_suat:
                # Lấy danh sách tất cả ghế trong phòng chiếu đó
                tat_ca_ghe = (
                    session.query(Ghe)
                    .join(TrangThaiGhe, Ghe.ma_ghe == TrangThaiGhe.ma_ghe)
                    .filter(TrangThaiGhe.ma_phong == suat.ma_phong)
                    .all()
                )
                tong_ghe = len(tat_ca_ghe)

                # Đếm số vé đã đặt cho suất chiếu
                ghe_da_dat = (
                    session.query(func.count(Ve.ma_ve))
                    .filter(Ve.ma_lich_chieu == suat.ma_lich_chieu)
                    .scalar()
                )

                so_ghe_trong = tong_ghe - ghe_da_dat

                if so_ghe_trong > 0:
                    ket_qua.append(
                        f"- Ngày {suat.ngay.strftime('%d/%m/%Y')} lúc {suat.gio.strftime('%H:%M')} còn {so_ghe_trong} ghế"
                    )

            if not ket_qua:
                return [f"Tất cả suất chiếu của phim '{ten_phim}' đều đã hết ghế."]

            return [f"Các suất chiếu còn trống của phim '{ten_phim}':"] + ket_qua

        finally:
            session.close()