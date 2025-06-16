from urllib.parse import urlparse, urlsplit


def get_item_id_from_item_url(url):
    parsed_url = urlparse(url)
    path_segments = urlsplit(parsed_url.path).path.strip('/').split('/')
    return path_segments[-1]

