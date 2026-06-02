"""
Custom middleware for development environment.
Adds cache control headers to prevent browser caching of responses.
"""


class NoCacheMiddleware:
    """
    Middleware that adds HTTP headers to prevent browser caching.
    
    This ensures that every page refresh retrieves fresh content from the server,
    eliminating delays when code is updated. Useful for development environments.
    
    Added headers:
    - Cache-Control: no-cache, no-store, must-revalidate, max-age=0
    - Pragma: no-cache
    - Expires: 0
    """
    
    def __init__(self, get_response):
        """
        Initialize middleware with Django's get_response callable.
        
        Args:
            get_response: Django's request/response handler
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process request and add cache control headers to response.
        
        Args:
            request: HTTP request object
            
        Returns:
            HTTP response with cache control headers added
        """
        # Get response from Django
        response = self.get_response(request)
        
        # Add cache control headers to disable browser caching
        # This prevents stale content from being displayed after updates
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        
        # Pragma header for HTTP/1.0 backwards compatibility
        response['Pragma'] = 'no-cache'
        
        # Expires header set to past date
        response['Expires'] = '0'
        
        # Return response with headers
        return response
