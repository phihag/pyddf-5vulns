'use strict';

document.addEventListener('DOMContentLoaded', function() {
	Reveal.initialize({
		transition: 'none',
		slideNumber: 'c',
		history: true,
		center: false,
		progress: true,
		dependencies: [{
			src: 'libs/plugin-highlight.js',
			async: true,
			callback: function() {
				hljs.initHighlightingOnLoad();
			}
		}],
	});
});
