const MAX_MOBILE_WIDTH = 800;
const TITLE_RESIZE_WIDTH = 1050;
var old_width = window.innerWidth;

function open_side_menu() {
  var non_sidebar_container = document.getElementById("non-sidebar-container");
  non_sidebar_container.style.borderRight = "1px solid #c9c9c9";
  non_sidebar_container.style.marginRight = "250px";
  non_sidebar_container.style.marginLeft = "-250px";

  var side_menu = document.getElementById("side-menu");
  side_menu.style.transition = "z-index .7s ease-in-out";
  side_menu.style.zIndex = 3;
  side_menu.style.visibility = "visible";

  var menu_img = document.getElementById("menu-img");
  menu_img.onclick = close_side_menu;

}

function close_side_menu() {
  var non_sidebar_container = document.getElementById("non-sidebar-container");
  non_sidebar_container.style.borderRight = "none";
  non_sidebar_container.style.marginRight = "0";
  non_sidebar_container.style.marginLeft = "0";

  var side_menu = document.getElementById("side-menu");
  side_menu.style.transition = "z-index 0s ease-in-out";
  side_menu.style.zIndex = -1;
  side_menu.style.visibility = "hidden";

  var menu_img = document.getElementById("menu-img");
  menu_img.onclick = open_side_menu;
}

function load_mobile_navbar() {
    var navbar = document.getElementById("navbar");
    navbar.style.height = "80px";
    var restaurant_name = create_element("a", navbar, "restaurant-name", "Embermill Aksum", null, null);
    restaurant_name.style.fontSize = "30px";
    var menu_img = create_element("img", navbar, "menu-icon", null, null, "../static/media/menu.png");
    menu_img.id = "menu-img";
    menu_img.height = 30;
    menu_img.width = 30;
    menu_img.onclick = open_side_menu;
}

function load_desktop_navbar() {
    var navbar = document.getElementById("navbar");
    var restaurant_name = create_element("a", navbar, "restaurant-name", "Embermill Aksum", null, null);
    if (window.innerWidth < TITLE_RESIZE_WIDTH) {
        restaurant_name.style.fontSize = "30px";
        navbar.style.height = "90px";
    } else {
        restaurant_name.style.fontSize = "50px";
        navbar.style.height = "120px";
    }
    var desktop_links_holder = create_element("div", navbar, "desktop-links-holder", null, null, null);

    create_element("a", desktop_links_holder, "desktop-link", "Welcome", "/", null);
    create_element("a", desktop_links_holder, "desktop-link", "Order Online", "https://m3orders.com/order/embermill-aksum", null);
    create_element("a", desktop_links_holder, "desktop-link", "Menu", "/menu", null);
    create_element("a", desktop_links_holder, "desktop-link", "Location & Hours", "/hours-and-location", null);
}

function clear_element(element) {
    while(element.firstChild && element.removeChild(element.firstChild));
}

function run_on_load() {
  const width = window.innerWidth;
  if (width <= MAX_MOBILE_WIDTH) {
      clear_element(document.getElementById("main-content"));
      clear_element(document.getElementById("navbar"));
      load_mobile_navbar();
      load_mobile_view();
  } else {
      if (document.getElementById("menu-img") != null) {
          close_side_menu();
      }
      clear_element(document.getElementById("main-content"));
      clear_element(document.getElementById("navbar"));
      load_desktop_navbar(900);
      load_desktop_view();
  }
}

function run_on_resize() {

    const width = window.innerWidth;
    if (width <= MAX_MOBILE_WIDTH) {
      if (old_width > MAX_MOBILE_WIDTH) {
        clear_element(document.getElementById("main-content"));
        clear_element(document.getElementById("navbar"));
        load_mobile_navbar();
        load_mobile_view();
      }
    } else {
        if (document.getElementById("menu-img") != null) {
            close_side_menu();
        }
        clear_element(document.getElementById("main-content"));
        clear_element(document.getElementById("navbar"));
        load_desktop_navbar(900);
        load_desktop_view();
    }
    old_width = width;
}

window.onresize = run_on_resize;
window.onload = run_on_load;
