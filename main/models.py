"""
Database models for the E-Food ordering system.
Defines Item, Reviews, and CartItems models.
"""

# Import Django model base class
from django.db import models

# Import Django settings for custom configurations
from django.conf import settings

# Import reverse URL resolution
from django.shortcuts import reverse

# Import timezone utilities for timestamps
from django.utils import timezone

# Import Django built-in User model for authentication
from django.contrib.auth.models import User


"""
============================
ITEM MODEL
============================
Represents a menu item that can be ordered from the restaurant.
Each item has a creator (admin/restaurant owner).
"""
class Item(models.Model):
    """
    Menu item model representing a dish/food item for sale.
    
    Attributes:
        title: Name of the dish
        description: Brief description of the item
        price: Cost of the item
        pieces: Default quantity/pieces per order
        instructions: Special instructions or variations
        image: Image file for the item
        labels: Category/special label (BestSeller, New, Spicy)
        label_colour: Badge color for the label
        slug: URL-friendly unique identifier
        created_by: The admin/owner who created this item
    """
    
    # Label choices for menu items
    LABELS = (
        ('BestSeller', 'BestSeller'),   # Best selling item
        ('New', 'New'),                   # Newly added item
        ('Spicy🔥', 'Spicy🔥'),         # Spicy item with emoji
    )
    
    # Badge color choices for labels
    LABEL_COLOUR = (
        ('danger', 'danger'),     # Red color for urgent/spicy
        ('success', 'success'),   # Green color for bestseller
        ('primary', 'primary'),   # Blue color for primary
        ('info', 'info')          # Light blue for info
    )
    
    # Item title - required field
    title = models.CharField(
        max_length=150,         # Maximum 150 characters
        help_text="Name of the menu item"
    )
    
    # Item description - optional field
    description = models.CharField(
        max_length=250,         # Maximum 250 characters
        blank=True              # Optional field
    )
    
    # Item price - stored as float for decimal precision
    price = models.FloatField(
        help_text="Price of the item in Ksh"
    )
    
    # Number of pieces/quantity included per standard order
    pieces = models.IntegerField(
        default=6              # Default 6 pieces per order
    )
    
    # Special instructions or variations for the item
    instructions = models.CharField(
        max_length=250,                      # Maximum 250 characters
        default="Jain Option Available"      # Default instructions
    )
    
    # Item image/photo file
    image = models.ImageField(
        default='default.png',              # Default image if none provided
        upload_to='images/'                 # Save to images directory
    )
    
    # Label/category for the item
    labels = models.CharField(
        max_length=25,                  # Maximum 25 characters
        choices=LABELS,                 # Must be one of LABELS
        blank=True                      # Optional field
    )
    
    # Color for the label badge display
    label_colour = models.CharField(
        max_length=15,                  # Maximum 15 characters
        choices=LABEL_COLOUR,           # Must be one of LABEL_COLOUR
        blank=True                      # Optional field
    )
    
    # URL-friendly slug for item URLs
    slug = models.SlugField(
        default="sushi_name",   # Default slug
        unique=True             # Ensure each item has unique slug
    )
    
    # Foreign key to User model - admin who created this item
    created_by = models.ForeignKey(
        User,                           # Link to User model
        on_delete=models.CASCADE        # Delete item if user deleted
    )

    def __str__(self):
        """
        String representation of the Item model.
        
        Returns:
            Item title as string
        """
        # Return item title for display in admin interface
        return self.title

    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug from title.
        
        Ensures that each item has a unique, URL-friendly slug
        based on its title for use in URLs.
        """
        # Import slugify to convert title to URL-friendly format
        from django.utils.text import slugify
        
        # Auto-generate slug from title if not already set
        if not self.slug or self.slug == "sushi_name":
            # Convert title to lowercase and replace spaces with hyphens
            self.slug = slugify(self.title)
        
        # Call parent save method to save the instance
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Get the absolute URL for this item's detail page.
        
        Returns:
            URL path for viewing this item
        """
        # Generate URL to item detail page using slug
        return reverse("main:dishes", kwargs={
            'slug': self.slug    # Pass slug as URL parameter
        })
    
    def get_add_to_cart_url(self):
        """
        Get the URL for adding this item to cart.
        
        Returns:
            URL path for adding item to cart
        """
        # Generate URL to add-to-cart view using slug
        return reverse("main:add-to-cart", kwargs={
            'slug': self.slug    # Pass slug as URL parameter
        })

    def get_item_delete_url(self):
        """
        Get the URL for deleting this item (admin only).
        
        Returns:
            URL path for deleting this item
        """
        # Generate URL to item delete view using slug
        return reverse("main:item-delete", kwargs={
            'slug': self.slug    # Pass slug as URL parameter
        })

    def get_update_item_url(self):
        """
        Get the URL for updating this item (admin only).
        
        Returns:
            URL path for editing this item
        """
        # Generate URL to item update view using slug
        return reverse("main:item-update", kwargs={
            'slug': self.slug    # Pass slug as URL parameter
        })


