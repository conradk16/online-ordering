'use strict';

var customers_pay_online = document.getElementById("helper").getAttribute('data-customers_pay_online') == "True";

if (customers_pay_online) {
    var stripe_account_id = document.getElementById("helper").getAttribute('data-stripe_account_id');
    var stripe_publishable_api_key = document.getElementById("helper").getAttribute('data-stripe_publishable_api_key');
    var stripe = Stripe(stripe_publishable_api_key, {
        stripeAccount: stripe_account_id
      });
} else {
  var stripe_publishable_api_key = document.getElementById("helper").getAttribute('data-stripe_publishable_api_key');
  var stripe = Stripe(stripe_publishable_api_key);
}

var restaurant_display_name = document.getElementById("helper").getAttribute('data-restaurant_display_name');

function set_error_msg(msg) {
    var msg_elem = document.getElementById("error_msg");
    msg_elem.innerHTML = msg;
}

function enableInputs(form) {
    Array.prototype.forEach.call(
        form.querySelectorAll(
            "input[type='text'], input[type='email'], input[type='tel']"
        ),
        function(input) {
            input.removeAttribute('disabled');
        }
    );
}

function disableInputs(form) {
    Array.prototype.forEach.call(
        form.querySelectorAll(
            "input[type='text'], input[type='email'], input[type='tel']"
        ),
        function(input) {
            input.setAttribute('disabled', 'true');
        }
    );
}

function triggerBrowserValidation(form) {
    // The only way to trigger HTML5 form validation UI is to fake a user submit
    // event.
    var submit = document.createElement('input');
    submit.type = 'submit';
    submit.style.display = 'none';
    form.appendChild(submit);
    submit.click();
    submit.remove();
}

function xhrOnLoadPayOnline(event, example, resetButton, client_secret, card, email_input_value) {
    var checkmark = document.getElementsByClassName("checkmark")[0];
    var border = document.getElementsByClassName("border")[0];
    var result_title = document.getElementsByClassName("result-title")[0];

    if (event.target.response != "accepting orders") {
        // Stop loading!
        example.classList.remove('submitting');
        example.classList.add('submitted');

        console.log(event.target.response);


        if (event.target.response == "not accepting orders") {
            result_title.innerHTML = "Sorry, orders are no longer being accepted.";
            resetButton.style.display = "none";
        } else if (event.target.response == "invalid email") {
            result_title.innerHTML = "Payment failed: invalid email address.";
        } else {
            result_title.innerHTML = "Payment failed";
        }
    } else {
        stripe.confirmCardPayment(client_secret, {
            payment_method: {
                card: card,
            }
        }).then(function(result) {
            // Stop loading!
            example.classList.remove('submitting');
            example.classList.add('submitted');

            if (result.error) {
                console.log(result.error.message);
                checkmark.setAttribute("d", "M25 25 59 59 M 25 59 59 25");
                border.style.stroke = "#de0909";
                result_title.innerHTML = "Payment failed";
            }
            else {
                // The payment has been processed!
                if (result.paymentIntent.status == 'succeeded') {
                    console.log("success");
                    checkmark.setAttribute("d", "M23.375 42.5488281 36.8840688 56.0578969 64.891932 28.0500338");
                    result_title.innerHTML = "Thank you, your order has been placed.";
                    var caption = document.getElementById("caption");
                    caption.innerHTML = "An email receipt has been sent to " + email_input_value + "."
                    resetButton.style.display = "none";
                }
            }
        });
    }
}

