function toggleShow(elementId) {
  let el = document.getElementById(elementId);
  el.style.display = "block";
}

function toggleHide(elementId) {
  let el = document.getElementById(elementId);
  el.style.display = "none";
}



$(document).ready(function(){

 $('#ButonListaDevize').click(function(){
     //https://makitweb.com/dynamically-load-content-in-bootstrap-modal-with-ajax/
   var devizID = $(this).data('id');
   // AJAX request
   $.ajax({
    url: '/api/datadevize/'+devizID,
       dataType: 'json',
    //url:'fiddle.jshell.net',
    // type: 'post',
    // data: {userid: userid},
    success: function(response) {
        // Add response in Modal body

        // Display Modal
        $('#empModal').modal('show');
       // alert("OK 2"+this.url);
        Devize=response['data']
        DevizeLink=response['datalink']
        let fLen = Devize.length;
        let text = "<ul>";
        for (let i = 0; i < fLen; i++) {
          text += '<li><a class="btn btn-dark" href="' + DevizeLink[i] +'">'  + Devize[i] + "</a></li>";
        }
        text += "</ul>";

        $('.modal-body').html(text);


    },
    fail : function (response) {
        alert("mata");
    }
  });
 });
 $("#urcaRepere").click(function() {

          $(this).prop("disabled", true);
      // add spinner to button
      $(this).html(
        `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`
      );
        });

});



function BtnLoading(elem) {
        $(elem).attr("data-original-text", $(elem).html());
        $(elem).prop("disabled", true);
        $(elem).html('<i class="spinner-border spinner-border-sm"></i> Loading...');
    }

    function BtnReset(elem) {
        $(elem).prop("disabled", false);
        $(elem).html($(elem).attr("data-original-text"));
    }
