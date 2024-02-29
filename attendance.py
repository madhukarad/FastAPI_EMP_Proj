from pydantic import BaseModel


class Attendance(BaseModel):
    employeeID: str
    attendanceID: str
    date: str
    day_status: str  # 'Week Off' | 'Holiday' | 'Leave' | 'Present'
    checkInTime: str = None
    checkOutTime: str = None
    worked_hours: str = None
    shift_name: str = None
    late_in: str = None
    early_checkout: str = None
    short_hours: str = None
