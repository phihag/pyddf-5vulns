'use strict';

document.addEventListener('DOMContentLoaded', () => {
	for (const form of document.querySelectorAll('.interactive_get_form')) {
		form.addEventListener('submit', (e) => {
			e.preventDefault();
			const form = e.target;
			const fd = new FormData(form);
			const qs = Array.from(fd.entries()).map(
				e => encodeURIComponent(e[0]) + '=' + encodeURIComponent(e[1])).join('&');
			form.querySelector('.interactive_get_form_output').innerText = qs;
		});
	}
});
