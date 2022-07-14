class UserUUIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # # Code to be executed for each request before
        # # the view (and later middleware) are called.
        # print('--process_request--')

        response = self.get_response(request)
        if request.user.is_authenticated:
            response['X-Remote-User-Uuid'] = request.user.uuid

        # # Code to be executed for each request/response after
        # # the view is called.
        # print('--process_response')

        return response

    # def process_view(self, view_func, *view_args, **view_kwargs):
    #     print('--process_view')