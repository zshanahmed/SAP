(function ($) {
  "use strict"; // Start of use strict

  $("#delAllyProfPicModal").on("show.bs.modal", function (event) {
            var button = $(event.relatedTarget); // Button that triggered the modal
            var recipient = button.data("url"); // Extract info from data-* attributes
            // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
            // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
            var modal = $(this);
            modal
              .find(".modal-title")
              .text("Are you sure you want to delete this user (" + recipient + ")");
            modal
              .find(".modal-footer a")
              .attr("href", "/delete_prof_pic/?username=" + recipient);
          });

})(jQuery); // End of use strict
