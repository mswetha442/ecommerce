from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Category, Order, OrderItem
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Sum
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps
from django.contrib.auth import logout
from django.contrib import messages

def staff_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_staff:
            return HttpResponseForbidden(
                "You are not authorized to access this page."
            )

        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
@staff_required
def dashboard(request):

    total_products = Product.objects.count()

    total_categories = Category.objects.count()

    total_customers = User.objects.filter(
        is_staff=False
    ).count()

    total_orders = Order.objects.count()



    pending_orders = Order.objects.filter(
        order_status="Pending"
    ).count()


    shipped_orders = Order.objects.filter(
        order_status="Shipped"
    ).count()


    delivered_orders = Order.objects.filter(
        order_status="Delivered"
    ).count()


    cancelled_orders = Order.objects.filter(
        order_status="Cancelled"
    ).count()



    total_revenue = sum(
        order.total_price
        for order in Order.objects.filter(
            order_status="Delivered"
        )
    )



    recent_orders = Order.objects.all().order_by(
        "-created_at"
    )[:5]



    # Chart Data

    chart_data = json.dumps([
        total_products,
        total_categories,
        total_orders,
        total_customers
    ])




    context = {

        "total_products": total_products,

        "total_categories": total_categories,

        "total_customers": total_customers,

        "total_orders": total_orders,


        "pending_orders": pending_orders,

        "shipped_orders": shipped_orders,

        "delivered_orders": delivered_orders,

        "cancelled_orders": cancelled_orders,


        "total_revenue": total_revenue,


        # Chart

        "chart_data": chart_data,


        # Recent Orders

        "recent_orders": recent_orders,

    }



    return render(
        request,
        "adminpanel/index.html",
        context
    )
    
@login_required 
@staff_required  
def product_list(request):
    
    
    query = request.GET.get("q")

    products = Product.objects.select_related("category")

    if query:

        products = products.filter(
            Q(name__icontains=query) |
            Q(vendor__icontains=query)
        )

    return render(
        request,
        "adminpanel/products/product_list.html",
        {
            "products": products,
            "query": query,
        },
    )
    
    
@login_required
@staff_required

def add_product(request):

    categories = Category.objects.filter(status=False)

    if request.method == "POST":

        category = get_object_or_404(
            Category,
            id=request.POST.get("category")
        )

        Product.objects.create(
            category=category,
            name=request.POST.get("name"),
            vendor=request.POST.get("vendor"),
            original_price=request.POST.get("original_price"),
            selling_price=request.POST.get("selling_price"),
            quantity=request.POST.get("quantity"),
            description=request.POST.get("description"),
            product_image=request.FILES.get("product_image"),
            trending=True if request.POST.get("trending") else False,
            status=True if request.POST.get("status") else False,
        )

        return redirect("product_list")

    return render(
        request,
        "adminpanel/products/add_product.html",
        {
            "categories": categories
        },
    )
    
@login_required   
@staff_required 
def edit_product(request, id):

    product = get_object_or_404(Product, id=id)
    categories = Category.objects.filter(status=False)

    if request.method == "POST":

        product.category = get_object_or_404(
            Category,
            id=request.POST.get("category")
        )

        product.name = request.POST.get("name")
        product.vendor = request.POST.get("vendor")
        product.original_price = request.POST.get("original_price")
        product.selling_price = request.POST.get("selling_price")
        product.quantity = request.POST.get("quantity")
        product.description = request.POST.get("description")

        if request.FILES.get("product_image"):
            product.product_image = request.FILES.get("product_image")

        product.trending = True if request.POST.get("trending") else False
        product.status = True if request.POST.get("status") else False

        product.save()

        return redirect("product_list")

    return render(
        request,
        "adminpanel/products/edit_product.html",
        {
            "product": product,
            "categories": categories,
        },
    )
    
    
@login_required
@staff_required
def delete_product(request, id):

    product = get_object_or_404(Product, id=id)

    if product.product_image:
        product.product_image.delete(save=False)

    product.delete()

    return redirect("product_list")

@login_required
@staff_required
def category_list(request):

   
    query = request.GET.get("q")

    categories = Category.objects.all()

    if query:

        categories = categories.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(
        request,
        "adminpanel/categories/category_list.html",
        {
            "categories": categories,
            "query": query,
        }
    )
    
