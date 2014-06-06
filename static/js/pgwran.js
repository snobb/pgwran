/*
 *  pgwran.js
 *  Author: Alex Kozadaev (2014)
 */


/********* Document handler code **********/
$('document').ready(function() {
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        e.target // activated tab
        e.relatedTarget // previous tab
        $('#title').text('PGW-RAN: ' + $('.active a').text())

        active_id = $('#menuTab .active')[0].id;

        if (active_id === 'menu_subs') {
            console.log('subscribers');
            //handleSubscribers();
        } else if (active_id === 'menu_subs_profile') {
            handleSubsProfile();
        } else if (active_id === 'menu_conn_profile') {
            handleConnProfile();
        } else if (active_id === 'menu_settings') {
            handleSettings();
        }
    });
});

/********* Subscribers code **********/
function handleSubscribers() {
    updateSubscribersData();
};

function updateSubscribersData(t) {
    $('.subscribers_body').html("");
    template = t.html();
    $.getJSON('/json/subscribers/get/', {}, function(data) {
        console.log(data);
        if (data.success) {
            var subs_body = "";
            for (var i = 0; i < data.subscribers.length; i++) {
                subs_body += getTemplate(data.subscribers[i].subs_id);
            }
            $('.subs_body').html(html);
        } else {
            showError("ERROR: " + data.statusText);
        }
    }).fail(function(e) {
        showError("ERROR: " + e.statusText);
    });
}

function getTemplate(id) {
    return
        '<div class="panel panel-default" id="' + id + '>  ' +
        '    <div class="panel-body"> ' +
        '        <input type="hidden" name="subs_id" id="subs_id" value="' + id + '"> ' +
        '        <div class="row"> ' +
        '            <div class="col-md-5"> ' +
        '                <div class="input-group"> ' +
        '                    <span class="input-group-addon">Subscriber</span> ' +
        '                    <input type="text" class="form-control input-sm" id="name" name="name" readonly="true"> ' +
        '                </div> ' +
        '            </div> ' +
        '            <div class="col-md-5"> ' +
        '                <div class="input-group"> ' +
        '                    <!-- Button and dropdown menu --> ' +
        '                    <span class="input-group-addon">Connection</span> ' +
        '                    <select name="conn_id" class="form-control input-sm"> ' +
        '                    </select> ' +
        '                </div> ' +
        '            </div> ' +
        '            <div class="col-md-1"> ' +
        '                <input type="checkbox" class="cbox"> ON ' +
        '            </div> ' +
        '        </div> ' +
        '    </div> ' +
        '</div>';
}

/********* Subscriber profile code **********/
function handleSubsProfile() {
    $('#button_subs_delete').on('click', function(data) {
        $('#modal_subscriber').modal('show');
        $('#button_subs_ok').on('click', function(data) {
            $('#modal_subscriber').modal('hide');
            form = $('#subsForm');
            $.getJSON('/json/subs_profile/delete/' +
                      $('#sprof_subs_id').val(), {}, function(data) {
                // output success
                showSuccess("The value has been deleted successfully");
                updateSubscriberProfileData(0);
            }).fail(function(data) {
                showError("ERROR: " + data.statusText);
            });
        });
    });


    $('#button_subs_save').on('click', function(data) {
        if ($('#sprof_subs_ipaddr').val() == "") {
            showError('ERROR: IP address field is required');
            return false;
        }
        $.ajax({
            type: 'POST',
            url: '/json/subs_profile/save/',
            data: $('#sprof_subs_form').serialize(),
            success: function(response) {
                if (response.success) {
                    showSuccess(response.statusText);
                    if (response.data.action == 'insert') {
                        $('#sprof_subs_id').val(response.data.subs_id);
                        updateSubscriberProfileData(response.data.subs_id)
                    }
                } else {
                    showError(response.statusText);
                }
            }
        }).fail(function(e) {
            showError('ERROR: ' + e.statusText);
        });
    });

    updateSubscriberProfileData(0);
    return false;
}

function updateSubscriberProfileData(current) {
    $.getJSON('/json/subs_profile/get/', {}, function(data) {
        if (data.success) {
            message = '';
            obj = data.data.subs_profiles;
            for(i=0; i < obj.length; i++) {
                message += '<li><a href="#" class="action" id="' +
                    i +'">' + obj[i].name + '</a></li>';
            }
            $('#subs_dropdown_mark')
                .first()
                .html('<li class="divider"></li>' +
                      '<li><a href="#" id="subs_new">Create New</a></li>')
                .prepend(message);
            $('#subs_dropdown_mark a.action').on('click', function(e) {
                populateSubsProfile(obj[this.id]);
            });
            $('#subs_dropdown_mark a#subs_new').on('click', function(e) {
                newSubsProfile();
            });
            $('#subs_dropdown_mark #' + current).click()
        } else {
            showError("ERROR: " + data.statusText)
        }
    }).fail(function(e) {
        showError("ERROR: " + e.statusText)
    });
}

function newSubsProfile() {
    $('#sprof_subs_name').val('New Subscriber');
    $('#sprof_subs_ipaddr').val('');
    $('#sprof_subs_calling_id').val('');
    $('#sprof_subs_called_id').val('');
    $('#sprof_subs_imsi').val('');
    $('#sprof_subs_imei').val('');
    $('#sprof_subs_loc_info').val('');
    $('#sprof_subs_id').val(-1);
}

function populateSubsProfile(obj) {
    $('#sprof_subs_id').val(obj.subs_id);
    $('#sprof_subs_name').val(obj.name);
    $('#sprof_subs_ipaddr').val(obj.ipaddr);
    $('#sprof_subs_calling_id').val(obj.calling_id);
    $('#sprof_subs_called_id').val(obj.called_id);
    $('#sprof_subs_imsi').val(obj.imsi);
    $('#sprof_subs_imei').val(obj.imei);
    $('#sprof_subs_loc_info').val(obj.loc_info);
}

