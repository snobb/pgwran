/*jshint browser:true, jquery:true */
/*global angular*/

/*
 pgwran-ang-directives.js
 Author: Alex Kozadaev (2015)
 */

var app = angular.module('Directives',[]);
app.directive('integer', function() {
    'use strict';

    var INTEGER_REGEXP = /^\-?\d+$/;
    return {
        require: 'ngModel',
        link: function(scope, elm, attrs, ctrl) {
            ctrl.$validators.integer = function(modelValue, viewValue) {
                return (INTEGER_REGEXP.test(viewValue));
            };
        }
    };
});

app.directive('ip', function() {
    'use strict';
    var IPV4_REGEXP = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
    var IPV6_REGEXP = /^(\d+)\:[:\d]+(\d+)$/;
    return {
        require: 'ngModel',
        link: function(scope, elm, attrs, ctrl) {
            ctrl.$validators.ip = function(modelValue, viewValue) {
                var res = IPV4_REGEXP.exec(viewValue);
                return (res && res.length == 5 &&
                            res[1] >  0 && res[1] < 256 &&
                            res[2] >= 0 && res[2] < 256 &&
                            res[3] >= 0 && res[3] < 256 &&
                            res[4] >  0 && res[4] < 255) ||
                        IPV6_REGEXP.test(viewValue);
            };
        }
    };
});

app.directive('imsi', function() {
    'use strict';
    return {
        require: 'ngModel',
        link: function(scope, elm, attrs, ctrl) {
            ctrl.$validators.imsi = function(modelValue, viewValue) {
                return (!isNaN(viewValue) && viewValue.length <= 15);
            };
        }
    };
});

app.directive('imei', function() {
    'use strict';
    return {
        require: 'ngModel',
        link: function(scope, elm, attrs, ctrl) {
            ctrl.$validators.imei = function(modelValue, viewValue) {
                return (!isNaN(viewValue) &&
                        (viewValue.length === 15 ||
                         viewValue.length === 16));
            };
        }
    };
});

app.directive('locationInfo', function() {
    'use strict';
    var HEX_LOC_INFO = /^[0-9a-fA-F]{16}$/;
    return {
        require: 'ngModel',
        link: function(scope, elm, attrs, ctrl) {
            ctrl.$validators.location_info = function(modelValue, viewValue) {
                return (HEX_LOC_INFO.test(viewValue));
            };
        }
    };
});

app.directive('callingId', function() {
    'use strict';
    return {
        require: 'ngModel',
        link: function(scope, elm, attrs, ctrl) {
            ctrl.$validators.calling_id = function(modelValue, viewValue) {
                return (!isNaN(viewValue) && viewValue.length >= 3);
            };
        }
    };
});

/* vim: ts=4 sts=8 sw=4 smarttab si tw=80 ci cino+=t0:0l1 fo=ctrocl list */

