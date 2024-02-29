from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from models.authentication import ResetPassword
from utils.aws_function import get_dynamodb_client
from routers.authenitication.forgotPassword_routes import is_email_in_database, is_valid_email

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/reset-password")
async def reset_password(reset_password: ResetPassword, dynamodb_client=Depends(get_dynamodb_client)):
    data = reset_password.dict()
    email = data.get("email")
    newpassword = data.get("newpassword")
    confirmpassword = data.get("confirmPassword")
    print(1234)
    validate_passwords(newpassword, confirmpassword)

    if not is_email_in_database(email, dynamodb_client):
        raise HTTPException(status_code=404, detail="User account was not found.")

    table = dynamodb_client.Table('employee-Details-dev')
    employee_id = get_employee_id(table, email)

    if employee_id:
        update_password(table, employee_id, newpassword)
    else:
        raise HTTPException(status_code=404, detail="User account not found.")

    try:
        return {
            "message": "Password reset successfully",
            "data": None,
            "error": None
        }

    except Exception as e:
        print(f"Error updating password: {e}")
        raise HTTPException(status_code=500, detail="Failed to update password")


def validate_passwords(newpassword, confirmpassword):
    """Validate new and confirm passwords."""
    if not newpassword:
        raise HTTPException(status_code=400, detail="New password is required")
    if not confirmpassword:
        raise HTTPException(status_code=400, detail="Confirm password is required")
    if newpassword != confirmpassword:
        raise HTTPException(status_code=400, detail="New password and confirm password must be the same")


def get_employee_id(table, email):
    """Get employee ID from DynamoDB based on email."""
    response = table.scan(
        FilterExpression='officeEmailAddress = :email',
        ExpressionAttributeValues={':email': email}
    )
    items = response.get('Items', [])
    if items:
        return items[0]['employeeId']
    return None


def update_password(table, employee_id, newpassword):
    """Update password in DynamoDB for the given employee ID."""
    hashed_password = hash_password(newpassword)
    table.update_item(
        Key={'employeeId': employee_id},
        UpdateExpression='SET password = :password',
        ExpressionAttributeValues={':password': hashed_password}
    )


def hash_password(password):
    print('calling here')
    """Hash the password using bcrypt."""
    return pwd_context.hash(password)
