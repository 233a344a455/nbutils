from datetime import datetime
from typing import Optional, Set, List, Union, Tuple, Dict, Type

from nonebot import on_command
from nonebot.adapters import Message, MessageSegment
from nonebot.dependencies import Dependent
from nonebot.internal.rule import Rule
from nonebot.matcher import Matcher
from nonebot.permission import Permission
from nonebot.typing import T_Handler, T_RuleChecker, T_PermissionChecker, T_State

from nonutils.stringres import Rstr


class Command:
    def __init__(self,
                 cmd: str,
                 rule: Optional[Union[Rule, T_RuleChecker]] = None,
                 aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
                 enable: bool = True,
                 hidden: bool = False,
                 desc: Optional[str] = None,
                 usage: Optional[str] = None,
                 *,
                 permission: Optional[Union[Permission, T_PermissionChecker]] = None,
                 handlers: Optional[List[Union[T_Handler, Dependent]]] = None,
                 temp: bool = False,
                 priority: int = 1,
                 block: bool = True,
                 state: Optional[T_State] = None):

        self.cmd = cmd
        # self.rule = rule
        self.aliases = aliases
        self.permission = permission
        # self.handlers = handlers
        # self.temp = temp
        # self.priority = priority
        # self.block = block
        # self.state = state
        self.enable = enable
        self.hidden = hidden
        self.desc = desc
        self.usage = usage

        self.matcher = on_command(cmd=cmd, rule=rule, aliases=aliases, permission=permission, handlers=handlers,
                                  temp=temp,
                                  priority=priority, block=block, state=state)

    def __getattr__(self, item: str):
        # Inherit control functions from nonebot.Matcher
        INHERIT_SET = {'handle', 'append_handler', 'receive', 'got', 'finish', 'pause', 'reject'}
        if item in INHERIT_SET:
            return getattr(Matcher, item)
        else:
            raise AttributeError(f"'Command' object has no attribute '{item}'")

    async def send(self, message: Union[str, Message, MessageSegment],
                   **kwargs):
        return await self.send(
            Rstr.FORMAT_BASIC_MSG.format(name=self.cmd, msg=message,
                                         time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_failure(self, message: Union[str, Message, MessageSegment],
                           **kwargs):
        return await self.send(
            Rstr.FORMAT_FAILURE_MSG.format(name=self.cmd, msg=message,
                                           time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_warning(self, message: Union[str, Message, MessageSegment],
                           **kwargs):
        return await self.send(
            Rstr.FORMAT_WARNING_MSG.format(name=self.cmd, msg=message,
                                           time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_question(self, message: Union[str, Message, MessageSegment],
                            **kwargs):
        return await self.send(
            Rstr.FORMAT_QUESTION_MSG.format(name=self.cmd, msg=message,
                                            time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_success(self, message: Union[str, Message, MessageSegment],
                           **kwargs):
        return await self.send(
            Rstr.FORMAT_SUCCESS_MSG.format(name=self.cmd, msg=message,
                                           time=datetime.now().strftime('%H:%M')),
            **kwargs)

    def get_usage_str(self):
        return Rstr.MSG_CMD_USAGE.format(cmd=self.cmd,
                                         doc=(self.doc if self.doc else Rstr.EXPR_NOT_AVAILABLE))

    def __repr__(self):
        return f"<Command '{self.cmd_name}', desc='{self.desc}', enable={self.enable}>"

    def __str__(self):
        return self.__repr__()


class CommandWithSwitch:
    def __init__(self,
                 cmd: str,
                 rule: Optional[Union[Rule, T_RuleChecker]] = None,
                 aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
                 enable: bool = True,
                 hidden: bool = False,
                 desc: Optional[str] = None,
                 usage: Optional[str] = None,
                 permission: Optional[Union[Permission, T_PermissionChecker]] = None,
                 priority: int = 1):
        self.cmd = cmd
        self.aliases = aliases

        self.rule = rule
        self.permission = permission
        self.priority = priority

        self.enable = enable
        self.hidden = hidden
        self.desc = desc
        self.usage = usage

        self.switches: Dict[str, Type[Matcher]] = {}

    def new_switch(self,
                   switch: str,
                   enable: bool = True,
                   hidden: bool = False,
                   desc: Optional[str] = None,
                   usage: Optional[str] = None,
                   rule: Optional[Union[Rule, T_RuleChecker]] = None,
                   permission: Optional[Union[Permission, T_PermissionChecker]] = None,
                   handlers: Optional[List[Union[T_Handler, Dependent]]] = None,
                   temp: bool = False,
                   priority: int = 1,
                   block: bool = True,
                   state: Optional[T_State] = None):

        self.switches[switch] = on_command(cmd=(self.cmd + ' ' + switch).strip(),
                                           rule=(rule if rule else self.rule),
                                           aliases={(als + ' ' + switch).strip() for als in self.aliases},
                                           permission=(permission if permission else self.permission),
                                           handlers=handlers,
                                           temp=temp,
                                           priority=(priority if priority else self.priority),
                                           block=block,
                                           state=state)

    def get_switch(self, switch: str):
        return self.switches[switch]
