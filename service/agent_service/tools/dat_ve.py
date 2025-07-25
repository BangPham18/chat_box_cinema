from sqlalchemy.orm import Session
from app.core.models import Phim, TrangThaiGhe, LichChieu, Ghe, Ve, KhachHang
from sqlalchemy import func
from uuid import uuid4
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import List, Type
from app.core.database import get_session

# 6. TOOL ĐẶT VÉ
# ==============================================================================

class DatVeInput(BaseModel):
    """Input cho công cụ đặt vé."""
    email: str = Field(description="Email của khách hàng.")
    ten_phim: str = Field(description="Tên bộ phim muốn đặt.")
    ngay: str = Field(description="Ngày xem phim, định dạng DD/MM/YYYY.")
    gio: str = Field(description="Giờ xem phim, định dạng HH:MM.")
    ghe: List[str] = Field(description="Danh sách các ghế muốn đặt, ví dụ: ['A1', 'A2'].")

class DatVeTool(BaseTool):
    """Thực hiện đặt vé sau khi đã thu thập ĐẦY ĐỦ thông tin từ khách hàng."""
    name: str = "dat_ve"
    description: str = (
        "CHỈ gọi công cụ này khi đã có đủ 7 thông tin: ten, nam_sinh, gioi_tinh, ten_phim, ngay, gio, ghe. "
        "Đây là bước cuối cùng trong quy trình đặt vé."
    )
    args_schema: Type[BaseModel] = DatVeInput

    def _run(self, email: str, ten_phim: str, ngay: str, gio: str, ghe: List[str]) -> str:
        session: Session = get_session()
        try:
            # 1. Chuyển định dạng
            ngay_chieu = datetime.strptime(datetime.strptime(ngay, "%d/%m/%Y").strftime("%Y-%m-%d"), "%Y-%m-%d").date()
            gio_chieu = datetime.strptime(gio, "%H:%M").time()

            # 2. Kiểm tra phim & suất chiếu
            lich_chieu = (
                session.query(LichChieu)
                .join(Phim)
                .filter(
                    Phim.ten_phim == ten_phim,
                    LichChieu.ngay == ngay_chieu,
                    LichChieu.gio == gio_chieu
                )
                .first()
            )
            if not lich_chieu:
                return "Không tìm thấy suất chiếu phù hợp."

            # 4. Đặt vé cho từng ghế
            ve_da_dat = []
            for ten_ghe in ghe:
                ghe_obj = (
                    session.query(Ghe)
                    .filter_by(ten_ghe=ten_ghe)
                    .join(TrangThaiGhe)
                    .filter(TrangThaiGhe.ma_phong == lich_chieu.ma_phong)
                    .first()
                )
                if not ghe_obj:
                    return f"Ghế {ten_ghe} không tồn tại trong phòng chiếu."

                # Kiểm tra ghế đã được đặt chưa
                da_dat = (
                    session.query(Ve)
                    .filter_by(ma_lich_chieu=lich_chieu.ma_lich_chieu, ma_ghe=ghe_obj.ma_ghe)
                    .first()
                )
                if da_dat:
                    return f"Ghế {ten_ghe} đã được người khác đặt."

                # Tạo vé
                ma_ve = uuid4().hex[:5].upper()
                ve = Ve(
                    ma_ve=ma_ve,
                    ngay_dat=datetime.now().date(),
                    ma_lich_chieu=lich_chieu.ma_lich_chieu,
                    ma_ghe=ghe_obj.ma_ghe,
                    email = email
                )
                session.add(ve)
                ve_da_dat.append(ten_ghe)

            session.commit()
            return f"Đặt vé thành công cho các ghế: {', '.join(ve_da_dat)}"

        except Exception as e:
            session.rollback()
            return f"Lỗi: {str(e)}"
        finally:
            session.close()