/*jshint browser:true, jquery:true */
/*global angular*/

/*
 pgwran-ang.js
 Author: Alex Kozadaev (2015)
 */
var app = angular.module('pgwran', ['ui.bootstrap',
                                    'subsServices',
                                    'subsProfileServices',
                                    'connProfileServices',
                                    'settingsServices']);

// modifying the template tokens so that they do not conflict with server-side
// code
app.config(function($interpolateProvider) {
    'use strict';

    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

// controller handling the tab navigation
app.controller('TabController', function() {
    'use strict';

    this.tab = 1;
    this.message = '';

    this.selectTab = function(tab) {
        this.tab = tab;
    };

    this.isSelected = function(tab) {
        return this.tab === tab;
    };
});

app.controller('MessageController',
               ['$scope', '$rootScope', '$timeout',
                   function($scope, $rootScope, $timeout) {
    'use strict';

    $scope.message = {
        msg_show: false,
        msg_text: '',
        msg_success: true,
    };

    $rootScope.$on('message', function(event, data) {
        $scope.message = {
            msg_show: true,
            msg_text: data.statusText,
            msg_class: data.success ? 'alert alert-success'
                                    : 'alert alert-danger',
            msg_success: data.success,
        };

        $timeout(function() {
            $scope.message.msg_show = false;
            $scope.message.msg_text = '';
        }, 3000);
    });
}]);

// Subscribers controller
app.controller('SubsController', function() {
    'use strict';
});

// Subscriber profile controller
app.controller('SubsProfileController',
               ['$scope', '$rootScope', 'SubsProfileService',
                   function($scope, $rootScope, SubsProfileService) {
    'use strict';

    // load the data
    SubsProfileService.get(function(data) {
        $scope.profiles = data.data;
        $scope.success = data.success;
        $scope.status = data.statusText;

        if ($scope.profiles.length > 0) {
            $scope.selected = $scope.profiles[0];
        } else {
            $scope.selected = {};
        }

        $scope.select = function(index) {
            if (index < $scope.profiles.length) {
                $scope.selected = $scope.profiles[index];
            }
        };
    });

    // create a new profile (just populate the form but not save)
    $scope.createNew = function() {
        $scope.selected = {
            'subs_id': -1,
            'called_id': 'default.apn',
            'name': 'new_subscriber',
            'ipaddr': '10.0.0.1',
            'imsi': '00000000000001',
            'imei': '00000000000001',
            'calling_id': '000000000000001',
            'loc_info': 'chertsey',
        };
    };

    // update database
    $scope.update = function(subs_profile) {
        SubsProfileService.update(subs_profile, function(data) {
            $rootScope.$emit('message', data);
        });
    };

    // delete the current profile
    $scope.delete = function(subs_profile) {
        SubsProfileService.delete(subs_profile, function(data) {
            $rootScope.$emit('message', data);
        });
    };
}]);

// Connection profile controller
app.controller('ConnProfileController',
               ['$scope', '$rootScope', 'ConnProfileService',
                   function($scope, $rootScope, ConnProfileService) {
    'use strict';

    // load the data
    ConnProfileService.get(function(data) {
        $scope.profiles = data.data;
        $scope.success = data.success;
        $scope.status = data.statusText;

        if ($scope.profiles.length > 0) {
            $scope.selected = $scope.profiles[0];
        } else {
            $scope.selected = {};
        }

        $scope.select = function(index) {
            if (index < $scope.profiles.length) {
                $scope.selected = $scope.profiles[index];
            }
        };
    });

    // create a new profile (just populate the form but not save)
    $scope.createNew = function() {
        $scope.selected = {
            conn_id: -1,
            name: 'new_connection',
            description: 'New connection profile',
            latency_up: 0,
            latency_down: 0,
            latency_jitter: 0,
            loss_up: 0.0,
            loss_down: 0.0,
            loss_jitter: 0,
            rat_type: 1,
            speed_down: 0,
            speed_up: 0,
            speed_var: 0
        };
    };

    // update database
    $scope.update = function(conn_profile) {
        ConnProfileService.update(conn_profile, function(data) {
            $rootScope.$emit('message', data);
        });
    };

    // delete the current profile
    $scope.delete = function(conn_profile) {
        ConnProfileService.delete(conn_profile, function(data) {
            $rootScope.$emit('message', data);
        });
    };
}]);

// Settings controller
app.controller('SettingsController',
               ['$scope', '$rootScope', 'SettingsService',
                   function($scope, $rootScope, SettingsService) {
    'use strict';
    $rootScope.msg_show = false;

    SettingsService.get(function(data) {
        $scope.settings = data.data;
        $scope.success = data.success;
        $scope.status = data.statusText;
    });

    $scope.update = function(settings) {
        SettingsService.update(settings, function(update_data) {
            $rootScope.$emit('message', update_data);
        });
    };
}]);

/* vim: ts=4 sts=8 sw=4 smarttab si tw=80 ci cino+=t0:0l1 fo=ctrocl list */

