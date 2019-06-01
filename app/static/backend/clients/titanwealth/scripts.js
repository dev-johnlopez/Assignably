

$(document).ready(function() {
  $('form').parsley();
  $( "#assignably_form" ).submit(function( event ) {
    event.preventDefault();
    swal({
      title: 'Sending your deal...',
      text: 'One moment while we process your deal.',
      showCancelButton: false,
      showConfirmButton: false
    })
    $.ajax({
      url: 'https://assignably.herokuapp.com/api/deals',
      async:true,
      type: "POST",
      data: JSON.stringify({
        "address": {
          "line_1": $( "#line_1" ).val(),
          "line_2": $( "#line_2" ).val(),
          "line_3": "",
          "line_4": "",
          "city": $( "#city" ).val(),
          "state_code": $( "#state_code" ).val(),
          "postal_code": $( "#postal_code" ).val()
        },
        "submitted_by": {
          "first_name": $( "#first_name" ).val(),
          "last_name": $( "#last_name" ).val(),
          "phone": $( "#phone_number" ).val(),
          "email": $( "#email" ).val()
        },
        "property_tax": parseInt($( "#property_tax" ).val()),
        "sq_feet": parseInt($( "#sq_feet" ).val()),
        "bedrooms_str": $( "#bedrooms" ).val(),
        "bathrooms_str": $( "#bathrooms" ).val(),
        "after_repair_value": parseInt($( "#after_repair_value" ).val()),
        "rehab_estimate": parseInt($( "#rehab_estimate" ).val()),
        "purchase_price": parseInt($( "#purchase_price" ).val()),
        "list_price": parseInt($( "#list_price" ).val()),
        "under_contract_ind": parseInt($( "#under_contract_ind" ).val())
      }),
      beforeSend: function (xhr) {
          xhr.setRequestHeader('Authorization', 'Bearer YCHV9VsAWNlRdKYh3OlhaBLDodITjc8olta6+C5oUKU=');
          xhr.setRequestHeader('Content-Type', 'application/json');
      }
    }).done(function(data) {
        swal("Thank you!", "We have received your submission. Please sit tight - we are analyzing your deal and will call/email you soon.", "success");
    })
    .fail(function(xhr, status, error) {
        swal("Oh no!", "We were unable to process your request. Please email us at info@titanwealthgroup.com.", "error");
    });
  });
});
