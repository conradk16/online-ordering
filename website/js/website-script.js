const MAX_MOBILE_WIDTH = 450;

function load_mobile_view() {
    
}

function load_desktop_view() {
    
}

function run_on_load() {
    run_on_resize();
}

function run_on_resize() {
    const width = window.innerWidth;
    if (width <= MAX_MOBILE_WIDTH) {
        load_mobile_view();
    } else {
        load_desktop_view();
    }
}

window.onresize = run_on_resize;
window.onload = run_on_load;
