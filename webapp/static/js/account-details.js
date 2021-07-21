'use strict';

function update_file_name() {
    var file_input = document.getElementById('file_upload');
    if(file_input.files[0].size > 10097152){
       alert("File must be smaller than 10 MB");
       this.value = "";
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

  // creates the element if it doesn't exist
  function getErrorElement() {
    if (document.getElementsByClassName("invalid-input-text").length == 0) {
        var invalid_input_text = document.createElement("span");
        invalid_input_text.classList.add("invalid-input-text");
        var form = document.getElementById("form");
        form.appendChild(invalid_input_text);
        return invalid_input_text;
    } else {
        return document.getElementsByClassName("invalid-input-text")[0];
    }
  }

  function submit_form() {
    var form = document.getElementById("form");
    form.submit();
  }

