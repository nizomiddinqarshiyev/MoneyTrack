from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        custom_data = {
            'status': 'error',
            'code': getattr(exc, 'default_code', 'error'),
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            'errors': response.data
        }
        if hasattr(exc, 'reasons'):
            custom_data['reasons'] = exc.reasons
            
        response.data = custom_data

    return response
