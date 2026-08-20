from django.http import JsonResponse
from django.shortcuts import render,redirect
from store.forms import CustomUserForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
import json
from .models import Cart, Order, OrderItem
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.pdfgen import canvas


def home(request):
    products = Product.objects.filter(trending=True)
    categories = Category.objects.filter(status=False)

    return render(
        request,
        "store/index.html",
        {
            "products": products,
            "categories": categories,
        }
    )

def add_to_cart(request):
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        if request.user.is_authenticated:

            data = json.loads(request.body)

            product_qty = int(data['product_qty'])
            product_id = int(data['pid'])

            product = Product.objects.get(id=product_id)

            if Cart.objects.filter(user=request.user, product_id=product_id).exists():
                return JsonResponse({'status': 'Product Already in Cart'})

            if product.quantity >= product_qty:
                Cart.objects.create(
                    user=request.user,
                    product_id=product_id,
                    product_qty=product_qty
                )
                return JsonResponse({'status': 'Product Added to Cart'})

            return JsonResponse({'status': 'Product Stock Not Available'})

        return JsonResponse({'status': 'Login to Add Cart'})

    return JsonResponse({'status': 'Invalid Access'})

def add_to_favourite(request):
  
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        if request.user.is_authenticated:

            data = json.loads(request.body)
            product_id = int(data['pid'])

            fav = Favourite.objects.filter(
                user=request.user,
                product_id=product_id
            )

            if fav.exists():
                fav.delete()
                return JsonResponse({
                    'status': 'Removed from Favourite',
                    'action': 'remove'
                })

            Favourite.objects.create(
                user=request.user,
                product_id=product_id
            )

            return JsonResponse({
                'status': 'Added to Favourite',
                'action': 'add'
            })

        return JsonResponse({
            'status': 'Login First'
        })

    return JsonResponse({
        'status': 'Invalid Request'
    })

def favviewpage(request):
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        return render(request, "store/fav.html", {"fav": fav})

    return redirect('/')

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out Successfully")
    return redirect('/')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        name = request.POST.get('username')
        pwd = request.POST.get('password')

        user = authenticate(request, username=name, password=pwd)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in Successfully")
            return redirect('/')
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, 'store/login.html')


def remove_fav(request,fid):
    item = Favourite.objects.get(id=fid)
    item.delete()
    return redirect('/favviewpage')

def cart_page(request):

    if not request.user.is_authenticated:
        return redirect("login")


    cart_items = Cart.objects.filter(
        user=request.user
    )


    cart_total = 0


    for item in cart_items:

        cart_total += item.total_cost


    context = {
        "cart": cart_items,
        "cart_total": cart_total,
    }


    return render(
        request,
        "store/cart.html",
        context
    )
   
def remove_cart(request,cid):
    cartitem = Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect('/cart')


def register(request):
    form = CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Registration Successful! Login Now.")
            return redirect('login')

    return render(request, 'store/register.html', {'form': form})
  
def collections(request):
    category = Category.objects.filter(status=0)
    return render(request,'store/collections.html',{"category":category})

def collectionsview(request,name):
 if(Category.objects.filter(name=name,status=0)):
        products = Product.objects.filter(category__name=name)
        return render(request,'store/products/index.html',{"products":products,"category_name" :name})
 else:
    messages.warning(request,"No such Category Found")
    return redirect('collections')

def product_details(request,cname,pname): 
    if(Category.objects.filter(name=cname,status=0)):
     if(Product.objects.filter(name=pname,status=0)):
        products=Product.objects.filter(name=pname,status=0).first()         
        return render(request,'store/products/product_details.html',{"products":products})
     else:
             messages.error(request,"No Such Product Found")
             return redirect('collections')  
    else:
        messages.error(request,"No Such Category Found")
        return redirect('collections')
    
def update_cart(request):

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        if request.user.is_authenticated:

            data = json.loads(request.body)

            cart_id = int(data['cart_id'])
            qty = int(data['qty'])

            cart = Cart.objects.get(id=cart_id, user=request.user)

            if qty <= cart.product.quantity:

                cart.product_qty = qty
                cart.save()

                return JsonResponse({
                    "status": "Quantity Updated"
                })

            else:

                return JsonResponse({
                    "status": "Stock Not Available"
                })

    return JsonResponse({
        "status": "Invalid Request"
    })
    


