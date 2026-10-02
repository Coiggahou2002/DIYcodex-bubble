# 气泡社区方案 / Bubble Community Proposal

**状态：规划中，尚未部署。** 当前仓库提供本机工坊。本文定义社区首版，不把构想当成已上线功能。

## 为什么值得做

用户不用在聊天里反复找 PNG：在作品库里先试效果、选喜欢的款式，再带到本机工坊应用。创作者不用掌握代码：已有 PNG 就可以在线调整拉伸和文字空间，再投稿。维护者可以逐件审核，而不是让未经确认的图片立即出现在公共库。

社区采用「作品库 + 在线工坊 + 登录投稿 + 人工审核」结构。公开作品先试效果、再决定下载；投稿有明确状态和审核门槛。

## 首版怎么用

| 页面 | 用户能做什么 | 边界 |
| --- | --- | --- |
| 气泡库 | 浏览、搜索、按风格筛选已审核作品 | 只展示已通过审核的具体版本 |
| 作品详情 | 看作者、素材来源、预览短句/长消息/自定义文字、切换浅色/深色 | 示例文字在浏览器里处理，不上传真实聊天 |
| 在线工坊 | 上传已有 PNG，拖拉伸线和文字框，调颜色、比例、圆角、边框 | 不登录也能本地预览；没有 AI 生图和 Codex 授权入口 |
| 投稿 | 登录，填写名称、来源和授权说明，明确同意公开展示与非商业下载，提交审核 | 点击投稿前，文件只在浏览器中；投稿后进入私有待审区 |
| 我的投稿 | 看待审、退回理由和已发布版本；修改后重新送审或撤下作品 | 不能绕过审核替换公开文件 |
| 审核台 | 看原图、长短预览和来源说明，通过、退回、下架 | 仅审核员访问，所有操作留记录 |

只有投稿需要登录。下载首版可不登录，方便首次体验；通过频率限制防止集中抓取。先做作品和创作者署名，不急着加评论、打赏或排行榜，减少审核负担并保持禁止商用原则。

## 预览与本机应用怎么衔接

在线工坊复用本项目的九切片渲染算法，预览是可输入示例文字的聊天模拟器。它不是实际 Codex 页面，也不连接用户本机或读取聊天。只有本机工坊才有「应用到 Codex」。

首版提供两个明确下载：PNG 图片和配套 `.bubble.json` 调节文件；准备好本机「导入设置」功能后，才发布整套可安装包。当前本机仅能导出设置，因此在兼容导入完成前，社区只能引导导入 PNG 后自行调整，不能宣称一键保留所有参数。

后续再做安全的作品包导入：固定版本 ID、PNG、结构化配置、校验哈希；不含脚本、HTML 或任意 CSS。下载后由用户在本机确认应用。先不做自定义协议和网页一键唤起，避免首版把发布、下载安装和连接桌面应用混成一个动作。

## 人工审核是真正的发布门槛

作品版本流转：**草稿 → 待审核 → 已通过 / 已退回 → 已下架**。编辑已通过作品时创建新版本重新审核；旧版本只有仍被批准时才能继续公开。作者不能在已批准的版本上覆盖 PNG 或配置。

每次审核至少检查：

1. PNG 可正常解码、尺寸和大小符合限制；用短句、长单行、多行、浅色和深色预览检查文字空间与拉伸。
2. 名称、作者、来源及授权说明齐全；IP、人物肖像、网络梗图等不得仅凭“网上找到”视为可公开下载。无法确认的作品退回补充依据。
3. 社区首版采用公开全年龄展示：不接受色情裸露、未经同意的私密影像、涉及未成年人的性内容、仇恨、骚扰或其他违法侵权内容。合法的个人私有预览不等于允许社区发布。
4. 投稿者明确同意社区展示和向他人提供非商业下载；代码许可证不自动赋予素材分发权。作品详情展示素材自己的授权条件，不把所有投稿一律说成项目拥有版权。

通过时记录审核员、时间、具体图片和配置的哈希、素材声明与版本 ID。退回附简短可操作的理由；公开作品提供举报入口，维护者能快速下架。下架立即停止公开页面与下载；已经下载的文件不能远程收回，不承诺做到这一点。

## 数据和权限

建议首版结构是 **静态网页 + 服务端 API + 数据库 + 私有文件存储 + 登录**，而不是把本机 Python 服务直接暴露到互联网。

- 浏览器上传后先落在私有待审存储，只允许作者和审核员读取；未审核的原图、缩略图和预览图也不能通过猜 URL 访问。
- 服务端校验 PNG 文件头、实际解码、两轴 2–4096 px、2 MB 上传限制、坐标、比例、颜色和配置范围；限制解码资源，生成去除元数据的公开派生图片。不能只信扩展名、客户端尺寸和用户填写的路径。
- 公共 API 和下载接口都查该版本的批准状态；缓存和公开文件在撤下时同步失效。不能只在前端隐藏待审卡片。
- 上传、修改、审核、下架均按登录身份和角色在服务端校验；作者只管理自己的投稿，审核员才可批准作品。
- 加投稿频率、大小和存储配额，记录必要的审核操作；不收集真实 Codex 聊天、API Key 或模型账号。预览不调用生成模型。

数据库建议至少有 `users`、`bubbles`、不可覆盖的 `bubble_versions`、`moderation_events`、`reports`；作品元数据包含名称、作者、来源、授权声明、尺寸、配置、文件哈希、状态与批准版本。

托管平台和域名尚未选择。选好后再落实登录提供方、对象存储权限、上传签名和部署预算；本文不承诺具体价格或可用性。

## 从现在到上线

**阶段一：把预览独立出来。** 做不依赖本机 API 的网页工坊，支持 PNG 拖入、本地预览与参数导出；完善本机配套配置导入。

**阶段二：把审核跑通。** 实现登录、私有投稿、我的投稿、审核台、已批准版本的公共作品库和下载。用“待审不可公开、不能越权批准、改图必须重审、下架停止下载”做上线验收。

**阶段三：再增加社区互动。** 举报和创作者主页优先；有稳定作品供应后再做收藏与排序，不先做复杂社交功能。

上线还需准备投稿授权文本、社区内容规则、隐私说明、版权投诉渠道和审核员账号。对于公开成人内容、版权不明素材等，单纯写“与作者无关”不能替代审核、授权和下架机制。

## English summary

The proposed community is not live yet. Its first version would offer an approved gallery, browser-based PNG preview and tuning, authenticated submissions, a human moderation dashboard, and downloads. It would not use Codex AI or any image-generation service.

Local previews stay in the browser until the creator submits. Pending assets remain private. Only an explicitly approved immutable version can appear in public pages or downloads. Edits require a new review; withdrawal stops further public downloads. Creator attribution and image-specific non-commercial permissions must be shown separately from the software license.

The first public release should pass authorization, moderation, image-validation, and takedown tests. Hosting, a domain, and a login provider still need to be selected. The desktop app also needs configuration import before the community can promise installation with saved tuning intact.
