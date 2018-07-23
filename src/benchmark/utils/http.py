

def get_lazy_request_browser(user_agent):
    """Lazy method to determine if user agent is MS Edge or not."""
    if 'edge' in user_agent.lower():
        return 'edge'