def checkout(request):

    if not request.user.is_authenticated:
        return redirect("login")

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("cart")

    # Calculate total
    total_price = 0
    for item in cart_items:
        total_price += item.total_cost

    if request.method == "POST":

        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")
        pincode = request.POST.get("pincode")

        payment_mode = request.POST.get("payment_mode")

        # Check stock before creating order
        for item in cart_items:

            if item.product.quantity < item.product_qty:

                messages.error(
                    request,
                    f"{item.product.name} has only {item.product.quantity} item(s) left in stock."
                )

                return redirect("cart")

        # Create Order
        order = Order.objects.create(

            user=request.user,

            fname=fname,
            lname=lname,
            email=email,
            phone=phone,

            address=address,
            city=city,
            state=state,
            country=country,
            pincode=pincode,

            total_price=total_price,

            payment_mode=payment_mode

        )

        # Create Order Items & Reduce Stock
        for item in cart_items:

            OrderItem.objects.create(

                order=order,

                product=item.product,

                price=item.product.selling_price,

                quantity=item.product_qty

            )

            # Reduce stock
            product = item.product
            product.quantity -= item.product_qty
            product.save()

        # Clear Cart
        cart_items.delete()

        return redirect(
            "order_success",
            order_id=order.id
        )

    return render(
        request,
        "store/checkout.html",
        {
            "cart_items": cart_items,
            "total": total_price,
        }
    )
    
@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "store/my_orders.html",
        {
            "orders": orders
        }
    )


@login_required
def order_details(request,oid):

    order = get_object_or_404(
        Order,
        id=oid,
        user=request.user
    )

    items = OrderItem.objects.filter(order=order)

    return render(
        request,
        "store/order_details.html",
        {
            "order": order,
            "items": items,
        }
    )
    
def order_success(request, order_id):

    order = Order.objects.get(id=order_id)

    return render(
        request,
        "store/order_success.html",
        {
            "order": order
        }
    )
    

@login_required
def cancel_order(request, id):

    order = get_object_or_404(
        Order,
        id=id,
        user=request.user
    )

    if order.order_status == "Pending":

        # Restore stock
        items = OrderItem.objects.filter(order=order)

        for item in items:
            product = item.product
            product.quantity += item.quantity
            product.save()

        order.order_status = "Cancelled"
        order.save()

        messages.success(
            request,
            "Order cancelled successfully."
        )

    else:

        messages.error(
            request,
            "This order cannot be cancelled."
        )

    return redirect("my_orders")

def download_invoice(request, oid):

    order = get_object_or_404(
        Order,
        id=oid,
        user=request.user
    )

    items = OrderItem.objects.filter(order=order)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Invoice_{order.id}.pdf"'
    )

    pdf = canvas.Canvas(response)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(200, 800, "PrimeBasket Invoice")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(50, 770, f"Invoice No : {order.id}")
    pdf.drawString(50, 750, f"Customer : {order.fname} {order.lname}")
    pdf.drawString(50, 730, f"Email : {order.email}")
    pdf.drawString(50, 710, f"Phone : {order.phone}")

    pdf.drawString(50, 690, "----------------------------------------------")

    y = 660

    pdf.drawString(50, y, "Product")
    pdf.drawString(270, y, "Qty")
    pdf.drawString(330, y, "Price")
    pdf.drawString(430, y, "Total")

    y -= 25

    for item in items:

        pdf.drawString(50, y, item.product.name)
        pdf.drawString(270, y, str(item.quantity))
        pdf.drawString(330, y, f"Rs.{item.price:.0f}")
        pdf.drawString(430, y, f"Rs.{item.total:.0f}")

        y -= 20

    pdf.drawString(50, y - 20, "----------------------------------------------")

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        300,
        y - 50,
        f"Grand Total : Rs.{order.total_price:.0f}"
    )

    pdf.save()

    return response