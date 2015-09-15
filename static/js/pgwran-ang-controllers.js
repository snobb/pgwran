/*jshint browser:true, jquery:true */
/*global angular*/

/*
 pgwran-ang.js
 Author: Alex Kozadaev (2015)
 */
var app = angular.module('pgwran', ['ui.bootstrap',
                                    'ui.bootstrap.modal',
                                    'subscriberServices',
                                    'subsProfileServices',
                                    'connProfileServices',
                                    'settingsServices',
                                    'Directives']);

// modifying the template tokens so that they do not conflict with server-side
// code
app.config(function($interpolateProvider) {
    'use strict';

    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

// controller handling the tab navigation
app.controller('TabController', ['$rootScope', function($rootScope) {
    'use strict';

    this.tab = 1;
    this.message = '';

    this.selectTab = function(tab) {
        this.tab = tab;

        // reload subscriber page every time it gets focus
        if (this.tab === 1) {
            $rootScope.$emit('subscriberReload');
        }
    };

    this.isSelected = function(tab) {
        return this.tab === tab;
    };
}]);

// message controller
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
app.controller('SubscriberController',
               ['$scope', '$rootScope', '$modal', 'SubscriberService',
                   function($scope, $rootScope, $modal, SubscriberService) {
    'use strict';

    // load the data
    $scope.loadData = function() {
        SubscriberService.get(function(data) {
            $scope.subscribers = data.data.subscribers;
            $scope.conn_profiles = data.data.conn_profiles;
            $scope.success = data.success;
            $scope.status = data.statusText;
        });
    };

    // initial load
    $scope.loadData();

    $rootScope.$on('subscriberReload', function() {
        $scope.loadData();
    });

    $scope.update = function(subscriber) {
        if (subscriber.conn_profile.conn_id !== subscriber.conn_id) {
            subscriber.conn_id = subscriber.conn_profile.conn_id;
        }
        SubscriberService.update(subscriber, function(data) {
            $rootScope.$emit('message', data);
            $scope.loadData();
        });
    };
}]);

// Subscriber profile controller
app.controller('SubsProfileController',
               ['$scope', '$rootScope', '$modal', 'SubsProfileService',
                   function($scope, $rootScope, $modal, SubsProfileService) {
    'use strict';

    var firstLoad = true;

    // load the data
    $scope.loadData = function() {
        SubsProfileService.get(function(data) {
            $scope.profiles = data.data;
            $scope.success = data.success;
            $scope.status = data.statusText;

            if (firstLoad) {
                if ($scope.profiles.length > 0) {
                    $scope.selected = $scope.profiles[0];
                } else {
                    $scope.selected = {};
                }
                firstLoad = false;
            }
        });
    };

    // initial load
    $scope.loadData();

    // select profile in the drop down
    $scope.select = function(index) {
        if (index < $scope.profiles.length) {
            $scope.selected = $scope.profiles[index];
        }
    };

    // create a new profile (just populate the form but not save)
    $scope.createNew = function() {
        $scope.selected = {
            'subs_id': -1,
            'called_id': 'default.apn',
            'name': 'new_subscriber',
            'ipaddr': '10.0.0.1',
            'imsi': '00000000000001',
            'imei': '000000000000001',
            'calling_id': '000000000000001',
            'loc_info': '01620210ffffffff',
        };
    };

    // update database
    $scope.update = function(subs_profile) {
        SubsProfileService.update(subs_profile, function(data) {
            $rootScope.$emit('message', data);
            $scope.loadData();
        });
    };

    // delete the current profile
    $scope.delete = function(subs_profile) {
        SubsProfileService.delete(subs_profile, function(data) {
            $rootScope.$emit('message', data);
            $scope.loadData();
            $scope.select(0);
        });
    };

    // open a modal dialog (delete)
    $scope.open = function () {
        var modalInstance = $modal.open({
            animation: true,
            size: 'sm',
            templateUrl: 'deleteSubsModalContent.html',
            controller: 'ModalDialogController',
            resolve: {},
        });

        modalInstance.result.then(function () {
            $scope.delete({subs_id: $scope.selected.subs_id});
        }, function () {
            // dialog dismissed - doing nothing
        });
    };
}]);

// Connection profile controller
app.controller('ConnProfileController',
               ['$scope', '$rootScope', '$modal', 'ConnProfileService',
                   function($scope, $rootScope, $modal, ConnProfileService) {
    'use strict';

    var firstLoad = true;

    // load the data
    $scope.loadData = function() {
        ConnProfileService.get(function(data) {
            $scope.profiles = data.data;
            $scope.success = data.success;
            $scope.status = data.statusText;

            if (firstLoad) {
                if ($scope.profiles.length > 0) {
                    $scope.selected = $scope.profiles[0];
                } else {
                    $scope.selected = {};
                }
                firstLoad = false;
            }
        });
    };

    // initial load
    $scope.loadData();

    // select profile in the drop down
    $scope.select = function(index) {
        if (index < $scope.profiles.length) {
            $scope.selected = $scope.profiles[index];
        }
    };

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
            $scope.loadData();
        });
    };

    // delete the current profile
    $scope.delete = function(conn_profile) {
        ConnProfileService.delete(conn_profile, function(data) {
            $rootScope.$emit('message', data);
            $scope.loadData();
            $scope.select(0);
        });
    };

    // open a modal dialog (delete)
    $scope.open = function () {
        var modalInstance = $modal.open({
            animation: true,
            size: 'sm',
            templateUrl: 'deleteConnModalContent.html',
            controller: 'ModalDialogController',
            resolve: {},
        });

        modalInstance.result.then(function () {
            $scope.delete({conn_id: $scope.selected.conn_id});
        }, function () {
            // dialog dismissed - doing nothing
        });
    };
}]);

app.controller('ModalDialogController', function ($scope, $modalInstance) {
    'use strict';

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.ok = function () {
        $modalInstance.close();
    };
});

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

