$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-events .modal-content").html("");
        $("#modal-events").modal("show");
      },
      success: function (data) {
        $("#modal-events .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#events-table tbody").html(data.html_events_list);
          $("#modal-events").modal("hide");
        }
        else {
          $("#modal-events .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };




  /* Binding */

  // Create book
  $(".js-create-events").click(loadForm);
  $("#modal-events").on("submit", ".js-events-create-form", saveForm);

  // Update book
  $("#events-table").on("click", ".js-update-events", loadForm);
  $("#modal-events").on("submit", ".js-events-update-form", saveForm);

  // Delete book
  $("#events-table").on("click", ".js-delete-events", loadForm);
  $("#modal-events").on("submit", ".js-events-delete-form", saveForm);

});
