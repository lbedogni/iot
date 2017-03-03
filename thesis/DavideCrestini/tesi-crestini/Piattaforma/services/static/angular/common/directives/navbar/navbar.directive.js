(function () {

  angular
    .module('crowdsense')
    .directive('navbar', navbar);

  function navbar () {
    return {
      restrict: 'EA',
      templateUrl: '/static/angular/common/directives/navbar/navbar.template.html',
      controller: 'navbarCtrl as navvm',
      scope: {location:'@'}
    };
  }

})();