function xhrOnLoadPayInStore(event, example, resetButton) {
    console.log(event.target.response);
    var checkmark = document.getElementsByClassName("checkmark")[0];
    var border = document.getElementsByClassName("border")[0];
    var result_title = document.getElementsByClassName("result-title")[0];

    // Stop loading!
    example.classList.remove('submitting');
    example.classList.add('submitted');

    if (event.target.response == "accepting orders") {
        checkmark.setAttribute("d", "M23.375 42.5488281 36.8840688 56.0578969 64.891932 28.0500338");
        result_title.innerHTML = "Thank you, your order has been placed.";
        resetButton.style.display = "none";
    } else if (event.target.response == "not accepting orders") {
        checkmark.setAttribute("d", "M25 25 59 59 M 25 59 59 25");
        border.style.stroke = "#de0909";
        result_title.innerHTML = "Sorry, orders are no longer being accepted.";
        resetButton.style.display = "none";
    } else if (event.target.response == "discount applied") {
        checkmark.setAttribute("d", "M23.375 42.5488281 36.8840688 56.0578969 64.891932 28.0500338");
        result_title.innerHTML = "Thank you, your order has been placed.";
        var caption = document.getElementById("caption");
        caption.innerHTML = "Your discount will be applied when you pay in-store."
        resetButton.style.display = "none";
    } else if (event.target.response == "discount failed") {
        example.classList.remove('submitted');
        // Show title
        var title = document.getElementsByClassName("title")[0];
        title.style.display = "block";
        var form = document.getElementById("form");
        resetForm(form, "*Invalid Discount Code", example, resetButton);
    } else {
        checkmark.setAttribute("d", "M25 25 59 59 M 25 59 59 25");
        border.style.stroke = "#de0909";
        result_title.innerHTML = "Order failed.";
    }
}

function resetFormFromClick(e, form, elements, error, error_msg, example, resetButton) {
    e.preventDefault();

    // Clear each Element.
    elements.forEach(function(element) {
        element.clear();
    });

    // Reset error state as well.
    error.classList.remove('visible');

    resetForm(form, error_msg, example, resetButton);
}

function resetForm(form, error_msg, example, resetButton) {
    // Resetting the form (instead of setting the value to `''` for each input)
    // helps us clear webkit autofill styles.
    form.reset();

    // reset border
    var border = document.getElementsByClassName("border")[0];
    border.style.stroke = "#87bbfd";


    // Resetting the form does not un-disable inputs, so we need to do it separately:
    enableInputs(form);
    example.classList.remove('submitted');

    // remove title if necessary
    var title = document.getElementsByClassName("title")[0];
    if (title) { title.remove(); }

    // add back the title
    var example1 = document.getElementsByClassName("cell example example1")[0];
    var title = document.createElement("h1");
    title.classList.add("title");
    title.innerHTML = "Enter Payment Details";
    example1.prepend(title);

    // set the error message
    set_error_msg(error_msg);

    // clear the (hidden) order info form
    var order_info_form = document.getElementById("order_info");
    const num_children = order_info_form.length;
    for (let i = 0; i < num_children; i++) {
        order_info_form[0].remove();
    }

}

