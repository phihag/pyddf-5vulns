'use strict';

document.addEventListener('DOMContentLoaded', function() {
	Reveal.initialize({
		transition: 'none',
		slideNumber: 'c',
		history: true,
		center: false,
		progress: true,
		controlsTutorial: false,
		dependencies: [{
			src: 'libs/plugin-highlight.js',
			async: true,
			callback: function() {
				hljs.initHighlightingOnLoad();
			}
		}],
	});

	var body = document.querySelector('body');

	var _hide_cursor_timeout;
	function hide_cursor() {
		_hide_cursor_timeout = null;
		body.style.cursor = 'none';
	}
	function show_cursor() {
		if (_hide_cursor_timeout) {
			clearTimeout(_hide_cursor_timeout);
		} else {
			body.style.cursor = 'default';
		}
		_hide_cursor_timeout = setTimeout(hide_cursor, 10000);
	}
	body.addEventListener('mousemove', show_cursor);
});
