from fastapi import APIRouter, Depends
from app.session import get_session
from app.cache import get_cache
from app.schemas.user_schemas import UserRegisterRequest
from app.models.user_models import User
from app.helpers.jwt_helper import JWTHelper
from app.helpers.mfa_helper import MFAHelper
from app.managers.entity_manager import EntityManager
from app.logger import log

router = APIRouter()


@router.post('/user', tags=['users'])
async def user_register(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(UserRegisterRequest)):
    mfa_key = MFAHelper.create_mfa_key()
    jti = JWTHelper.create_jti()
    user = User(schema.user_login, schema.user_pass, schema.first_name, schema.last_name, mfa_key, jti)

    em = EntityManager(session, log)
    await em.insert(user, commit=True)
    return {"res": "user"}
