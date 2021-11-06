# Nonutils
非官方的Nonebot2的便捷工具类模块  
**早期开发阶段，请勿实际使用!!!**  
尚无完整的说明文档。  

## 功能简介

本模块的核心功能及为服务(`Service`)系统。  

服务(`Service`) 是一套命令管理工具，功能方面类似于 `Nonebot` 中的 `command_group`，而在管理方面类似于 `(sub)plugin`
每一个 `Service` 都可以添加多个命令，在会话中通过以下方式激活：

```
<command_start><sv_name|sv_aliases> <cmd|aliases> <args>
```

如 `/test_service test_cmd arg1 arg2`，即可触发 `test_service` 的 `test_cmd`
其中 `sv_name` 与 `cmd` 都可设置相应的 `aliases`

可以通过 `service.on_command` 声明命令，用法同 `nonebot.on_command`  

除基础的命令组的功能外，服务提供以下功能：
- [x] 自动生成 服务帮助 & 命令帮助，可用 `/help` 命令在会话中查询
- [x] 提供基于 `pydantic` 的配置持久化服务
- [x] 格式化会话信息
- [x] 完全可自定义的内部会话信息
- [ ] 自动化API管理
- [ ] 错误处理与追踪
- [ ] 权限与命令停用的动态化管理
- [ ] 数据库系统

本项目受 [ATRI的Service系统](https://github.com/Kyomotoi/ATRI/blob/HEAD/ATRI/service.py) 启发  
**早期开发阶段，请勿实际使用!**
