from typing import Optional, Union, Tuple, Set, List, Dict

from loguru import logger
from nonebot.adapters import Bot, Event
from nonebot.handler import Handler
from nonebot.permission import Permission
from nonebot.typing import T_Handler

from nonutils.command import Command
from nonutils.stringres import Rstr


class Service:
    """服务类，用于命令组管理。

    服务(Service) 是一套命令管理工具，功能方面类似于 Nonebot 中的 command_group，而在管理方面类似于 (sub)plugin
    每一个 Service 都可以添加多个命令，在会话中通过以下方式激活：

        <command_start><sv_name|sv_aliases> <cmd|aliases> <args>

    如 /test_service test_cmd arg1 arg2，即可触发 test_service 的 test_cmd
    其中 sv_name 与 cmd 都可设置相应的 aliases

    可以通过 service.on_command 声明命令，用法同 nonebot.on_command
    设置 on_command 的 cmd 为 None，即声明 当服务被调用了未声明的命令 / 只输入服务名 时的处理方式

    Inspired by https://github.com/Kyomotoi/ATRI/blob/HEAD/ATRI/service.py
    """

    def __init__(self, name: str,
                 aliases: Optional[Set[str]] = None,
                 desc: Optional[str] = None,
                 doc: Optional[str] = None,
                 hidden: bool = False):

        self.sv_name = name
        self.sv_aliases = aliases
        self.desc = desc
        self._sv_prefix = {name} | (aliases or set())
        self.hidden = hidden

        self.sv_doc: str = doc.strip() if (doc is not None) else None

        self.cmds: Dict[str, Command] = {}

        # Handle a cmd assigned to the very service, but doesn't match any cmd declared in the service.
        _default_cmd = self.on_command(cmd=None, hidden=True)

        @_default_cmd.handle()
        async def _handle_default_cmd(bot: Bot, event: Event):
            if event.get_message():
                await _default_cmd.send_failed(
                    Rstr.MSG_UNKNOWN_CMD.format(sv=self.sv_name, cmd=event.get_message(),
                                                usage=self.get_usage_str()))
            else:
                await _default_cmd.send_failed(
                    Rstr.MSG_NO_CMD_INPUT.format(sv=self.sv_name, usage=self.get_usage_str())
                )

        if self.sv_name in services:
            raise ValueError(f"Duplicated sv '{self.sv_name}' is not allowed.")
        services[self.sv_name] = self

    def get_command(self, cmd_name: str) -> Optional[Command]:
        return self.cmds.get(cmd_name, None)

    def on_command(self,
                   cmd: Optional[str] = None, aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
                   desc: Optional[str] = None, doc: Optional[str] = None,
                   permission: Optional[Permission] = None,
                   handlers: Optional[List[Union[T_Handler, Handler]]] = None,
                   hidden: bool = False,
                   **kwargs) -> Command:

        if not cmd:
            if aliases or desc or doc:
                logger.warning("Aliases / desc / doc are not available for service default command. "
                               "Please set aliases for service instead.")

            matcher = None
            if self.get_command(''):
                # Override default cmd handler
                matcher = self.cmds[''].matcher
                del matcher.handlers[-1]  # Delete '_handle_default_cmd' handler

            self.cmds[''] = Command(sv_name=self.sv_name, cmd_name='', aliases=self.sv_aliases,
                                    desc=desc, doc=doc,
                                    permission=permission,
                                    handlers=handlers, matcher=matcher,
                                    hidden=hidden,
                                    **kwargs)
            return self.cmds['']

        if self.get_command(cmd):
            raise ValueError(f"Duplicated cmd_name '{cmd}' in a service is not allowed.")

        cmd_prefix = {cmd} | (aliases or set())
        cmd_aliases = {f"{s} {c}" for s in self._sv_prefix for c in cmd_prefix} - set(f"{self.sv_name} {cmd}")

        cmd_obj = Command(sv_name=self.sv_name, cmd_name=cmd, aliases=cmd_aliases,
                          desc=desc, doc=doc,
                          permission=permission,
                          handlers=handlers,
                          hidden=hidden,
                          **kwargs)
        self.cmds[cmd] = cmd_obj

        return cmd_obj

    def get_cmds_list_str(self) -> Optional[str]:
        cmds = {c for c in self.cmds.values() if not c.hidden}
        if not cmds:
            return Rstr.EXPR_NO_CMDS_IN_SV
        return '\n'.join(
            Rstr.FORMAT_CMDS_LIST.format(
                cmd=(c.cmd_name if c.cmd_name else Rstr.EXPR_CALL_SV_DIRECTLY), desc=(f"({c.desc})" if c.desc else ''),
                sv_name=self.sv_name
            )
            for c in cmds)

    def get_usage_str(self) -> str:
        cmds_list_str = self.get_cmds_list_str()
        return Rstr.MSG_SERVICE_USAGE.format(sv=self.sv_name,
                                             desc=(self.desc if self.desc else Rstr.EXPR_NOT_AVAILABLE),
                                             doc=(self.sv_doc if self.sv_doc else Rstr.EXPR_NOT_AVAILABLE),
                                             cmds_list=cmds_list_str)

    def __repr__(self):
        return f"<Service '{self.sv_name}', desc='{self.desc}'>"

    def __str__(self):
        return self.__repr__()

    # def __eq__(self, other: Union['Service', str]):
    #     assert isinstance(other, (Service, str)), TypeError(
    #         f"'==' Not supported between instances of 'Service' and '{type(other)}'")
    #     if isinstance(other, str):
    #         return self.sv_name == other
    #     return self.sv_name == other.sv_name


# A dict for preserving all maintained services
# {sv_name: sv_obj}
services: Dict[str, Service] = {}
