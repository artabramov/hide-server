from fastapi import APIRouter, Depends
from app.session import get_session
from app.cache import get_cache
from app.schemas.user_schemas import UserRegisterRequest
from app.models.user_models import User

router = APIRouter()


@router.post('/user', tags=['users'])
async def user_register(session = Depends(get_session), cache = Depends(get_cache), schema = Depends(UserRegisterRequest)):
    user = User(schema.user_login, schema.user_pass, schema.first_name, schema.last_name)
    return {"res": "user"}
