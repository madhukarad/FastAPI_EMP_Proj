from fastapi import APIRouter, HTTPException, Depends
from models.authentication import ValidateOtp, SendInstruction
from utils.aws_function import get_dynamodb_client
from utils.sendgrid import generate_otp, send_otp_email
import re

router = APIRouter()
# Dictionary to store email-otp pairs
otp_storage = {}


@router.post("/send-instructions")
async def send_otp(send_instruction: SendInstruction, dynamodb_client=Depends(get_dynamodb_client)):
    data = send_instruction.dict()
    email = data.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not is_valid_email(email):
        raise HTTPException(status_code=422, detail="Invalid email format")
    if not is_email_in_database(email, dynamodb_client):
        raise HTTPException(status_code=404, detail="User account was not found.")

    try:
        otp = generate_otp()
        # Store OTP for otp validation
        otp_storage[email] = otp

        # Send OTP via email
        send_otp_email(email, otp)

        # Return HTTP 200 OK for successful OTP sending
        return {
            "message": "OTP sent successfully",
            "data": {
                "email": email,
            },
            "error": None
        }

    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP email")


def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)


def is_email_in_database(email, dynamodb_resource):
    table_name = 'employee-Details-dev'
    try:
        table = dynamodb_resource.Table(table_name)
        response = table.scan(
            FilterExpression="officeEmailAddress = :val",
            ExpressionAttributeValues={":val": email}
        )
        return len(response.get("Items", [])) > 0
    except Exception as e:
        print(f"Error: {e}")
        return False


@router.post("/validate-otp")
async def email_otp_validation(validate_otp: ValidateOtp):
    data = validate_otp.dict()
    email = data.get("email")
    otp = data.get("otp")

    # Check if the email and OTP exist in the storage
    if email not in otp_storage or otp != otp_storage[email]:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    # Clear the OTP from storage after successful validation (optional)
    del otp_storage[email]

    # Return HTTP 200 OK for successful OTP validation
    return {
        "message": "OTP verified successfully",
        "data": {
            "email": email,
        },
        "error": ""
    }
