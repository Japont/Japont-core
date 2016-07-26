# Japont

Dynamic Subsetting System for Japanese fonts.

日本語フォントをWebフォントとして軽量化して配信するために，動的に必要文字グリフを抽出したフォントを生成するシステム

比較的簡単に日本語フォントを導入できます

## DEMO

[DEMO](https://japont.herokuapp.com)

## Installation

### Very Easy (Heroku)

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

### Easy (Docker)

- Prepare fonts
  - See [3846masa/japont-fonts]
- Edit ``docker-compose.yml``
  - Set ``volumes`` to fonts path
  - Set ``PUBLISHER`` env to your name
  - If you use [jwilder/nginx-proxy], set ``VIRTUAL_HOST`` and ``VIRTUAL_PORT`` env
  - Else, set ``ports``
- Run
  - ``docker-compose up -d``

## Usage

### REQUIRED

- Add script in your site

```html
<!-- https://github.com/WebComponents/webcomponentsjs/# -->
<script src="//cdnjs.cloudflare.com/ajax/libs/webcomponentsjs/0.6.0/CustomElements.min.js"></script>
<script src="//{HOST}/japont.min.js"></script>
```

### EASY

- Add ``japont-config`` tag in HTML

```html
<japont-config src="mplus/mplus-1p-light.woff" selector="*" alias="mplus"/>
```

### ADVANCED

- Write JavaScript

```js
var webFont = document.createElement('japont-config');
webFont.setAttribute('src', 'mplus/mplus-1p-light.woff');
webFont.setAttribute('selector', '.css-selector');
document.head.appendChild(webFont);
```

## LICENSE

Apply the Apache License version 2.0.

Apache License version 2.0を適用します

Copyright 2015- 3846masa

## Fonts

See [3846masa/japont-fonts].

[jwilder/nginx-proxy]: https://github.com/jwilder/nginx-proxy
[3846masa/japont-fonts]: https://github.com/3846masa/japont-fonts
