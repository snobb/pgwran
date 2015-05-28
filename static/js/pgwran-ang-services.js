/*jshint browser:true, jquery:true */
/*global angular*/

/*
 pgwran-ang-services.js
 Author: Alex Kozadaev (2015)
 */

// subscriber services
angular.module('subsServices', ['ngResource'])
    .factory('SubsService', ['$resource', function($resource) {
        'use strict';

        return $resource('/subscriber', {}, {
            get: { method: 'GET', params:{}, isArray:false },
            update: { method: 'POST', params: {}},
            delete: { method: 'GET', params: {}}
        });
    }]);

// subscriber profile services
angular.module('subsProfileServices', ['ngResource'])
    .factory('SubsProfileService', ['$resource', function($resource) {
        'use strict';

        return $resource('/subs_profile', {}, {
            get: { method: 'GET', params:{}, isArray:false },
            update: { method: 'POST', params: {}},
            delete: {
                method: 'DELETE',
                url: '/subs_profile/:subs_id',
                params: {subs_id: '@subs_id'}
            },
        });
    }]);

// connection profile services
angular.module('connProfileServices', ['ngResource'])
    .factory('ConnProfileService', ['$resource', function($resource) {
        'use strict';

        return $resource('/conn_profile', {}, {
            get: { method: 'GET', params:{}, isArray:false },
            update: { method: 'POST', params: {}},
            delete: {
                method: 'DELETE',
                url: '/conn_profile/:conn_id',
                params: {conn_id: '@conn_id'}
            },
        });
    }]);

// settings services
angular.module('settingsServices', ['ngResource'])
    .factory('SettingsService', ['$resource', function($resource) {
        'use strict';

        return $resource('/settings', {}, {
            get: { method:'GET', params:{} },
            update: { method:'POST', params:{} },
        });
    }]);

/* vim: ts=4 sts=8 sw=4 smarttab si tw=80 ci cino+=t0:0l1 fo=ctrocl list */

