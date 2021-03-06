'use strict';

function _empty(node) {
	let last;
	while ((last = node.lastChild)) {
		node.removeChild(last);
	}
}

function _text(node, str) {
	_empty(node);
	node.appendChild(node.ownerDocument.createTextNode(str));
}

document.addEventListener('DOMContentLoaded', () => {
	for (const form of document.querySelectorAll('.interactive_get_form')) {
		form.addEventListener('submit', (e) => {
			e.preventDefault();
			const form = e.target;
			const fd = new FormData(form);
			const qs = Array.from(fd.entries()).map(
				e => encodeURIComponent(e[0]) + '=' + encodeURIComponent(e[1])).join('&');
			const out_el = form.querySelector('.interactive_get_form_output');
			const prefix = out_el.getAttribute('data-prefix');
			const url = (prefix || '') + qs;
			_text(out_el, url);
		});
	}
});
