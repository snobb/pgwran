/*
 *  pgwran.js
 *  Author: Alex Kozadaev (2014)
 */


/********* Document handler code **********/
$("document").ready(function() {
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        e.target // activated tab
        e.relatedTarget // previous tab
        $("#title").text("PGW-RAN: " + $(".active a").text())
        active_id = $("#menuTab .active")[0].id;
    if (active_id === "subs") {
        console.log("subscribers");
    } else if (active_id === "subs_profile") {
        console.log("subs_profile");
    } else if (active_id === "conn_profile") {
        console.log("conn_profile");
        handleConnProfile();
    } else if (active_id === "settings") {
        console.log("settings");
    }
    });
});

/********* Subscriber profile code **********/
function popSubscribers(subscribers, connections) {
    for (i = 0; i < subscribers.length; i++) {
    }
}

/********* Connection profile code **********/
function handleConnProfile() {
    $.getJSON("/data/connection/", {}, function(data) {
        message = "";
        obj = data.connection
        for(i=0; i < obj.length; i++) {
            message += '<li><a href="#" class="action" id="' + i + '">' + obj[i].name + '</a></li>';
        }
        $("#conn_dropdown_mark").first().prepend(message);
        $("#conn_dropdown_mark a.action").on("click", function(data) {
            populateConnProfile(this.id);
        });
        $("#conn_dropdown_mark a#connNew").on("click", function(data) {
            newConnProfile()
        });
        populateConnProfile(0)
    });
    return false;
}

function newConnProfile() {
    $("#cprof_name").val("New connection");
    $("#cprof_description").val("");
    $("#cprof_speed_down").val(0);
    $("#cprof_speed_up").val(0);
    $("#cprof_speed_var").val(0);
    $("#cprof_latency_down").val(0);
    $("#cprof_latency_up").val(0);
    $("#cprof_latency_jitter").val(0);
    $("#cprof_loss_down").val(0);
    $("#cprof_loss_up").val(0);
    $("#cprof_loss_jitter").val(0);
}

function populateConnProfile(id) {
    $("#cprof_name").val(obj[id].name);
    $("#cprof_description").val(obj[id].description);
    $("#cprof_speed_down").val(obj[id].speed_down);
    $("#cprof_speed_up").val(obj[id].speed_up);
    $("#cprof_speed_var").val(obj[id].speed_var);
    $("#cprof_latency_down").val(obj[id].latency_down);
    $("#cprof_latency_up").val(obj[id].latency_up);
    $("#cprof_latency_jitter").val(obj[id].latency_jitter);
    $("#cprof_loss_down").val(obj[id].loss_down);
    $("#cprof_loss_up").val(obj[id].loss_up);
    $("#cprof_loss_jitter").val(obj[id].loss_jitter);
}

/* vim: ts=4 sts=8 sw=4 smarttab et si tw=80 ci cino+=t0(0:0 fo=crtocl list */

