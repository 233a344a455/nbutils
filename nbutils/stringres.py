from pydantic import BaseSettings

class StringRes(BaseSettings):
    UNKNOWN_CMD_REP = "<{sv_name}>: 未知命令: '{cmd}'"

Rstring = StringRes()