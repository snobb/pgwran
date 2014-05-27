/*
 *  pgwran.js
 *  Author: Alex Kozadaev (2014)
 */

$("document").ready(function() {
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        e.target // activated tab
        e.relatedTarget // previous tab
        $("#title").text("PGW-RAN: " + $(".active a").text())
        active_id = $("#menuTab .active")[0].id;
        if (active_id === "subs") {
            $.getJSON("/data/connection/", {}, function(data) {
                obj = data.connections
                for(i=0; i < obj.length; i++) {
                message += '<li><a href="#" class="action" id="' + i + '">' + obj[i].name + '</a></li>';
                }
            $("#conn_dropdown_mark").first().prepend(message);
            $("#conn_dropdown_mark a.action").on("click", function(data) {
                popConnection(this.id);
            });
            $("#conn_dropdown_mark a#connNew").on("click", function(data) {
                $("#name").val("New connection");
                $("#description").val("");
                $("#speed_down").val(0);
                $("#speed_up").val(0);
                $("#speed_var").val(0);
                $("#latency_down").val(0);
                $("#latency_up").val(0);
                $("#latency_jitter").val(0);
                $("#loss_down").val(0)
                $("#loss_up").val(0)
                $("#loss_jitter").val(0)
                $("#conn_id").val(-1)
            });
            popConnection(0);

            });
        } else if (active_id === "subs_profile") {
            console.log("subs_profile")
        } else if (active_id === "conn_profile") {
            console.log("conn_profile")
        } else if (active_id === "settings") {
            console.log("settings")
        }
    })
});

function popSubscribers(subscribers, connections) {
    for (i = 0; i < subscribers.length; i++) {
        $("").
    }
}

function popConnection(id) {
    $("#name").val(obj[id].name);
    $("#description").val(obj[id].description);
    $("#speed_down").val(obj[id].speed_down);
    $("#speed_up").val(obj[id].speed_up);
    $("#speed_var").val(obj[id].speed_var);
    $("#latency_down").val(obj[id].latency_down);
    $("#latency_up").val(obj[id].latency_up);
    $("#latency_jitter").val(obj[id].latency_jitter);
    $("#loss_down").val(obj[id].loss_down);
    $("#loss_up").val(obj[id].loss_up);
    $("#loss_jitter").val(obj[id].loss_jitter);
    $("#conn_id").val(obj[id].conn_id);
}

/* vim: ts=4 sts=8 sw=4 smarttab et si tw=80 ci cino+=t0(0:0 fo=crtocl list */

