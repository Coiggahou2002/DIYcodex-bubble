# 开发与运行说明

面向贡献者的技术信息。普通用户请先读 [README](README.md)。

## 运行源码

macOS、Python 3.9+、Node.js 22+；无需 npm 安装或前端构建。

```sh
git clone https://github.com/kaitongg-bit/DIYcodex-bubble.git
cd DIYcodex-bubble
python3 app/server.py
```

打开 http://127.0.0.1:19329 。可用 `BUBBLE_STUDIO_DATA` 设置私有数据目录、`BUBBLE_STUDIO_NODE` 指定 Node 路径，`--port` 指定工作台端口。

## 结构

- `app/server.py`：本机素材库、导入、预设、回收区与 macOS 文件夹窗口。
- `app/bridge.mjs`：连接桌面应用、应用与撤销用户消息样式。
- `app/static/`：可视化编辑器、预览与九切片画布绘制；`i18n.mjs` 管理中英文 UI，语言保存在浏览器本地，不改变气泡预设。
- `tests/`：隔离临时目录的服务测试。
- `.local/`：私人素材、收藏、设置、回收文件和日志，不提交。

## 参数与连接

PNG 两轴分别支持 2–4096 px；直接导入单张限制 2 MB，连接文件夹读取不设这一限制。新素材默认按不超过 240×98 页面像素适配，已有预设不自动覆盖。缩放范围 1%–200%，100% 为原图像素大小；文字字号不随素材缩放。

圆角 0 保留原图，边框粗细 0 关闭描边。圆角裁切画布四角；额外边框沿画布外框描边。调节不重写 PNG。

通过绑定 `127.0.0.1:19327` 的 CDP 端口注入运行时样式，不修改官方应用包。九切片绘制到同一画布，避免分块接缝。匹配数是当前挂载的用户消息数，虚拟化或页面切换时可能为 0。调试端口对本机程序可见，完全退出并正常启动桌面应用可关闭它。关闭工作台不会自动撤销已注入样式；请先恢复默认或完全重启应用。

目前仅 macOS 桌面端经过验证，应用升级后可能需要适配。

## 验证

```sh
python3 -m unittest discover -s tests -v
node --check app/bridge.mjs
node --check app/static/app.js
```

更多验证记录见 [VALIDATION.md](VALIDATION.md)。截图必须使用隔离演示数据，不包含用户私人素材、路径或聊天。
