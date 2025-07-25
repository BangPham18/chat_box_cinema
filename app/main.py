from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes, routes_tai_khoan

app = FastAPI(title="CGV Agent API")

# Cho phép frontend truy cập (nếu có)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Đổi thành domain frontend nếu cần bảo mật hơn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký router
app.include_router(routes.router)

app.include_router(routes_tai_khoan.router)