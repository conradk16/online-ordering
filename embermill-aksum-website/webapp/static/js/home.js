var about_us_text = "Aksum is a city in northern Ethiopia. It's known for its tall, carved obelisks, relics of the ancient Kingdom of Aksum. Most are in the northern Stelae Park, including a huge fallen pillar, now in pieces. Centuries-old St. Mary of Zion is a Christian church and pilgrimage site believed to have housed the biblical Ark of the Covenant. The neighboring Chapel of the Tablet is said to contain the Ark today.";

function load_mobile_view() {
    var welcome_side_bar_link = document.getElementsByClassName("side-menu-link")[0];
    welcome_side_bar_link.style.fontWeight = "700";

    var main_content = document.getElementById("main-content");

    var top_container = create_element("div", main_content, "mobile-home-top-container", null, null, null);
    create_element("img", top_container, "mobile-home-top-pic", null, null, "../static/media/restaurant-home-1.jpeg");
    var btn = create_element("button", top_container, "mobile-home-online-ordering-button", "Order Online", null, null);
    btn.onclick = function () {
      window.location.href = "https://m3orders.com/order/embermill-aksum";
    }

    var about_us_container = create_element("div", main_content, "mobile-home-about-us-container", null, null, null);

    create_element("a", about_us_container, "mobile-home-about-us-title", "Welcome", null, null);
    create_element("a", about_us_container, "mobile-home-about-us-content", about_us_text, null, null);

    create_element("img", main_content, "mobile-home-bottom-pic", null, null, "../static/media/restaurant-home-2.jpeg");

    var bottom_pic3 = document.createElement("img");
    bottom_pic3.setAttribute('src', '../static/media/restaurant-home-3-mobile.jpg');
    bottom_pic3.classList.add("mobile-home-bottom-pic");
    main_content.appendChild(bottom_pic3);

    var bottom_pic4 = document.createElement("img");
    bottom_pic4.setAttribute('src', '../static/media/restaurant-home-4-mobile.jpg');
    bottom_pic4.classList.add("mobile-home-bottom-pic");
    main_content.appendChild(bottom_pic4);

    var bottom_pic5 = document.createElement("img");
    bottom_pic5.setAttribute('src', '../static/media/restaurant-home-5-mobile.jpg');
    bottom_pic5.classList.add("mobile-home-bottom-pic");
    main_content.appendChild(bottom_pic5);
}


function load_desktop_view() {
    var home_desktop_link = document.getElementsByClassName("desktop-link")[0];
    home_desktop_link.style.fontWeight = "700";

    var main_content = document.getElementById("main-content");
    var first_row = document.createElement("div");
    first_row.classList.add("desktop-home-first-row");
    main_content.appendChild(first_row);

    var left_pic = document.createElement("img");
    left_pic.setAttribute('src', '../static/media/restaurant-home-1.jpeg');
    left_pic.classList.add("desktop-home-left-pic");
    left_pic.width = window.innerWidth * 0.55;
    left_pic.height = window.innerWidth * 0.55 * 183 / 275;
    first_row.appendChild(left_pic);

    var about_us_container = document.createElement("div");
    about_us_container.classList.add("desktop-home-about-us-container");
    first_row.appendChild(about_us_container);

    var about_us_title = document.createElement("a");
    about_us_title.innerHTML = "Welcome";
    about_us_title.classList.add("desktop-home-about-us-title");
    about_us_container.appendChild(about_us_title);

    var about_us_content = document.createElement("a");
    about_us_content.innerHTML = about_us_text;
    about_us_content.classList.add("desktop-home-about-us-content");
    about_us_container.appendChild(about_us_content);

    var bottom_pic = document.createElement("img");
    bottom_pic.setAttribute('src', '../static/media/restaurant-home-2.jpeg');
    bottom_pic.classList.add("desktop-home-bottom-pic");
    main_content.appendChild(bottom_pic);

    var bottom_pic3 = document.createElement("img");
    bottom_pic3.setAttribute('src', '../static/media/restaurant-home-3.png');
    bottom_pic3.classList.add("desktop-home-bottom-pic");
    main_content.appendChild(bottom_pic3);

    var bottom_pic4 = document.createElement("img");
    bottom_pic4.setAttribute('src', '../static/media/restaurant-home-4.jpg');
    bottom_pic4.classList.add("desktop-home-bottom-pic");
    main_content.appendChild(bottom_pic4);

    var bottom_pic5 = document.createElement("img");
    bottom_pic5.setAttribute('src', '../static/media/restaurant-home-5.jpg');
    bottom_pic5.classList.add("desktop-home-bottom-pic");
    main_content.appendChild(bottom_pic5);
}
