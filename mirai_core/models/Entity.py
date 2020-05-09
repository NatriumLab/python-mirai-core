from pydantic import BaseModel
from typing import Optional
from enum import Enum


class Friend(BaseModel):
    id: int
    nickname: str
    remark: Optional[str]

    def __repr__(self):
        return f"<Friend id={self.id} nickname='{self.nickname}' remark='{self.remark}'>"

    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'


class Permission(Enum):
    Member = "MEMBER"
    Administrator = "ADMINISTRATOR"
    Owner = "OWNER"


class Group(BaseModel):
    id: int
    name: str
    permission: Permission

    def __repr__(self):
        return f"<Group id={self.id} name='{self.name}' permission={self.permission.name}>"

    def get_avatar_url(self) -> str:
        return f'https://p.qlogo.cn/gh/{self.id}/{self.id}/'


class Member(BaseModel):
    id: int
    memberName: str
    permission: Permission
    group: Group

    def __repr__(self):
        return f"<Member id={self.id} group={self.group} permission={self.permission} group={self.group.id}>"

    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'


class MemberChangeableSetting(BaseModel):
    name: str
    specialTitle: str

    def modify(self, **kwargs):
        for i in ("name", "kwargs"):
            if i in kwargs:
                setattr(self, i, kwargs[i])
        return self


class GroupSetting(BaseModel):
    name: str
    announcement: str
    confessTalk: bool
    allowMemberInvite: bool
    autoApprove: bool
    anonymousChat: bool

    def modify(self, **kwargs):
        for i in ("name",
                  "announcement",
                  "confessTalk",
                  "allowMemberInvite",
                  "autoApprove",
                  "anonymousChat"
                  ):
            if i in kwargs:
                setattr(self, i, kwargs[i])
        return self
