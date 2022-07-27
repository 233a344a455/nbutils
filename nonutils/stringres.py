from pydantic import BaseSettings

FULL_SPACE = '　'  # \u3000，全角空格

EMOJI_WARNING = '⚠'
EMOJI_FAILED = '✘'
EMOJI_SUCCEED = '✔'
EMOJI_QUESTION = '�'


class StringRes(BaseSettings):
    MSG_UNKNOWN_CMD = "未知命令 '{cmd}'。\n" \
                      "请使用 '/help' 获取可用命令列表。"

    MSG_MAIN_USAGE_DOC = "使用帮助\n\n" \
                         "► 命令列表\n{cmd_list}\n\n" \
                         "► 使用说明\n" \
                         + FULL_SPACE + "» /help <命令>\n" \
                         + FULL_SPACE + "显示该命令的帮助文档。\n"

    MSG_CMD_USAGE = "'{cmd}' 命令帮助\n\n" \
                    "► 使用说明\n{usage}"

    MSG_CMD_WITH_SWITCH_USAGE = "'{cmd}' 命令帮助\n\n" \
                                "► 说明文档\n{doc}\n\n" \
                                "► 使用方式\n{switch_list}"

    EXPR_NOT_AVAILABLE = "（无可用信息）"
    EXPR_NO_CMDS = "（无可用命令）"

    FORMAT_CMDS_LIST = FULL_SPACE + "» {cmd}" + FULL_SPACE + "{desc}"
    FORMAT_SWITCHES_LIST = FULL_SPACE + "» {usage}"

    FORMAT_BASIC_MSG = " <{cmd}>: {msg}"  # {time} -> %H:%M
    FORMAT_SUCCESS_MSG = EMOJI_SUCCEED + FORMAT_BASIC_MSG
    FORMAT_FAILURE_MSG = EMOJI_FAILED + FORMAT_BASIC_MSG
    FORMAT_WARNING_MSG = EMOJI_WARNING + FORMAT_BASIC_MSG
    FORMAT_QUESTION_MSG = EMOJI_QUESTION + FORMAT_BASIC_MSG


Rstr = StringRes()
