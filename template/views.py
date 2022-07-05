# 세번째 개발 : 로직을 설계
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser,FileUploadParser
from .serializers import TemplateSerializer
from .models import Template_info,OpenStack_Instance_info, CloudStack_Instance_info
import os, sys,shutil
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, get_list_or_404
import json

# Manage All Objects
class TemplateView(APIView):
	parser_classes = (MultiPartParser, FormParser,FileUploadParser)
		
	# upload template file
	def post(self, request, *args, **kwargs):
			serializer =TemplateSerializer(data=request.data)
			if serializer.is_valid():
				if os.path.isdir("/home/ubuntu/Template-Manager/media/") == False:
					os.makedirs("/home/ubuntu/Template-Manager/media/")
				with open('/home/ubuntu/Template-Manager/media/'+request.data['name']+'.tf.json', "w", encoding="utf-8") as mk_f:
					content = json.loads(request.data['upload_files'].replace("\'", "\""))
					json.dump(content, mk_f, indent='\t')
					response = JsonResponse(content, status = status.HTTP_201_CREATED)
					response['Access-Control-Allow-Origin'] ='*'
					serializer.save()
					return response

			response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			response['Access-Control-Allow-Origin'] ='*'
			return response

	def delete(self,request):
			templates = Template_info.objects.all()
			shutil.rmtree("/home/ubuntu/Template-Manager/media/")
			templates.delete()
			response = Response("Delete All Templates Suceess!")
			response['Access-control-allow-origin'] ='*'
			response['Access-control-allow-methods'] ='*'
			return response

	def options(self,request):
		response = Response()
		response['Access-Control-Allow-Origin'] ='*'  
		response['Access-Control-Allow-Methods'] ='DELETE,POST,PUT'
		response['Access-Control-Allow-Headers'] ='content-type'
		return response

    # show all template information
	def get(self,request):
		templates = Template_info.objects.all()
		serializer =TemplateSerializer(templates,many=True)
		X_total_count = len(serializer.data)
		response = Response(serializer.data)
		response['Access-control-expose-headers'] ="X-total-count"
		response['X-total-count'] = len(serializer.data)
		response['Access-control-allow-origin'] ='*' 
		if templates:
			return response
		else:
		    response = Response([])
		    response['X-total-count']= 0
		    response['Access-control-allow-origin'] ='*'
		    response['Access-control-expose-headers'] ="X-total-count"
		    return response

	def put(self,request):
		#terraform destroy
		os.chdir("/home/ubuntu/Template-Manager/terraform/")
		os.system('terraform destroy -auto-approve')
		# openstack instance 삭제
		OpenStack_Instance_Info = OpenStack_Instance_info.objects.filter(user_id="openstack")
		OpenStack_Instance_Info.delete()
		# cloudstack instance 삭제 
		CloudStack_Instance_Info = CloudStack_Instance_info.objects.filter(user_id="cloudstack")
		CloudStack_Instance_Info.delete()
		return HttpResponse("There is no Template File")

