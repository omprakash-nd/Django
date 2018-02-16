# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.views import APIView
from rest_framework import status
from models import Status, Employee, LeaveType, LeaveRequest, LeaveCredit
from django.core.serializers.python import Serializer
from rest_framework.response import Response
from .serializers import LeaveRequestSerializer, EmployeeSerializer, LeaveTypeSerializer, LeaveCreditSerializer
import datetime
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.generics import GenericAPIView
from django.db.models.query import QuerySet
from django.http import JsonResponse


class ApplyGetView(APIView):
    
    def get(self, request, pk, format=None):
        try:
            # import pdb;pdb.set_trace()
            employee = Employee.objects.filter(id=pk)
            leave_types = LeaveType.objects.all()
            serializer = EmployeeSerializer(employee, many=True)
            leave_type_serializer = LeaveTypeSerializer(leave_types, many=True)
            return Response({"employee":serializer.data,"leave_types":leave_type_serializer.data})
        except Exception as exception:
            template = "An exception of function {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)

class ApplyPostView(APIView):  

    
    def post(self, request, format=None):
        try:
            # response = exception_handler(request)
            # print "sad",response
            # import pdb;pdb.set_trace()
            user = Employee.objects.get(name=request.data["name"])
            request.data["name"] = user.id
            request.data["reporter"] = user.reporting_senior.id
            leave = LeaveType.objects.get(catagory = request.data["leave_type"])
            available = LeaveCredit.objects.get(name=request.data["name"], leave_type=leave)
            from_date = datetime.datetime.strptime(self.request.data.get('from_date'), "%Y-%m-%d")
            to_date = datetime.datetime.strptime(self.request.data.get('to_date'), "%Y-%m-%d")
            no_days = abs((to_date-from_date).days)
            if no_days > available.available:
                return Response("Sorry the no of days that you applied is not available in your balance")
            else:
                request.data["no_days"] = no_days
            status = Status.objects.get(status="Pending")
            request.data["status"]= status.id
            serializer = LeaveRequestSerializer(data=request.data, many=False)
            if serializer.is_valid(raise_exception=True):
              serializer.save()
              return Response(serializer.data)
            return JsonResponse(serializer.errors)
        except Exception as exception:
                    template = "An exception of function {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(exception).__name__, exception.args)
                    return Response(message)

class UserHistoryView(APIView):

    def get(self,request, pk, format=None):
        try:
            # import pdb;pdb.set_trace()
            employee = Employee.objects.get(id=pk)
            employee_history = LeaveRequest.objects.filter(name=employee.id)
            leave_history_serializer = LeaveRequestSerializer(employee_history, many=True)
            return Response(leave_history_serializer.data)

        except Exception as exception:
                    template = template = "An exception of function {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(exception).__name__, exception.args)
                    return Response(message)

class WAPPRView(APIView):

    def get(self, request, pk, format=None):
        try:
            reporter = Employee.objects.get(id=pk)
            employees = Employee.objects.filter(reporting_senior=reporter).values_list("id", flat=True)
            status = Status.objects.get(status="Pending")
            waiting_for_approval = LeaveRequest.objects.filter(name__in=employees, status=status.id)
            pending_serializer = LeaveRequestSerializer(waiting_for_approval, many=True)
            return Response(pending_serializer.data)
        except Exception as exception:
            template = template = "An exception of function {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)

class PendingRecordView(APIView):

    def get(self, request, pk,format=None):
        pending_records = LeaveRequest.objects.filter(name=pk, status=Status.objects.get(status="Pending"))
        pending_records_serializer =  LeaveRequestSerializer(pending_records, many=True)
        return Response(pending_records_serializer.data)
   
class LeaveBalance(APIView):

    def get(self, request, format=None):
        pk = request.GET.get('id')
        try:
            # import pdb;pdb.set_trace()
            employee = Employee.objects.get(id=pk)
            credits = LeaveCredit.objects.filter(name=employee)
            serializer = LeaveCreditSerializer(credits, many=True)
            return Response(serializer.data)
        except Exception as exception:
            template = "An exception of type function {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)

class LeaveRequestView(APIView):

    def get(self, request, format=None):
        pk = request.GET.get('id')
        try:
            leave_id = LeaveRequest.objects.get(id=pk)
            leave_serializer = LeaveRequestSerializer(leave_id, many=False)
            return Response(leave_serializer.data)
        except Exception as exception:
            template = "An exception of type function {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)

class DenyView(APIView):
    
    def put(self,request, format=None):
        try:
            user = LeaveRequest.objects.get(id=request.data["id"])
            if user:
                status = Status.objects.get(code=101)
                if user.status == status:
                    serializer = LeaveRequestSerializer(user)
                    return Response(serializer.data)
                else:
                    user.status = status
                    user.save()
                    serializer = LeaveRequestSerializer(user)
                    return Response(serializer.data)
            else:
                return Response(serializer.errors)
        except Exception as exception:
            template = "An exception of type function {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)

class ApproveView(APIView):

    def put(self,request,format=None):
        try:
            user = LeaveRequest.objects.get(id=request.data["id"])
            if user:
                status = Status.objects.get(code=100)
                if user.status != status:
                    user_data = self.check_leave_type(user)
                    user.status = status
                    user.save()
                    serializer = LeaveRequestSerializer(user_data)
                    return Response(serializer.data)              
            else:
                return Response(serializer.errors)
        except Exception as exception:
            template = "An exception of type function {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)

    def check_leave_type(self, user):
        lop = LeaveType.objects.get(code=100)
        if user.leave_type == lop:
            user = self.add_lop(user)
        else:
            user = self.reduce_leave_balance(user)
        return user

    # def get_leave_balance(self, user):
    #     leave_balance = LeaveCredit.objects.get(name=user.name, leave_type=user.leave_type)
    #     return leave_balance

    def reduce_leave_balance(self, user):
        leave_balance = LeaveCredit.objects.get(name=user.name, leave_type=user.leave_type)
        if leave_balance.available >= user.no_days:
            available = int(leave_balance.available)
            no_days = int(user.no_days)
            available -= no_days
            leave_balance.available = long(available)
            leave_balance.save()
            return user
    
    def add_lop(self, user):
        leave_balance = LeaveCredit.objects.get(name=user.name, leave_type=user.leave_type)
        available = int(leave_balance.available)
        no_days = int(user.no_days)
        available += no_days
        leave_balance.available = long(available)
        leave_balance.save()
        return user

    # def leave_lop(self, user):
    #     type_lop = LeaveType.objects.get(code=100)
    #     user.leave_type =  type_lop
    #     user.save()
    #     return user
