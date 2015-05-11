/*jshint node:true*/

/*
 pgwran-ang-services.js
 Author: Alex Kozadaev (2015)
 */

'use strict';


// connection profile services
var connProfileServices = angular.module('connProfileServices', ['ngResource']);
connProfileServices.factory('ConnProfileService', ['$resource', function($resource) {
    return $resource('/conn_profile', {}, {
        get: { method: 'GET', params:{}, isArray:false },
        update: { method: 'POST', params: {}}
    });
}]);

// settings services
var settingsServices = angular.module('settingsServices', ['ngResource']);
settingsServices.factory('SettingsService', ['$resource', function($resource) {
    return $resource('/settings', {}, {
        get: { method:'GET', params:{} },
        update: { method:'POST', params:{} },
    });
}]);


/* vim: ts=4 sts=8 sw=4 smarttab si tw=80 ci cino+=t0:0l1 fo=ctrocl list */

