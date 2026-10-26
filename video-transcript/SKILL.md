---
name: video-transcript
description: Use when extracting subtitles or spoken-text transcripts from a user-provided video URL or local video/audio file.
---

# Video Transcript

从用户提供的视频链接或本地媒体中提取字幕/口播文本并保存为 Markdown。优先复用仓库现有下载与转写工具，不重复实现下载、ASR 或字幕解析。

## 适用条件

- 用户要求下载视频、提取视频文字稿、字幕或口播内容。
- 来源是用户提供的链接或本地文件；不要擅自搜索和扩大来源范围。

## 工作流

1. 确认链接对应的视频标题、频道/作者、时长和可用字幕；记录原始链接。不要把搜索命中当作目标视频。
2. 选择一个由用户指定或现有项目约定的输出目录。大型视频和音频不要放进 Git 仓库；转写稿放入本期研究目录或用户指定位置。
3. 链接优先尝试字幕并允许工具回退为音轨转写：

   ```bash
   python3 tools/extract-audio-content/extract_audio_content.py "$URL" --prefer-subs --language auto -o "$TRANSCRIPT.md"
   ```

   `--prefer-subs` 有可用自动字幕时直接解析；没有字幕时，工具会尝试下载音轨并转写。默认豆包引擎需配置火山 ASR 凭证；没有凭证时，使用已安装的本地 Whisper 引擎：

   ```bash
   python3 tools/extract-audio-content/extract_audio_content.py "$URL" --prefer-subs --language auto --engine whisper --model medium -o "$TRANSCRIPT.md"
   ```

4. 需要先保存完整源视频、或链接转音频工具不支持该来源时，调用隔离下载器：

   ```bash
   node skills/investigation-video/scripts/download-source.mjs --platform "$PLATFORM" --url "$URL" --output-dir "$MEDIA_DIR" --json
   ```

   只使用支持的平台名：`bilibili`、`dailymotion`、`tiktok`、`douyin`、`youtube`、`pinterest`、`reddit`。可先用 `--probe-seconds 5` 检查访问；该文件只有 5 秒，不能用于整段转写。确认可访问后，完整下载时省略该参数。若直连遇到 YouTube 登录或机器人验证，且用户已明确授权使用 Chrome 登录态（包括同一连续任务中已给出的授权），可再用 `--browser chrome --probe-seconds 5` 探测一次；探测成功后省略 `--probe-seconds` 完整下载。不要查看、导出或复制 Cookies。
5. 下载器必须返回 `verified`，且结果记录中的文件路径须存在，才把完整视频文件交给转写工具：

   ```bash
   python3 tools/extract-audio-content/extract_audio_content.py "$VIDEO_FILE" --language "$LANGUAGE" -o "$TRANSCRIPT.md"
   ```

6. 打开输出 Markdown，核对来源、引擎、正文和时间戳段落；检查内容非空且语言合理。字幕/ASR 是机器结果，听不清或专名不确定处标为待核，不要凭空补齐。交付时说明是平台字幕还是 ASR 转写，并给出文件路径和未确认项。

## 阻断处理

- 遇到 YouTube 登录或机器人验证时，先判断用户是否明确授权使用 Chrome 登录态：已授权则按工作流用 `--browser chrome` 做一次短探测；未授权就停止并说明。登录态探测仍遇到验证，或出现验证码、年龄/地区限制、平台拒绝访问时立即停止。如实说明；不得循环重试、绕过验证码、伪造身份或索取用户 Cookies。
- 即使视频页面能播放，也不代表下载器可访问。下载失败时可请用户提供有权使用的本地视频/音频，或直接粘贴平台提供的文字稿。
- 下载和转写只解决技术提取，不授予再发布权。若用户计划公开使用，提醒其确认原视频、字幕/讲稿及配乐等相关授权；必要时把原稿整理为摘要或新写讲述稿，而不是把机器逐字稿当作可直接发布的原创内容。

## 现有工具

- `tools/extract-audio-content/extract_audio_content.py`：链接/本地视频或音频 → Markdown；支持自动字幕优先、豆包 ASR、本地 Whisper 和可选人声分离。
- `skills/investigation-video/scripts/download-source.mjs`：七个平台的单视频下载与 `ffprobe` 校验；只支持明确传入的平台和 URL，不负责搜索或转写。
