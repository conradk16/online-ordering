'use strict';
function update_file_name(is_website_setup) {
    var file_input = document.getElementById('file_upload');
    var file_name = document.getElementById('file_name');
    if (file_input.files.length == 0) {
        return;
    }

    if (!is_website_setup && file_input.files[0].size > 10097152) {
        alert("File must be smaller than 10 MB");
        file_input.value = "";
        file_name.innerHTML = "";
        return;
    } else if (is_website_setup && file_input.files[0].size > 26214400) {
        alert("File must be smaller than 25 MB");
        file_input.value = "";
        file_name.innerHTML = "";
        return;
    }


    var fullPath = file_input.value;
    var startIndex = (fullPath.indexOf('\\') >= 0 ? fullPath.lastIndexOf('\\') : fullPath.lastIndexOf('/'));
    var filename = fullPath.substring(startIndex);
    if (filename.indexOf('\\') === 0 || filename.indexOf('/') === 0) {
        filename = filename.substring(1);
    }

    var file_name_element = document.getElementById("file_name");
    file_name.innerHTML = filename;
  }

  function getErrorElement() {
    return document.getElementsByClassName("invalid-input-text")[0];
  }

  function submit_form() {
    var form = document.getElementById("form");
    form.submit();
  }
