from django.db import models

# Create your models here.
class products(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Reference Ingredient via app_label.ModelName and through model with its app label
    ingredients = models.ManyToManyField('ingredient.Ingredient', through='dishingredient.DishIngredient')

    class Meta:
        db_table = "products"