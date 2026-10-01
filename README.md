# 气泡工坊 · Bubble Studio

把原创抖音气泡 PNG 做成你自己的 Codex 消息皮肤。项目同时提供 **设计 skill** 和 **本机气泡工作台**：读取 PNG 素材库、调整横竖拉伸线、预览长短消息、保存每款设置，再只替换你发送的气泡。

## 运行

需要 Python 3.9+ 和 Node.js 22+。工作台不需要前端构建或 npm 依赖。

```sh
git clone https://github.com/kaitongg-bit/douyin-codex-bubble-studio.git
cd douyin-codex-bubble-studio
python3 app/server.py
```

打开 http://127.0.0.1:19329 。macOS 也可以在 Finder 中双击 `Start Bubble Studio.command`。

1. 点击「连接素材文件夹」，粘贴你之前聊天的 `outputs` 路径；或者直接导入 PNG。
2. 在气泡库中选一款，拖动四条线，避开猫头、尾巴、文字和强纹理。拉伸线采用原图像素坐标。
3. 切换「文字位置」，直接拖动文字框或拖动四角缩放；也可输入四边文字留白。调整颜色和显示比例，检查短句、十四行长消息、自定义文本与深色预览。
4. 保存这款的设置，再点击「应用到 Codex」。每款 PNG 的设置独立保存。
5. 若 Codex 未连接，先保存输入并用 `⌘Q` 完全退出，再点击「启动 Codex 并换肤」。程序不会自动关闭你的应用。

首次打开不会内置私人素材或自动连接私人目录。原图不会被修改。导入副本、收藏、设置和日志均存放在 `.local/`，已被 Git 排除。可用 `BUBBLE_STUDIO_DATA` 指定其他数据目录。

## 设计 skill

```sh
python3 scripts/install-skill.py
```

安装后向 Codex 说：

> 使用 $douyin-bubble-studio 设计一款原创抖音气泡，完成点九结构、镜像、边距、四边锚点和长消息预检，加入我的气泡素材库，再用气泡工坊调整并应用到 Codex。

安装器会把工作台源码一起放入 skill 的资源目录，便于独立运行。skill 使用所在客户端的图像生成工具；工作台不附带云端生图模型、账号或 API Key。「设计新气泡」入口提供可复制给 Codex 的设计提示。

预检脚本需要 Pillow：

```sh
python3 -m pip install -r skills/douyin-bubble-studio/requirements.txt
python3 skills/douyin-bubble-studio/scripts/edge_spacing.py bubble.png --anchor-rect 47 32 174 126
```

尺寸合规不代表完整抖音审核通过；装饰跨越拉伸带仍可能变形。必须检查实际 PNG，保留用户自选分割线和预览环节。

## Codex 连接与恢复

通过仅绑定 `127.0.0.1:19327` 的 CDP 调试端口注入运行时 CSS，不改官方应用包，不发送或读取聊天文字。调试端口对本机其他程序可见；完全退出并正常启动应用可关闭它。

「恢复默认」会清空活动气泡并删除运行时样式。工作台打开期间，后台会在页面刷新后重新应用当前气泡。关闭工作台不会自动删除已经注入的样式；先恢复或完全重启应用。

匹配数反映当前页面挂载的用户消息，切换面板或消息虚拟化时可能为 0；保存、连接、匹配和视觉验收是不同状态。

**兼容范围：** macOS ChatGPT/Codex 桌面端的 `app://-/` 窗口已做实机验证；兼容当前与旧版用户消息容器。其他系统可使用素材库与编辑器，但本项目只提供 macOS 启动流程。应用升级后 DOM、调试参数或应用名称变化可能需要适配。本项目不是 OpenAI 官方插件，也不是抖音官方气泡工具。

## 测试

```sh
python3 -m unittest discover -s tests -v
node --check app/bridge.mjs
node --check app/static/app.js
```

后端测试覆盖真实 PNG 导入、原图保护、每款设置独立保存、非法坐标、应用与恢复状态、配置导出和素材路径隔离。前端及实机换肤的验收过程见 `VALIDATION.md`。

## 项目结构

- `app/`：本机服务、Codex 注入桥与工作台界面。
- `skills/douyin-bubble-studio/`：设计及应用 skill、抖音规则参考、预检脚本。
- `scripts/install-skill.py`：安装自包含 skill。
- `tests/`：不依赖私人素材的测试。

## 来源与许可

MIT License。Codex 运行时样式注入思路参考 [codex-candy-jelly-skin](https://github.com/suki052/codex-candy-jelly-skin)，设计规则和预检脚本延续 [douyinQIPAO](https://github.com/kaitongg-bit/douyinQIPAO)。应用桥和工作台是本项目实现，没有复用前者的整套主题或安装器。

用户自行导入素材的权利属于各自权利人，不随代码许可证转授。项目不捆绑用户素材、聊天记录或私人路径。
