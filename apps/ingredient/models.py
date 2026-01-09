from django.db import models

# Create your models here.
class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    number_of = models.DecimalField(max_digits=10, decimal_places=2)


    class Meta:
        db_table = "ingredient"