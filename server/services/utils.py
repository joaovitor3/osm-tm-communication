class InvalidMediaWikiToken(Exception):
    """
    Custom exception to indicate that mediawiki API Token is invalid
    """
    pass


class PageNotFoundError(Exception):
    """
    Custom exception to indicate that a page does not exists in the mediawiki
    """
    pass


class ExistingPageError(Exception):
    """
    Custom exception to indicate that a page already exists in the mediawiki
    """
    pass
