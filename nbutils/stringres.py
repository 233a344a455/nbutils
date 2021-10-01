from pydantic import BaseSettings

FULL_SPACE = '　' # \u3000，全角空格

class StringRes(BaseSettings):

    EXPR_UNKNOWN_CMD = "<{sv_name}>: 未知命令: '{cmd}'\n\n{doc}"
    EXPR_CALL_SV_DIRECTLY = "<直接调用>"
    EXPR_NOT_AVAILABLE = "（无可用信息）"
    EXPR_NO_CMDS_IN_SV = "（无可用命令）"

    DOC_SERVICE_HELP = "【{name} 服务帮助】\n\n" \
                        "► 功能简述\n{desc}\n\n" \
                        "► 说明文档\n{doc}\n\n" \
                        "► 命令列表\n{cmds_list}\n\n"

    FORMAT_CMDS_LIST = FULL_SPACE + "➢ {cmd} {desc}"

Rstr = StringRes()