@login_required
@staff_required
def add_category(request):

    if request.method == "POST":

        Category.objects.create(

            name=request.POST.get("name"),
            description=request.POST.get("description"),
            image=request.FILES.get("image"),
            trending=True if request.POST.get("trending") else False,
            status=True if request.POST.get("status") else False,

        )

        return redirect("category_list")

    return render(
        request,
        "adminpanel/categories/add_category.html"
    )
    
@login_required
@staff_required
def edit_category(request, id):
 
   category = get_object_or_404(Category, id=id)

   if request.method == "POST":

        category.name = request.POST.get("name")
        category.description = request.POST.get("description")

        if request.FILES.get("image"):
            category.image = request.FILES.get("image")

        category.trending = True if request.POST.get("trending") else False
        category.status = True if request.POST.get("status") else False

        category.save()

        return redirect("category_list")
   return render(
        request,
        "adminpanel/categories/edit_category.html",
        {
            "category": category
        }
    )
 
@login_required
@staff_required
def delete_category(request, id):

 category = get_object_or_404(Category, id=id)

 if category.image:
        category.image.delete(save=False)
        category.delete()

        return redirect("category_list")

@login_required    
@staff_required
def order_list(request):

    query = request.GET.get("q")

    orders = Order.objects.all().order_by("-created_at")

    if query:
        orders = orders.filter(
            Q(fname__icontains=query) |
            Q(lname__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(id__icontains=query)
        )

    context = {
        "orders": orders,
        "query": query,
    }

    return render(
        request,
        "adminpanel/orders/order_list.html",
        context
    )


@login_required  
@staff_required
def orders(request):

    orders = Order.objects.all().order_by("-created_at")

    return render(
        request,
        "adminpanel/orders/index.html",
        {
            "orders": orders
        }
    )

@login_required
@staff_required
def index(request):

    context = {

        "total_products": Product.objects.count(),

        "total_orders": Order.objects.count(),

        "pending_orders": Order.objects.filter(
            order_status="Pending"
        ).count(),

        "total_customers": User.objects.count(),

        "recent_orders": Order.objects.all()
                         .order_by('-created_at')[:5]
    }
    return render(
        request,
        "adminpanel/index.html",
        context
    )
    
    
@login_required
@staff_required    
def customer_list(request):

    customers = User.objects.all().order_by("-date_joined")

    return render(
        request,
        "adminpanel/customers/customer_list.html",
        {
            "customers": customers
        }
    )    
@login_required    
@staff_required
def customer_details(request, id):

    customer = get_object_or_404(User, id=id)

    orders = Order.objects.filter(user=customer).order_by("-created_at")

    return render(
        request,
        "adminpanel/customers/customer_details.html",
        {
            "customer": customer,
            "orders": orders,
        }
    )
    
@login_required  
@staff_required
def sales_report(request):

    total_orders = Order.objects.count()

    delivered_orders = Order.objects.filter(
        order_status="Delivered"
    ).count()

    pending_orders = Order.objects.filter(
        order_status="Pending"
    ).count()

    cancelled_orders = Order.objects.filter(
        order_status="Cancelled"
    ).count()

    total_revenue = (
        Order.objects.filter(order_status="Delivered")
        .aggregate(total=Sum("total_price"))["total"]
        or 0
    )

    recent_orders = (
        Order.objects.filter(order_status="Delivered")
        .order_by("-created_at")[:10]
    )

    context = {
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "pending_orders": pending_orders,
        "cancelled_orders": cancelled_orders,
        "total_revenue": total_revenue,
        "recent_orders": recent_orders,
    }

    return render(
        request,
        "adminpanel/reports/sales_report.html",
        context
    )


@login_required 
@staff_required
def admin_order_details(request, id):

    order = Order.objects.get(id=id)

    if request.method == "POST":

        status = request.POST.get("status")

        order.order_status = status

        order.save()

        return redirect(
            "admin_order_details",
            id=id
        )


    items = OrderItem.objects.filter(
        order=order
    )


    return render(
        request,
        "adminpanel/orders/order_details.html",
        {
            "order": order,
            "items": items,
        }
    )
    
def admin_logout(request):

    if request.user.is_authenticated:

        logout(request)

        messages.success(
            request,
            "Admin logged out successfully."
        )

    return redirect("admin_login")
