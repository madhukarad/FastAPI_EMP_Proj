from fastapi import FastAPI
from mangum import Mangum
from routers.authenitication.forgotPassword_routes import router as forgot_password
from routers.authenitication.resetPassword import router as reset_password
from routers.authenitication.login import router as login
from routers.attendance.attendance_summary import router as attendance_summary
from routers.attendance.add_attendance import router as add_attendance
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
handler = Mangum(app)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
app.include_router(forgot_password, prefix="/api/auth", tags=["auth"])
app.include_router(reset_password, prefix="/api/auth", tags=["auth"])
app.include_router(login, prefix="/api/auth", tags=["auth"])

# Attendance
app.include_router(attendance_summary, prefix="/api/attendance", tags=["attendance"])
app.include_router(add_attendance, prefix="/api/attendance", tags=["attendance"])
