from nonebot import Bot
from nonebot.adapters import Event

from nonutils.command import Command, cmdmgr
from nonutils.stringres import Rstr


usage_cmd = Command('help', aliases={'usage'}, desc='查看帮助',
                    usage='查看帮助信息。')


@usage_cmd.handle()
async def _(bot: Bot, event: Event):

    cmd_list = [
        Rstr.FORMAT_CMDS_LIST.format(
            cmd=c.cmd,
            desc=(c.desc if c.desc else '')
        )
        for c in cmdmgr.get_all_cmds(exclude_hidden_cmd=True)
    ]

    if cmd_list:
        cmd_list_str = '\n'.join(cmd_list).strip()
    else:
        cmd_list_str = Rstr.EXPR_NO_CMDS

    arg = event.get_message().extract_plain_text()

    if not arg:
        await usage_cmd.send(Rstr.MSG_MAIN_USAGE_DOC.format(cmd_list=cmd_list_str))
    else:
        cmd_obj = cmdmgr.fetch_cmd(arg)
        if cmd_obj:
            await usage_cmd.send(Rstr.MSG_CMD_USAGE.format(cmd=arg, usage=cmd_obj.get_usage_str()))
        else:
            await usage_cmd.send_failure(Rstr.MSG_UNKNOWN_CMD.format(cmd=arg))
