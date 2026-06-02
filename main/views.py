"""
Main views module for the E-Food ordering system.
Contains all view logic for displaying menu, handling cart, orders, reviews, and admin dashboard.
"""

# Import Django shortcut functions for rendering and redirecting
from django.shortcuts import render, get_object_or_404, redirect

# Import database models
from .models import Item, CartItems, Reviews

# Import Django messaging framework for user feedback
from django.contrib import messages

# Import Django class-based views
from django.views.generic import (
    ListView,      # For displaying lists of objects
    DetailView,    # For displaying single object details
    CreateView,    # For creating new objects
    UpdateView,    # For updating existing objects
    DeleteView,    # For deleting objects
)

# Import timezone utilities for timestamps
from django.utils import timezone

# Import authentication decorators
from django.contrib.auth.decorators import login_required

# Import authentication mixins for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Import custom decorators from this app
from .decorators import *

# Import database aggregation functions
from django.db.models import Sum


"""
============================
CUSTOMER VIEWING VIEWS
============================
"""

class MenuListView(ListView):
    """
    View for displaying all available menu items on the home page.
    
    Attributes:
        model: Database model to query (Item)
        template_name: HTML template to render
        context_object_name: Variable name used in template for items list
    """
    # Specify the model to query
    model = Item
    
    # Template to render with the data
    template_name = 'main/home.html'
    
    # Name of variable in template context for items
    context_object_name = 'menu_items'


def menuDetail(request, slug):
    """
    Display detailed information about a specific menu item.
    Shows item details, price, reviews, and review contribution form.
    
    Args:
        request: HTTP request object
        slug: URL slug identifier for the item
    
    Returns:
        Rendered template with item and reviews data
    """
    # Query the item by slug, return None if not found
    item = Item.objects.filter(slug=slug).first()
    
    # Get last 7 reviews for this item, sorted by newest first
    reviews = Reviews.objects.filter(rslug=slug).order_by('-id')[:7]
    
    # Prepare data to send to template
    context = {
        'item': item,           # The menu item object
        'reviews': reviews,     # List of reviews for this item
    }
    
    # Render the dish detail template with context
    return render(request, 'main/dishes.html', context)


@login_required
def add_reviews(request):
    """
    Handle review submission for a menu item.
    Only allows POST requests and requires user to be logged in.
    
    Args:
        request: HTTP request object containing review data
    
    Returns:
        Redirect to the item detail page
    """
    # Check if request method is POST (form submission)
    if request.method == "POST":
        # Get current logged-in user
        user = request.user
        
        # Get the item slug from form data
        rslug = request.POST.get("rslug")
        
        # Query the item from database
        item = Item.objects.get(slug=rslug)
        
        # Get review text from form data
        review = request.POST.get("review")

        # Create new review object
        reviews = Reviews(
            user=user,              # Associate review with current user
            item=item,              # Link review to the item
            review=review,          # Store review text
            rslug=rslug             # Store item slug for reference
        )
        
        # Save review to database
        reviews.save()
        
        # Display success message to user
        messages.success(request, "Thank you for reviewing this product!")
    
    # Redirect back to the item detail page
    return redirect(f"/dishes/{item.slug}")


"""
============================
ADMIN MENU ITEM MANAGEMENT VIEWS
============================
"""

class ItemCreateView(LoginRequiredMixin, CreateView):
    """
    Admin view for creating new menu items.
    Requires user to be logged in.
    
    Attributes:
        model: The Item model to create
        fields: Form fields to display
    """
    # Specify the model for creation
    model = Item
    
    # Fields to display in the form
    fields = [
        'title',            # Item name
        'image',            # Item image upload
        'description',      # Item description
        'price',            # Item price
        'pieces',           # Quantity per order
        'instructions',     # Special instructions
        'labels',           # Item category/label
        'label_colour',     # Color for label badge
        'slug'              # URL slug identifier
    ]

    def form_valid(self, form):
        """
        Process valid form submission.
        Automatically sets the creator to the current user.
        
        Args:
            form: Validated form object
            
        Returns:
            Result of parent form_valid method
        """
        # Set the created_by field to current user
        form.instance.created_by = self.request.user
        
        # Call parent class form_valid method
        return super().form_valid(form)


