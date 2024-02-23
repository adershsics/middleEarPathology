from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import doctor
from .serializers import DoctorSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.exceptions import APIException

@api_view(['POST'])
def doctor_list_create_view(request):
    try:
        if request.method == 'POST':
            serializer = DoctorSerializer(data=request.data)
            if serializer.is_valid():
                doctor_instance = serializer.save()
                serialized_doctor = {
                    "id": doctor_instance.id,
                    "name": doctor_instance.name,
                    "mobile_number": str(doctor_instance.mobile_number),
                    "password": doctor_instance.password,
                    "email": doctor_instance.email,
                    "hospital_name": doctor_instance.hospital_name,
                    "doctor_id_number": doctor_instance.doctor_id_number
                }
                response_data = {
                    "status": True,
                    "message": "Doctor Created",
                    "doctor": serialized_doctor
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": False, "message": "Doctor creation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        error_message = "Error: Request failed. " + str(e)
        return Response({"status": False, "message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def login_api_view(request):
    try:
        mobile_number = request.data.get('mobile_number')
        password = request.data.get('password')

        if not mobile_number or not password:
            return Response({"status": False, "message": "Please provide both 'mobile_number' and 'password.'"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, mobile_number=mobile_number, password=password)

        if user:
            serializer = DoctorSerializer(user)
            response_data = {
                "status": True,
                "message": "Login successful",
                "user": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"status": False, "message": "Invalid mobile number or password."}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        error_message = "Error: Request failed. " + str(e)
        return Response({"status": False, "message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['GET'])
# def login_api_view(request):
#     try:
#         mobile_number = request.query_params.get('mobile_number')
#         password = request.query_params.get('password')
#         # Add '+' to the front of mobile_number
#         mobile_number = '+' + mobile_number

#         print(mobile_number,password)
#         if not mobile_number or not password:
#             return Response({"status": False, "message": "Please provide both 'mobile_number' and 'password' as query parameters."}, status=status.HTTP_400_BAD_REQUEST)

#         user = authenticate(request, mobile_number=mobile_number, password=password)
#         if user:
#             serializer = DoctorSerializer(user)
#             response_data = {
#                 "status": True,
#                 "message": "Login successful",
#                 "user": serializer.data
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         else:
#             return Response({"status": False, "message": "Invalid mobile number or password."}, status=status.HTTP_401_UNAUTHORIZED)
#     except Exception as e:
#         error_message = "Error: Request failed. " + str(e)
#         return Response({"status": False, "message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def view_doctors(request):
    try:
        if request.method == 'GET':
            details = doctor.objects.all()
            serialized_details = []
            for detail in details:
                serialized_detail = {
                    'id': detail.id,
                    'name': detail.name,
                    'mobile_number': str(detail.mobile_number),
                    'password': detail.password,
                    'email': detail.email,
                    'hospital_name': detail.hospital_name,
                    'doctor_id_number': detail.doctor_id_number
                }
                serialized_details.append(serialized_detail)
            response_data = {
                "status": True,
                "message": "Doctor details listed",
                "doctorDetails": serialized_details
            }
            return Response(response_data)
    except Exception as e:
        error_message = "Error: Request failed. " + str(e)
        return Response({"status": False, "message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      
@api_view(['DELETE'])
def delete_doctor(request, doctor_id):
    try:
        doctor_instance = doctor.objects.get(id=doctor_id)
    except doctor.DoesNotExist:
        return Response({"status": False, "message": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        if request.method == 'DELETE':
            doctor_instance.delete()
            return Response({"status": True, "message": "Doctor deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        error_message = "Error: Request failed. " + str(e)
        return Response({"status": False, "message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
