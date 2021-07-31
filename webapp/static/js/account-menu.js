'use strict';

function resize_logo() {
    var logo = document.getElementById("logo");
    var topnav = document.getElementsByClassName("topnav")[0];
    if (topnav.clientWidth < 450) {
        logo.width="100";
        logo.height="14.2";
    } else {
        logo.width="200";
        logo.height="28.4";
    }
}

function run_on_resize() {
    resize_logo();
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

function clear_stripe() {
    var menu_stripe_block = document.getElementById("menu_stripe_block");
    menu_stripe_block.remove();
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

    var customers_pay_online = document.getElementById("account-menu-script").getAttribute('data-website_url');
    if (!customers_pay_online) {
        clear_stripe();
    }
}

function click_link(link) {
    window.location.href = link;
}
