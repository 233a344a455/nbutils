from typing import Optional, Set, List, Union, Callable, NoReturn, Any

import nonebot
from nonebot.adapters import Message, MessageSegment
from nonebot.handler import Handler
from nonebot.matcher import Matcher
from nonebot.permission import Permission
from nonebot.typing import T_Handler, T_ArgsParser


class Command:
    def __init__(self,
                 sv_name: str, cmd: str,
                 aliases: Optional[Set[str]] = None,
                 desc: Optional[str] = None, doc: Optional[str] = None,
                 permission: Optional[Permission] = None,
                 handlers: List[Union[T_Handler, Handler]] = None,
                 matcher: Optional[Matcher] = None,
                 **kwargs):

        self.sv_name = sv_name
        self.cmd = cmd
        self.desc = desc
        self.doc = doc
        self.matcher = matcher

        if not self.matcher:
            if handlers:
                kwargs['handlers'] = handlers
            self.matcher = nonebot.on_command(cmd, aliases=aliases, **kwargs)

    # ==================================================
    # "Inherited" methods from nonebot.matcher.Matcher
    # ==================================================

    def handle(self) -> Callable[[T_Handler], T_Handler]:
        return self.matcher.handle()

    def append_handler(self, handler: T_Handler) -> Handler:
        return self.matcher.append_handler(handler)

    def receive(self) -> Callable[[T_Handler], T_Handler]:
        return self.matcher.receive()

    def got(self,
            key: str,
            prompt: Optional[Union[str, Message, MessageSegment]] = None,
            args_parser: Optional[T_ArgsParser] = None
            ) -> Callable[[T_Handler], T_Handler]:
        return self.matcher.got(key, prompt, args_parser)

    async def send(self, message: Union[str, Message, MessageSegment],
                   **kwargs) -> Any:
        return await self.matcher.send(message, **kwargs)

    async def finish(self,
                     message: Optional[Union[str, Message,
                                             MessageSegment]] = None,
                     **kwargs) -> NoReturn:
        return await self.matcher.finish(message, **kwargs)

    async def pause(self,
                    prompt: Optional[Union[str, Message,
                                           MessageSegment]] = None,
                    **kwargs) -> NoReturn:
        return await self.matcher.pause(prompt, **kwargs)

    async def reject(self,
                     prompt: Optional[Union[str, Message,
                                            MessageSegment]] = None,
                     **kwargs) -> NoReturn:
        return await self.matcher.reject(prompt, **kwargs)

    def __repr__(self):
        return f"<Command '{self.sv_name}.{self.cmd}', desc='{self.desc}'>"

    def __str__(self):
        return self.__repr__()
