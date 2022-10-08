---
title: KDE-Plasma-Beautify-主题美化
date: 2020-05-18T19:39:26.000Z
tags: KDE
---

# KDE Beautify

<!-- more -->

## 外观

主题存放在哪里？

* 全局主题

/usr/share/plasma/look-and-feel/

~/.local/share/plasma/look-and-feel/

* Plasma 样式

~/.local/share/plasma/desktoptheme/

/usr/share/plasma/desktoptheme/

* 应用程序风格 - 窗口装饰

/usr/share/aurorae/themes/

~/.local/share/aurorae/themes/

* 颜色

/usr/share/color-schemes/

* 图标

/usr/share/icons/

~/.local/share/icons/

* 字体

/usr/share/fonts
~/.fonts

* 光标

## 工作区

* 开机和关机 - 登录屏幕 (SDDM)

/usr/share/sddm/themes/

~/.local/share/sddm/themes/

* 开机和关机 - 欢迎屏幕


## 壁纸

/usr/share/backgrounds/

~/.local/share/backgrounds/

## Dock
```
sudo pacman -S plank  #首选，流畅
sudo pacman -S latte-dock
```

## 社区或AUR收录的主题/图标/登录屏幕 (SDDM)/壁纸推荐安装：

[AdaptaBreath](0)
```
sudo pacman -S plasma5-theme-adaptabreath maia-cursor-theme  papirus-maia-icon-theme  noto-fonts-compat
````

[Breath2](0)
```
sudo pacman -S breath2-icon-themes  #图标
sudo pacman -S breath2-wallpaper  #壁纸
sudo pacman -S plasma5-themes-breath2  #全局主题
sudo pacman -S sddm-breath2-theme  #登录屏幕 (SDDM)
```

[infinity](0)
```
sudo pacman -S plasma-theme-infinitybook  #全局主题
sudo pacman -S wallpapers-infinity-book  #壁纸
```

[maia](0)
```
sudo pacman -S plasma5-themes-maia
sudo pacman -S manjaro-openbox-maia
```

[archlinux](0)
`sudo pacman -S archlinuxcn/plasma-theme-archlinux #全局主题`

[PapirusDevelopmentTeam/papirus-icon-theme: Papirus icon theme for Linux ](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme)
`sudo pacman -S papirus-icon-theme #图标`

[PapirusDevelopmentTeam/adapta-kde: Adapta KDE customization](https://github.com/PapirusDevelopmentTeam/adapta-kde)
`sudo pacman -S adapta-kde #全局主题`

[PapirusDevelopmentTeam/arc-kde: Arc KDE customization](https://github.com/PapirusDevelopmentTeam/arc-kde)
`sudo pacman -S arc-kde #全局主题`

[PapirusDevelopmentTeam/materia-kde: Materia KDE customization](https://github.com/PapirusDevelopmentTeam/materia-kde)
`sudo pacman -S materia-kde #全局主题`

[ChromeOS](https://aur.archlinux.org/packages.php?K=plasma+theme)
```
yay -S kvantum-theme-chromeos-git chromeos-kde-git  #全局主题
yay -S chromeos-gtk-theme #GTK主题
sudo pacman -S archlinuxcn/tela-icon-theme-git  #图标
```

[aex](https://aur.archlinux.org/packages.php?K=plasma+theme)
`yay -S plasma5-theme-aex-nomad-git plasma5-theme-aex-nomad-dark-git #全局主题`

[Flat Remix ICON theme](https://drasite.com/flat-remix)
`sudo pacman -S archlinuxcn/flat-remix-git #图标`

[McMojave-circle](https://store.kde.org/p/1305429/)
```
sudo pacman -S archlinuxcn/mcmojave-circle-icon-theme-git  #图标
sudo pacman -S archlinuxcn/numix-circle-icon-theme-git  #继承自图标
```

[Citrus icon theme](https://store.kde.org/p/1334044)
`sudo pacman -S aur/citrus-icon-theme-git`

[Aura KDE](https://www.pling.com/p/1355746/) | [Aura Sddm Theme](https://www.pling.com/p/1355742/)
```
git clone https://github.com/yeyushengfan258/Aura-kde.git
cd Aura-kde
./install.sh
cd sddm
sudo ./install.sh
```

[Sweet KDE](https://store.kde.org/p/1294729/)
```
yay -S aur/sddm-theme-sugar-candy-git  #登录屏幕 (SDDM)
yay -S aur/sweet-kde-git  #全局主题
yay -S aur/candy-icons-git  #图标
```

[Chili login theme for SDDM ](https://www.pling.com/p/1240784/)
`yay -S aur/chili-sddm-theme #登录屏幕 (SDDM)`
[Chili login theme for KDE Plasma](https://www.pling.com/p/1214121)


## 自定义主题

* 如果对主题不满意可以使用 kvantummanager 来修改主题。
`sudo pacman -S kvantum-qt5`
~/.config/Kvantum
