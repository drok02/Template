# 첫번째로 개발 : Model을 이용해 Database의 ORM(Object Relational Mappling)을 설계함
from django.db import models


# 업로드 일자 / 파일명 / 설명 / 업로드 일자 
class Template_info(models.Model):
    upload_files = models.CharField(max_length=500,blank=False, null=False)
    name = models.CharField(max_length = 50)
    description = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True)
    class Meta:
        # table name
        db_table = 'Templates_info'

class OpenStack_Instance_info(models.Model):
    ins_id = models.TextField(primary_key=True)
    user_id = models.TextField()
    ins_name = models.TextField()
    vol_id = models.TextField()
    os_name = models.TextField()
    created = models.TextField()

    class Meta:
        managed = False
        db_table = 'snap_mig_service_openstack_instance_info'


class CloudStack_Instance_info(models.Model):
    ins_id = models.TextField(primary_key=True)
    user_id = models.TextField()
    ins_name = models.TextField()
    vol_id = models.TextField()
    os_name = models.TextField()
    created = models.TextField()

    class Meta:
        managed = False
        db_table = 'snap_mig_service_cloudstack_instance_info'
