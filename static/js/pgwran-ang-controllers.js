/*jshint browser:true, jquery:true */
/*global angular*/

/*
 pgwran-ang.js
 Author: Alex Kozadaev (2015)
 */


var app = angular.module('pgwran', ['subsServices',
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
app.controller('TabCtrl', function() {
    'use strict';

    this.tab = 1;
    this.message = '';
    this.isMessage = false;
    this.isError = false;

    this.selectTab = function(tab) {
        this.tab = tab;
    };

    this.isSelected = function(tab) {
        return this.tab === tab;
    };

//    this.showMessage= function(msg, status) {
//        if (status) {
//            this.msgClass = 'msg-board, alert alert-success';
//        } else {
//            this.msgClass = 'alert alert-error';
//        }
//
//        $('.msg-board').fadeIn(500).delay(2000).fadeOut(500,function() {
//            this.message = '';
//        });
//    };
});

// Subscribers controller
app.controller('SubsCtrl', function() {
    'use strict';
});

// Subscriber profile controller
app.controller('SubsProfileCtrl', ['$scope', 'SubsProfileService', function($scope, SubsProfileService) {
    'use strict';

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

    $scope.update = function(subs_profile) {
        SubsProfileService.update(subs_profile);
    };

    $scope.delete = function(subs_profile) {
        SubsProfileService.delete(subs_profile);
    };

}]);

// Connection profile controller
app.controller('ConnProfileCtrl', ['$scope', 'ConnProfileService', function($scope, ConnProfileService) {
    'use strict';

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

    $scope.update = function(conn_profile) {
        ConnProfileService.update(conn_profile);
    };

    $scope.delete = function(conn_profile) {
        ConnProfileService.delete(conn_profile);
    };
}]);

// Settings controller
app.controller('SettingsCtrl', ['$scope', 'SettingsService', function($scope, SettingsService) {
    'use strict';

    SettingsService.get(function(data) {
        $scope.settings = data.data;
        $scope.success = data.success;
        $scope.status = data.statusText;
    });

    $scope.update = function(settings) {
        SettingsService.update(settings);
    };
}]);

/* vim: ts=4 sts=8 sw=4 smarttab si tw=80 ci cino+=t0:0l1 fo=ctrocl list */

