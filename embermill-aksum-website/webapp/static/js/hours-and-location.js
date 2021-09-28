function load_content() {
    var main_content = document.getElementById("main-content");

    var location_hours_section = create_element("div", main_content, "location-hours-section", null, null, null);
    var hours_section = create_element("div", location_hours_section, "title-text-container", null, null, null);
    create_element("a", hours_section, "title", "Hours", null, null);

    create_element("a", hours_section, "text-line", "Tuesday - Saturday: 12 pm - 4 pm", null, null);
    create_element("a", hours_section, "text-line", "Closed Sunday and Monday", null, null);

    var location_section = create_element("div", location_hours_section, "title-text-container", null, null, null);
    var location_title = create_element("a", location_section, "title", "Location", null, null);

    var location_lines = create_element("div", location_section, "location-lines", null, null, null);
    //create_element("a", location_lines, "text-line", "Embermill Aksum", null, null);
    create_element("a", location_lines, "text-line", "1031 State Street, Santa Barbara, CA", null, null);
    //create_element("a", location_lines, "text-line", "Santa Barbara, CA 93101", null, null);
    create_element("a", location_lines, "text-line", "805-452-3377", null, null);

    create_element("img", main_content, "img", null, null, "../static/media/restaurant-hours-2.jpg");
}

function load_mobile_view() {
    var hours_side_bar_link = document.getElementsByClassName("side-menu-link")[3];
    hours_side_bar_link.style.fontWeight = "700";
    load_content();
}

function load_desktop_view() {
    var hours_desktop_link = document.getElementsByClassName("desktop-link")[3];
    hours_desktop_link.style.fontWeight = "700";

    load_content();
}
