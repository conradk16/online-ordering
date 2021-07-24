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

function gray_view_orders() {
    var menu_view_orders_block = document.getElementById("menu_view_orders_block");
    var menu_view_orders = document.getElementById("menu_view_orders");
    menu_view_orders_block.style.backgroundColor = "#fff";
    menu_view_orders_block.style.pointerEvents = "none";

    menu_view_orders.style.cursor = "default";
    menu_view_orders.style.color = "gray";
}

function clear_view_orders() {
    var menu_view_orders_block = document.getElementById("menu_view_orders_block");
    menu_view_orders_block.remove();
}

function check_if_view_orders() {
    var order_url = document.getElementById("account-menu-script").getAttribute('data-order_url');
    var active_subscription = document.getElementById("account-menu-script").getAttribute('data-active_subscription');
    var charges_enabled = document.getElementById("account-menu-script").getAttribute('data-charges_enabled');
    var website_url = document.getElementById("account-menu-script").getAttribute('data-website_url');
    var paid_for_website = document.getElementById("account-menu-script").getAttribute('data-paid_for_website');
    
    if (charges_enabled == "False" || active_subscription == "False" || (order_url == "None" && paid_for_website == "False") || (website_url == "None" && paid_for_website == "True")) {
        clear_view_orders(); 
    }
}

function click_link(link) {
    window.location.href = link;
}
