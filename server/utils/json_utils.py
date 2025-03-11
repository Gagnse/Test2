from flask import jsonify
from datetime import datetime, date
import decimal
import uuid


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def api_response(success=True, message=None, data=None, status_code=200):
    """
    Create a standardized API response

    Args:
        success (bool): Whether the API call was successful
        message (str): Optional message to include in the response
        data (dict): Optional data to include in the response
        status_code (int): HTTP status code to return

    Returns:
        tuple: (jsonified response, status code)
    """
    response = {'success': success}

    if message:
        response['message'] = message

    if data:
        response.update(data)

    return jsonify(response), status_code