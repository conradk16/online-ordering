'use strict';

function submit_form(selection) {
    var form = document.getElementById('select-form');
    var input = document.getElementById('inp');
    input.value = selection;
    form.submit();
  }

function run_on_load() {
run_on_resize();
}

function run_on_resize() {
var bullet_text_elements = document.getElementsByClassName("plan-bullet-text");
for (const elem of bullet_text_elements) {
    if (window.innerWidth < 500) {
        elem.style.fontSize = "12px";
    } else {
        elem.style.fontSize = "15px";
    }
}
}

window.onload = run_on_load;
window.onresize = run_on_resize;
