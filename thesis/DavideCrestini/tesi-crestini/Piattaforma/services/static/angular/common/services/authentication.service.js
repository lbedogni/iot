(function () {

  angular
    .module('crowdsense')
    .service('authentication', authentication);

  authentication.$inject = ['$http', '$window','$location'];
  function authentication ($http, $window,$location) {

    var saveToken = function (token) {
      $window.localStorage['mean-token'] = token;
    };

    var removeToken = function(){
      $window.localStorage['mean-token'] = null;
    }

    var getToken = function () {
      return $window.localStorage['mean-token'];
    };


    var isLoggedIn = function() {
      var token = getToken();
      var payload;


      if(token){
        payload = token.split('.')[1];
        payload = $window.atob(payload);
        payload = JSON.parse(payload);

        return payload.exp > Date.now() / 1000;
      } else {
        console.log("no token")
        return false;
      }
    };

    var currentUser = function() {
      if(isLoggedIn()){
        var token = getToken();
        var payload = token.split('.')[1];
        payload = $window.atob(payload);
        payload = JSON.parse(payload);
        return {
          username : payload.username
        };
      }
      else return null;
    };

    registerUser = function(user) {
      return $http.post('/api/register/', user).success(function(data){
      });
    };
      
    login = function(user) {
      return $http.post('/api/login/', user).success(function(data) {
        saveToken(data.token);
      });
    };

    getServices = function (){
      return $http.get('/api/templates/' ).success(function(data) {
        //saveToken(data.token);
      }); 
    }

    logout = function() {
      $window.localStorage.removeItem('mean-token');
      $location.path("/")

    };

    return {
      currentUser : currentUser,
      saveToken : saveToken,
      getToken : getToken,
      isLoggedIn : isLoggedIn,
      registerUser : registerUser,
      login : login,
      logout : logout,
      getServices : getServices
    };
  }


})();