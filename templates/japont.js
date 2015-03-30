/*
 * japont font-face library
 * Copyright 2015 3846masa
 * Released under the Apache license version 2.0
 */

(function() {

var DOMLoaded = false;
window.addEventListener('DOMContentLoaded', function(){
  DOMLoaded = true;
}, false);

var FontFace = document.registerElement('font-face', {
  prototype: Object.create(HTMLMetaElement.prototype, {
    createdCallback: {value: function() {
      this._attached = false;
    }},
    attachedCallback: {value: function() {
      this._attached = true;
      var fontname = this.getAttribute('src');
      var selector = this.getAttribute('selector');
      var alias = this.getAttribute('alias');
      if (fontname != null) {
        if (DOMLoaded) {
          this._sendRequest(fontname, selector, alias);
        } else {
          if (this._callback != null)
            window.removeEventListener(
              'DOMContentLoaded', this._callback, false);
          var callerElem = this;
          this._callback = function() {
            callerElem._sendRequest(fontname, selector, alias);
          };
          window.addEventListener('DOMContentLoaded', this._callback, false);
        }
      }
    }},
    detachedCallback: {value: function() {
      this._attached = false;
      this.fontElement.remove();
      this.styleElement.remove();

      this.fontElement = this.styleElement = null;
    }},
    attributeChangedCallback: {value: function(attrName, oldVal, newVal) {
      if (this._attached) {
        var fontname = this.getAttribute('src');
        var selector = this.getAttribute('selector');
        var alias = this.getAttribute('alias');
        if (attrName === 'selector')
          this._setFont(alias, selector);
        else if (attrName === 'src' || attrName === 'alias') {
          if (DOMLoaded) {
            this._sendRequest(fontname, selector, alias);
          } else {
            if (this._callback != null)
              window.removeEventListener(
                'DOMContentLoaded', this._callback, false);
            var callerElem = this;
            this._callback = function() {
              callerElem._sendRequest(fontname, selector, alias);
            };
            window.addEventListener('DOMContentLoaded', this._callback, false);
          }
        }
      }
    }},
    _sendRequest : {value: _sendRequest},
    _setFont     : {value: _setFont},
    _attached    : {value: false, writable: true},
    _callback    : {value: null,  writable: true}
  })
});

function _sendRequest(fontname, selector, alias) {
  if (fontname == null) {
    throw new Error('Invalid value.');
  }
  selector = selector || '*';
  alias = alias || '';

  var callerElem = this;

  var targetNode;
  if (selector == null) {
    targetNode = document.documentElement;
  } else {
    targetNode = document.querySelector(selector);
  }
  var content = targetNode.textContent || targetNode.innerText || '';
  content = content.replace(/[\r\n]/g, '');
  var charArr = _uniqueChars(content);

  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'https://{{HEROKU_URL}}/font.css');
  xhr.onload = _embedFontCSS;
  xhr.send(JSON.stringify({
    text       : charArr.join(''),
    fontName   : fontname,
    fontFamily : alias
  }));

  function _embedFontCSS(e) {
    var xhr = e.target;
    if (xhr.status !== 200) {
      throw new Error("Can't read font file.");
    }

    if (callerElem.fontElement != null)
      callerElem.fontElement.remove();

    var fontNode = document.createElement('style');
    var textNode = document.createTextNode(xhr.responseText);
    fontNode.setAttribute('class', 'japont-face');
    fontNode.appendChild(textNode);

    callerElem.fontElement = fontNode;
    callerElem.appendChild(fontNode);
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
  var styleText = selector + "{ font-family : \"" + alias + "\", inherit; }";
  var styleNode = document.createElement('style');
  var textNode = document.createTextNode(styleText);
  styleNode.setAttribute('class', 'japont-face');
  styleNode.appendChild(textNode);

  if (this instanceof FontFace) {
    if (this.styleElement != null)
      this.styleElement.remove();

    this.styleElement = styleNode;
    this.appendChild(styleNode);
  } else {
    document.querySelector('head').appendChild(styleNode);
  }
}

})();
