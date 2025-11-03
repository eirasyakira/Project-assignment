from django.contrib import admin
from xdinaryBooks.models import Book, Order, Review, Customer
# Register your models here.
admin.site.register(Book)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Customer)