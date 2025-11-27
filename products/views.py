from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from .models import Product, Category, Review, Wishlist
from .forms import ProductForm, ProductSearchForm, ReviewForm
from accounts.views import track_user_activity


class ProductListView(ListView):
    """
    Product List View - Class-Based View
    """
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'seller')
        
        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        # Track user activity
        if self.request.user.is_authenticated:
            track_user_activity(self.request, 'Product List')
        
        return context


class ProductDetailView(DetailView):
    """
    Product Detail View - Class-Based View
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Increment view count
        product.views_count += 1
        product.save(update_fields=['views_count'])
        
        # Get reviews
        context['reviews'] = product.reviews.all().order_by('-created_at')
        context['review_form'] = ReviewForm()
        
        # Check if user has wishlist item
        if self.request.user.is_authenticated:
            context['in_wishlist'] = Wishlist.objects.filter(
                user=self.request.user, 
                product=product
            ).exists()
            
            # Track user activity
            track_user_activity(self.request, f'Product: {product.name}')
        
        # Related products
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        
        return context


def product_search_view(request):
    """
    Product Search View with Filters
    """
    form = ProductSearchForm(request.GET or None)
    products = Product.objects.filter(is_active=True)
    
    if form.is_valid():
        # Search by query
        query = form.cleaned_data.get('query')
        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )
        
        # Filter by category
        category = form.cleaned_data.get('category')
        if category:
            products = products.filter(category=category)
        
        # Filter by minimum eco score
        min_eco_score = form.cleaned_data.get('min_eco_score')
        if min_eco_score:
            products = products.filter(eco_score__gte=min_eco_score)
        
        # Filter by maximum price
        max_price = form.cleaned_data.get('max_price')
        if max_price:
            products = products.filter(price__lte=max_price)
    
    # Track user activity
    if request.user.is_authenticated:
        track_user_activity(request, 'Product Search')
    
    context = {
        'form': form,
        'products': products,
        'search_query': request.GET.get('query', ''),
        'categories': Category.objects.all(),
    }
    return render(request, 'products/search_results.html', context)


class CategoryListView(ListView):
    """
    Category List View
    """
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'


@login_required
def add_to_wishlist(request, product_id):
    """
    Add/Remove product from wishlist
    """
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'{product.name} added to wishlist!')
    else:
        wishlist_item.delete()
        messages.info(request, f'{product.name} removed from wishlist!')
    
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))


@login_required
def wishlist_view(request):
    """
    User Wishlist View
    """
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    # Track user activity
    track_user_activity(request, 'Wishlist')
    
    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'products/wishlist.html', context)


@login_required
def add_review(request, product_id):
    """
    Add Product Review
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            
            # Check if user has purchased this product
            from orders.models import OrderItem
            has_purchased = OrderItem.objects.filter(
                order__user=request.user,
                product=product
            ).exists()
            review.is_verified_purchase = has_purchased
            
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('products:product_detail', slug=product.slug)
    
    return redirect('products:product_detail', slug=product.slug)


@login_required
def product_create_view(request):
    """
    Create Product (For Sellers)
    """
    if not request.user.is_seller:
        messages.error(request, 'Only sellers can create products!')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Product created successfully!')
            return redirect('products:product_detail', slug=product.slug)
    else:
        form = ProductForm()
    
    context = {'form': form}
    return render(request, 'products/product_form.html', context)


@login_required
def product_update_view(request, slug):
    """
    Update Product (For Sellers)
    """
    product = get_object_or_404(Product, slug=slug, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products:product_detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)
    
    context = {'form': form, 'product': product}
    return render(request, 'products/product_form.html', context)

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f'{product.name} removed from wishlist!')
    return redirect('products:wishlist')