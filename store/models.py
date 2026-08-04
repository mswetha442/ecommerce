from django.db import models
from django.contrib.auth.models import User
import datetime 
import os


def getFileName(request,filename):
    now_time =datetime.datetime.now().strftime("%Y%m%d%H:%M:%S")
    new_filename="%s%s"%(now_time,filename)
    return os.path.join('uploads/',new_filename)

class Category(models.Model):
    name = models.CharField(max_length=150,null=False,blank=False)
    image = models.ImageField(upload_to=getFileName ,null=True,blank=True)
    description = models.TextField(max_length=500,null=False,blank=True)
    status = models.BooleanField(default=False,help_text="0-show,1-Hidden")
    trending = models.BooleanField(default=False,help_text="0-default,1-Trending")
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.CharField(max_length=150,null=False,blank=False)
    vendor = models.CharField(max_length=150,null=False,blank=False)
    product_image = models.ImageField(upload_to=getFileName ,null=True,blank=True)
    quantity=models.IntegerField(null=False,blank=False)  
    original_price=models.FloatField(null=False,blank=False)   
    selling_price=models.FloatField(null=False,blank=False)   
    description = models.TextField(max_length=500,null=False,blank=True)
    status = models.BooleanField(default=False,help_text="0-show,1-Hidden")
    trending = models.BooleanField(default=False,help_text="0-default,1-Trending")
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    product_qty = models.IntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)

    @property
    def total_cost(self):
     return self.product_qty*self.product.selling_price 

class Favourite(models.Model):
   user=models.ForeignKey(User,on_delete=models.CASCADE)
   product=models.ForeignKey(Product,on_delete=models.CASCADE)
   created_at=models.DateTimeField(auto_now_add=True)
   
class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    fname = models.CharField(max_length=150)
    lname = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)

    address = models.TextField()
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    pincode = models.CharField(max_length=20)

    total_price = models.FloatField()

    payment_mode = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=250, null=True, blank=True)

    order_status = models.CharField(max_length=50,default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()
    created_at = models.DateTimeField(
        auto_now_add=True)
    
    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return self.product.name
    
