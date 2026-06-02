"""
Django forms for the E-Food application.
Contains model forms for menu items and other entities.

Note: This file is currently not in active use as the views
use direct model field exposure via Django's generic views.
The forms below are kept for reference and future use.
"""

# Import Django forms module
from django import forms

# Import Item model
from .models import Item


class AddForm(forms.ModelForm):
    """
    Model form for adding/editing menu items.
    Currently not in use - ItemCreateView and ItemUpdateView
    define fields directly instead of using this form.
    
    Can be used in the future for enhanced form handling.
    """
    
    class Meta:
        """
        Meta class to configure the form.
        
        Attributes:
            model: The model this form is based on
            fields: Which fields to include in the form
        """
        # Specify the model to create form from
        model = Item
        
        # Fields to include in the form
        fields = (
            'created_by',           # Admin/creator of the item
            'title',                # Item name
            'image',                # Item image
            'description',          # Item description
            'price',                # Item price
            'pieces',               # Quantity per order
            'instructions',         # Special instructions
            'labels',               # Category label
            'label_colour',         # Label badge color
            'slug'                  # URL identifier
        )
