from django.db import models

class DishIngredient(models.Model):
    dish = models.ForeignKey('products.products', on_delete=models.CASCADE)
    ingredient = models.ForeignKey('ingredient.Ingredient', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)