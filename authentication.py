from pydantic import BaseModel


class Login(BaseModel):
    email: str
    password: str


class ResetPassword(BaseModel):
    email: str
    newpassword: str
    confirmPassword: str


class ValidateOtp(BaseModel):
    email: str
    otp: str


class SendInstruction(BaseModel):
    email: str
