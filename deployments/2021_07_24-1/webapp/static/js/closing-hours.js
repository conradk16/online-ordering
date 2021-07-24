'use strict';

  function update_input_text(text_input_id, checkbox_input_id) {
    var checkbox = document.getElementById(checkbox_input_id);
    var text_input = document.getElementById(text_input_id);
    if (checkbox.checked) {
        text_input.value = "";
    }
  }

  function clear_checkbox(checkbox_input_id) {
    var checkbox = document.getElementById(checkbox_input_id);
    checkbox.checked = false;
  }

  // returns an array of dictionaries matching given criteria
  // day is a string (lowercase day of week)
  // time is a string (could be multiple comma-separated times)
  // time_zone is a string with the time zone

  // returns null if invalid criteria

  function get_times(day_of_week, times, time_zone) {
    if (times.length == 0) {
        return null;
    }

    var to_return = new Array();
    const time_strings = times.split(",")
    for (var time of time_strings) {
        time = time.trim();
        const halves = time.split(":"); // hour and minutes
        if (halves.length != 2) {
            return null;
        }
        var hr = parseInt(halves[0]);
        if (isNaN(hr) || hr < 0 || hr > 12) {
            return null;
        }
        const minutes_and_ampm = halves[1];
        if (minutes_and_ampm.length < 3) {
            return null;
        }
        const minutes = parseInt(minutes_and_ampm.substring(0, minutes_and_ampm.length-2));
        const ampm = minutes_and_ampm.substring(minutes_and_ampm.length-2);
        if (isNaN(minutes) || minutes < 0 || minutes > 59) {
            return null;
        }
        if (ampm != "am" && ampm != "pm") {
            return null;
        }

        if (day_of_week == "Monday") { var day = 0; }
        else if (day_of_week == "Tuesday") { var day = 1; }
        else if (day_of_week == "Wednesday") { var day = 2; }
        else if (day_of_week == "Thursday") { var day = 3; }
        else if (day_of_week == "Friday") { var day = 4; }
        else if (day_of_week == "Saturday") { var day = 5; }
        else if (day_of_week == "Sunday") { var day = 6; }

        // convert to 24-hr
        if (ampm == "pm" && hr != 12) {
            hr += 12;
        } else if (ampm == "am" && hr == 12) {
            hr = 0;
        }

        // add to array
        var dict = {};
        dict["day"] = day;
        dict["hour"] = hr;
        dict["minute"] = minutes;
        dict["timezone"] = time_zone;
        to_return.push(dict);

    }
    return to_return;
  }

  function getErrorElement() {
    return document.getElementsByClassName("invalid-input-text")[0];
  }

  // returns null on error, time zone string on success
  function validate_time_zone() {
     var time_zone = document.getElementsByClassName("drop-down")[0].value;
      if (time_zone == "") {
        var invalid_input_text = getErrorElement();
        invalid_input_text.innerHTML = "*Please select a time zone";
        return null;
      } else {
        return time_zone;
      }
  }


  function validate_form() {
    // validate time zone
    var is_update = document.getElementById("closing-times-script").getAttribute('data-is_update') == "true";
    if (!is_update) {
        var time_zone = validate_time_zone();
        if (time_zone == null) {
            return;
        }
    } else {
        var closing_times = JSON.parse(document.getElementById("closing-times-script").getAttribute('data-closing_times'));
        var time_zone = document.getElementById("closing-times-script").getAttribute('data-timezone');
    }

    // validate days of the week and add them to array

    var arr = new Array();

    var time_elements = document.getElementsByClassName("time");
    var checkboxes = document.getElementsByClassName("checkbox");
    var day_labels = document.getElementsByClassName("day-label");
    for (let i = 0; i < time_elements.length; i++) {
        const time = time_elements[i].value;
        const checked = checkboxes[i].checked;
        const day = day_labels[i].innerHTML;

        if (!checked && time == "") {
            var invalid_input_text = getErrorElement();
            invalid_input_text.innerHTML = "*Please enter a closing time for " + day + " or mark as closed for that day.";
            return;
        }

        if (checked) {
            continue;
        }

        var times = get_times(day, time, time_zone);
        if (times == null) {
            var invalid_input_text = getErrorElement();
            invalid_input_text.innerHTML = "*Invalid entry for " + day + ", please enter a valid time or times, for example, \"8:00pm\" or \"2:00pm, 6:00pm\".";
            return;
        }

        // add times to the array
        for (const time of times) {
            arr.push(time);
        }
    }

    var input = document.getElementById("inp");
    input.value = JSON.stringify(arr);
    var input_timezone = document.getElementById("inp-timezone");

    if (input_timezone) {
        input_timezone.value = time_zone;
    }

    /*arr = JSON.parse(input.value);
    for (const elem of arr) {
        console.log(elem["day"] + ", " + elem["hour"] + ", " + elem["minute"] + ", " + elem["timezone"]);
    }*/

    submit_form();
  }

  function submit_form() {
    var form = document.getElementById("closing_times_to_send");
    form.submit();
  }
