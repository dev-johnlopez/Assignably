$(document).ready(function() {
  "use strict";
  $("#basicwizard").bootstrapWizard(),
  $("#rootwizard").bootstrapWizard({
    onNext: function(t,r,a) {
      var o=$($(t).data("targetForm"));
      if(o&&(o.addClass("was-validated"),!1===o[0].checkValidity()))
        return event.preventDefault(),event.stopPropagation(),!1
      }
    }
  )}
);
