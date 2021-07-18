'use strict';
 
var stripe_account_id = document.getElementById("helper").getAttribute('data-stripe_account_id'); 
var stripe = Stripe('pk_test_51J8elwLGQW192ovfOXJfdSNVRLnM2WeeTF0Mk1KaInlzDqvlXk8Em97iK5Xj3zvCGwhfDL7HQqk3Ur5MPdvUKSh5008yyI3tSj', {
    stripeAccount: stripe_account_id
  });

function registerElements(elements, exampleName) {
  var formClass = '.' + exampleName;
  var example = document.querySelector(formClass);

  var form = example.querySelector('form');
  var resetButton = example.querySelector('a.reset');
  var error = form.querySelector('.error');
  var errorMessage = error.querySelector('.message');

  function enableInputs() {
    Array.prototype.forEach.call(
      form.querySelectorAll(
        "input[type='text'], input[type='email'], input[type='tel']"
      ),
      function(input) {
        input.removeAttribute('disabled');
      }
    );
  }

  function disableInputs() {
    Array.prototype.forEach.call(
      form.querySelectorAll(
        "input[type='text'], input[type='email'], input[type='tel']"
      ),
      function(input) {
        input.setAttribute('disabled', 'true');
      }
    );
  }

  function triggerBrowserValidation() {
    // The only way to trigger HTML5 form validation UI is to fake a user submit
    // event.
    var submit = document.createElement('input');
    submit.type = 'submit';
    submit.style.display = 'none';
    form.appendChild(submit);
    submit.click();
    submit.remove();
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
    e.preventDefault();

    // Trigger HTML5 validation UI on the form if any of the inputs fail
    // validation.
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
      triggerBrowserValidation();
      return;
    }
    
    // Hide title
    var title = document.getElementsByClassName("title")[0];
    title.style.display = "none";

    // Show a loading screen...
    example.classList.add('submitting');

    // Disable all inputs.
    disableInputs();

    // Gather additional customer data we may have collected in our form.
    var name = form.querySelector('#' + exampleName + '-name');
    var address1 = form.querySelector('#' + exampleName + '-address');
    var city = form.querySelector('#' + exampleName + '-city');
    var state = form.querySelector('#' + exampleName + '-state');
    var zip = form.querySelector('#' + exampleName + '-zip');
    var additionalData = {
      name: name ? name.value : undefined,
      address_line1: address1 ? address1.value : undefined,
      address_city: city ? city.value : undefined,
      address_state: state ? state.value : undefined,
      address_zip: zip ? zip.value : undefined,
    };

    // set order_info form data
    var input = document.getElementById("inp");
    var name_element = document.getElementById("example1-name");
    input.value = name_element.value;
    
    // send post request with order_info form
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/update-order-details");
    xhr.onload = function(event) {
        alert("success, server responded with: " + event.target.response);
    };
    var formData = new FormData(document.getElementById("order_info"));
    xhr.send(formData);


    var card = elements[0];
    var client_secret = document.getElementById("helper").getAttribute('data-stripe_client_secret');
    stripe.confirmCardPayment(client_secret, {
      payment_method: {
        card: card,
        billing_details: {
          address: {
            postal_code: 93434
          }
        }
      }
    }).then(function(result) {
      // Stop loading!
      example.classList.remove('submitting');
      example.classList.add('submitted');
        

      var checkmark = document.getElementsByClassName("checkmark")[0];
      var border = document.getElementsByClassName("border")[0];
      var result_title = document.getElementsByClassName("result-title")[0];

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
          result_title.innerHTML = "Payment successful";
          resetButton.style.display = "none";
        }
      }
    });    

  resetButton.addEventListener('click', function(e) {
    e.preventDefault();
    // Resetting the form (instead of setting the value to `''` for each input)
    // helps us clear webkit autofill styles.
    form.reset();

    // Clear each Element.
    elements.forEach(function(element) {
      element.clear();
    });

    // Reset error state as well.
    error.classList.remove('visible');

    // reset border
    var border = document.getElementsByClassName("border")[0];
    border.style.stroke = "#87bbfd";
    

    // Resetting the form does not un-disable inputs, so we need to do it separately:
    enableInputs();
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
  });
});
  var price = document.getElementById("helper").getAttribute('data-price');
  price = price / 100;
  var submit_button = document.getElementById("submit-button");
  submit_button.innerHTML = "Pay $" + price;
}
