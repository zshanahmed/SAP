(function ($) {
  "use strict"; // Start of use strict

  // Toggle the side navigation
  $("#sidebarToggle, #sidebarToggleTop").on("click", function (e) {
    $("body").toggleClass("sidebar-toggled");
    $(".sidebar").toggleClass("toggled");
    if ($(".sidebar").hasClass("toggled")) {
      $(".sidebar .collapse").collapse("hide");
    }
  });

  // Close any open menu accordions when window is resized below 768px
  $(window).resize(function () {
    if ($(window).width() < 768) {
      $(".sidebar .collapse").collapse("hide");
    }

    // Toggle the side navigation when window is resized below 480px
    if ($(window).width() < 480 && !$(".sidebar").hasClass("toggled")) {
      $("body").addClass("sidebar-toggled");
      $(".sidebar").addClass("toggled");
      $(".sidebar .collapse").collapse("hide");
    }
  });

  // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
  $("body.fixed-nav .sidebar").on(
    "mousewheel DOMMouseScroll wheel",
    function (e) {
      if ($(window).width() > 768) {
        var e0 = e.originalEvent,
          delta = e0.wheelDelta || -e0.detail;
        this.scrollTop += (delta < 0 ? 1 : -1) * 30;
        e.preventDefault();
      }
    }
  );

  // Scroll to top button appear
  $(document).on("scroll", function () {
    var scrollDistance = $(this).scrollTop();
    if (scrollDistance > 100) {
      $(".scroll-to-top").fadeIn();
    } else {
      $(".scroll-to-top").fadeOut();
    }
  });

  // Smooth scrolling using jQuery easing
  $(document).on("click", "a.scroll-to-top", function (e) {
    var $anchor = $(this);
    $("html, body")
      .stop()
      .animate(
        {
          scrollTop: $($anchor.attr("href")).offset().top,
        },
        1000,
        "easeInOutExpo"
      );
    e.preventDefault();
  });

  $("#delAllyModal").on("show.bs.modal", function (event) {
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
      .attr("href", "/delete/?username=" + recipient);
  });

  $("#eventModal").on("show.bs.modal", function (event) {
    var el = $(event.relatedTarget);

    var start_time = el.data('start')
    var end_time = el.data('end')
    var title = el.data('title')
    var description = el.data('description')
    var location = el.data('location')

    const start_date = new Date(start_time)
    const end_date = new Date(end_time)

    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    var modal = $(this);
    modal
      .find(".modal-title")
      .html("<div><strong>"+title+"</strong></div>");
    modal
      .find(".modal-body")
      .html(
          "<strong>Description:</strong>  "+ description + "<br/>"+
          "<strong>Location:</strong>  "+ location + "<br/>"+
          "<div class='pt-3 d-flex justify-content-between'>" +
          "<div><strong>Start Day:</strong>  "+ start_date.toDateString()+ "</div>" +
          "<div><strong>Start Time:</strong>  "+ start_date.toLocaleTimeString('en-US')+ "</div></div>"+
          "<div class='d-flex justify-content-between'>" +
          "<div><strong>End Day:</strong>  "+ end_date.toDateString()+ "</div>" +
          "<div><strong>End Time:</strong>  "+ end_date.toLocaleTimeString('en-US')+ "</div></div>"
      );
  });

  $('input[type="file"]').change(function(e){
            var fileName = e.target.files[0].name;
            console.log(fileName);
            $('#uploadCsvLabel').text(fileName);
  });

})(jQuery); // End of use strict
