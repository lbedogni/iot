(function () {

  angular
    .module('crowdsense')
    .controller('navbarCtrl', navbarCtrl);

  navbarCtrl.$inject = ['$location','$mdSidenav','$mdDialog','authentication','$scope'];
  function navbarCtrl($location,$mdSidenav,$mdDialog,authentication,$scope) {
    var vm = this;

    vm.logged = authentication.isLoggedIn();

    function performLogin(credentials){
      authentication.login(credentials)
        .error(function(err){
          console.log(err)
        })
        .then(function(data){
          console.log("QUa")
          $location.path('profile');
        }); 
    }

    vm.logout = function(){
      authentication.logout();
      $location.path('/#');
    }

    vm.navigateTo = function(destination){
      $location.path(destination);
    }


    /*LOGIN DIALOG E CONTROLLER*/
    vm.showLoginDialog = function(event) {
      var parentEl = angular.element(document.body);
      $mdDialog.show({
       parent: parentEl,
       targetEvent: event,
       templateUrl: '/static/angular/dialog/login.dialog.template.html',
       controller: LoginDialogController
      });
    }


    function LoginDialogController($scope, $mdDialog,$location){
      $scope.credentials = {
      	username: '',
      	password: ''
      }

      $scope.login = function() {
      	 performLogin($scope.credentials)
          $mdDialog.hide();
      }

      $scope.closeDialog = function() {
        $mdDialog.hide();
      }  
    }

    /*REGISTER DIALOG E CONTROLLER*/
    vm.showRegisterDialog = function(event) {
      console.log("Registro")
      var parentEl = angular.element(document.body);
      $mdDialog.show({
       parent: parentEl,
       targetEvent: event,
       templateUrl: '/static/angular/dialog/register.dialog.template.html',
       controller: RegisterDialogController
      });
    }


    function RegisterDialogController($scope, $mdDialog,$location){
      $scope.credentials = {
        username: '',
        email:'',
        password: ''
      }

      $scope.register = function() {
        authentication.registerUser($scope.credentials)
        .error(function(err){
            console.log(err);
        })
        .then(function(data){
          performLogin($scope.credentials)
          $location.path('profile');
        }); 
            $mdDialog.hide();
      }

      $scope.closeDialog = function() {
        $mdDialog.hide();
      }  
    }


  }

})();