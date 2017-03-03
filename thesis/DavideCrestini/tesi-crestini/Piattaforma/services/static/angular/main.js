(function () {

	function routing($routeProvider, $locationProvider) {
		$routeProvider
			.when('/', {
				templateUrl: '/static/angular/home/home.view.html',
				controller: 'homeCtrl',
				controllerAs: 'vm'
			})
			.when('/profile', {
				templateUrl: '/static/angular/profile/profile.view.html',
				controller: 'profileCtrl',
				controllerAs: 'vm'
			})
			.when('/templateDetail/:id', {
				templateUrl: '/static/angular/templateDetail/templateDetail.view.html',
				controller: 'templateDetailCtrl',
				controllerAs: 'vm'
			})
			.when('/service/:id', {
				templateUrl: '/static/angular/service/service.view.html',
				controller: 'serviceCtrl',
				controllerAs: 'vm'
			})
			.otherwise({redirectTo: '/'});
			// use the HTML5 History API
			$locationProvider.html5Mode(true);
	}	
	
	function config($interpolateProvider){
		$interpolateProvider.startSymbol('[[');
		$interpolateProvider.endSymbol(']]');
	}

	function successToast($mdThemingProvider){
		$mdThemingProvider.theme('success-toast')
	}

	function errorToast($mdThemingProvider){
		$mdThemingProvider.theme('error-toast')
	}
	
    angular
        .module('crowdsense')
        .config(['$routeProvider', '$locationProvider', routing])
        .config(['$interpolateProvider', config])
        .config(['$mdThemingProvider', successToast])
        .config(['$mdThemingProvider', errorToast])

})();