# Manage Specific Object 
class TemplateDetails(APIView):
	def get_object(self, id):
		response = Response()
		response['Access-Control-Allow-Origin'] ='*' 
		try:
			return Template_info.objects.get(id=id)
		except Template.DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)
	
	# show template content
	def get(self, request, id):
		templates = self.get_object(id)
		serializer = TemplateSerializer(templates)
		if serializer.data['name']:
			with open('/home/ubuntu/Template-Manager/media/'+ serializer.data['name']+'.tf.json',"r") as f:
				content = json.load(f)
			response = Response([{"id":serializer.data['id'],"info":content}])
			response['Access-Control-Allow-Origin'] ='*' 
			#print(json.dumps(content,indent='\t'))		
			return response
		else:
			response['Access-Control-Allow-Origin'] ='*'
			reponse =Response("Invalid File")
			return reponse

	# delete template information
	def delete(self, request, id):
		templates = self.get_object(id)
		serializer = TemplateSerializer(templates)
		os.remove('/home/ubuntu/Template-Manager/media/'+serializer.data['name']+'.tf.json')
		templates.delete()
		response = Response("Delete Template File",status=status.HTTP_204_NO_CONTENT)
		response['Access-Control-Allow-Origin'] ='*' 
		return response

		
	# conversion JSON template file  --> file change
	def put(self, request, id):
		templates = self.get_object(id)
		serializer = TemplateSerializer(templates)

		cloudstack_instance = dict([("name","cloudstack"),("service_offering","Small Instance"),("network_id","5a72a038-2851-4c29-8c36-13b7e29c48da"),("zone","zone1"),("template","centos 7")])
		openstack_instance = dict([("name","openstack"),("image_id","fc739109-e625-4267-ab1d-178fa4242702"),("network",dict([("name","public")])),("flavor_name","m1.small")])
		cloudstack_volume = dict([("name","volume_1"),("disk_offering","Small"),("zone","zone1")])
		openstack_volume = dict([("name","volume_1"),("region","RegionOne"),("size",3)])
		cloudstack_network = dict([("name","network_1"),("cidr","10.0.0.0/16"),("network_offering","DefaultSharedNetworkOffering"),("zone","zone1")])
		openstack_network = dict([("name","network_1"),("admin_state_up","true")])
		# cloudstack_volume

		# before template file read	
		with open('/home/ubuntu/Template-Manager/media/'+ serializer.data['name']+'.tf.json','r') as json_file:
			json_data = json.load(json_file) # json -> dict
			type_ = json_data["resource"]

			if "openstack_compute_instance_v2" in type_: # openstack --> cloudstack
				type_["cloudstack_instance"] = type_.pop("openstack_compute_instance_v2")
				type_["cloudstack_instance"]["instance_1"] = cloudstack_instance
				print(json.dumps(type_, indent='\t'))

			elif "cloudstack_instance" in type_: # cloudstack --> openstack
				type_["openstack_compute_instance_v2"] = type_.pop("cloudstack_instance")
				type_["openstack_compute_instance_v2"]["instance_1"] = openstack_instance
				print(json.dumps(type_, indent='\t'))

			elif "openstack_blockstorage_volume_v3" in type_: # cloudstack --> openstack
				type_["cloudstack_disk"] = type_.pop("openstack_blockstorage_volume_v3")
				type_["cloudstack_disk"]["volume_1"] = cloudstack_volume
				print(json.dumps(type_, indent='\t'))

			elif "cloudstack_disk" in type_: # cloudstack --> openstack
				type_["openstack_blockstorage_volume_v3"] = type_.pop("cloudstack_disk")
				type_["openstack_blockstorage_volume_v3"]["volume_1"] = openstack_volume
				print(json.dumps(type_, indent='\t'))

			elif "openstack_networking_network_v2" in type_: # openstack --> cloudstack
				type_["cloudstack_network"] = type_.pop("openstack_networking_network_v2")
				type_["cloudstack_network"]["network_1"] = cloudstack_network
				print(json.dumps(type_, indent='\t'))	
					
			elif "cloudstack_network" in type_: # cloudstack --> openstack
				type_["openstack_networking_network_v2"] = type_.pop("cloudstack_network")
				type_["openstack_networking_network_v2"]["network_1"] = openstack_network
				print(json.dumps(type_, indent='\t'))

		# write template file after conversing
		with open('/home/ubuntu/Template-Manager/media/'+ serializer.data['name']+'.tf.json', "w", encoding="utf-8") as mk_f:
			json.dump(json_data, mk_f, indent='\t')

		# read after conversing template file
		with open('/home/ubuntu/Template-Manager/media/'+ serializer.data['name']+'.tf.json', "r", encoding="utf-8") as f:
			json_data = json.load(f)
		print(json.dumps(json_data, indent='\t'))
		response = Response(json_data)
		response['Access-Control-Allow-Origin'] ='*' 
		return response


	def options(self,request,id):
		response = Response()
		response['Access-Control-Allow-Origin'] ='*'
		response['Access-Control-Allow-Methods'] ='PUT,DELETE'
		response['Access-Control-Allow-Headers'] ='content-type'
		return response


class Terraform(APIView):
	def get_object(self, id):
		try:
			return Template_info.objects.get(id=id)
		except Template_info.DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)

	# terraform apply
	def get(self,request,id):
		templates = self.get_object(id)
		serializer = TemplateSerializer(templates)
		# read file
		with open('/home/ubuntu/Template-Manager/media/'+serializer.data['name']+'.tf.json',"r") as f:
			json_data = json.load(f)
		# write file to main.tf
		with open('/home/ubuntu/Template-Manager/terraform/main.tf.json', "w", encoding="utf-8") as mk_f:
			json.dump(json_data, mk_f, indent='\t')
		os.chdir("/home/ubuntu/Template-Manager/terraform/") # terraform 으로 현재 디렉토리 변경
		os.system('terraform init')
		os.system('terraform apply -auto-approve')
		if serializer.data['name'] == 'openstack instance':
			OpenStack_Instance_Info = OpenStack_Instance_info(ins_id = "c3bc33fe-5ef7-4e24-ae1b-093bdc469cf6",user_id = "openstack",ins_name = "openstack",vol_id = "6eb1439b-84d4-4fbf-b210-23ee5da57e1b",os_name = "centos 7",created = serializer.data['uploaded_at'])
			OpenStack_Instance_Info.save()
		elif serializer.data['name'] == 'cloudstack instance':
			CloudStack_Instance_Info = CloudStack_Instance_info(ins_id = "77da7015-636b-48b8-9077-7707652fc5c6",user_id = "cloudstack",ins_name = "cloudstack",vol_id = "7596c19f-cb13-4946-955a-2c74628c1aa0",os_name = "centos 7",created = serializer.data['uploaded_at'])
			CloudStack_Instance_Info.save()
		os.chdir("/home/ubuntu/Template-Manager/template/") # terraform 으로 현재 디렉토리 변경

		return Response("terraform apply success",status = status.HTTP_201_CREATED)

