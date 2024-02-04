"""JWT helper."""

import random
import string
import jwt
import time
from app.config import get_cfg

JTI_LENGTH = 24

cfg = get_cfg()


class JWTHelper:
    """JWT mixin."""

    @staticmethod
    def create_jti() -> str:
        """Create JWT identifier."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=JTI_LENGTH))

    @staticmethod
    def encode_token(user_id: int, user_role: str, user_login: str, jti: str, exp: int=None) -> str:
        """Encode user data into JWT token."""
        payload = {
            'user_id': user_id,
            'user_role': user_role,
            'user_login': user_login,
            'jti': jti,
            'iat': int(time.time()),
        }
        if exp:
            payload['exp'] = int(exp)

        return jwt.encode(payload, cfg.APP_JWT_SECRET, algorithm=cfg.APP_JWT_ALGORITHM)

    @staticmethod
    def decode_token(jwt_token: str) -> dict:
        """Decode user data from JWT token."""
        payload = jwt.decode(jwt_token, cfg.APP_JWT_SECRET, algorithms=cfg.APP_JWT_ALGORITHM)
        res = {
            'user_id': payload['user_id'],
            'user_role': payload['user_role'],
            'user_login': payload['user_login'],
            'iat': payload['iat'],
            'jti': payload['jti'],
        }
        if 'exp' in payload:
            res['exp'] = payload['exp']
        return res