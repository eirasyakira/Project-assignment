from django.shortcuts import render, redirect, get_object_or_404
from xdinaryBooks.models import Book, Customer, Order, Review
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import uuid  # Add this import for generating unique review IDs

# Create your views here.
def main(request):
    books = Book.objects.all()
    return render(request, 'main.html', {'books': books})

def search(request):
    search_by = request.GET.get('search_by')
    search_value = request.GET.get('search_value')
    if search_by == 'title':
        data = Book.objects.filter(title__icontains=search_value)
    elif search_by == 'author':
        data = Book.objects.filter(author__icontains=search_value)
    else:
        data = Book.objects.filter(
            title__icontains=search_value
        ) | Book.objects.filter(
            author__icontains=search_value
        ) | Book.objects.filter(
            genre__icontains=search_value
        ) | Book.objects.filter(
            description__icontains=search_value
        )
    return render(request, 'search.html', {'data': data, 'message': 'Search Results'})

@login_required(login_url='/login/')
def profile(request):
    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return render(request, 'profile.html', {'error': 'Customer not found.'})
    if request.method == 'POST':
        customer.password = request.POST['password']
        customer.email = request.POST['email']
        customer.phone = request.POST['phone']
        customer.save()
        user = User.objects.get(username=request.user.username)
        user.set_password(request.POST['password'])
        user.email = request.POST['email']
        user.save()
        login(request, user)
        return redirect('profile')
    return render(request, 'profile.html', {'customer': customer})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        phone = request.POST['phone']
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists. Please choose another username.'})
        user = User.objects.create_user(username=username, password=password, email=email)
        customer = Customer(username=username, password=password, email=email, phone=phone)
        customer.save()
        login(request, user)
        return redirect('profile')
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('main')

@login_required(login_url='/login/')
def add_to_cart(request, book_id):
    book = Book.objects.get(bookid=book_id)
    if 'cart' not in request.session:
        request.session['cart'] = []
    request.session['cart'].append(book_id)
    request.session.modified = True
    return redirect('cart')

@login_required(login_url='/login/')
def remove_from_cart(request, book_id):
    if 'cart' in request.session:
        request.session['cart'].remove(book_id)
        request.session.modified = True
    return redirect('cart')

@login_required(login_url='/login/')
def view_cart(request):
    cart = request.session.get('cart', [])
    books = Book.objects.filter(bookid__in=cart)
    total_price = sum(book.price for book in books)
    return render(request, 'cart.html', {'books': books, 'total_price': total_price})

@login_required(login_url='/login/')
def process_purchase(request):
    cart = request.session.get('cart', [])
    if not cart:
        return redirect('cart')
    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return render(request, 'purchase.html', {'error': 'Customer not found.'})
    total_price = sum(Book.objects.get(bookid=book_id).price for book_id in cart)
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return render(request, 'purchase.html', {
                'books': Book.objects.filter(bookid__in=cart),
                'total_price': total_price,
                'customer': customer,
                'error': 'Email is required to send the E-Book.'
            })
        order = Order(username=customer, totalprice=total_price, orderdate=timezone.now())
        order.save()
        for book_id in cart:
            book = Book.objects.get(bookid=book_id)
            order.bookid.add(book)
        request.session['cart'] = []
        return redirect('order_confirmation', order_id=order.orderid)
    return render(request, 'purchase.html', {
        'books': Book.objects.filter(bookid__in=cart),
        'total_price': total_price,
        'customer': customer
    })

@login_required(login_url='/login/')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, orderid=order_id)
    customer = order.username
    books = order.bookid.all()
    return render(request, 'order_confirmation.html', {
        'order': order,
        'customer': customer,
        'books': books
    })

def book_detail(request, book_id):
    book = Book.objects.get(bookid=book_id)
    reviews = Review.objects.filter(bookid=book)
    return render(request, 'book.html', {'book': book, 'reviews': reviews})

@login_required(login_url='/login/')
def submit_review(request, book_id):
    book = get_object_or_404(Book, bookid=book_id)
    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return redirect('login')
    
    # Check if the user has purchased the book
    if not Order.objects.filter(username=customer, bookid=book).exists():
        return redirect('book_detail', book_id=book_id)
    
    if request.method == 'POST':
        review_text = request.POST.get('reviewtext')
        review_image = request.FILES.get('reviewimage')
        review = Review(
            reviewid=str(uuid.uuid4())[:3],
            bookid=book,
            username=customer,
            review_datetime=timezone.now(),
            reviewtext=review_text,
            reviewimage=review_image
        )
        review.save()
        return redirect('book_detail', book_id=book_id)  # Redirect to book detail page after saving review
    return render(request, 'submit_review.html', {'book': book})

@login_required(login_url='/login/')
def view_orders(request):
    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return render(request, 'orders.html', {'error': 'Customer not found.'})
    orders = Order.objects.filter(username=customer)
    return render(request, 'orders.html', {'orders': orders})

@login_required(login_url='/login/')
def my_purchases(request):
    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return redirect('login')
    orders = Order.objects.filter(username=customer)
    books = Book.objects.filter(order__in=orders).distinct()
    return render(request, 'my_purchases.html', {'books': books})
