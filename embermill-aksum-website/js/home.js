function load_mobile_view() {
    
}

function load_desktop_view() {
    var main_content = document.getElementById("main-content");
    var first_row = document.createElement("div");
    first_row.classList.add("desktop-home-first-row");
    main_content.appendChild(first_row);

    var left_pic = document.createElement("img");
    left_pic.setAttribute('src', './media/restaurant-home-1.jpeg');
    left_pic.classList.add("desktop-home-left-pic");
    left_pic.width = window.innerWidth * 0.55;
    left_pic.height = window.innerWidth * 0.55 * 183 / 275;
    first_row.appendChild(left_pic);

    var about_us_container = document.createElement("div");
    about_us_container.classList.add("desktop-home-about-us-container");
    first_row.appendChild(about_us_container);
    
    var about_us_title = document.createElement("a");
    about_us_title.innerHTML = "About Us";
    about_us_title.classList.add("desktop-home-about-us-title");
    about_us_container.appendChild(about_us_title);

    var about_us_content = document.createElement("a");
    about_us_content.innerHTML = "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?";
    about_us_content.classList.add("desktop-home-about-us-content");
    about_us_container.appendChild(about_us_content);

    var bottom_pic = document.createElement("img");
    bottom_pic.setAttribute('src', './media/restaurant-home-2.jpeg');
    bottom_pic.classList.add("desktop-home-bottom-pic");
    main_content.appendChild(bottom_pic);
}
