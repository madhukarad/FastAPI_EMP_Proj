from boto3.dynamodb import table
from fastapi import APIRouter, HTTPException, Depends, Query

from models.attendance import Attendance
from tables.create_attendance_table import table_exists, create_table
from utils.aws_function import get_dynamodb_client
import json
from botocore.exceptions import ClientError
import logging
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key

router = APIRouter()



def get_today_attendance(employeeID):
    today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = table.get_item(Key={'employee_id': employeeID, 'date': today_date})
    return response.get('Item')


def save_attendance(employee_id, action, employeeID=None):
    today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table.put_item(Item={'employee_id': employeeID, 'date': today_date, 'action': action})

@router.post("/check-in")
def check_in(attendance: Attendance, dynamodb_client=Depends(get_dynamodb_client)):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if attendance.day_status == 'Present':
        if attendance.checkInTime == 'checkInTime':
            print(123456)
            today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response = table.get_item(Key={'employee_id': employeeID, 'date': today_date})
            existing_record = get_today_attendance(attendance.employeeID)
            if existing_record:
                raise HTTPException(status_code=400, detail="You have already checked in for today.")
            save_attendance(attendance.employeeID, 'check-in')
            return response



#@router.post("/check-out")
#def check_out(attendance: Attendance, dynamodb_client=Depends(get_dynamodb_client)):
    #current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #if attendance.day_status == 'Present':
        #if attendance.checkOutTime == 'checkOutTime':
            #today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #response = table.get_item(Key={'employeeID': employeeID, 'date': today_date})
            #existing_record = get_today_attendance(attendance.employeeID)
            #if existing_record:
                #raise HTTPException(status_code=400, detail="You have already checked out for today.")
            #save_attendance(attendance.employeeID, 'checkOutTime')
            #return response



