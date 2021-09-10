// send null for no class_name, innerHTML, or href
// create_element returns the element
function create_element(type, parent_elem, class_name, innerHTML, href, src) {
    var elem = document.createElement(type);
    if (class_name != null) {
        elem.classList.add(class_name);
    }
    if (innerHTML != null) {
        elem.innerHTML = innerHTML;
    }
    if (href != null) {
        elem.href = href;
    }
    if (src != null) {
        elem.src = src;
    }
    parent_elem.appendChild(elem);
    return elem;
}

