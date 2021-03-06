# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.views import APIView
from rest_framework import status
from models import Status, Employee, LeaveType, LeaveRequest, LeaveCredit
from django.core.serializers.python import Serializer
from rest_framework.response import Response
from .serializers import LeaveRequestSerializer,LeaveRequestApplySerializer, EmployeeSerializer, LeaveTypeSerializer, LeaveCreditSerializer
import datetime
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.generics import GenericAPIView
from django.db.models.query import QuerySet
from django.http import JsonResponse

class User(APIView):
    
    def get(self, request, format=None):
        try:
            # import pdb;pdb.set_trace()
            pk = int(request.GET.get('id'))
            employee = Employee.objects.filter(id=pk)
            if employee:
                serializer = EmployeeSerializer(employee, many=True)
                return Response(serializer.data)
            else:
                return Response("Invalid id")
        except Exception as exception:
            template = "An exception of function {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)
        
class LoginCheck(APIView):

    def get(self, request, format=None):
        try:
           
            pk = request.GET.get("id")
            employee = Employee.objects.filter(id=pk)
            if employee:
                reporter = Employee.objects.filter(reporting_senior=employee)
                if reporter:
                    message={"user":"reporter"}
                    return Response(message)
                else:
                    message={"user":"employee"}
                    return Response(message)
            else:
                message={"user":"invalid"}
                return Response(message)
        except Exception as exception:
            template = "An exception of function {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)

class Leave(APIView):

    def get(self, request, format=None):
        try:
            leave_types = LeaveType.objects.all()
            serializer = LeaveTypeSerializer(leave_types, many=True)
            return Response(serializer.data)
        except Exception as exception:
            template = "An exception of function {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)
        
class Apply(APIView):  

    def post(self, request, format=None):
        try:
            # import pdb;pdb.set_trace()
            user = Employee.objects.get(name=request.data.get('name'))
            request.data["name"] = user.id
            request.data["reporter"] = user.reporting_senior.id
            leave = LeaveType.objects.get(catagory = request.data["leave_type"])
            
            available = LeaveCredit.objects.get(name=request.data["name"], leave_type=leave)
            # no_days = self.validate_date(from_date, to_date)
            if request.data.get('from_date'):
                if request.data.get('to_date'):
                    from_date = datetime.datetime.strptime(request.data.get('from_date'), "%Y-%m-%d")
                    to_date = datetime.datetime.strptime(request.data.get('to_date'), "%Y-%m-%d")
                    if from_date < to_date:
                        no_days = abs((from_date-to_date).days)+1
                        if no_days > available.available:
                            lop = LeaveType.objects.get(catagory = "LOP")
                            request.data["leave_type"] = lop.id
                            print "lop", lop
                            # return JsonResponse("Sorry no available balance", safe=False)
                        else:
                            request.data["leave_type"] = leave.id
                        request.data["no_days"] = no_days
                        _status = Status.objects.get(status="Pending")
                        request.data["status"]= _status.id
                        print "request", request.data
                        serializer = LeaveRequestApplySerializer(data=request.data, many=False)
                        if serializer.is_valid(raise_exception=True):
                            serializer.save()
                            return Response("Applied successfully")
                        else:
                            return JsonResponse(serializer.errors, safe=False)
                    else:
                        return Response("Invalid date")
                else:
                    return Response("Please fill to date")
            else:
                return Response("Please fill from date")
        except Exception as exception:
                template = template = "An exception of function {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(exception).__name__, exception.args)
                return Response(message)
                
class Detail(APIView):

    def get(self, request, format=None):
        pk = int(request.GET.get('id'))
        try:
            employee = Employee.objects.filter(id=pk)
            if employee:
                details = LeaveRequest.objects.filter(name=employee)
                details_serializer =  LeaveRequestSerializer(details, many=True)
                pending_records = LeaveRequest.objects.filter(name=employee, status=Status.objects.get(status="Pending"))
                pending_records_serializer =  LeaveRequestSerializer(pending_records, many=True)
                return Response({
                    "details":details_serializer.data, 
                    "pending_records":pending_records_serializer.data
                })
            else:
                return Response("Invalid id")
        except Exception as exception:
                template = template = "An exception of function {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(exception).__name__, exception.args)
                return Response(message)

