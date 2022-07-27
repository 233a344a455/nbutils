from datetime import datetime
from functools import wraps
from typing import Optional, Set, Union, Tuple, Dict, List, Any, Callable, NoReturn

from nonebot import on_command
from nonebot.adapters import Message, MessageSegment
from nonebot.internal.adapter import MessageTemplate
from nonebot.matcher import Matcher
from nonebot.permission import Permission
from nonebot.typing import T_PermissionChecker, T_Handler

from nonutils.stringres import Rstr


class Command:
    def __init__(self,
                 cmd: str,
                 aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
                 permission: Optional[Union[Permission, T_PermissionChecker]] = None,
                 enable: bool = True,
                 hidden: bool = False,
                 desc: Optional[str] = None,
                 usage: Optional[str] = None,
                 **kwargs):
        self.cmd = cmd
        self.aliases = aliases
        self.permission = permission
        self.enable = enable
        self.hidden = hidden
        self.desc = desc
        self.usage = usage

        self.matcher = on_command(cmd=cmd, aliases=aliases, permission=permission, **kwargs)
        cmdmgr.register_cmd(self)


    # ==================================================
    # "Inherited" methods from nonebot.matcher.Matcher
    # ==================================================

    # def __getattr__(self, item: str):
    #     # Inherit control functions from nonebot.Matcher
    #     INHERIT_SET = {'handle', 'append_handler', 'receive', 'got', 'finish', 'pause', 'reject'}
    #     if item in INHERIT_SET:
    #         return getattr(Matcher, item)
    #     else:
    #         raise AttributeError(f"'Command' object has no attribute '{item}'")

    @wraps(Matcher.receive)
    def receive(
            self, id: str = "", parameterless: Optional[List[Any]] = None
    ) -> Callable[[T_Handler], T_Handler]:
        """装饰一个函数来指示 NoneBot 在接收用户新的一条消息后继续运行该函数

        参数:
            id: 消息 ID
            parameterless: 非参数类型依赖列表
        """
        return self.matcher.receive(id=id, parameterless=parameterless)

    @wraps(Matcher.handle)
    def handle(
            self, parameterless: Optional[List[Any]] = None
    ) -> Callable[[T_Handler], T_Handler]:
        """装饰一个函数来向事件响应器直接添加一个处理函数

        参数:
            parameterless: 非参数类型依赖列表
        """
        return self.matcher.handle(parameterless=parameterless)

    @wraps(Matcher.got)
    def got(
            self,
            key: str,
            prompt: Optional[Union[str, Message, MessageSegment, MessageTemplate]] = None,
            parameterless: Optional[List[Any]] = None,
    ) -> Callable[[T_Handler], T_Handler]:
        """装饰一个函数来指示 NoneBot 获取一个参数 `key`

        当要获取的 `key` 不存在时接收用户新的一条消息再运行该函数，如果 `key` 已存在则直接继续运行

        参数:
            key: 参数名
            prompt: 在参数不存在时向用户发送的消息
            parameterless: 非参数类型依赖列表
        """
        return self.matcher.got(key=key, prompt=prompt, parameterless=parameterless)

    @wraps(Matcher.send)
    async def send_raw(
            self,
            message: Union[str, Message, MessageSegment, MessageTemplate],
            **kwargs: Any,
    ) -> Any:
        """发送一条消息给当前交互用户

        参数:
            message: 消息内容
            kwargs: {ref}`nonebot.adapters.Bot.send` 的参数，请参考对应 adapter 的 bot 对象 api
        """
        return await self.matcher.send(message=message, **kwargs)

    @wraps(Matcher.finish)
    async def finish(
            self,
            message: Optional[Union[str, Message, MessageSegment, MessageTemplate]] = None,
            **kwargs,
    ) -> NoReturn:
        """发送一条消息给当前交互用户并结束当前事件响应器

        参数:
            message: 消息内容
            kwargs: {ref}`nonebot.adapters.Bot.send` 的参数，请参考对应 adapter 的 bot 对象 api
        """
        return await self.matcher.finish(message=message, **kwargs)

    @wraps(Matcher.pause)
    async def pause(
            self,
            prompt: Optional[Union[str, Message, MessageSegment, MessageTemplate]] = None,
            **kwargs,
    ) -> NoReturn:
        """发送一条消息给当前交互用户并暂停事件响应器，在接收用户新的一条消息后继续下一个处理函数

        参数:
            prompt: 消息内容
            kwargs: {ref}`nonebot.adapters.Bot.send` 的参数，请参考对应 adapter 的 bot 对象 api
        """
        return await self.matcher.pause(prompt=prompt, **kwargs)

    @wraps(Matcher.reject)
    async def reject(
            self,
            prompt: Optional[Union[str, Message, MessageSegment, MessageTemplate]] = None,
            **kwargs,
    ) -> NoReturn:
        """最近使用 `got` / `receive` 接收的消息不符合预期，
        发送一条消息给当前交互用户并将当前事件处理流程中断在当前位置，在接收用户新的一个事件后从头开始执行当前处理函数

        参数:
            prompt: 消息内容
            kwargs: {ref}`nonebot.adapters.Bot.send` 的参数，请参考对应 adapter 的 bot 对象 api
        """
        return await self.matcher.reject(prompt, **kwargs)

    # ==================================================
    # "Inherited" methods end
    # ==================================================

    async def send(self, message: Union[str, Message, MessageSegment],
                   **kwargs):
        return await self.send_raw(
            Rstr.FORMAT_BASIC_MSG.format(cmd=self.get_name_str(), msg=message,
                                         time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_failure(self, message: Union[str, Message, MessageSegment],
                           **kwargs):
        return await self.send(
            Rstr.FORMAT_FAILURE_MSG.format(cmd=self.get_name_str(), msg=message,
                                           time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_warning(self, message: Union[str, Message, MessageSegment],
                           **kwargs):
        return await self.send(
            Rstr.FORMAT_WARNING_MSG.format(cmd=self.get_name_str(), msg=message,
                                           time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_question(self, message: Union[str, Message, MessageSegment],
                            **kwargs):
        return await self.send(
            Rstr.FORMAT_QUESTION_MSG.format(cmd=self.get_name_str(), msg=message,
                                            time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_success(self, message: Union[str, Message, MessageSegment],
                           **kwargs):
        return await self.send(
            Rstr.FORMAT_SUCCESS_MSG.format(cmd=self.get_name_str(), msg=message,
                                           time=datetime.now().strftime('%H:%M')),
            **kwargs)

    def get_name_str(self) -> str:
        return self.cmd

    def get_usage_str(self) -> str:
        return Rstr.MSG_CMD_USAGE.format(cmd=self.cmd,
                                         doc=(self.usage if self.usage else Rstr.EXPR_NOT_AVAILABLE))

    def __repr__(self):
        return f"<Command '{self.get_name_str()}'>"

    def __str__(self):
        return self.__repr__()


class Switch:

    def __init__(self,
                 base_cmd: str,
                 base_aliases: Optional[Set[str]],
                 switch: str,
                 permission: Optional[Union[Permission, T_PermissionChecker]] = None,
                 enable: bool = True,
                 hidden: bool = False,
                 usage: Optional[str] = None,
                 **kwargs):
        self.switch = switch
        self.hidden = hidden
        self.enable = enable
        self.usage = usage

        self.matcher = on_command(cmd=(base_cmd + ' ' + switch).strip(),
                                  aliases={(als + ' ' + switch).strip() for als in base_aliases},
                                  permission=permission,
                                  **kwargs)

        # TODO: Inherit funcs form `Command`.


class CommandWithSwitch:
    def __init__(self,
                 cmd: str,
                 aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
                 enable: bool = True,
                 hidden: bool = False,
                 desc: Optional[str] = None,
                 usage: Optional[str] = None,
                 permission: Optional[Union[Permission, T_PermissionChecker]] = None):
        self.cmd = cmd
        self.aliases = aliases
        self.permission = permission
        self.enable = enable
        self.hidden = hidden
        self.desc = desc
        self.usage = usage

        self.switches: Dict[str, Switch] = {}

        cmdmgr.register_cmd(self)

    def new_switch(self,
                   switch: str,
                   enable: Optional[bool] = None,
                   hidden: Optional[bool] = None,
                   usage: Optional[str] = None,
                   permission: Optional[Union[Permission, T_PermissionChecker]] = None,
                   **kwargs):
        if self.get_switch(switch):
            raise ValueError(f"Duplicated switch in '{self.cmd}': {switch}")

        self.switches[switch] = Switch(base_cmd=self.cmd, base_aliases=self.aliases, switch=switch,
                                       enable=(self.enable if enable is None else enable),
                                       hidden=(self.hidden if hidden is None else hidden),
                                       permission=(self.permission if permission is None else permission),
                                       usage=usage, **kwargs)
        return self.switches[switch]

    def get_switch(self, switch: str):
        return self.switches[switch]

    def get_usage_str(self):
        sw_usage = [(s.usage if s.usage else self.cmd + ' ' + s.switch + Rstr.EXPR_NOT_AVAILABLE)
                    for s in self.switches.values() if not s.hidden]
        return Rstr.MSG_CMD_WITH_SWITCH_USAGE.format(cmd=self.cmd,
                                                     usage=(self.usage if self.usage else Rstr.EXPR_NOT_AVAILABLE),
                                                     switches_usage='\n'.join(sw_usage).strip())
    # TODO: enable control, permission control


class CmdManager:
    def __init__(self):
        self.commands: Dict[str, Union[Command, CommandWithSwitch]] = {}

    def register_cmd(self, cmd_obj: Union[Command, CommandWithSwitch]) -> None:
        if ' ' in cmd_obj.cmd:
            raise ValueError(f'Space is invalid in command name: {cmd_obj.cmd}')
        if self.fetch_cmd(cmd_obj.cmd):
            raise ValueError(f"Command duplicated: {cmd_obj.cmd}.")
        self.commands[cmd_obj.cmd] = cmd_obj

    def fetch_cmd(self, cmd: str) -> Optional[Union[Command, CommandWithSwitch]]:
        if cmd in self.commands.keys():
            return self.commands[cmd]
        else:
            return None

    def get_all_cmds(self, exclude_hidden_cmd: bool = True) -> Set[Union[Command, CommandWithSwitch]]:
        if exclude_hidden_cmd:
            return {c for c in self.commands.values() if not c.hidden}
        else:
            return set(self.commands.values())


cmdmgr = CmdManager()
