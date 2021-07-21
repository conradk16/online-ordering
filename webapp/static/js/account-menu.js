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

function check_if_view_orders() {
    var orders_link = document.getElementById("account-menu-script").getAttribute('data-order_url');

    //orders_link = null;

    var menu_view_orders = document.getElementById("menu_view_orders");
    if (orders_link == null) {
        menu_view_orders.style.cursor = "default";
        menu_view_orders.style.color = "gray";
        menu_view_orders.style.pointerEvents = "none";

        var menu_view_orders_block = document.getElementById("menu_view_orders_block");
        menu_view_orders_block.display = "block";
        menu_view_orders_block.style.backgroundColor = "#fff";
    } else {
        orders_link = "https://m3orders.com/" + orders_link;
        menu_view_orders.style.cursor = "pointer";
        menu_view_orders.style.color = "black";
        menu_view_orders.style.pointerEvents = "auto";
        
    }
}

var perfEntries = performance.getEntriesByType("navigation");
if (perfEntries[0].type === "back_forward") {
    location.reload(true);
}
