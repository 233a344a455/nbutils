from datetime import datetime
from typing import Optional, Set, List, Union, Callable, NoReturn, Any
from functools import wraps

import nonebot
from nonebot.adapters import Message, MessageSegment
from nonebot.handler import Handler
from nonebot.matcher import Matcher
from nonebot.permission import Permission
from nonebot.typing import T_Handler, T_ArgsParser

from nonutils.stringres import Rstr


class Command:
    def __init__(self,
                 sv_name: str, cmd_name: str,
                 raw_cmd: Optional[str] = None, aliases: Optional[Set[str]] = None,
                 desc: Optional[str] = None, doc: Optional[str] = None,
                 permission: Optional[Permission] = None,
                 handlers: List[Union[T_Handler, Handler]] = None,
                 matcher: Optional[Matcher] = None,
                 hidden: bool = False,
                 **kwargs):

        self.sv_name = sv_name
        self.cmd_name = cmd_name
        self.raw_cmd = raw_cmd if raw_cmd else (f"{sv_name} {cmd_name}" if cmd_name else sv_name)
        self.desc = desc
        self.doc = doc
        self.matcher = matcher
        self.hidden = hidden

        if not self.matcher:
            if handlers:
                kwargs['handlers'] = handlers
            self.matcher = nonebot.on_command(self.raw_cmd, aliases=aliases, **kwargs)

    # ==================================================
    # "Inherited" methods from nonebot.matcher.Matcher
    # ==================================================

    @wraps(Matcher.handle)
    def handle(self) -> Callable[[T_Handler], T_Handler]:
        return self.matcher.handle()

    @wraps(Matcher.append_handler)
    def append_handler(self, handler: T_Handler) -> Handler:
        return self.matcher.append_handler(handler)

    @wraps(Matcher.receive)
    def receive(self) -> Callable[[T_Handler], T_Handler]:
        return self.matcher.receive()

    @wraps(Matcher.got)
    def got(self,
            key: str,
            prompt: Optional[Union[str, Message, MessageSegment]] = None,
            args_parser: Optional[T_ArgsParser] = None
            ) -> Callable[[T_Handler], T_Handler]:
        return self.matcher.got(key, prompt, args_parser)

    @wraps(Matcher.send)
    async def send_raw(self, message: Union[str, Message, MessageSegment],
                       **kwargs) -> Any:
        """
        Send the raw message without being formatted.
        """
        return await self.matcher.send(message, **kwargs)

    @wraps(Matcher.finish)
    async def finish(self,
                     message: Optional[Union[str, Message,
                                             MessageSegment]] = None,
                     **kwargs) -> NoReturn:
        return await self.matcher.finish(message, **kwargs)

    @wraps(Matcher.pause)
    async def pause(self,
                    prompt: Optional[Union[str, Message,
                                           MessageSegment]] = None,
                    **kwargs) -> NoReturn:
        return await self.matcher.pause(prompt, **kwargs)

    @wraps(Matcher.reject)
    async def reject(self,
                     prompt: Optional[Union[str, Message,
                                            MessageSegment]] = None,
                     **kwargs) -> NoReturn:
        return await self.matcher.reject(prompt, **kwargs)

    # ==================================================
    # "Inherited" methods end
    # ==================================================

    async def send(self, message: Union[str, Message, MessageSegment],
                   **kwargs):
        return await self.matcher.send(
            Rstr.FORMAT_BASIC_MSG.format(name=self.get_name_str(), msg=message,
                                         time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_failed(self, message: Union[str, Message, MessageSegment],
                          **kwargs):
        return await self.matcher.send(
            Rstr.FORMAT_FAILED_MSG.format(name=self.get_name_str(), msg=message,
                                          time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_warn(self, message: Union[str, Message, MessageSegment],
                        **kwargs):
        return await self.matcher.send(
            Rstr.FORMAT_WARNING_MSG.format(name=self.get_name_str(), msg=message,
                                           time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_question(self, message: Union[str, Message, MessageSegment],
                            **kwargs):
        return await self.matcher.send(
            Rstr.FORMAT_QUESTION_MSG.format(name=self.get_name_str(), msg=message,
                                            time=datetime.now().strftime('%H:%M')),
            **kwargs)

    async def send_succ(self, message: Union[str, Message, MessageSegment],
                        **kwargs):
        return await self.matcher.send(
            Rstr.FORMAT_SUCC_MSG.format(name=self.get_name_str(), msg=message,
                                        time=datetime.now().strftime('%H:%M')),
            **kwargs)

    def get_name_str(self):
        return f"{self.sv_name}.{self.cmd_name}" if self.cmd_name else self.sv_name

    def get_usage_str(self):
        return Rstr.MSG_CMD_USAGE.format(cmd=self.get_name_str(),
                                         doc=(self.doc if self.doc else Rstr.EXPR_NOT_AVAILABLE))

    def __repr__(self):
        return f"<Command '{self.sv_name}.{self.cmd_name}', desc='{self.desc}'>"

    def __str__(self):
        return self.__repr__()
