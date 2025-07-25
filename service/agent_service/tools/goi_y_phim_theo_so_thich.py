from sqlalchemy.orm import Session
from app.core.models import Phim
from sqlalchemy import or_
from app.core.database import get_session
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import List, Type

# 2. TOOL GỢI Ý PHIM THEO SỞ THÍCH
# ==============================================================================

class GoiYPhimInput(BaseModel):
    """Input cho công cụ gợi ý phim."""
    so_thich: str = Field(description="Từ khóa mô tả sở thích, thể loại, hoặc đối tượng xem phim (ví dụ: 'phim ma', 'phim cho người yêu', 'phim hài hước').")

class GoiYPhimTool(BaseTool):
    """Công cụ gợi ý phim dựa trên sở thích do người dùng cung cấp."""
    name: str = "goi_y_phim_theo_so_thich"
    description: str = (
        "Sử dụng công cụ này khi người dùng không biết xem phim gì và cần một vài gợi ý."
    )
    args_schema: Type[BaseModel] = GoiYPhimInput

    def _run(self, so_thich: str) -> List[str]:
        mapping = {
            "người yêu": ["tình cảm", "lãng mạn"],
            "ma": ["kinh dị"],
            "trẻ con": ["hoạt hình", "gia đình", "thiếu nhi"],
            "hài": ["hài"],
            "hành động": ["hành động"],
            "viễn tưởng": ["khoa học viễn tưởng"],
        }
        matched_tags = []
        for keyword, tags in mapping.items():
            if keyword in so_thich.lower():
                matched_tags.extend(tags)

        if not matched_tags:
            return ["Không rõ sở thích bạn đề cập đến là gì. Vui lòng nói rõ hơn."]

        session: Session = get_session()
        try:
            results = (
                session.query(Phim)
                .filter(or_(*[Phim.the_loai.ilike(f"%{tag}%") for tag in matched_tags]))
                .all()
            )
            if not results:
                return [f"Không tìm thấy phim phù hợp với sở thích '{so_thich}'"]
            return [phim.ten_phim for phim in results]
        finally:
            session.close()