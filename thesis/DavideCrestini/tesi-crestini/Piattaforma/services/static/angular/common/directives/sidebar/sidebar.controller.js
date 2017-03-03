(function () {

  angular
    .module('crowdsense')
    .controller('sidebarCtrl', sidebarCtrl);

  sidebarCtrl.$inject = ['$location','$route','$mdSidenav','authentication','djangoData'];
  function sidebarCtrl($location,$route,$mdSidenav,authentication,djangoData) {
    var vm = this;

    vm.currentUser = authentication.currentUser();

    vm.openLeftMenu = function() {
      $mdSidenav('left').toggle();
    };


    vm.serviceDetail = function(id){
        destination = "/service/"+id
        console.log(destination)
        $location.path(destination);
    }

    djangoData.getServices().success(function(data) {
          vm.userServices = data;
          
      }).error(function (e) {
          console.log(e);
      });
  }

})();