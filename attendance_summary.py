from fastapi import APIRouter, HTTPException, Depends, Query
from tables.create_attendance_table import table_exists, create_table
from utils.aws_function import get_dynamodb_client
import json
from botocore.exceptions import ClientError
import logging
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key
from boto3.dynamodb import table

router = APIRouter()


@router.get("/get-attendance-summary")
async def attendance_summary(
        month_year: str = Query(..., title="MonthYear", description="Month and Year in MM-YYYY format"),
        employee_id: str = Query(..., title="EmployeeID", description="Employee ID to filter the data"),
        day_status: str = Query(None, title="DayStatus", description="Return the list based on status"),
        dynamodb_client=Depends(get_dynamodb_client),
):
    try:
        # Parse month and year from the input parameter
        month, year = map(int, month_year.split('-'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid MonthYear format. Use MM-YYYY")

    table_name = 'EmployeeAttendance'
    table = dynamodb_client.Table(table_name)
    if not table_exists(table):
        table = create_table(table_name, dynamodb_client)

    try:
        response = table.scan(
            FilterExpression=Key("employeeID").eq(employee_id)
        )
        items = response.get('Items', [])

        if not items:
            raise HTTPException(status_code=404, detail="No record found.")

        # Convert DynamoDB items to a list of Python dictionaries
        items_data = []
        present_days = 0
        total_holidays = 0
        total_leaves = 0
        week_offs = 0
        total_days = 0

        month_start_date = datetime(year, month, 1).date()
        month_end_date = (month_start_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        for item in items:
            formatted_item = {}
            for key, value in item.items():
                try:
                    # Check if the value is a string before attempting JSON parsing
                    if isinstance(value, str):
                        parsed_value = json.loads(value)
                        formatted_item[key] = parsed_value
                    else:
                        formatted_item[key] = value
                except json.JSONDecodeError:
                    formatted_item[key] = value

            # Check if the item has a checkInTime within the specified month and year
            check_in_time = formatted_item.get("checkInTime", None)
            if check_in_time:
                check_in_date = datetime.fromisoformat(check_in_time).date()
                if month_start_date <= check_in_date <= month_end_date:
                    if str(formatted_item.get("employeeID", None)) == str(employee_id):
                        total_days += 1
                    try:
                        status = formatted_item.get("day_status", None)
                        if status == 'Week Off':
                            week_offs += 1
                        elif status == 'Holiday':
                            total_holidays += 1
                        elif status == 'Leave':
                            total_leaves += 1
                        elif status == 'Present':
                            present_days += 1
                        else:
                            logging.warning(f"Unknown day_status: {status}")
                    except Exception as e:
                        logging.exception(f"Error processing item: {str(e)}")
                    if not day_status:
                        items_data.append(formatted_item)
                    elif str(formatted_item.get("day_status", None)) == str(day_status):
                        items_data.append(formatted_item)

        return HTTPException(status_code=200, detail={
            "total_days": total_days,
            "present_days": present_days,
            "week_offs": week_offs,
            "holidays": total_holidays,
            "leaves": total_leaves,
            "attendance_list": items_data
        })

    except ClientError as ce:
        logging.exception(f"ClientError in attendance_summary: {str(ce)}")
        raise HTTPException(status_code=500, detail=f"ClientError in attendance_summary: {str(ce)}")
    except HTTPException as he:
        # Reraise HTTPException to maintain the status code and detail message
        raise he
    except ValueError as ve:
        logging.exception(f"ValueError in attendance_summary: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"ValueError in attendance_summary: {str(ve)}")
    except Exception as e:
        logging.exception(f"Error in attendance_summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in attendance_summary: {str(e)}")
