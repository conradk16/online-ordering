var one_column_max_width = 740;
var two_column_max_width = 1200;

class menuItem {
    constructor(item_name, item_description, price) {
        this.item_name = item_name;
        this.item_description = item_description;
        this.price = price;
    }
}

var menuItems = Array();
menuItems.push(new menuItem("Yedero Wot", "Tender chicken cooked with Ethiopian spices, barbecue sauce, onion, garlic, and gluten free bread injera.", "$19.00"));
menuItems.push(new menuItem("Yebeg Siga Wot", "Tender pieces of lamb braised in Ethiopian special barbecue sauce served with bread injera gluten free.", "$21.00"));
menuItems.push(new menuItem("Meat Combination", "Yebeg siga wot(Mild spicy lamb), and yebeg alicha wot(None spicy lamb). Served with side of gluten free bread injera with chicken and beef.", "$23.00"));
menuItems.push(new menuItem("Vegetarian Combination", "Split lentil, split peas, shio, green beans, cabbage, carrot, potato, collared green.", "$16.00"));
menuItems.push(new menuItem("Miser Wot", "Lentil and red pepper sauce seasoned with assorted psices and tomatoes. Served with side of bread injera.", "$12.00"));
menuItems.push(new menuItem("Yemeser Wot", "Served with red lentils, cabbage, potato, and carrots.", "$13.00"));
menuItems.push(new menuItem("Atakilt Wat", "Served with red lentils, cabbage, potato, and carrots.", "$12.00"));


function get_num_columns() {
    if (window.innerWidth < one_column_max_width) {
        return 1;
    } else if (window.innerWidth < two_column_max_width) {
        return 2;
    }
    return 3;
}

function load_menu() {
    var num_columns = get_num_columns();
    var main_content = document.getElementById("main-content");

    var current_column_index = 0;
    for (let i = 0; i < menuItems.length; i++) {
        if (current_column_index == 0) { // create a new row
            var menu_row = create_element("div", main_content, "menu-row", null, null, null);
        }

        var menu_item = menuItems[i];
        var name = menu_item.item_name;
        var descrip = menu_item.item_description;
        var price = menu_item.price;

        var menu_item = create_element("div", menu_row, "menu-item", null, null, null);
        var menu_item_top = create_element("div", menu_item, "menu-item-top", null, null, null);
        create_element("a", menu_item_top, "menu-item-title", name, null, null);
        create_element("a", menu_item_top, "menu-item-price", price, null, null);
        create_element("a", menu_item, "menu-item-description", descrip, null, null);

        current_column_index += 1;
        current_column_index %= num_columns;
    }

    // finish the row
    if (current_column_index != 0) {
        while (current_column_index < num_columns) {
            create_element("div", menu_row, "menu-item", null, null, null);
            current_column_index += 1
        }
    }
}

function load_mobile_view() {
    var menu_side_bar_link = document.getElementsByClassName("side-menu-link")[2];
    menu_side_bar_link.style.fontWeight = "700";

    var main_content = document.getElementById("main-content");
    var top_container = create_element("div", main_content, "top-container", null, null, null);
    var top_pic = create_element("img", top_container, "top-pic-mobile", null, null, "../static/media/restaurant-menu-1.jpg");
    var menu_title = create_element("a", top_container, "menu-title-mobile", "Our Menu", null, null);

    create_element("br", main_content, null, null, null, null);
    create_element("br", main_content, null, null, null, null);
    load_menu();
}


function load_desktop_view() {
    var menu_desktop_link = document.getElementsByClassName("desktop-link")[2];
    menu_desktop_link.style.fontWeight = "700";

    var main_content = document.getElementById("main-content");
    var top_container = create_element("div", main_content, "top-container", null, null, null);
    var top_pic = create_element("img", top_container, "top-pic", null, null, "../static/media/restaurant-menu-1.jpg");
    var menu_title = create_element("a", top_container, "menu-title", "Our Menu", null, null);
    create_element("br", main_content, null, null, null, null);
    create_element("br", main_content, null, null, null, null);

    load_menu();
}
