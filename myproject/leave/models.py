# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import datetime

class Designation(models.Model):
	code = models.IntegerField()
	name = models.CharField(max_length=30)

	def __str__(self):
		return self.name

class User(models.Model):
	code = models.IntegerField()
	name = models.CharField(max_length = 30)
	email = models.CharField(max_length = 30)
	join_date = models.DateField()
	mode = models.BooleanField()
	designation = models.ForeignKey(Designation,
		on_delete=models.CASCADE)
	reporting_senior =models.CharField(max_length = 30)
	
	def __str__(self):
		return self.name

class Status(models.Model):
	code = models.IntegerField()
	status = models.CharField(max_length=30)  

	def __str__(self):
		return self.status

class LeaveType(models.Model):
	code = models.IntegerField()
	catagory = models.CharField(max_length=30)

	def __str__(self):
		return self.catagory
	
class LeaveCredit(models.Model):
	user_name = models.ForeignKey(User,
		on_delete=models.CASCADE)
	leave_type = models.ForeignKey(LeaveType,
		on_delete=models.CASCADE)
	available = models.IntegerField()

	def __str__(self):
		return str(self.user_name)

class LeaveRequest(models.Model):
	employee_name = models.ForeignKey(User, null=True, related_name='employee_name')
	reporter = models.ForeignKey(User, null=True, related_name='reporter')
	leave_type = models.ForeignKey(LeaveType, null=True, related_name='leave_type')
	from_date = models.DateField()
	to_date = models.DateField()
	no_days = models.IntegerField()
	reason = models.CharField(max_length=500)
	status = models.ForeignKey(Status,
		on_delete=models.CASCADE)

	def __str__(self):
		return str(self.employee_name)
