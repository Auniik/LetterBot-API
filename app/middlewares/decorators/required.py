import inspect
from functools import wraps

from fastapi import Request

from app.core.response import Response
from app.utils.types.user_context import UserCtx, AuthMode, UserCtxType


def validate_user_ctx(**ctx_kwargs) -> callable:
    """
        Usage Example:
        ----------
        @validate_user_ctx(
            auth=AuthMode.REQUIRED,
            language=["EN", "TH", "MY", "KM", "ZH"],
            tel_type=["PREPAID", "POSTPAID"],
            brand=["TRUE", "DTAC"]
        )
        async def your_route_name(request: Request, user_ctx: UserCtxType):
            print(user_ctx.language)
            print(user_ctx.digital_id)

        ---------
        Parameters:
        ---------
        :param ctx_kwargs:
            - auth (AuthMode): [optional] Defines the authentication mode for the route.
                Values:
                    * AuthMode.REQUIRED - user must be logged in
                    * AuthMode.GUEST    - only guest users allowed (x-user-id = "guest")
                    * AuthMode.RELAXED  - both guests and logged-in users allowed (default)
            - language (List[str] | str): [optional] = ["EN", "TH", "MY", "KM", "ZH"]
            - tel_type (List[str] | str): [optional] (e.g., "PREPAID", "POSTPAID", "guest")
            - brand (List[str] | str): [optional]  = ["TVS", "TOL", "CVG", "TMH", "TRUE", "DTAC"]
        """
    constraints = UserCtx(**ctx_kwargs)
    allowed_languages = ["EN", "TH", "MY", "KM", "ZH"]
    allowed_tel_types = ["PREPAID", "POSTPAID"]
    allowed_brands = ['TVS', 'TOL', 'CVG', 'TMH', 'TRUE', 'DTAC']

    if not constraints.language:
        constraints.language = allowed_languages
    if not constraints.tel_type:
        constraints.tel_type = allowed_tel_types
    if not constraints.brand:
        constraints.brand = allowed_brands

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if not request:
                return Response.code(500, 'T-GBS-00907').send_technical_error(
                    error_message="Destination error, found HTTP status 500 - Internal Server Error",
                    error_description="Request not injected"
                )

            digital_id = request.headers.get("x-user-id")
            is_guest = digital_id == "guest" or digital_id is None
            auth_mode = constraints.auth or AuthMode.RELAXED

            if auth_mode == AuthMode.REQUIRED and (not digital_id or is_guest):
                return Response.code(403, "T-GBS-00403").send_technical_error(
                    error_message="Login required",
                    error_description="This route requires a logged-in user"
                )
            if auth_mode == AuthMode.GUEST and not is_guest:
                return Response.code(403, "T-GBS-00403").send_technical_error(
                    error_message="Only guests allowed"
                )
            if auth_mode == AuthMode.REQUIRED and not digital_id:
                return Response.code(401, "T-GBS-00401").send_technical_error(
                    error_message="Unauthorized",
                    error_description="User ID is missing"
                )

            # extract values
            language = request.headers.get("language", "").upper()
            tel_type = request.headers.get("x-user-type", "").upper()
            brand = request.headers.get("x-user-brand", "").upper()
            segment = request.headers.get("x-product-segment", "").upper() or None
            brand = "TRUE" if brand == "TMH" else brand
            brand = "CVG" if segment == "CVG" else brand
            platform = request.headers.get("platform", "WEB")
            version = request.headers.get("version", "1.0.0")
            is_child = request.headers.get("x-child-number") == "1"

            if language not in [x.upper() for x in constraints.language]:
                return Response.code(400, 'B-GBS-93000').send_error(
                    error_message="Language not supported",
                    error_description=f"Language must be one of {', '.join(constraints.language or allowed_languages)}"
                )

            if not is_guest:
                if tel_type not in [x.upper() for x in constraints.tel_type]:
                    return Response.code(400, 'B-GBS-93005').send_error(
                        error_message="Invalid tel type",
                        error_description=f"Tel type must be one of {', '.join(constraints.tel_type)}"
                    )
                if brand not in [brand.upper() for brand in constraints.brand]:
                    return Response.code(400, 'B-GBS-93004').send_error(
                        error_message="Invalid brand",
                        error_description=f"Brand must be one of {', '.join(constraints.brand)}"
                    )

            sig = inspect.signature(func)
            if 'user_ctx' in sig.parameters:
                user_ctx = UserCtx(
                    language=language.lower(),
                    platform=platform,
                    is_guest=is_guest,
                    version=version,
                    auth=auth_mode,
                    session_id=request.headers.get("sessionId", "NA"),
                    device_id=request.headers.get("deviceId", 'NA'),
                    source_system_id=request.headers.get("sourceSystemId", "TRUE"),
                )
                if not is_guest:
                    user_ctx.digital_id = digital_id
                    user_ctx.brand = brand
                    user_ctx.tel_type = tel_type
                    user_ctx.is_child = is_child
                    user_ctx.token = request.headers.get("Authorization")


                kwargs["user_ctx"] = user_ctx

            return await func(*args, **kwargs)

        return wrapper
    return decorator