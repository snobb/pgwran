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
                if (INTEGER_REGEXP.test(viewValue)) {
                    return true; //valid
                }

                return false; // invalid
            };
        }
    };
});

app.directive('ipv4', function() {
    'use strict';
    var INTEGER_REGEXP = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;
    return {
        require: 'ngModel',
        link: function(scope, elm, attrs, ctrl) {
            ctrl.$validators.integer = function(modelValue, viewValue) {
                if (INTEGER_REGEXP.test(viewValue)) {
                    return true;
                }
                return false;
            };
        }
    };
});

var isValidOctet = function(num) {
    'use strict';
    return (num >= 0 && num <= 255);
};


/* vim: ts=4 sts=8 sw=4 smarttab si tw=80 ci cino+=t0:0l1 fo=ctrocl list */

