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
            handleSubsProfile();
        } else if (active_id === "conn_profile") {
            console.log("conn_profile");
            handleConnProfile();
        } else if (active_id === "settings") {
            console.log("settings");
            handleSettings()
        }
    });
});

/********* Subscriber profile code **********/
function handleSubsProfile() {
    $.getJSON('/data/subs_profile/', {}, function(data) {
        message = "";
        obj = data.subs_profiles;
        for(i=0; i < obj.length; i++) {
            message += '<li><a href="#" class="action" id="' + i + '">' + obj[i].name + '</a></li>'
        }
        $("#subs_dropdown_mark li").first().before(message);
        $("#subs_dropdown_mark a.action").on("click", function(data) {
            populateSubsProfile(this.id);
        });
        $("#subs_dropdown_mark a#subsNew").on("click", function(data) {
            newSubsProfile()
        });
        populateSubsProfile(0)
    }).fail(function (jqXHR, textStatus) {
        console.log(jqXHR);
        console.log(jqXHR.statusText);
    });
    return false;

}

function newSubsProfile() {
    $("#subs_name").val("New connection");
    $("#subs_ipaddr").val("");
    $("#subs_acct_interval").val("");
    $("#subs_calling_id").val("");
    $("#subs_called_id").val("");
    $("#subs_imsi").val("");
    $("#subs_imei").val("");
    $("#subs_loc_info").val("");
    $("#subs_id").val(-1);
}

function populateSubsProfile(id) {
    $("#subs_id").val(obj[id].subs_id);
    $("#subs_name").val(obj[id].name);
    $("#subs_ipaddr").val(obj[id].ipaddr);
    $("#subs_calling_id").val(obj[id].calling_id);
    $("#subs_called_id").val(obj[id].called_id);
    $("#subs_imsi").val(obj[id].imsi);
    $("#subs_imei").val(obj[id].imei);
    $("#subs_loc_info").val(obj[id].loc_info);
}

/********* Connection profile code **********/
function handleConnProfile() {
    $.getJSON("/data/conn_profile/", {}, function(data) {
        message = "";
        obj = data.conn_profiles
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
    }).fail(function (jqXHR, textStatus) {
        console.log(jqXHR);
        console.log(jqXHR.statusText);
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

/********* Settings code **********/
function handleSettings() {
    $.getJSON("/data/settings/", {}, function(data) {
        message = "";
        obj = data.settings
        populateSettings()
    }).fail(function (jqXHR, textStatus) {
        console.log(jqXHR);
        console.log(jqXHR.statusText);
    });

    return false;
}


function populateSettings() {
    $("#settings_rad_ip").val(obj.rad_ip);
    $("#settings_rad_port").val(obj.rad_port);
    $("#settings_rad_user").val(obj.rad_user);
    $("#settings_rad_pass").val(obj.rad_pass);
    $("#settings_rad_secret").val(obj.rad_secret);
}

/* vim: ts=4 sts=8 sw=4 smarttab et si tw=80 ci cino+=t0(0:0 fo=crtocl list */