/********* Connection profile code **********/
function handleConnProfile() {
    $('#button_conn_delete').on('click', function(data) {
        $('#modal_connection').modal('show');
        $('#button_conn_ok').on('click', function(data) {
            $('#modal_connection').modal('hide');
            form = $('#connForm');
            $.getJSON('/json/conn_profile/delete/' +
                      $('#cprof_conn_id').val(), {}, function(data) {
                // output success
                showSuccess("The value has been deleted successfully");
                updateConnectionProfileData(0);
            }).fail(function(data) {
                showError("ERROR: " + data.statusText);
            });
        });
    });

    $('#button_conn_save').on('click', function(data) {
        $.ajax({
            type: 'POST',
            url: '/json/conn_profile/save/',
            data: $("#cprof_conn_form").serialize(),
            success: function(response) {
                if (response.success) {
                    showSuccess(response.statusText);
                    if (response.data.action == "insert") {
                        $("#cprof_conn_id").val(response.data.conn_id);
                        updateConnectionProfileData(response.data.conn_id)
                    }
                } else {
                    showError(response.statusText);
                }
            }
        }).fail(function(e) {
            showError("ERROR: " + e.statusText);
        });
    });

    updateConnectionProfileData(0);
    return false;
}

function updateConnectionProfileData(current) {
    $.getJSON('/json/conn_profile/get/', {}, function(data) {
        if (data.success) {
            message = '';
            obj = data.data.conn_profiles
            for(i=0; i < obj.length; i++) {
                message += '<li><a href="#" class="action" id="' +
                    i + '">' + obj[i].name + '</a></li>';
            }
            $('#conn_dropdown_mark')
                .first()
                .html('<li class="divider"></li>' +
                      '<li><a href="#" id="conn_new">Create New</a></li>')
                .prepend(message);
            $('#conn_dropdown_mark a.action').on('click', function(e) {
                populateConnProfile(obj[this.id]);
            });
            $('#conn_dropdown_mark a#conn_new').on('click', function(e) {
                newConnProfile();
            });
            $('#conn_dropdown_mark #' + current).click();
        } else {
            showError("ERROR: " + data.statusText)
        }
    }).fail(function (e) {
        showError("ERROR: " + e.statusText)
    });
}


function newConnProfile() {
    $('#cprof_name').val('New connection');
    $('#cprof_description').val('');
    $('#cprof_speed_down').val(0);
    $('#cprof_speed_up').val(0);
    $('#cprof_speed_var').val(0);
    $('#cprof_latency_down').val(0);
    $('#cprof_latency_up').val(0);
    $('#cprof_latency_jitter').val(0);
    $('#cprof_loss_down').val(0);
    $('#cprof_loss_up').val(0);
    $('#cprof_loss_jitter').val(0);
    $('#cprof_conn_id').val(-1);
}

function populateConnProfile(obj) {
    $('#cprof_name').val(obj.name);
    $('#cprof_description').val(obj.description);
    $('#cprof_speed_down').val(obj.speed_down);
    $('#cprof_speed_up').val(obj.speed_up);
    $('#cprof_speed_var').val(obj.speed_var);
    $('#cprof_latency_down').val(obj.latency_down);
    $('#cprof_latency_up').val(obj.latency_up);
    $('#cprof_latency_jitter').val(obj.latency_jitter);
    $('#cprof_loss_down').val(obj.loss_down);
    $('#cprof_loss_up').val(obj.loss_up);
    $('#cprof_loss_jitter').val(obj.loss_jitter);
    $('#cprof_conn_id').val(obj.conn_id);
}

/********* Settings code **********/
function handleSettings() {
    $('#button_settings_save').on('click', function(e) {
        console.out("settings here");
        $.ajax({
            type: 'POST',
            url: '/json/settings/save/',
            data: $("#settings_form").serialize(),
            success: function(response) {
                if (response.success) {
                    showSuccess(response.statusText);
                } else {
                    showError(response.statusText);
                }
            },
        }).fail(function (e) {
            showError("ERROR: " + e.statusText)
        });
    });

    $.getJSON('/json/settings/get/', {}, function(data) {
        if (data.success) {
            message = '';
            obj = data.data.settings
            populateSettings()
        } else {
            showError("ERROR: " + data.statusText);
        }
    }).fail(function(e) {
        showError("ERROR: " + e.statusText)
    });

    return false;
}


function populateSettings() {
    $('#settings_rad_ip').val(obj.rad_ip);
    $('#settings_rad_port').val(obj.rad_port);
    $('#settings_rad_user').val(obj.rad_user);
    $('#settings_rad_pass').val(obj.rad_pass);
    $('#settings_rad_secret').val(obj.rad_secret);
}


/********* Generic code **********/
function searchId(obj, id_name, id_value) {
    for (i = 0; i < obj.length; i++) {
        if (obj[i][id_name] === id_value) {
            return i;
        }
    }
    return 0
}

function showSuccess(msg) {
    $('.msg-board').html('<p><div class="alert alert-success">' +
                         msg + '</div></p>')
    $('.msg-board').fadeIn(500).delay(2000).fadeOut(500,function(success) {
        $('.msg-board').html('')
    });
}

function showError(msg) {
    $('.msg-board').html('<p><div class="alert alert-danger">' +
                         msg + '</div></p>')
    $('.msg-board').fadeIn(500).delay(2000).fadeOut(500, function(success) {
        $('.msg-board').html('')
    });

}
/* vim: ts=4 sts=8 sw=4 smarttab et si tw=80 ci cino+=t0(0:0 fo=crtocl list */

