# 气泡作品库 / Bubble Gallery

首版采用零预算静态作品库：GitHub Pages 承载页面，GitHub Releases 提供已收录 PNG 下载与下载次数。无需自建服务器、数据库或付费域名。地址：https://kaitongg-bit.github.io/DIYcodex-bubble/

## 已提供

- 外星小猫、LOVE、小猫炒菜三款预设。
- 作品卡片、作者、非商业使用说明与 PNG 下载次数。
- 点击作品进入 Codex 风格模拟聊天，切换浅色/深色、输入短句或长消息。
- 下载 PNG 与 `.bubble.json`，在本机工坊导入配套设置。
- 自己的 PNG 可在浏览器私有预览，不上传、不自动发布、不调用 AI。

下载次数来自 GitHub Releases PNG asset 的 `download_count`，不是去重人数，可能延迟。公共接口失败时显示「暂未统计」，不伪造数字。本机工坊的作品库另有明确标记的本机统计。

## 手动投稿

[打开气泡库，点击「贡献气泡」](https://kaitongg-bit.github.io/DIYcodex-bubble/#contribute)。无需注册，只需昵称、气泡名、PNG 和分享授权。图片先进入私有待审仓库，审核通过后才公开。线上接收服务目前正在接入，表单会明确提示启用状态；「预览自己的 PNG」仍只在浏览器本地预览。

作者收到素材后，人工检查：

1. PNG 可正常解码、尺寸合理，没有伪装文件或私人信息。
2. 短句、长消息、宽窄布局均可读；装饰不被拉坏，拉伸线与文字框合理。
3. 投稿人说明素材来源，并明确允许社区展示与提供非商业下载；不以代码许可代替素材授权。
4. 公共作品库保持全年龄展示，不收录色情裸露、未经同意的私密影像、涉及未成年人的性内容、仇恨、骚扰或违法侵权内容。

审核通过才把 PNG、配置和元数据加入 `presets/`，发布下载资产，再更新静态页面。记录作品版本、授权依据和审核日期；私人审核资料不要提交到公开仓库。退回时说明修改意见。版权问题可以通过文字 Issue 联系维护者，下架时删除页面条目并移除对应 Release 下载资产；已下载副本无法远程收回。

## 维护与部署

配套设置使用版本 1 的 `.bubble.json`（`filename` 与 `config`），由本机工坊导出。先在隔离数据目录验证导入，再将审核后的配置写入 `presets/manifest.json`。每个公开作品记录作者、名称、中英文说明、文件名、配置、下载 URL 和统计 URL。

静态导出：

```sh
python3 scripts/export-gallery.py /tmp/bubble-gallery
```

把导出文件发布到 `gh-pages` 分支，Pages 来源选该分支根目录。不要导出 `.local/`、用户聊天、连接文件夹或日志。新增 PNG 发布到独立的预设 Release；其统计 API 使用 GitHub 的公共、只读接口，不在网页内放 token。预设 Release 不标记为桌面软件最新版。

匿名接收的 Worker 和维护者审核工具已提供；线上部署配置见 `community/DEPLOYMENT.md`。没有 AI 生图服务。

## Manual submissions

This version is a static gallery hosted on GitHub Pages. Approved PNGs and their download counts use GitHub Releases. The static gallery needs no paid domain or login. Anonymous intake uses a Cloudflare Worker and a private GitHub review queue; production intake is being connected.

Preview a PNG locally in your browser; it is never uploaded or automatically published. Open [the gallery’s contribution form](https://kaitongg-bit.github.io/DIYcodex-bubble/#contribute), enter a nickname and bubble name, choose a PNG and confirm sharing rights. The image stays private until reviewed. The form clearly shows when production intake is not yet enabled. Maintainer setup is documented in `community/DEPLOYMENT.md`.

The gallery is all-ages. The maintainer reviews safety, rights, readable stretch behavior, and configuration before publishing. Report rights concerns with a text Issue. Removing an entry and its release asset prevents further public access but cannot recall files already downloaded. Download counts are GitHub PNG asset downloads, may be delayed, and are not unique-user counts. No AI generation is provided.
