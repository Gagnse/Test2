from flask import session, request, url_for
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse


def set_toast(message, toast_type='info'):
    """
    Set a toast message in the session to be displayed on the next page load

    Args:
        message (str): The message to display
        toast_type (str): The type of toast ('success', 'error', 'info', 'warning')
    """
    session['toast_message'] = message
    session['toast_type'] = toast_type


def redirect_with_toast(url, message, toast_type='info'):
    """
    Add toast parameters to a URL for client-side toast display

    Args:
        url (str): The URL to redirect to
        message (str): The message to display
        toast_type (str): The type of toast ('success', 'error', 'info', 'warning')

    Returns:
        str: URL with toast parameters
    """
    # Parse the URL
    parsed_url = urlparse(url)

    # Get the existing query parameters
    query_params = parse_qs(parsed_url.query)

    # Add toast parameters
    query_params['toast_message'] = [message]
    query_params['toast_type'] = [toast_type]

    # Rebuild the query string
    new_query = urlencode(query_params, doseq=True)

    # Rebuild the URL with the new query string
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))

    return new_url