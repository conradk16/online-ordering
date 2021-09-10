var about_us_text = "Aksum is a city in northern Ethiopia. It's known for its tall, carved obelisks, relics of the ancient Kingdom of Aksum. Most are in the northern Stelae Park, including a huge fallen pillar, now in pieces. Centuries-old St. Mary of Zion is a Christian church and pilgrimage site believed to have housed the biblical Ark of the Covenant. The neighboring Chapel of the Tablet is said to contain the Ark today.";

function add_news_element(_parent) {
    var news_container = create_element("div", _parent, "news-container", null, null, null);
    news_container.onclick = function () {
        window.location.href = 'https://www.independent.com/2021/06/14/ethiopian-food-coming-to-embermill/';
    }

    create_element("hr", news_container, null, null, null, null); 

    var horizontal_holder = create_element("div", news_container, "article-title-holder", null, null, null);

    var article_title = create_element("a", horizontal_holder, "article-title", "Santa Barbara Independent: Ethiopian Food Coming to Embermill", null, null);

    var article_caption_holder = create_element("div", news_container, "article-caption-holder", null, null, null);
    
    var article_caption = create_element("a", article_caption_holder, "article-caption", "Saba Tewolde Hosting Tigray Benefit on June 20; Starts Serving Lunch at State Street Restaurant", null, null);

    var gray_bar = document.createElement("hr");
    news_container.appendChild(gray_bar);
}

function set_column_img_width(img) {
    img.width = (window.innerWidth - 20) / 3 - (10 * 2 / 3);
}

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

    add_news_element(main_content);

    create_element("img", main_content, "mobile-home-bottom-pic", null, null, "../static/media/restaurant-home-2.jpeg");

    create_element("img", main_content, "mobile-home-bottom-pic", null, null, "../static/media/restaurant-home-4.jpg");

    create_element("img", main_content, "mobile-home-bottom-pic", null, null, "../static/media/restaurant-home-5.jpg");


    create_element("img", main_content, "mobile-home-bottom-pic", null, null, "../static/media/restaurant-home-6.jpg");

    create_element("img", main_content, "mobile-home-bottom-pic", null, null, "../static/media/restaurant-home-7.jpg");

    create_element("img", main_content, "mobile-home-bottom-pic", null, null, "../static/media/restaurant-home-8.jpg");

    create_element("img", main_content, "mobile-home-bottom-pic", null, null, "../static/media/restaurant-home-9.jpg");

    create_element("img", main_content, "mobile-home-bottom-pic", null, null, "../static/media/restaurant-home-10.jpg");

    create_element("img", main_content, "mobile-home-bottom-pic", null, null, "../static/media/restaurant-home-11.jpg");

    create_element("img", main_content, "mobile-home-bottom-pic", null, null, "../static/media/restaurant-home-3.jpeg");
}

function load_desktop_view() {
    var home_desktop_link = document.getElementsByClassName("desktop-link")[0];
    home_desktop_link.style.fontWeight = "700";

    var main_content = document.getElementById("main-content");
    var first_row = create_element("div", main_content, "desktop-home-first-row", null, null, null);

    var left_pic = document.createElement("img");
    left_pic.setAttribute('src', '../static/media/restaurant-home-1.jpeg');
    left_pic.classList.add("desktop-home-left-pic");
    left_pic.width = window.innerWidth * 0.55;
    left_pic.height = window.innerWidth * 0.55 * 183 / 275;
    first_row.appendChild(left_pic);

    var about_us_container = create_element("div", first_row, "desktop-home-about-us-container", null, null, null);

    var about_us_title = create_element("a", about_us_container, "desktop-home-about-us-title", "Welcome", null, null);

    var about_us_content = create_element("a", about_us_container, "desktop-home-about-us-content", about_us_text, null, null);

    add_news_element(main_content);

    var bottom_pic = document.createElement("img");
    bottom_pic.setAttribute('src', '../static/media/restaurant-home-2.jpeg');
    bottom_pic.classList.add("desktop-home-bottom-pic");
    main_content.appendChild(bottom_pic);

    // create column pics
    var column_pics_container = create_element("div", main_content, "desktop-home-column-pics-container", null, null, null);
    
    var column_1 = create_element("div", column_pics_container, "desktop-home-pics-column", null, null, null);

    var column_2 = create_element("div", column_pics_container, "desktop-home-pics-column", null, null, null);

    var column_3 = create_element("div", column_pics_container, "desktop-home-pics-column", null, null, null);

    var img_1_1 = create_element("img", column_1, "desktop-home-column-pic", null, null, "../static/media/restaurant-home-3.jpeg");
    set_column_img_width(img_1_1);

    var img_1_2 = create_element("img", column_1, "desktop-home-column-pic", null, null, "../static/media/restaurant-home-4.jpg");
    set_column_img_width(img_1_2);

    var img_1_3 = create_element("img", column_1, "desktop-home-column-pic", null, null, "../static/media/restaurant-home-5.jpg");
    set_column_img_width(img_1_3);


    var img_2_1 = create_element("img", column_2, "desktop-home-column-pic", null, null, "../static/media/restaurant-home-6.jpg");
    set_column_img_width(img_2_1);

    var img_2_2 = create_element("img", column_2, "desktop-home-column-pic", null, null, "../static/media/restaurant-home-7.jpg");
    set_column_img_width(img_2_2);

    var img_2_3 = create_element("img", column_2, "desktop-home-column-pic", null, null, "../static/media/restaurant-home-8.jpg");
    set_column_img_width(img_2_3);


    var img_3_1 = create_element("img", column_3, "desktop-home-column-pic", null, null, "../static/media/restaurant-home-9.jpg");
    set_column_img_width(img_3_1);

    var img_3_2 = create_element("img", column_3, "desktop-home-column-pic", null, null, "../static/media/restaurant-home-10.jpg");
    set_column_img_width(img_3_2);

    var img_3_3 = create_element("img", column_3, "desktop-home-column-pic", null, null, "../static/media/restaurant-home-11.jpg");
    set_column_img_width(img_3_3);

    
}
