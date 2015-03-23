/*
  japont.js
  Copyright 2015 3846masa
*/
(function(){
	var content = document.documentElement.textContent;
	content = content.replace(/[\r\n]/g, '');
	var charArr = uniqueArray(content.split(''));	
	
  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://testbox.5000.post-internet.ml/font.css');
  xhr.onload = embedFontCSS;
	xhr.send(JSON.stringify({
		text     : charArr.join(''),
		fontName : ''
	}));

	function embedFontCSS(e) {
		console.log(e);
		var xhr = e.target;
		if (xhr.status !== 200) {
			console.error("Can't read font file.");
			return;
		}
		var styleNode = document.createElement('style');
    styleNode.setAttribute('class', 'japont-face');
		var textNode = document.createTextNode(xhr.responseText);
    styleNode.appendChild(textNode);
		document.querySelector('head').appendChild(styleNode);
		console.info("Loaded font file.");
	}

	function uniqueArray(arr) {
		var i, o = {}, l = arr.length;
		for (i = 0; i < l; i++) {
			o[arr[i]] = 1;
		}
		return Object.keys(o);
	}
})();