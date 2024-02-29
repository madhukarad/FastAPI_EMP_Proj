from fastapi import APIRouter, HTTPException, Depends

from routers.authenitication.resetPassword import pwd_context
from utils.aws_function import get_dynamodb_client
from routers.authenitication.forgotPassword_routes import (
    is_email_in_database, is_valid_email
)
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
from models.authentication import Login

router = APIRouter()

# Secret key to sign JWT
SECRET_KEY = "employee-portal-Hyniva-2@@4$"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT token."""
    to_encode = data.copy()
    try:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create JWT token: {e}")


def validate_login_data(email, input_password):
    """Validate email and password data."""
    if not email or not input_password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    if not is_valid_email(email):
        raise HTTPException(status_code=422, detail="Invalid email id")


def get_user_password(table, email):
    """Get password from DynamoDB based on email."""
    try:
        response = table.scan(
            FilterExpression='officeEmailAddress = :email',
            ExpressionAttributeValues={':email': email}
        )
        items = response.get('Items', [])
        return items if items else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user password: {e}")


def is_password_in_database(email, password, dynamodb_resource):
    """Check if the email and password combination exists in the database."""
    table_name = 'employee-Details-dev'
    try:
        table = dynamodb_resource.Table(table_name)
        response = table.query(
            KeyConditionExpression=f"{'officeEmailAddress'} = :email and {'password'} = :password",
            ExpressionAttributeValues={":email": email, ":password": {password}}
        )
        return len(response.get("Items", [])) > 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in database query: {e}")


def verify_password(input_password, hashed_password):
    """Verify the input password against the hashed password."""
    try:
        return pwd_context.verify(input_password, hashed_password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying password: {e}")


@router.post("/login")
async def user_login(login: Login, dynamodb_client=Depends(get_dynamodb_client)):
    """Login endpoint."""
    data = login.dict()
    try:
        email = data.get("email")
        input_password = data.get("password")

        validate_login_data(email, input_password)

        user = is_email_in_database(email, dynamodb_client)
        if not user:
            raise HTTPException(status_code=404, detail="User account was not found.")

        table = dynamodb_client.Table('employee-Details-dev')
        userdata = get_user_password(table, email)
        if not userdata:
            raise HTTPException(status_code=404, detail="User data not found.")

        password = userdata[0]['password']

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_jwt_token(
            {"email": data.get("email"), "employeeId": userdata[0]['employeeId']},
            expires_delta=access_token_expires
        )

        try:
            if verify_password(input_password, password):
                return {
                    "message": "Login Successfully",
                    "data": {
                        "email": email,
                        "employeeID": userdata[0]['employeeId'],
                        "access_token": access_token,
                        "firstName": userdata[0]['firstName'],
                        "lastName": userdata[0]['lastName'],
                        "mobileNumber": userdata[0]['mobileNumber'],
                        "gender": userdata[0]['gender'],
                        "department": userdata[0]['department'],
                    },
                    "error": None
                }
            else:
                raise HTTPException(status_code=404, detail="Invalid Password")
        except Exception as e:
            raise HTTPException(status_code=404, detail="Invalid Password")
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    
    #jdahf
    #dhfj
