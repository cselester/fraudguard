# Simple fraud detection logic
def get_device_info(request):
    """Extracts device information from request headers"""
    user_agent = request.headers.get("User-Agent", "Unknown")
    return user_agent
