import time
from django.utils.http import cookie_date


class ReferMiddleware(object):
    def process_response(self, request, response):
        if not request.COOKIES.get('REFERRER', None):
            referrer = request.META.get('HTTP_REFERER', '')
            max_age = request.session.get_expiry_age()
            expires_time = time.time() + max_age
            expires = cookie_date(expires_time)
            response.set_cookie('REFERRER', referrer, max_age=max_age, expires=expires)
        return response
