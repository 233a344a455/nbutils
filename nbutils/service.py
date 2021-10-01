from typing import Optional, Union, Tuple, Set, Type, List, Dict

import nonebot
from loguru import logger
from nonebot.adapters import Bot, Event
from nonebot.handler import Handler
from nonebot.matcher import Matcher
from nonebot.permission import Permission
from nonebot.typing import T_Handler

from nbutils.stringres import Rstr


class Command:
    def __init__(self,
                 cmd: str, aliases: Optional[Set[str]] = None,
                 desc: Optional[str] = None, doc: Optional[str] = None,
                 permission: Optional[Permission] = None,
                 handlers: List[Union[T_Handler, Handler]] = None,
                 matcher: Optional[Matcher] = None,
                 **kwargs):

        self.cmd = cmd
        self.desc = desc
        self.doc = doc
        self.matcher = matcher

        if not self.matcher:
            if handlers:
                kwargs['handlers'] = handlers
            self.matcher = nonebot.on_command(cmd, aliases=aliases, **kwargs)

    def __repr__(self):
        return f"<Command '{self.cmd}', desc='{self.desc}'>"

    def __str__(self):
        return self.__repr__()


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
                 doc: Optional[str] = None):

        self.sv_name = name
        self.sv_aliases = aliases
        self.desc = desc
        self._sv_prefix = {name} | (aliases or set())

        self.sv_doc: str = doc.strip() if (doc is not None) else None

        self.cmds: Dict[str, Command] = {}

        # Handle a cmd assigned to the very service, but doesn't match any cmd declared in the service.
        _default_cmd = self.on_command(cmd=None)

        @_default_cmd.handle()
        async def _handle_default_cmd(bot: Bot, event: Event):
            await _default_cmd.send(
                Rstr.EXPR_UNKNOWN_CMD.format(sv_name=self.sv_name, cmd=event.get_message(), doc=self.get_doc_str()))

    def get_command(self, cmd_name: str) -> Optional[Command]:
        return self.cmds.get(cmd_name, None)

    def on_command(self,
                   cmd: Optional[str] = None, aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
                   desc: Optional[str] = None, doc: Optional[str] = None,
                   permission: Optional[Permission] = None,
                   handlers: Optional[List[Union[T_Handler, Handler]]] = None,
                   **kwargs) -> Type[Matcher]:

        if self.get_command(cmd):
            raise ValueError(f"Duplicated cmd_name ('{cmd}') in a service is not allowed.")

        if not cmd:
            if aliases:
                logger.warning("Aliases are not available for service default command. "
                               "Please set aliases for service instead.")

            matcher = None
            if self.get_command(''):
                # Override default cmd handler
                matcher = self.cmds[''].matcher
                del matcher.handlers[-1]  # Delete '_handle_default_cmd' handler

            self.cmds[''] = Command(self.sv_name, self.sv_aliases, desc, doc, permission, handlers, matcher, **kwargs)
            return self.cmds[''].matcher

        cmd_prefix = {cmd} | (aliases or set())
        aliases = {f"{s} {c}" for s in self._sv_prefix for c in cmd_prefix} - set(f"{self.sv_name} {cmd}")

        cmd_obj = Command(f"{self.sv_name} {cmd}", aliases, desc, doc, permission, handlers, **kwargs)
        self.cmds[cmd] = cmd_obj

        return cmd_obj.matcher

    def get_cmds_list_str(self) -> Optional[str]:
        if not self.cmds:
            return None
        return '\n'.join(
            Rstr.FORMAT_CMDS_LIST.format(
                cmd=(k if k else Rstr.EXPR_CALL_SV_DIRECTLY), desc=(v.desc if v.desc else '')
            )
            for k, v in self.cmds.items()).strip(' ')

    def get_doc_str(self) -> str:
        cmds_list = self.get_cmds_list_str()
        return Rstr.DOC_SERVICE_HELP.format(name=self.sv_name,
                                            desc=(self.desc if self.desc else Rstr.EXPR_NOT_AVAILABLE),
                                            doc=(self.sv_doc if self.sv_doc else Rstr.EXPR_NOT_AVAILABLE),
                                            cmds_list=(cmds_list if cmds_list else Rstr.EXPR_NO_CMDS_IN_SV))

    def __repr__(self):
        return f"<Service '{self.sv_name}', desc='{self.desc}'>"

    def __str__(self):
        return self.__repr__()
