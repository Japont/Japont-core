# Japont
Dynamic Subsetting System for Japanese fonts.

日本語フォントをWebフォントとして軽量化して配信するために，動的に必要文字グリフを抽出したフォントを生成するシステム

比較的簡単に日本語フォントを導入できます

## How to use

サンプルサイトは[こちら](https://japont.herokuapp.com)

まずは，自分専用の配信サーバを作りましょう．

<del>[Heroku](https://www.heroku.com/)を使って無料で作れます．</del>

<del>[![Deploy](https://www.herokucdn.com/deploy/button.png)](#)</del>

**==調整中==**

そしたら，立ち上がったサーバにアクセスしましょう．


### Sample Code

配信サーバのトップページは，テストページになっています．

サンプルコードもテストページで生成できます．

```html
<!-- https://github.com/WebComponents/webcomponentsjs/# -->
<script src="//cdnjs.cloudflare.com/ajax/libs/webcomponentsjs/0.6.0/CustomElements.min.js"></script>
<script src="//{HEROKU_URL}/japont.js"></script>
<meta is="web-font" src="mplus/mplus-1p-light.woff" selector="*" alias="mplus"/>
```

```js
var webFont = document.createElement('meta', 'web-font');
webFont.setAttribute('src', 'mplus/mplus-ip-light.woff');
webFont.setAttribute('selector', '#any-id');
document.head.appendChild(webFont);
```

## LICENSE
Apply the Apache License version 2.0.
Apache License version 2.0を適用します．

-----------------------
Copyright 2015- 3846masa

## Fonts

**準備中**


## 改善点他
- 読み込みが遅い
  - Herokuのスペックが低い

- フォントの追加
  - 追加方法をまとめておく