function onSubmit(e, form, example, resetButton) {
    e.preventDefault();

    // Trigger HTML5 validation UI on the form if any of the inputs fail
    // validation.
    if (customers_pay_online) {
        var plainInputsValid = true;
        Array.prototype.forEach.call(form.querySelectorAll('input'), function(
          input
        ) {
          if (input.checkValidity && !input.checkValidity()) {
            plainInputsValid = false;
            return;
          }
        });
        if (!plainInputsValid) {
          triggerBrowserValidation(form);
          return;
        }
    }

    // Hide title
    var title = document.getElementsByClassName("title")[0];
    title.style.display = "none";

    // Show a loading screen...
    example.classList.add('submitting');

    // Disable all inputs.
    disableInputs(form);

    // set order_info form data
    var name_element = document.getElementById("example1-name");
    var email_element = document.getElementById("example1-email");
    var discount_code_element = document.getElementById("example1-discount-code");

    var order_info_form = document.getElementById("order_info");
    var name_input = document.createElement("input");
    name_input.type = "hidden";
    name_input.name = "customer_name";
    name_input.value = name_element.value;
    order_info_form.appendChild(name_input);

    var email_input = document.createElement("input");
    email_input.type = "hidden";
    email_input.name = "customer_email";
    email_input.value = email_element.value;
    order_info_form.appendChild(email_input);

    var discount_code_input = document.createElement("input");
    discount_code_input.type = "hidden";
    discount_code_input.name = "discount_code";
    discount_code_input.value = discount_code_element.value;
    order_info_form.appendChild(discount_code_input);

    if (!customers_pay_online) {
        var order_id = document.getElementById("helper").getAttribute('data-order_id');
        var order_id_input = document.createElement("input");
        order_id_input.type = "hidden";
        order_id_input.name = "order_id";
        order_id_input.value = order_id;
        order_info_form.appendChild(order_id_input);

    } else {
        var payment_intent_id = document.getElementById("helper").getAttribute('data-payment_intent_id');
        var payment_intent_id_input = document.createElement("input");
        payment_intent_id_input.type = "hidden";
        payment_intent_id_input.name = "payment_intent_id";
        payment_intent_id_input.value = payment_intent_id;
        order_info_form.appendChild(payment_intent_id_input);

        var connected_account_id = document.getElementById("helper").getAttribute('data-stripe_account_id');
        var connected_account_id_input = document.createElement("input");
        connected_account_id_input.type = "hidden";
        connected_account_id_input.name = "connected_account";
        connected_account_id_input.value = connected_account_id
        order_info_form.appendChild(connected_account_id_input);

        var client_secret = document.getElementById("helper").getAttribute('data-stripe_client_secret');
    }

    // send post request with order_info form
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/update-order-details");
    xhr.onload = function(event) {
        if (!customers_pay_online) {
            xhrOnLoadPayInStore(event, example, resetButton);
        } else {
            xhrOnLoadPayOnline(event, example, resetButton, client_secret, elements[0], email_input.value);
        }
    }

    var order_info_formData = new FormData(document.getElementById("order_info"));
    xhr.send(order_info_formData);

    resetButton.addEventListener('click', function(e) {
        resetFormFromClick(e, form, elements, error, "", example, resetButton);
    });
}

function registerElements(elements, exampleName) {
  var formClass = '.' + exampleName;
  var example = document.querySelector(formClass);

  var form = example.querySelector('form');
  var resetButton = example.querySelector('a.reset');
  var error = form.querySelector('.error');
  var errorMessage = error.querySelector('.message');


  if (!customers_pay_online) {
    // change title
    var title = document.getElementsByClassName("title")[0];
    title.innerHTML = "Confirm Order"

    // remove card input
    var card_input = document.getElementById("example1-card");
    var card_row = document.getElementById("card-row");
    var card_fieldset = document.getElementById("card-fieldset");
    card_input.remove();
    card_row.remove();
    card_fieldset.remove();

    // set button text
    var button = document.getElementById("submit-button");
    button.innerHTML = "Place Pickup Order";
  } else {
    // set button text
    var price = document.getElementById("helper").getAttribute('data-price');
    price = price / 100;
    price = price.toFixed(2);
    var submit_button = document.getElementById("submit-button");
    submit_button.innerHTML = "Pay $" + price;
  }

  // Listen for errors from each Element, and show error messages in the UI.
  var savedErrors = {};
  elements.forEach(function(element, idx) {
    element.on('change', function(event) {
      if (event.error) {
        error.classList.add('visible');
        savedErrors[idx] = event.error.message;
        errorMessage.innerText = event.error.message;
      } else {
        savedErrors[idx] = null;

        // Loop over the saved errors and find the first one, if any.
        var nextError = Object.keys(savedErrors)
          .sort()
          .reduce(function(maybeFoundError, key) {
            return maybeFoundError || savedErrors[key];
          }, null);

        if (nextError) {
          // Now that they've fixed the current error, show another one.
          errorMessage.innerText = nextError;
        } else {
          // The user fixed the last error; no more errors.
          error.classList.remove('visible');
        }
      }
    });
  });
 
  // Listen on the form's 'submit' handler...
  form.addEventListener('submit', function(e) {
    onSubmit(e, form, example, resetButton);
  });
}
