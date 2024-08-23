---
title: Hexo-Theme-Next-Configuration
date: 2021-08-16T17:08:31.000Z
tags: hexo
---

# Hexo Theme Next Configuration

## 创建主题配置文件

```
# Installed through npm
cp node_modules/hexo-theme-next/_config.yml _config.next.yml
# Installed through Git
cp themes/next/_config.yml _config.next.yml
```

> <https://theme-next.js.org/docs/getting-started/configuration.html>

<!-- more -->
## 修改主题

> <https://theme-next.js.org/docs/theme-settings/>


## 修改主题后实时预览

```
hexo clean && hexo g && hexo s
```



Next主题配置修改：
```sh
vim _config.next.yml

...
# Schemes
#scheme: Muse
#scheme: Mist
#scheme: Pisces
scheme: Gemini

# Dark Mode
darkmode: false

menu:
  #home: / || fa fa-home
  #about: /about/ || fa fa-user
  #tags: /tags/ || fa fa-tags
  #categories: /categories/ || fa fa-th
  #archives: /archives/ || fa fa-archive
  #schedule: /schedule/ || fa fa-calendar
  #sitemap: /sitemap.xml || fa fa-sitemap
  #commonweal: /404/ || fa fa-heartbeat

# Sidebar Avatar
avatar:
  # Replace the default image and set the url here.
  url: avatar.gif #/images/avatar.gif
  # If true, the avatar will be displayed in circle.
  rounded: true
  # If true, the avatar will be rotated with the cursor.
  rotated: true

social:
  GitHub: https://github.com/leiontong || fab fa-github
  E-Mail: mailto:leion.tong@outlook.com || fa fa-envelope

links:
  Leion.co: https://www.leion.co

body_scrollbar:
  # Place the scrollbar over the content.
  overlay: true
  # Present the scrollbar even if the content is not overflowing.
  stable: false

# `Follow me on GitHub` banner in the top-right corner.
github_banner:
  enable: true
  permalink: https://github.com/leiontong
  title: Follow me on GitHub

# Google Analytics
# See: https://analytics.google.com
google_analytics:
  tracking_id: UA-99348322-1
  # By default, NexT will load an external gtag.js script on your site.
  # If you only need the pageview feature, set the following option to true to get a better performance.
  only_pageview: false

```
