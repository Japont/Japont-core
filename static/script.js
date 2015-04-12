(function(){
  var $ = function(selector, elem) {
    return (elem || document).querySelector(selector);
  };
  var $$ = function(selector, elem) {
    var nodeList = (elem || document).querySelectorAll(selector);
    var nodeArray = [];
    for (var i = 0; i < nodeList.length; i++) {
      nodeArray.push(nodeList[i]);
    }
    return nodeArray;
  };

  window.addEventListener('load', function(){
    var statusSpan = $('#status');

    var sampleCode = $('#sampleCode > div').textContent;

    var fontLoader = $('#testFont');
    fontLoader.addEventListener('load', function(){
      statusSpan.textContent = "loaded."
      $('#testText').style.opacity = 1.0;
    });
    fontLoader.addEventListener('error', function(){
      statusSpan.textContent = "error."
    });

    var fontlist;
    var fontGroupSel = $('#fontGroup');
    var fontNameSel = $('#fontName');

    var fontGroupSelFire = function(){
      $$('*', fontNameSel).forEach(function(elem){
        elem.parentNode.removeChild(elem);
      });
      fontlist[this.value].forEach(function(fontName){
        var opt = document.createElement('option');
        opt.textContent = fontName;
        opt.setAttribute('value', fontName);
        fontNameSel.appendChild(opt);
      });
    };
    fontGroupSel.addEventListener('change', fontGroupSelFire);
    fontGroupSel.addEventListener('keyup', fontGroupSelFire);

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/fontlist.json');
    xhr.addEventListener('load',function(e){
      var xhr = e.target;
      if (xhr.status !== 200) return;
      $('#sampleCode > div').textContent += xhr.responseText;

      fontlist = JSON.parse(xhr.responseText);

      Object.keys(fontlist).forEach(function(groupName){
        var opt = document.createElement('option');
        opt.textContent = groupName;
        opt.setAttribute('value', groupName);
        fontGroupSel.appendChild(opt);
      });
      fontGroupSelFire.call(fontGroupSel);
    });
    xhr.send(null);

    var applyButton = $('#apply');
    applyButton.addEventListener('click', function(){
      var fontSrc = fontGroupSel.value + '/' + fontNameSel.value;
      if (fontLoader.getAttribute('src') === fontSrc) {
        fontLoader.reload();
      } else {
        fontLoader.setAttribute('src', fontSrc);
      }
      statusSpan.textContent = "loading."
      $('#testText').style.opacity = 0.0;

      var oldCode = $('#sampleCode');
      var newCode = document.createElement('pre');
      newCode.setAttribute('id', 'sampleCode');
      newCode.setAttribute('class', 'brush: html;');
      newCode.textContent = sampleCode.replace('{fontSrc}', fontSrc);
      oldCode.parentNode.insertBefore(newCode, oldCode);
      oldCode.parentNode.removeChild(oldCode);
      SyntaxHighlighter.highlight();
    });
  });
})();
