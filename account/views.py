from django.shortcuts import render
import json
import requests
from .models import Account_info
from django.views import View
from django.http import HttpResponse, JsonResponse

# 사용자 정보 저장, 회원가입
class AccountView(View):
    def post(self, request):
        data2 = json.loads(request.body)
        # Admin으로 Token 발급 Body
        token_payload = {
            "name": "admin",
            "password": "0000",
            "project_id": "f7048d5ea4844f458c1f1a86738745e8"
        }

        # Openstack keystone token 발급
        auth_res = requests.post("http://52.78.82.160:7014/token",
            headers = {'content-type' : 'application/json'},
            data = json.dumps(token_payload))

        #발급받은 token
        admin_token = auth_res.json()["token"]
        print("token",admin_token)

        # 사용자의 openstack 정보 
        openstack_uesr_payload = {
            "user": {
                "name":data2['name'],
                "password": str(data2['password']),
                "default_project_id": "f7048d5ea4844f458c1f1a86738745e8"
            }
        }
        signature_payload ={
            "requests": {
                    "apiKey":"0OcHRmqlLKxseRjIRoqW2sBtpIbaDDvnUElpbZVedZIVoZ1F11fcKi1n1MDGNuDWDXxBnG6Ba-jMFqSpAi5Tfg",
                    "response": "json",
                    "command": "createAccount",
                    "email": "test",
                    "firstname": "ricky",
                    "lastname": "test",
                    "password": str(data2['password']),
                    "username": data2['name'],
                    "domainid": "be9b0383-d57b-11eb-9d77-52540057817c",
                    "roleid": "f2153fca-d57b-11eb-9d77-52540057817c"
            },
            "secretKey": "xtbZVaUeYuds-ke_lCyRh0pZSdKdzUNHufwJeSvynO6847jJpWEb_aODEvsuHZ10os--xVFRAl3jepBiA33BAA"
        }
        #cloudstack key 생성
        key_res = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data = json.dumps(signature_payload))
        key = key_res.json()
        user_response = requests.post("http://164.125.70.26:8080/client/api?"+key)
        user_id = user_response.json()['createaccountresponse']["account"]["user"][0]["id"]

        body = {
            "requests": {
                    "apiKey": "0OcHRmqlLKxseRjIRoqW2sBtpIbaDDvnUElpbZVedZIVoZ1F11fcKi1n1MDGNuDWDXxBnG6Ba-jMFqSpAi5Tfg",
                    "response": "json",
                    "command": "registerUserKeys",
                    "id": user_id
            },
            "secretKey": "xtbZVaUeYuds-ke_lCyRh0pZSdKdzUNHufwJeSvynO6847jJpWEb_aODEvsuHZ10os--xVFRAl3jepBiA33BAA"
        }
        signature_res = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data = json.dumps(body))
        # signature 생성
        signature = signature_res.json()
        key_res = requests.get("http://164.125.70.26:8080/client/api?"+signature)
        # api key, secret key  생성 
        api_key = key_res.json()["registeruserkeysresponse"]["userkeys"]["apikey"]
        secret_key = key_res.json()["registeruserkeysresponse"]["userkeys"]["secretkey"]

        # DB 저장 
        Account_info.objects.create(
            name = data2['name'],
            password = data2['password'],
            api_key = api_key,
            secret_key = secret_key
        )        

        #openstack 사용자 생성
        user_res = requests.post("http://164.125.70.22/identity/v3/users",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(openstack_uesr_payload))
        print(user_res.json())

        #openstack id 확인
        openstack_id = user_res.json()["user"]["id"]
        # 생성된 사용자를 admins 그룹에 추가
        group_res = requests.put("http://164.125.70.22/identity/v3/groups/65d8b8f223c249dbb5c316b3c604bea2/users/"+ openstack_id,
            headers = {'X-Auth-Token' : admin_token})

        permission_req = requests.put("http://164.125.70.22/identity/v3/domains/default/users/"+openstack_id+"/roles/a72b87b6428c4a568b4116b2a500da9b")
        response = JsonResponse(data2,status = 200)
        response['Access-Control-Allow-Origin'] ='*'
        return response

    def get(self, request):
        Account_data = Account_info.objects.values()
        return JsonResponse({'accounts' : list(Account_data)}, status = 200)

    def delete(self,request):
        Account_data = Account_info.objects.all()
        Account_data.delete()
        return HttpResponse("Delete Success")


# 로그인
class SignView(View):
    def post(self, request):
        data = json.loads(request.body)
        # 사용자의 openstack 정보 
        try:
            if Account_info.objects.filter(name = data['name']).exists():
                user = Account_info.objects.get(name=data['name'])
                if user.password == data['password']:
                    token_payload = {
                        "name": user.name,
                        "password": str(user.password),
                        "project_id": "f7048d5ea4844f458c1f1a86738745e8"
                    }                  
                    # Openstack keystone token 발급
                    auth_res2 = requests.post("http://52.78.82.160:7014/token",
                        headers = {'content-type' : 'application/json'},
                        data = json.dumps(token_payload))
                    token = auth_res2.json()["token"]
                    response = JsonResponse({"token":token,"apikey":user.api_key,"secretkey":user.secret_key},status=200)
                    response['Access-Control-Allow-Origin'] ='*'
                    return response
                response = HttpResponse("Wrong Password",status=401)
                response['Access-Control-Allow-Origin'] ='*'                
                return response
            response = HttpResponse("Invalid name",status = 400)
            response['Access-Control-Allow-Origin'] ='*'                
            return response
        except KeyError:
            response = JsonResponse({'message': "INVALID_KEYS"}, status =400)
            response['Access-Control-Allow-Origin'] ='*'  
            return response
