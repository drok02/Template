from django.db import models

class Account_info(models.Model):
    name = models.CharField(max_length = 50, primary_key = True)
    password = models.CharField(max_length = 100)
    api_key = models.CharField(max_length = 200)
    secret_key = models.CharField(max_length = 200)
    class Meta:
        # table name
        db_table = 'accounts_info'
