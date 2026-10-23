from datetime import datetime

from pydantic import BaseModel


# 响应模型用于 Android 端生成类型及 OpenAPI 契约。
class AppMembershipInfo(BaseModel):
    level: str
    is_active: bool
    expires_at: datetime | None


class AppProfile(BaseModel):
    id: str
    phone: str
    nickname: str
    avatar_url: str
    membership: AppMembershipInfo
