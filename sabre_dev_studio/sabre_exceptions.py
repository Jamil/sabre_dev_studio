# Base API Exception
class SabreDevStudioException(Exception):
    pass

# 400
class SabreErrorBadRequest(SabreDevStudioException):
    pass

# 401
class SabreErrorUnauthorized(SabreDevStudioException):
    pass

# 403
class SabreErrorForbidden(SabreDevStudioException):
    pass

# 404
class SabreErrorNotFound(SabreDevStudioException):
    pass

# 406
class SabreErrorNotAcceptable(SabreDevStudioException):
    pass

# 429
class SabreErrorRateLimited(SabreDevStudioException):
    pass

# 500
class SabreInternalServerError(SabreDevStudioException):
    pass

# 503
class SabreErrorServiceUnavailable(SabreDevStudioException):
    pass

# 504
class SabreErrorGatewayTimeout(SabreDevStudioException): 
    pass
