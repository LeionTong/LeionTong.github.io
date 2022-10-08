---
title: Ubuntu-16.04-LTS-themes-&-icons-tweak
date: 2018-03-16T09:00:00.000Z
tags: null
---

# Ubuntu 16.04 LTS themes & icons tweak

## First of all, install 'ubuntu tweak tool' or 'unity tweak tool'.

If your Desktop Environment is Gnome: `sudo apt-get install gnome-tweak-tool`.

or

If your Desktop Environment is Unity: `sudo apt-get install unity-tweak-tool`.

## Favoriate Themes, icons

### Arc

<http://www.noobslab.com/2017/01/arc-theme-light-dark-versions-and-arc.html>

```
sudo add-apt-repository ppa:noobslab/themes
sudo apt-get update
sudo apt-get install arc-theme
sudo add-apt-repository ppa:noobslab/icons
sudo apt-get update
sudo apt-get install arc-icons
```

<!-- more --> 

### Flatabulous

<https://github.com/anmoljagetia/Flatabulous>

<https://blog.anmoljagetia.me/flatabulous-ubuntu-theme/>

<http://www.noobslab.com/2016/07/flatabulous-theme-makes-your-desktop.html>

```
sudo add-apt-repository ppa:noobslab/themes
sudo apt-get update
sudo apt-get install flatabulous-theme
sudo add-apt-repository ppa:noobslab/icons
sudo apt-get update
sudo apt-get install ultra-flat-icons
```

### MacBuntu

<http://www.noobslab.com/2016/04/macbuntu-1604-transformation-pack-for.html>

#### Install themes, icons and cursors.

```
sudo add-apt-repository ppa:noobslab/macbuntu
sudo apt-get update
sudo apt-get install macbuntu-os-icons-lts-v7 macbuntu-os-ithemes-lts-v7
```

After installation choose theme, icons and mac cursor from tweak tool.

#### To Uninstall themes, icons and cursors.

```
cd /usr/share/icons/mac-cursors && sudo ./uninstall-mac-cursors.sh
sudo apt-get remove macbuntu-os-icons-lts-v7 macbuntu-os-ithemes-lts-v7
```

### Equilux

<https://www.opendesktop.org/p/1182169/>

#### Description:

The Equilux themes provide a neutral dark-balanced color-scheme not designed to be fancy, but to be useful for a few specific goals.

- Minimize eye strain: when you pass many hours in front of the screen or you are hyper-sensitive to light, saturation and contrast, your eyes will benefit from a dull UI

- Avoid disrupting your circadian rhythms: a neutral color-cast-free UI helps your body to produce enough melatonin at night time and sleep better, working nicely with software like f.lux, redshift, NightLight, ...

- Professional use in image editing, graphic design, 3D rendering: in that fields any color cast or excessive contrast, brightness or darkness introduced by the UI would affect the overall perception of the color and balance of the images

- You may just like it: even if the style is not the main goal, many people find that its very clean and minimalistic UI looks cool and professional

This theme is based on the Materia Theme.
