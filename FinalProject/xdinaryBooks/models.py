from django.db import models
import uuid

# Create your models here.
class Book(models.Model):
    bookid = models.CharField(max_length=3, primary_key=True)
    title = models.CharField(max_length=30)
    author = models.CharField(max_length=15)
    genre = models.CharField(max_length=10)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)

class Customer(models.Model):
    username = models.CharField(max_length=10, primary_key=True)
    password = models.CharField(max_length=128)
    email = models.EmailField()
    phone = models.CharField(max_length=12)

class Order(models.Model):
    orderid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bookid = models.ManyToManyField(Book)
    username = models.ForeignKey(Customer, on_delete=models.CASCADE)
    orderdate = models.DateField()
    totalprice = models.DecimalField(max_digits=10, decimal_places=2)

class Review(models.Model):
    reviewid = models.CharField(max_length=3, primary_key=True)
    bookid = models.ForeignKey(Book, on_delete=models.CASCADE)
    username = models.ForeignKey(Customer, on_delete=models.CASCADE)
    review_datetime = models.DateTimeField()
    reviewtext = models.TextField()
    reviewimage = models.ImageField(upload_to='review_images/', null=True, blank=True)