---
title: 一条命令配置好 Hermes Agent,Nous Portal 让我放弃了收集 API Key
date: 2026-05-26
pillar: P1
tags: [Hermes Agent, Nous Portal, AI工具, 配置]
source: Hermes官方文档 + GitHub数据 + NATASHA-INTEL情报
mother_theme: AI帮减负
---

# 一条命令配置好 Hermes Agent,Nous Portal 让我放弃了收集 API Key

之前配置 AI 工具，最烦的不是安装，是收集 API Key。

一个模型要一个 Key，搜索要一个 Key，图像生成要一个 Key，TTS 要一个 Key，浏览器要一个 Key，加起来五六个 Key，要去各个平台注册、充值、配置。

我之前配置 Hermes Agent，光收集 Key 就花了两天。

后来发现了 Nous Portal，一条命令搞定所有配置，不需要自己收集 Key。

今天分享 Hermes Agent + Nous Portal 的快速配置方案。

---


简单讲，Hermes Agent 是一个会自我进化的 AI Agent。

它不只能执行任务，还会观察你的行为，总结你的模式，主动优化。GitHub Stars 165,352，2026 年 5 月采集的数据，主要贡献者 teknium1 提交了 4,670 次 commits，迭代非常频繁。

核心特性包括，闭合学习循环，Agent 会自己从经验中学习和改进。多渠道接入，Telegram、Discord、Slack、WhatsApp、Signal、Email。定时自动化，用自然语言配置定时任务。多后端支持，本地、Docker、SSH、Modal、Daytona 等 7 种。

---


简单讲，Nous Portal 是一个一站式 API 订阅服务。

以前你需要分别注册 OpenAI、Anthropic、DeepSeek 等平台，收集各自 API Key，配置到 Hermes Agent 里。

现在你只需要一个 Nous Portal 订阅，它提供 300 多个模型，包括 OpenAI、Anthropic、DeepSeek 等，Tool Gateway 功能覆盖搜索、图像生成、TTS、浏览器，全部用一个订阅搞定。

一条命令配置，`hermes setup --portal`，登录 OAuth，设置 Nous 为 Provider，开启 Tool Gateway，不需要手动配置各个 API Key。

---


Linux 或 macOS，一条命令。

`curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`

Windows 用 PowerShell。

`iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)`

安装程序会处理所有依赖，包括 uv、Python 3.11、Node.js、ripgrep、ffmpeg，甚至还有一个便携的 Git Bash。

安装完之后，`source ~/.bashrc`，然后 `hermes` 就能跑了。

---


这是最关键的部分。

如果你用 Nous Portal，一条命令搞定所有配置。

`hermes setup --portal`

它会通过 OAuth 登录，设置 Nous 为你的 Provider，自动开启 Tool Gateway。

Tool Gateway 包含这些功能。

Web 搜索，Firecrawl 提供。

图像生成，FAL 提供。

文本转语音，OpenAI 提供。

云端浏览器，Browser Use 提供。

不需要分别去各个平台注册 Key，全部通过 Nous Portal 一个订阅搞定。

---


如果你想用自己的 Key，Hermes 支持配置各个 Provider。

查看可用的模型命令，`hermes model`。

它会列出所有可用的 Provider，包括 OpenAI、Anthropic、OpenRouter、DeepSeek、Kimi、MiniMax 等。

配置单个 Key，`hermes config set`，设置你想用的 Provider 和模型。

---


Hermes 支持多个消息渠道，Telegram、Discord、Slack、WhatsApp、Signal、Email。

配置命令，`hermes gateway setup`，会引导你一步步配置各个渠道。

以 Telegram 为例，你需要先创建一个 Bot，从 BotFather 获取 Token，然后 `hermes config set telegram.token`，填入你的 Token。

配置完之后，`hermes gateway start`，网关就跑起来了，你可以在 Telegram 上给 Bot 发消息。

---


Hermes 支持 7 种后端运行方式。

本地、Docker、SSH、Singularity、Modal、Daytona、Vercel Sandbox。

我最喜欢的是 Daytona 和 Modal，它们提供 serverless persistence。

什么意思，你让 Hermes 跑一个任务，它执行完之后环境会休眠，不占用资源。等你下次发消息，它才唤醒。

空闲时不计费，用多少算多少。

---


Hermes 内置 cron 调度器，用自然语言配置定时任务。

比如每天早上 8 点推送资讯，`hermes schedule create`，然后跟它说，每天早上 8 点推送今日 AI 热点，它自动配置好 cron 表达式。

推送内容可以指定，输出路径可以指定，通知渠道可以指定。

比如定时推送到 Telegram，或者定时存入 Obsidian，或者定时发邮件。

---


### 坑一，第一次运行有点慢

Hermes 第一次启动会初始化环境，下载模型，建立索引，大概需要 1 到 2 分钟。

不是卡了，是在初始化。之后就正常了。

### 坑二，Windows 早期 Beta

原生 Windows 支持目前是早期 Beta，能跑但可能有问题。

官方推荐用 WSL2，那是目前最稳定的 Windows 方案。

### 坑三，微信和 QQ 不支持

Hermes 目前不支持微信和 QQ，如果重度依赖这两个渠道，需要用 OpenClaw。

---


用了 Hermes Agent + Nous Portal 之后，我再也不需要收集 API Key 了。

以前配置一个 AI 工具，光收集 Key 就花两天，现在一条命令，10 分钟搞定所有配置。

这种感觉太爽了。

---


安装 Hermes，`curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`

快速配置，`hermes setup --portal`

查看模型，`hermes model`

配置渠道，`hermes gateway setup`

启动网关，`hermes gateway start`

健康检查，`hermes doctor`

---

*情报来源,GitHub nousresearch/hermes-agent 2026-05-24 + Hermes Agent 官方文档 + NATASHA-INTEL 智能体部署情报 2026-05-23*
