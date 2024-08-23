---
title: Joplin-desktop_改变编辑字体样式和调整markdown渲染效果字体大小
date: 2020-05-18T19:39:26.000Z
tags: joplin
---

# Joplin-desktop_改变编辑字体样式和调整markdown渲染效果字体大小

1. 打开设置->外观->高级选项

适用于已渲染 Markdown 的自定义样式表 -> userstyle.css -> 影响展示区域字体样式。
适用于 Joplin 全域应用样式的自定义样式表 -> userchrome.css -> 影响了除展示区域的字体样式。

2. 从typera拷贝出来的CSS，可以直接放进userchrome.css 和 userstyle.css

```
*{font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif;
    -webkit-font-smoothing: antialiased;
}
```
<!-- more -->

3. 调整markdown渲染字体大小，外观->显示高级选项->适用于已渲染 Markdown 的自定义样式表->编辑。

```
body, th, td, .inline-code {
    font-size: 18px;
}
h2 {
    background-color: #46515c;
    color:white;
}
```

4. 编辑器字体族
Cascadia Code

5. Reference:
https://java-er.com/blog/joplin-css-font/
https://cloud.tencent.com/developer/article/1655173
https://blog.csdn.net/heimu24/article/details/81189700