"""
============================
REVIEWS MODEL
============================
Stores customer reviews for menu items.
"""
class Reviews(models.Model):
    """
    Customer review model for menu items.
    
    Attributes:
        user: The user who posted the review
        item: The menu item being reviewed
        rslug: Slug of the item (for quick reference)
        review: The review text content
        posted_on: Date when review was posted
    """
    
    # Foreign key to User model - who posted the review
    user = models.ForeignKey(
        User,                       # Link to User model
        on_delete=models.CASCADE    # Delete review if user deleted
    )
    
    # Foreign key to Item model - which item is being reviewed
    item = models.ForeignKey(
        Item,                       # Link to Item model
        on_delete=models.CASCADE    # Delete review if item deleted
    )
    
    # Slug of the item for quick lookups
    rslug = models.SlugField(
        help_text="Slug reference to the reviewed item"
    )
    
    # The actual review text content
    review = models.TextField(
        help_text="Customer's review text"
    )
    
    # Date when the review was posted
    posted_on = models.DateField(
        default=timezone.now        # Default to current date/time
    )

    class Meta:
        """Meta options for Reviews model"""
        # Singular name for the model
        verbose_name = 'Review'
        # Plural name for the model
        verbose_name_plural = 'Reviews'

    def __str__(self):
        """
        String representation of the Review model.
        
        Returns:
            Review text content as string
        """
        # Return review text for display in admin interface
        return self.review


"""
============================
CART ITEMS MODEL
============================
Represents items in shopping cart and order history.
"""
class CartItems(models.Model):
    """
    Cart and order items model.
    Tracks items in cart and order history with status.
    
    Attributes:
        user: The user who owns this cart/order item
        item: The menu item in the cart
        ordered: Whether this item has been ordered
        quantity: Number of this item in cart
        ordered_date: When the item was ordered
        status: Current status (Active/Delivered)
        delivery_date: When item was delivered
    """
    
    # Order status choices
    ORDER_STATUS = (
        ('Active', 'Active'),           # Order is being prepared
        ('Delivered', 'Delivered')      # Order has been delivered
    )
    
    # Foreign key to User model - who owns this cart item
    user = models.ForeignKey(
        User,                       # Link to User model
        on_delete=models.CASCADE    # Delete cart if user deleted
    )
    
    # Foreign key to Item model - which menu item
    item = models.ForeignKey(
        Item,                       # Link to Item model
        on_delete=models.CASCADE    # Delete cart item if item deleted
    )
    
    # Boolean flag indicating if this item has been ordered
    ordered = models.BooleanField(
        default=False               # Default is not ordered (in cart)
    )
    
    # Quantity of this item in the cart
    quantity = models.IntegerField(
        default=1                   # Default quantity is 1
    )
    
    # Date when the item was ordered
    ordered_date = models.DateField(
        default=timezone.now        # Default to current date/time
    )
    
    # Current status of the order (Active or Delivered)
    status = models.CharField(
        max_length=20,              # Maximum 20 characters
        choices=ORDER_STATUS,       # Must be one of ORDER_STATUS
        default='Active'            # Default status is Active
    )
    
    # Date when the item was delivered
    delivery_date = models.DateField(
        default=timezone.now        # Default to current date/time
    )

    class Meta:
        """Meta options for CartItems model"""
        # Singular name for the model
        verbose_name = 'Cart Item'
        # Plural name for the model
        verbose_name_plural = 'Cart Items'

    def __str__(self):
        """
        String representation of CartItem model.
        
        Returns:
            Item title as string
        """
        # Return the item title for display in admin interface
        return self.item.title
    
    def get_remove_from_cart_url(self):
        """
        Get the URL for removing this item from cart.
        
        Returns:
            URL path for removing this from cart
        """
        # Generate URL to remove-from-cart view using primary key
        return reverse("main:remove-from-cart", kwargs={
            'pk': self.pk       # Pass primary key as URL parameter
        })

    def update_status_url(self):
        """
        Get the URL for updating this order's status.
        
        Returns:
            URL path for updating order status
        """
        # Generate URL to update_status view using primary key
        return reverse("main:update_status", kwargs={
            'pk': self.pk       # Pass primary key as URL parameter
        })

    


