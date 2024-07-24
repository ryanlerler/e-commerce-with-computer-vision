from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order
from .forms import ProductForm, RegistrationForm
import cv2
from django.contrib.auth import login, authenticate
import numpy as np
import base64
from django.http import HttpResponseBadRequest

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            
            if 'image' in request.FILES:
                # Save the original image temporarily
                product.image.save(request.FILES['image'].name, request.FILES['image'])
                
                # Read the image and encode it to base64 for displaying in HTML
                image = cv2.imread(product.image.path)
                _, buffer = cv2.imencode('.jpg', image)
                img_str = base64.b64encode(buffer).decode('utf-8')
                
                # Pass the image to the template for user selection
                return render(request, 'select_area.html', {'product_id': product.id, 'image': img_str})
            
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

def process_image(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Get coordinates from the form
        x = int(request.POST.get('x', 0))
        y = int(request.POST.get('y', 0))
        width = int(request.POST.get('width', 0))
        height = int(request.POST.get('height', 0))
        
        # Read the image
        image = cv2.imread(product.image.path)
        
        # Check if the selected area is valid
        if width < 10 or height < 10 or x < 0 or y < 0 or x + width > image.shape[1] or y + height > image.shape[0]:
            return HttpResponseBadRequest("Invalid selection area. Please select a larger area.")
        
        # Create a mask
        mask = np.zeros(image.shape[:2], np.uint8)
        
        # Define the rectangle for the foreground
        rect = (x, y, width, height)
        
        # GrabCut operation
        try:
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)
            cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        except cv2.error as e:
            return HttpResponseBadRequest("Error processing image. Please try selecting a different area.")
        
        # Modify the mask
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        # Apply the mask
        result = image * mask2[:, :, np.newaxis]
        
        # Create a white background
        background = np.ones_like(image, np.uint8) * 255
        background = background * (1 - mask2[:, :, np.newaxis])
        
        # Combine the result with the white background
        final_result = result + background
        
        # Save the processed image
        cv2.imwrite(product.image.path, final_result)
        
        return redirect('product_list')

    return redirect('product_list')

def cart(request):
    orders = Order.objects.filter(user=request.user)
    total = sum(order.product.price * order.quantity for order in orders)
    return render(request, 'cart.html', {'orders': orders, 'total': total})

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Order.objects.create(user=request.user, product=product, quantity=1)
    return redirect('cart')


