/*
 * japont font-face library
 * Copyright 2015 3846masa
 * Released under the Apache license version 2.0
 */

(function() {

/**
 * THIS SCRIPT IS DEPRECATED
 */
console.warn('This Japont script is deprecated. See https://{{HOST}}.');

window.Japont = {};

var DOMLoaded =
  (document.readyState === "interactive" ||
   document.readyState === "complete");

document.addEventListener('DOMContentLoaded', function(){
  DOMLoaded = true;
}, false);
window.addEventListener('load', function(){
  DOMLoaded = true;
}, false);

Japont.HTMLWebFontElement = document.registerElement('web-font', {
  prototype: Object.create(HTMLMetaElement.prototype, {
    createdCallback: {value: function() {
      this._attached = false;
    }},
    attachedCallback: {value: function() {
      this._attached = true;
      var fontname = this.getAttribute('src');
      var selector = this.getAttribute('selector');
      var alias = this.getAttribute('alias');
      if (fontname != null && fontname !== "") {
        if (DOMLoaded) {
          this._sendRequest(fontname, selector, alias);
        } else {
          if (this._callback != null)
            document.removeEventListener(
              'DOMContentLoaded', this._callback, false);
          var callerElem = this;
          this._callback = function() {
            callerElem._sendRequest(fontname, selector, alias);
          };
          document.addEventListener('DOMContentLoaded', this._callback, false);
        }
      }
    }},
    detachedCallback: {value: function() {
      this._attached = false;
      this.fontElement.parentNode.removeChild(this.fontElement);
      this.styleElement.parentNode.removeChild(this.styleElement);

      this.fontElement = this.styleElement = null;
    }},
    attributeChangedCallback: {value: function(attrName, oldVal, newVal) {
      if (this._attached) {
        var fontname = this.getAttribute('src');
        var selector = this.getAttribute('selector');
        var alias = this.getAttribute('alias');
        if (attrName === 'alias')
          this._setFont(alias, selector);
        else if (attrName === 'src' || attrName === 'selector') {
          if (DOMLoaded) {
            this._sendRequest(fontname, selector, alias);
          } else {
            if (this._callback != null)
              document.removeEventListener(
                'DOMContentLoaded', this._callback, false);
            var callerElem = this;
            this._callback = function() {
              callerElem._sendRequest(fontname, selector, alias);
            };
            document.addEventListener('DOMContentLoaded', this._callback, false);
          }
        }
      }
    }},
    reload: {value: function(){
      var fontname = this.getAttribute('src');
      var selector = this.getAttribute('selector');
      var alias = this.getAttribute('alias');
      if (fontname != null) {
        this._sendRequest(fontname, selector, alias);
      }
    }},
    _sendRequest : {value: _sendRequest},
    _setFont     : {value: _setFont},
    _callback    : {value: null,  writable: true}
  }),
  extends      : 'meta'
});

function _sendRequest(fontname, selector, alias) {
  if (fontname === "") return;
  if (fontname == null) {
    throw new Error('Invalid value.');
  }
  selector = selector || '*';
  alias = alias || '';

  var callerElem = this;

  var targetNodes;
  if (selector == null) {
    targetNodes = [document.documentElement];
  } else {
    targetNodes = document.querySelectorAll(selector);
  }
  if (targetNodes == null || targetNodes.length === 0) {
    throw new Error('Selector "' + selector + '" is not matched.');
  }
  var content = "";
  for(var _i = 0; _i < targetNodes.length; _i++) {
    content += targetNodes[_i].textContent;
  }
  content = content.replace(/[\r\n]/g, '');
  var charArr = _uniqueChars(content);

  var xhr = new XMLHttpRequest();
  xhr.open('POST', '//{{HOST}}/font.css');
  xhr.onload = _embedFontCSS;
  xhr.send(JSON.stringify({
    text       : charArr.join(''),
    fontName   : fontname,
    fontFamily : alias
  }));

  function _embedFontCSS(e) {
    var xhr = e.target;
    if (xhr.status !== 200) {
      var event = document.createEvent('HTMLEvents');
      event.initEvent('error', false, false);
      callerElem.dispatchEvent(event);

      throw new Error("Can't read font file.");
    }

    if (callerElem.fontElement != null)
      callerElem.fontElement.parentNode.removeChild(callerElem.fontElement);

    callerElem.fontName = xhr.responseText.split('\n')[1];
    var fontNode = document.createElement('style');
    var textNode = document.createTextNode(xhr.responseText);
    fontNode.setAttribute('class', 'japont-face');
    fontNode.appendChild(textNode);

    callerElem.fontElement = fontNode;
    callerElem.appendChild(fontNode);

    var event = document.createEvent('HTMLEvents');
    event.initEvent('load', false, false);
    callerElem.dispatchEvent(event);
    console.info("Loaded font file.");

    callerElem._setFont(alias, selector);
  }

  function _uniqueChars(str) {
    var arr = str.split('');
    var i, o = {}, l = arr.length;
    for (i = 0; i < l; i++) {
      o[arr[i]] = 1;
    }
    return Object.keys(o);
  }
}

function _setFont(alias, selector) {
  if (this instanceof Japont.HTMLWebFontElement &&
      this.fontElement != null) {
    var fontCss = this.fontElement.textContent;
    alias = alias || this.fontName || "undefined";
    fontCss =
      fontCss.replace(/font-family: '[^']*'/, "font-family: '" + alias + "'")
    this.fontElement.textContent = fontCss;
  }

  var styleText = selector + "{ font-family : \"" + alias + "\"; }";
  var styleNode = document.createElement('style');
  var textNode = document.createTextNode(styleText);
  styleNode.setAttribute('class', 'japont-face');
  styleNode.appendChild(textNode);

  if (this instanceof Japont.HTMLWebFontElement) {
    if (this.styleElement != null)
      this.styleElement.parentNode.removeChild(this.styleElement);

    this.styleElement = styleNode;
    this.appendChild(styleNode);
  } else {
    document.querySelector('head').appendChild(styleNode);
  }
}

})();
