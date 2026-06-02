"""
URL routing configuration for the main e-food application.
Defines all URL patterns for customer and admin views.
"""

# Import Django path function for URL routing
from django.urls import path

# Import all views from this app
from . import views

# Import specific class-based views for explicit registration
from .views import (
    MenuListView,           # Display all menu items
    menuDetail,             # Display single item details
    add_to_cart,            # Add item to shopping cart
    get_cart_items,         # Display shopping cart
    order_item,             # Confirm and place order
    CartDeleteView,         # Remove item from cart
    order_details,          # Show order history
    admin_view,             # Admin delivered orders view
    item_list,              # Admin item list
    pending_orders,         # Admin pending orders
    ItemCreateView,         # Create new menu item
    ItemUpdateView,         # Edit menu item
    ItemDeleteView,         # Delete menu item
    update_status,          # Update order status
    add_reviews,            # Post a review
)

# Django app name for URL reversing
app_name = "main"

# URL pattern routing for all app views
urlpatterns = [
    # ===== CUSTOMER VIEWS =====
    
    # Home page - displays all menu items
    # URL: /
    path(
        '',                         # Root path
        MenuListView.as_view(),     # Class-based view
        name='home'                 # URL name for reversing
    ),
    
    # Single item detail page with reviews
    # URL: /dishes/<slug>/
    path(
        'dishes/<slug>', 
        views.menuDetail,           # Function-based view
        name='dishes'               # URL name for reversing
    ),
    
    # Add item to shopping cart
    # URL: /add-to-cart/<slug>/
    path(
        'add-to-cart/<slug>/',
        views.add_to_cart,          # Function-based view
        name='add-to-cart'          # URL name for reversing
    ),
    
    # View shopping cart
    # URL: /cart/
    path(
        'cart/',
        views.get_cart_items,       # Function-based view
        name='cart'                 # URL name for reversing
    ),
    
    # Remove item from shopping cart
    # URL: /remove-from-cart/<id>/
    path(
        'remove-from-cart/<int:pk>/',
        CartDeleteView.as_view(),   # Class-based view
        name='remove-from-cart'     # URL name for reversing
    ),
    
    # Place/confirm order from cart
    # URL: /ordered/
    path(
        'ordered/',
        views.order_item,           # Function-based view
        name='ordered'              # URL name for reversing
    ),
    
    # View order history and status
    # URL: /order_details/
    path(
        'order_details/',
        views.order_details,        # Function-based view
        name='order_details'        # URL name for reversing
    ),
    
    # Post a review for an item
    # URL: /postReview
    path(
        'postReview',
        views.add_reviews,          # Function-based view
        name='add_reviews'          # URL name for reversing
    ),
    
    # ===== ADMIN VIEWS =====
    
    # Admin dashboard with analytics
    # URL: /admin_dashboard/
    path(
        'admin_dashboard/',
        views.admin_dashboard,      # Function-based view
        name='admin_dashboard'      # URL name for reversing
    ),
    
    # Admin menu item management
    # URL: /item_list/
    path(
        'item_list/',
        views.item_list,            # Function-based view
        name='item_list'            # URL name for reversing
    ),
    
    # Create new menu item
    # URL: /item/new/
    path(
        'item/new/',
        ItemCreateView.as_view(),   # Class-based view
        name='item-create'          # URL name for reversing
    ),
    
    # Edit/update existing menu item
    # URL: /item-update/<slug>/
    path(
        'item-update/<slug>/',
        ItemUpdateView.as_view(),   # Class-based view
        name='item-update'          # URL name for reversing
    ),
    
    # Delete menu item
    # URL: /item-delete/<slug>/
    path(
        'item-delete/<slug>/',
        ItemDeleteView.as_view(),   # Class-based view
        name='item-delete'          # URL name for reversing
    ),
    
    # View pending orders (not delivered)
    # URL: /pending_orders/
    path(
        'pending_orders/',
        views.pending_orders,       # Function-based view
        name='pending_orders'       # URL name for reversing
    ),
    
    # Update order delivery status
    # URL: /update_status/<id>
    path(
        'update_status/<int:pk>',
        views.update_status,        # Function-based view
        name='update_status'        # URL name for reversing
    ),
    
    # View completed/delivered orders
    # URL: /admin_view/
    path(
        'admin_view/',
        views.admin_view,           # Function-based view
        name='admin_view'           # URL name for reversing
    ),
]

