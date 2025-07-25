from .get_phim_hot import GetPhimHotTool
from .goi_y_phim_theo_so_thich import GoiYPhimTool
from .get_lich_chieu import TraCuuLichChieuTool
from .phim_con_suat_trong import PhimConSuatTrongTool
from .kiem_tra_ghe_trong import PhimConSuatTrongTool
from .dat_ve import DatVeTool
from .kiem_tra_phim import KiemTraPhimTonTaiTool
tools = [
    GetPhimHotTool(),
    GoiYPhimTool(),
    TraCuuLichChieuTool(),
    PhimConSuatTrongTool(),
    PhimConSuatTrongTool(),
    DatVeTool(),
    KiemTraPhimTonTaiTool()
]
