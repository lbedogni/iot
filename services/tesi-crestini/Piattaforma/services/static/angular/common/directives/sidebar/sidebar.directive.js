(function () {

  angular
    .module('crowdsense')
    .directive('sidebar', sidebar);

  function sidebar () {
    return {
      restrict: 'EA',
      templateUrl: '/static/angular/common/directives/sidebar/sidebar.template.html',
      controller: 'sidebarCtrl as sidevm'
    };
  }

})();