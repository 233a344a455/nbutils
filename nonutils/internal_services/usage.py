from nonebot import Bot
from nonebot.adapters import Event

from nonutils.service import Service, services
from nonutils.stringres import Rstr

sv_usage = Service(name='help',
                   aliases={'usage', '帮助'},
                   desc='输出使用帮助',
                   hidden=True)

cmd_usage = sv_usage.on_command('')


@cmd_usage.handle()
async def _(bot: Bot, event: Event):
    sv_list = [Rstr.FORMAT_SV_LIST.format(sv=s.sv_name, desc=f'({s.desc})' if s.desc else '')
               for s in services.values() if not s.hidden]
    if sv_list:
        sv_list_str = '\n'.join(sv_list)
    else:
        sv_list_str = Rstr.EXPR_NO_AVAILABLE_SV

    args = event.get_message().extract_plain_text().split()
    # FIXME: handle cmd with space in cmd_name

    if not args:
        await cmd_usage.send(Rstr.MSG_MAIN_USAGE_DOC.format(sv_list=sv_list_str))
    else:
        if args[0] in services:
            sv = services[args[0]]
            if len(args) == 1:
                await cmd_usage.send(sv.get_usage_str())
            elif sv.get_command(args[1]):
                await cmd_usage.send(sv.get_command(args[1]).get_usage_str())
            else:
                await cmd_usage.send_failed(Rstr.MSG_UNKNOWN_CMD_IN_SV.format(sv=args[0], cmd=args[1]))
        else:
            await cmd_usage.send_failed(Rstr.MSG_UNKNOWN_SV.format(sv=args[0]))
