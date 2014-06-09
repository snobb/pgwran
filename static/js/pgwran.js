/*
 *  pgwran.js
 *  Author: Alex Kozadaev (2014)
 */


/********* Document handler code **********/
$('document').ready(function() {
    handleSubscribers();
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        e.target // activated tab
        e.relatedTarget // previous tab
        $('#title').text('PGW-RAN: ' + $('.active a').text())

        active_id = $('#menuTab .active')[0].id;

        if (active_id === 'menu_subs') {
            handleSubscribers();
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
    $('#subscriber_screen').html('');
    $.getJSON('/json/subscriber/get/', {}, function(data) {
        if (data.success) {
            subs = data.data.subscribers
            conn_profiles = data.data.conn_profiles
            var subs_body = '';
            for (var i = 0; i < subs.length; i++) {
                subs_body += getSubsTemplate(subs[i], conn_profiles);
            }
            $('#subscriber_screen').html(subs_body);
            $('#subscriber_screen .cbox').each(function(index) {
                $(this).on('change', function(data) {
                    action = (this.checked) ? 'enable' : 'disable';
                    updateForm(this, action);
                });
            });
            $('#subscriber_screen select').each(function(index) {
                $(this).on('change', function(data) {
                    updateForm(this, 'save');
                });
            });
        } else {
            showError('ERROR: ' + data.statusText);
        }
    }).fail(function(e) {
        showError('ERROR: error accessing the backend - ' + e.statusText);
    });
    return false;
}

function updateForm(obj, action) {
    $.ajax({
        type: 'POST',
        url: '/json/subscriber/' + action + '/',
        data: $('#subscriber_screen #form' + obj.id).serialize(),
        success: function(response) {
            if (response.success) {
                showSuccess('The subscriber has been updated successfully');
            } else {
                showError(response.statusText);
            }
        }
    }).fail(function (e) {
        showError('ERROR: error accessing the backend - ' + e.statusText);
        $('#subscriber_screen').html('');
    });
}

function getSubsTemplate(obj, conn_list) {
    var options = '', selected = ''
    var id = obj.subs_id
    for (var i = 0; i < conn_list.length; i++) {
        conn = conn_list[i];
        selected = (conn.conn_id == obj.conn_id) ? ' selected' : ''
        options += '<option value="' + conn.conn_id + '"' + selected + '>' + conn.name + '</option>'
    }
    checked = (obj.enabled) ? ' checked' : '';
    return '<form class="form" role="form" method="post" ' +
        'action="/json/subscriber/save" id="form' + id + '">' +
        '<div class="panel panel-default"> ' +
        '    <div class="panel-body">' +
        '        <input type="hidden" name="subs_id" id="subs_id" value="' + id + '">' +
        '        <div class="row">' +
        '            <div class="col-md-5">' +
        '                <div class="input-group">' +
        '                    <span class="input-group-addon">Subscriber</span>' +
        '                    <input type="text" class="form-control input-sm"' +
        ' readonly="true" value="' + obj.name + '">' +
        '                </div>' +
        '            </div>' +
        '            <div class="col-md-5">' +
        '                <div class="input-group">' +
        '                    <!-- Button and dropdown menu -->' +
        '                    <span class="input-group-addon">Connection</span> ' +
        '                    <select name="conn_id" class="form-control input-sm" id="' + id + '">' +
        options + '</select>' +
        '                </div>' +
        '            </div>' +
        '            <div class="col-md-1">' +
        '                <input type="checkbox" class="cbox" name="enabled" id="' + id + '"' +
        checked + '> ON</div>' +
        '        </div>' +
        '    </div>' +
        '</div></form>';
}

/********* Subscriber profile code **********/
function handleSubsProfile() {
    $('#subs_screen #button_delete').on('click', function(data) {
        $('#subs_screen #modal').modal('show');
        $('#subs_screen #button_ok').on('click', function(data) {
            $('#subs_screen #modal').modal('hide');
            $.getJSON('/json/subs_profile/delete/' +
                      $('#subs_screen #subs_id').val(), {}, function(data) {
                // output success
                showSuccess('The value has been deleted successfully');
                updateSubscriberProfileData(0);
            }).fail(function(e) {
                showError('ERROR: error accessing the backend - ' + e.statusText);
            });
        });
    });


    $('#subs_screen #button_save').on('click', function(data) {
        if ($('#subs_screen #ipaddr').val() == '') {
            showError('ERROR: IP address field is required');
            return false;
        }
        $.ajax({
            type: 'POST',
            url: '/json/subs_profile/save/',
            data: $('#subs_screen form').serialize(),
            success: function(response) {
                if (response.success) {
                    showSuccess(response.statusText);
                    if (response.data.action == 'insert') {
                        $('#subs_screen #subs_id').val(response.data.subs_id);
                        updateSubscriberProfileData(response.data.subs_id)
                    }
                } else {
                    showError(response.statusText);
                }
            }
        }).fail(function(e) {
            showError('ERROR: error accessing the backend - ' + e.statusText);
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
            $('#subs_screen #dropdown_mark')
                .first()
                .html('<li class="divider"></li>' +
                      '<li><a href="#" id="subs_new">Create New</a></li>')
                .prepend(message);
            $('#subs_screen #dropdown_mark a.action').on('click', function(e) {
                populateSubsProfile(obj[this.id]);
            });
            $('#subs_screen #dropdown_mark a#subs_new').on('click', function(e) {
                newSubsProfile();
            });
            $('#subs_screen #dropdown_mark #' + current).click()
        } else {
            showError('ERROR: ' + data.statusText)
        }
    }).fail(function(e) {
        showError('ERROR: error accessing the backend - ' + e.statusText);
    });
}

function newSubsProfile() {
    $('#subs_screen #subs_id').val(-1);
    $('#subs_screen #name').val('New Subscriber');
    $('#subs_screen #ipaddr').val('');
    $('#subs_screen #calling_id').val('');
    $('#subs_screen #called_id').val('');
    $('#subs_screen #imsi').val('');
    $('#subs_screen #imei').val('');
    $('#subs_screen #loc_info').val('');
}

function populateSubsProfile(obj) {
    $('#subs_screen #subs_id').val(obj.subs_id);
    $('#subs_screen #name').val(obj.name);
    $('#subs_screen #ipaddr').val(obj.ipaddr);
    $('#subs_screen #calling_id').val(obj.calling_id);
    $('#subs_screen #called_id').val(obj.called_id);
    $('#subs_screen #imsi').val(obj.imsi);
    $('#subs_screen #imei').val(obj.imei);
    $('#subs_screen #loc_info').val(obj.loc_info);
}

/********* Connection profile code **********/
function handleConnProfile() {
    $('#conn_screen #button_delete').on('click', function(data) {
        $('#conn_screen #modal').modal('show');
        $('#conn_screen #button_ok').on('click', function(data) {
            $('#conn_screen #modal').modal('hide');
            $.getJSON('/json/conn_profile/delete/' +
                      $('#conn_screen #conn_id').val(), {}, function(data) {
                // output success
                showSuccess('The value has been deleted successfully');
                updateConnectionProfileData(0);
            }).fail(function(data) {
                showError('ERROR: ' + data.statusText);
            });
        });
    });

    $('#conn_screen #button_save').on('click', function(data) {
        $.ajax({
            type: 'POST',
            url: '/json/conn_profile/save/',
            data: $('#conn_screen form').serialize(),
            success: function(response) {
                if (response.success) {
                    showSuccess(response.statusText);
                    if (response.data.action == 'insert') {
                        $('#conn_screen #conn_id').val(response.data.conn_id);
                        updateConnectionProfileData(response.data.conn_id)
                    }
                } else {
                    showError(response.statusText);
                }
            }
        }).fail(function(e) {
            showError('ERROR: ' + e.statusText);
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
            $('#conn_screen #dropdown_mark')
                .first()
                .html('<li class="divider"></li>' +
                      '<li><a href="#" id="conn_new">Create New</a></li>')
                .prepend(message);
            $('#conn_screen #dropdown_mark a.action').on('click', function(e) {
                populateConnProfile(obj[this.id]);
            });
            $('#conn_screen #dropdown_mark a#conn_new').on('click', function(e) {
                newConnProfile();
            });
            $('#conn_screen #dropdown_mark #' + current).click();
        } else {
            showError('ERROR: ' + data.statusText)
        }
    }).fail(function (e) {
        showError('ERROR: ' + e.statusText)
    });
}

function newConnProfile() {
    $('#conn_screen #name').val('New connection');
    $('#conn_screen #description').val('');
    $('#conn_screen #speed_down').val(0);
    $('#conn_screen #speed_up').val(0);
    $('#conn_screen #speed_var').val(0);
    $('#conn_screen #latency_down').val(0);
    $('#conn_screen #latency_up').val(0);
    $('#conn_screen #latency_jitter').val(0);
    $('#conn_screen #loss_down').val(0);
    $('#conn_screen #loss_up').val(0);
    $('#conn_screen #loss_jitter').val(0);
    $('#conn_screen #conn_id').val(-1);
}

function populateConnProfile(obj) {
    $('#conn_screen #name').val(obj.name);
    $('#conn_screen #description').val(obj.description);
    $('#conn_screen #speed_down').val(obj.speed_down);
    $('#conn_screen #speed_up').val(obj.speed_up);
    $('#conn_screen #speed_var').val(obj.speed_var);
    $('#conn_screen #latency_down').val(obj.latency_down);
    $('#conn_screen #latency_up').val(obj.latency_up);
    $('#conn_screen #latency_jitter').val(obj.latency_jitter);
    $('#conn_screen #loss_down').val(obj.loss_down);
    $('#conn_screen #loss_up').val(obj.loss_up);
    $('#conn_screen #loss_jitter').val(obj.loss_jitter);
    $('#conn_screen #conn_id').val(obj.conn_id);
}

/********* Settings code **********/
function handleSettings() {
    $('#settings_screen #button_save').on('click', function(e) {
        $.ajax({
            type: 'POST',
            url: '/json/settings/save/',
            data: $('#settings_screen form').serialize(),
            success: function(response) {
                if (response.success) {
                    showSuccess(response.statusText);
                } else {
                    showError(response.statusText);
                }
            },
        }).fail(function (e) {
            showError('ERROR: ' + e.statusText)
        });
    });

    $.getJSON('/json/settings/get/', {}, function(data) {
        if (data.success) {
            message = '';
            obj = data.data.settings
            populateSettings()
        } else {
            showError('ERROR: ' + data.statusText);
        }
    }).fail(function(e) {
        showError('ERROR: ' + e.statusText)
    });

    return false;
}

function populateSettings() {
    $('#settings_screen #rad_ip').val(obj.rad_ip);
    $('#settings_screen #rad_port').val(obj.rad_port);
    $('#settings_screen #rad_user').val(obj.rad_user);
    $('#settings_screen #rad_pass').val(obj.rad_pass);
    $('#settings_screen #rad_secret').val(obj.rad_secret);
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