class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Admin view for editing menu items.
    Only allows the original creator to edit.
    
    Attributes:
        model: The Item model to update
        fields: Form fields to display
    """
    # Specify the model for updating
    model = Item
    
    # Fields to display in the form
    fields = [
        'title',            # Item name
        'image',            # Item image
        'description',      # Item description
        'price',            # Item price
        'pieces',           # Quantity per order
        'instructions',     # Special instructions
        'labels',           # Item category/label
        'label_colour',     # Color for label badge
        'slug'              # URL slug identifier
    ]

    def form_valid(self, form):
        """
        Process valid form submission for update.
        
        Args:
            form: Validated form object
            
        Returns:
            Result of parent form_valid method
        """
        # Set the created_by field to current user
        form.instance.created_by = self.request.user
        
        # Call parent class form_valid method
        return super().form_valid(form)

    def test_func(self):
        """
        Check if user has permission to update this item.
        User must be the original creator.
        
        Returns:
            Boolean indicating if update is allowed
        """
        # Get the item being updated
        item = self.get_object()
        
        # Allow update only if user is the creator
        if self.request.user == item.created_by:
            return True
        
        # Deny update if not creator
        return False


class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Admin view for deleting menu items.
    Only allows the original creator to delete.
    
    Attributes:
        model: The Item model to delete
        success_url: URL to redirect to after deletion
    """
    # Specify the model for deletion
    model = Item
    
    # URL to redirect to after successful deletion
    success_url = '/item_list'

    def test_func(self):
        """
        Check if user has permission to delete this item.
        User must be the original creator.
        
        Returns:
            Boolean indicating if deletion is allowed
        """
        # Get the item being deleted
        item = self.get_object()
        
        # Allow deletion only if user is the creator
        if self.request.user == item.created_by:
            return True
        
        # Deny deletion if not creator
        return False


"""
============================
SHOPPING CART VIEWS
============================
"""

@login_required
def add_to_cart(request, slug):
    """
    Add a menu item to the user's cart.
    
    Args:
        request: HTTP request object
        slug: URL slug identifier for the item to add
    
    Returns:
        Redirect to cart page
    """
    # Query the item from database, return 404 if not found
    item = get_object_or_404(Item, slug=slug)
    
    # Create new cart item entry
    cart_item = CartItems.objects.create(
        item=item,                  # Link to the menu item
        user=request.user,          # Associate with current user
        ordered=False,              # Mark as not yet ordered
    )
    
    # Display info message to user
    messages.info(request, "Added to Cart! Continue Shopping!")
    
    # Redirect to cart page
    return redirect("main:cart")


@login_required
def get_cart_items(request):
    """
    Display all items in the user's shopping cart.
    Calculates totals, count, and pieces.
    
    Args:
        request: HTTP request object
    
    Returns:
        Rendered cart template with cart data
    """
    # Query all unordered cart items for current user
    cart_items = CartItems.objects.filter(
        user=request.user,      # For current user
        ordered=False           # Not yet ordered
    )
    
    # Calculate total bill by summing item prices
    bill = cart_items.aggregate(Sum('item__price'))
    
    # Calculate number of items
    number = cart_items.aggregate(Sum('quantity'))
    
    # Calculate total pieces available
    pieces = cart_items.aggregate(Sum('item__pieces'))
    
    # Extract total price from aggregation result
    total = bill.get("item__price__sum")
    
    # Extract item count from aggregation result
    count = number.get("quantity__sum")
    
    # Extract pieces total from aggregation result
    total_pieces = pieces.get("item__pieces__sum")
    
    # Prepare context data for template
    context = {
        'cart_items': cart_items,       # All cart items
        'total': total,                 # Total price
        'count': count,                 # Number of items
        'total_pieces': total_pieces    # Total quantity
    }
    
    # Render cart template with context
    return render(request, 'main/cart.html', context)


class CartDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View for removing items from shopping cart.
    Only allows the user who owns the cart item to delete it.
    
    Attributes:
        model: The CartItems model
        success_url: URL to redirect to after deletion
    """
    # Specify the model for deletion
    model = CartItems
    
    # URL to redirect to after successful deletion
    success_url = '/cart'

    def test_func(self):
        """
        Check if user has permission to delete this cart item.
        User must own the cart item.
        
        Returns:
            Boolean indicating if deletion is allowed
        """
        # Get the cart item being deleted
        cart = self.get_object()
        
        # Allow deletion only if user owns the cart item
        if self.request.user == cart.user:
            return True
        
        # Deny deletion if not the owner
        return False


"""
============================
ORDER MANAGEMENT VIEWS
============================
"""

@login_required
def order_item(request):
    """
    Convert shopping cart items to a confirmed order.
    Sets ordered status to True and records order date.
    
    Args:
        request: HTTP request object
    
    Returns:
        Redirect to order details page
    """
    # Query all unordered cart items for current user
    cart_items = CartItems.objects.filter(
        user=request.user,      # For current user
        ordered=False           # Not yet ordered
    )
    
    # Get current date and time
    ordered_date = timezone.now()
    
    # Update all cart items as ordered with timestamp
    cart_items.update(
        ordered=True,               # Mark as ordered
        ordered_date=ordered_date   # Record order date
    )
    
    # Display info message to user
    messages.info(request, "Item Ordered")
    
    # Redirect to order confirmation/details page
    return redirect("main:order_details")


@login_required
def order_details(request):
    """
    Display user's order history with pending and delivered orders.
    Shows order summary with totals.
    
    Args:
        request: HTTP request object
    
    Returns:
        Rendered order details template
    """
    # Query pending orders (status="Active")
    items = CartItems.objects.filter(
        user=request.user,          # For current user
        ordered=True,               # Is ordered
        status="Active"             # Still pending
    ).order_by('-ordered_date')     # Newest first
    
    # Query delivered orders
    cart_items = CartItems.objects.filter(
        user=request.user,          # For current user
        ordered=True,               # Is ordered
        status="Delivered"          # Has been delivered
    ).order_by('-ordered_date')     # Newest first
    
    # Calculate total bill for pending orders
    bill = items.aggregate(Sum('item__price'))
    
    # Calculate item count for pending orders
    number = items.aggregate(Sum('quantity'))
    
    # Calculate pieces total for pending orders
    pieces = items.aggregate(Sum('item__pieces'))
    
    # Extract total price
    total = bill.get("item__price__sum")
    
    # Extract item count
    count = number.get("quantity__sum")
    
    # Extract pieces total
    total_pieces = pieces.get("item__pieces__sum")
    
    # Prepare context data
    context = {
        'items': items,                 # Pending orders
        'cart_items': cart_items,       # Delivered orders
        'total': total,                 # Total for pending
        'count': count,                 # Item count for pending
        'total_pieces': total_pieces    # Quantity for pending
    }
    
    # Render order details template
    return render(request, 'main/order_details.html', context)


"""
============================
ADMIN DASHBOARD VIEWS
============================
"""

@login_required(login_url='/accounts/login/')
@admin_required
def admin_view(request):
    """
    Admin view showing all delivered orders for items they created.
    
    Args:
        request: HTTP request object
    
    Returns:
        Rendered admin view template with delivered orders
    """
    # Query all delivered orders for items created by this admin
    cart_items = CartItems.objects.filter(
        item__created_by=request.user,  # Items created by admin
        ordered=True,                   # Is ordered
        status="Delivered"              # Has been delivered
    ).order_by('-ordered_date')         # Newest first
    
    # Prepare context
    context = {
        'cart_items': cart_items,  # All delivered orders
    }
    
    # Render admin view template
    return render(request, 'main/admin_view.html', context)


@login_required(login_url='/accounts/login/')
@admin_required
def item_list(request):
    """
    Admin view displaying all menu items created by this admin.
    
    Args:
        request: HTTP request object
    
    Returns:
        Rendered item list template with admin's items
    """
    # Query all items created by this admin
    items = Item.objects.filter(created_by=request.user)
    
    # Prepare context
    context = {
        'items': items  # All items created by this admin
    }
    
    # Render item list template
    return render(request, 'main/item_list.html', context)


@login_required
@admin_required
def update_status(request, pk):
    """
    Admin view for updating order status (mark as delivered).
    
    Args:
        request: HTTP request object containing status data
        pk: Primary key of the cart item to update
    
    Returns:
        Rendered pending orders template
    """
    # Check if request is POST (form submission)
    if request.method == 'POST':
        # Get new status from form data
        status = request.POST['status']
    
    # Query the specific order to update
    cart_items = CartItems.objects.filter(
        item__created_by=request.user,  # Created by this admin
        ordered=True,                   # Is ordered
        status="Active",                # Currently pending
        pk=pk                           # Specific order ID
    )
    
    # Get current date and time for delivery timestamp
    delivery_date = timezone.now()
    
    # If status is being marked as delivered
    if status == 'Delivered':
        # Update the order status and delivery date
        cart_items.update(
            status=status,              # Change status to Delivered
            delivery_date=delivery_date # Record delivery date
        )
    
    # Render pending orders template
    return render(request, 'main/pending_orders.html')


@login_required(login_url='/accounts/login/')
@admin_required
def pending_orders(request):
    """
    Admin view displaying all pending orders for items they created.
    
    Args:
        request: HTTP request object
    
    Returns:
        Rendered pending orders template
    """
    # Query all pending orders for items created by this admin
    items = CartItems.objects.filter(
        item__created_by=request.user,  # Items created by admin
        ordered=True,                   # Is ordered
        status="Active"                 # Still pending
    ).order_by('-ordered_date')         # Newest first
    
    # Prepare context
    context = {
        'items': items,  # All pending orders
    }
    
    # Render pending orders template
    return render(request, 'main/pending_orders.html', context)


@login_required(login_url='/accounts/login/')
@admin_required
def admin_dashboard(request):
    """
    Main admin dashboard showing business statistics and metrics.
    Displays pending/completed orders count, revenue, and item sales breakdown.
    
    Args:
        request: HTTP request object
    
    Returns:
        Rendered admin dashboard template with analytics
    """
    # Query all orders for items created by this admin
    cart_items = CartItems.objects.filter(
        item__created_by=request.user,  # Items created by admin
        ordered=True                    # Is ordered
    )
    
    # Count pending orders (not yet delivered)
    pending_total = CartItems.objects.filter(
        item__created_by=request.user,  # Items created by admin
        ordered=True,                   # Is ordered
        status="Active"                 # Still pending
    ).count()
    
    # Count completed/delivered orders
    completed_total = CartItems.objects.filter(
        item__created_by=request.user,  # Items created by admin
        ordered=True,                   # Is ordered
        status="Delivered"              # Has been delivered
    ).count()
    
    # Count orders for item with ID 3
    count1 = CartItems.objects.filter(
        item__created_by=request.user,  # Items created by admin
        ordered=True,                   # Is ordered
        item="3"                        # Specific item ID
    ).count()
    
    # Count orders for item with ID 4
    count2 = CartItems.objects.filter(
        item__created_by=request.user,  # Items created by admin
        ordered=True,                   # Is ordered
        item="4"                        # Specific item ID
    ).count()
    
    # Count orders for item with ID 5
    count3 = CartItems.objects.filter(
        item__created_by=request.user,  # Items created by admin
        ordered=True,                   # Is ordered
        item="5"                        # Specific item ID
    ).count()
    
    # Calculate total revenue (sum of all item prices in orders)
    total = CartItems.objects.filter(
        item__created_by=request.user,  # Items created by admin
        ordered=True                    # Is ordered
    ).aggregate(Sum('item__price'))
    
    # Extract total revenue from aggregation result
    income = total.get("item__price__sum")
    
    # Prepare context with all analytics
    context = {
        'pending_total': pending_total,     # Number of pending orders
        'completed_total': completed_total, # Number of delivered orders
        'income': income,                   # Total revenue
        'count1': count1,                   # Sales for item 3
        'count2': count2,                   # Sales for item 4
        'count3': count3,                   # Sales for item 5
    }
    
    # Render admin dashboard template with analytics
    return render(request, 'main/admin_dashboard.html', context)

