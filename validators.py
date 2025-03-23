import validators

def is_valid_url(url):
    if not url:
        return False
    return validators.url(url)