class Approval(APIView):

    def get(self, request, format=None):
        pk = request.GET.get('id')
        try:
            # import pdb;pdb.set_trace()
            employee = Employee.objects.filter(id=pk)
            if employee:
                reporter = Employee.objects.filter(reporting_senior=employee)
                if reporter:
                    employees = Employee.objects.filter(reporting_senior=employee).values_list("id", flat=True)
                    status = Status.objects.get(status="Pending")
                    waiting_for_approval = LeaveRequest.objects.filter(name__in=employees, status=status.id)
                    waiting_for_approval_serializer = LeaveRequestSerializer(waiting_for_approval, many=True)
                    return Response(waiting_for_approval_serializer.data)
                else:
                    return Response("Invalid id1")
            else:
                return Response("Invalid id")
        except Exception as exception:
                template = template = "An exception of function {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(exception).__name__, exception.args)
                return JsonResponse(message)

class LeaveBalance(APIView):

    def get(self, request, format=None):
        pk = request.GET.get('id')
        try:
            # import pdb;pdb.set_trace()
            employee = Employee.objects.filter(id=pk)
            if employee:
                credits = LeaveCredit.objects.filter(name=employee)
                serializer = LeaveCreditSerializer(credits, many=True)
                return Response(serializer.data)
            else:
                return Response("Invalid id")
        except Exception as exception:
            template = "{0}:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)

class LeaveRequestView(APIView):

    def get(self, request, format=None):
        if request.GET.get('id') is None:
            try:
                leave_id = LeaveRequest.objects.all()
                leave_serializer = LeaveRequestSerializer(leave_id, many=True)
                return Response(leave_serializer.data)
            except Exception as exception:
                template = "{0}:\n{1!r}"
                message = template.format(type(exception).__name__, exception.args)
                return Response(message)
        elif request.GET.get('id'):
            try:
                pk = request.GET.get('id')
                leave_id = LeaveRequest.objects.get(id=pk)
                leave_serializer = LeaveRequestSerializer(leave_id, many=False)
                return Response(leave_serializer.data)
            except Exception as exception:
                template = "{0}:\n{1!r}"
                message = template.format(type(exception).__name__, exception.args)
                return Response(message)

class DenyView(APIView):
    
    def put(self, request, format=None):
        try:
            reporter = Employee.objects.get(id=request.data["reporter_id"])
            if reporter:
                requester = LeaveRequest.objects.get(id=request.data["request_id"])
                if requester:
                    if requester.reporter == reporter:
                        status = Status.objects.get(code=101)
                        if requester.status == status:
                            serializer = LeaveRequestSerializer(requester)
                            return Response(serializer.data)
                        else:
                            requester.status = status
                            requester.save()
                            serializer = LeaveRequestSerializer(requester)
                            return Response("Leave Denied" )
                    else:
                        return Response("Invalid Id")
                else:
                    return Response("Invalid Id")
            else:
                return Response("Invalid Id")
        except Exception as exception:
            template = "{0}:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)

class ApproveView(APIView):

    def put(self,request,format=None):
        try:
            reporter_id = Employee.objects.get(id=request.data["reporter_id"])
            if reporter_id:
                requester = LeaveRequest.objects.get(id=request.data["request_id"])
                if requester:
                    if requester.reporter == reporter_id:
                        status = Status.objects.get(code=100)
                        if requester.status == status:
                            serializer = LeaveRequestSerializer(requester)
                            return Response(serializer.data)
                        else:
                            requester.status = status
                            requester.save()
                            serializer = LeaveRequestSerializer(requester)
                            return Response("Leave Approved")
                    else:
                        return Response("Invalid request id")
                else:
                    return Response("Invalid request id")
            else:
                return Response("Invalid Id")

        except Exception as exception:
            template = "{0}:\n{1!r}"
            message = template.format(type(exception).__name__, exception.args)
            return Response(message)

    def check_leave_type(self, user):
        lop = LeaveType.objects.get(code=100)
        if user.leave_type == lop:
            user = self.add_lop(user)
        else:
            user = self.reduce_leave_balance(user)
        return user

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

    def leave_lop(self, user):
        type_lop = LeaveType.objects.get(code=100)
        user.leave_type =  type_lop
        user.save()
        return user
