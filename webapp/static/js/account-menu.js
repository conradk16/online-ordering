'use strict';

function run_on_resize() {
    var logo = document.getElementById("logo");
    if (window.innerWidth < 450) {
        logo.width="100";
        logo.height="14.2";
    } else {
        logo.width="200";
        logo.height="28.4";
    }
}

