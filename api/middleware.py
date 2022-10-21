class CorsMiddleware:
    # def process_request(self, req, resp):
    #     pass

    # def process_resource(self, req, resp, resource, params):
    #     pass

    def process_resource(self, req, resp, resource, params):
        print(req.path)
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        resp.set_header('Access-Control-Expose-Headers', 'Content-Disposition')
        # resp.set_header('Vary', 'Origin')

        methods = []
        if hasattr(resource, 'on_get'):
            methods.append('GET')
        if hasattr(resource, 'on_post'):
            methods.append('POST')
        if hasattr(resource, 'on_put'):
            methods.append('PUT')
        if hasattr(resource, 'on_delete'):
            methods.append('DELETE')

        resp.set_header('Access-Control-Allow-Methods', ', '.join(methods))
