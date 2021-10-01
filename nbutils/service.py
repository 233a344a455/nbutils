from typing import Optional, Union, Tuple, Set, Type

import nonebot
from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.typing import T_RuleChecker

from nbutils.stringres import Rstring


class Service:
    """命令组，用于声明一组有相同名称前缀的命令。"""

    def __init__(self, name: str, aliases: Optional[Set[str]] = None):
        self.sv_name = name
        self.sv_aliases = aliases
        self._sv_prefix = {name} | (aliases or set())

        # Handle a cmd assigned to the very service, but doesn't match any cmd declared in the service.
        self._unk_cmd_matcher = nonebot.on_command(self.sv_name, aliases=self.sv_aliases)
        @self._unk_cmd_matcher.handle()
        async def _handle_unk_cmd(bot: Bot, event: Event):
            await self._unk_cmd_matcher.send(
                Rstring.UNKNOWN_CMD_REP.format(sv_name=self.sv_name, cmd=event.get_message()))

    def on_command(self,
                   cmd_name: str,
                   rule: Optional[Union[Rule, T_RuleChecker]] = None,
                   cmd_aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
                   **kwargs) -> Type[Matcher]:

        if cmd_name is None:
            del self._unk_cmd_matcher
            # Delete the default unknown cmd matcher,
            # which is maintained by nonebot.plugin._plugin_matchers

            return nonebot.on_command(self.sv_name, rule, self.sv_aliases, **kwargs)

        cmd_prefix = {cmd_name} | (cmd_aliases or set())
        prefix = {f"{s} {c}" for s in self._sv_prefix for c in cmd_prefix}

        return nonebot.on_command(f"{self.sv_name} {cmd_name}",
                                  rule,
                                  prefix - set(f"{self.sv_name} {cmd_name}"),
                                  **kwargs)



    # def on_command(self,
    #                cmd: str,
    #                rule: Optional[Union[Rule, T_RuleChecker]] = None,
    #                aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
    #                **kwargs) -> Type[Matcher]:
    #
    #     async def _strip_cmd(bot: "Bot", event: "Event", state: "T_State"):
    #         # 预处理 handler: 去除命令前缀
    #         message = event.get_message()
    #         segment = message.pop(0)
    #
    #         text = str(segment).lstrip()
    #         text = text[len(state["_prefix"]["raw_command"]):].lstrip() # Remove sv_name
    #
    #         new_message = message.__class__(text)
    #
    #         for new_segment in reversed(new_message):
    #             message.insert(0, new_segment)
    #
    #     # 将 _strip_cmd (handler) 合并到此 matcher 的 handlers 列表的第一个
    #     handlers = kwargs.pop("handlers", [])
    #     handlers.insert(0, _strip_cmd)
    #
    #     # self._base_cmd: {'cmd', 'alias'}
    #     return on_message(command(*self._base_cmd) & rule, handlers=handlers, **kwargs)
    #
