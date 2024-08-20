from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=255)
    creator = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
