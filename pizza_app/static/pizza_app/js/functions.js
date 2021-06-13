$(document).ready( function() {

    // evento al seleccionar un author
    $('#combobox').change( function () {
        console.log('change')
        var optionSelected = $("option:selected", this);
        var optionSelected = $("option:selected", this);
        var valueSelected = this.text;
        console.log(optionSelected)
        console.log(valueSelected)

        $('#inputText').val($("#combobox option:selected" ).text())

    });
    
});

function get_price2(id) {
    console.log('click get price: ' + id)
    var csrf = $("input[name=csrfmiddlewaretoken]").val();
    console.log(csrf)
    $.ajax({
        method : "GET",
        url : "/get_price/"+id,
        dataType : "JSON",
        data : {
            csrfmiddlewaretoken: csrf
        }
    })
    .done (function(response){
        console.log(response)
        $('#price').val(response["price"])
    })
}

function get_price(){
    var data = $("#form_create_pizza").serialize()
    $.ajax({
        method : "POST",
        url : "/get_price",
        data : data,
        dataType : "JSON"
    })
    .done (function(response){
        console.log(response)
        $('#price').val(response["price"])
    })
}

function deleteComment(id) {
    console.log('click comentario: ' + id)
    var csrf = $("input[name=csrfmiddlewaretoken]").val();
    console.log(csrf)
    $.ajax({
        method : "GET",
        url : "/wall/delete_comment_ajax/"+id,
        dataType : "JSON",
        data : {
            csrfmiddlewaretoken: csrf
        }
    })
    .done (function(response){
        console.log(response)
        var size = Object.keys(response["alert"]).length
        if ( size > 0 ) {
            alert(response["alert"])
            //$('#messages').html(JSON.stringify(response["errors"]));
        }
    })

}



function addComment(formComment){
    var data = $("#"+formComment).serialize()
    $.ajax({
        method : "POST",
        url : "/wall/add_comment_ajax",
        data : data,
        dataType : "JSON"
    })
    .done (function(response){
        var size = Object.keys(response["alert"]).length
        if ( size > 0 ) {
            alert(response["alert"])
        } else {
            console.log("no hay mensajes")
        }

    })
    location.reload();
}
