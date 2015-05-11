/*jshint node:true*/

/*
 pgwran-ang.js
 Author: Alex Kozadaev (2015)
 */

'use strict';

var app = angular.module('pgwran', ['settingsServices', 'connProfileServices']);

app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

// controller handling the tab navigation
app.controller('TabCtrl', function() {
    this.tab = 1;

    this.selectTab = function(tab) {
        this.tab = tab;
    };

    this.isSelected = function(tab) {
        return this.tab === tab;
    }
});

app.controller('SubsCtrl', function() {
});

app.controller('SubsProfileCtrl', function() {
});

app.controller('ConnProfileCtrl', ['$scope', 'ConnProfileService', function($scope, ConnProfileService) {
    ConnProfileService.get(function(data) {
        $scope.profiles = data.data;
        $scope.success = data.success;
        $scope.status = data.statusText;
        if ($scope.profiles.length > 0) {
            $scope.selected = 0;
        }

        $scope.select = function(conn_id) {
            console.log($scope.profiles);
            for (var i = 0; i < $scope.profiles; i++) {
                if ($scope.profiles[i].conn_id === conn_id) {
                    $scope.selected = i;
                    break;
                }
            }
            $scope.selected = -1;
        };
    });

    $scope.update = function(conn_profile) {
        ConnProfileService.update(conn_profile);
    };
}]);

// settings controller (and all related code)
app.controller('SettingsCtrl', ['$scope', 'SettingsService', function($scope, SettingsService) {
    SettingsService.get(function(data) {
        $scope.settings = data.data;
        $scope.success = data.success;
        $scope.status = data.statusText;
    });

    $scope.update = function(settings) {
        SettingsService.update(settings);
    }
}]);



/* vim: ts=4 sts=8 sw=4 smarttab si tw=80 ci cino+=t0:0l1 fo=ctrocl list */

