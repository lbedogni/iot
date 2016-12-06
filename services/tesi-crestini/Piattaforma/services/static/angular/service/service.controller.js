(function() {
  
  angular
    .module('crowdsense')
    .controller('serviceCtrl', serviceCtrl);


    serviceCtrl.$inject = ['$location','$routeParams','authentication','djangoData','$mdToast','$q'];

    function getAddress(title){
        return title.split('-')[1]
    }

    function serviceCtrl ($location,$routeParams,authentication,djangoData,$mdToast,$q) {

		var vm = this;

        if(!authentication.isLoggedIn()){
            $location.path("/#");
            return;
        }

        vm.goBack = function(){
            $location.path("/profile");   
        }
        
        var currentId = $routeParams.id
        var map = null
        var geocoder = null
        vm.expression = null
        vm.currentStreams = []
        /*Recupero le classi presenti nel database e dopodichè cerco quali di queste sono necessarie a risolvere l'espressione*/
        djangoData.getServiceById($routeParams.id)
        .success(function(service) {
            vm.currentService = service;
            var el = angular.element( document.querySelector('#service-map'))[0]
            map = new google.maps.Map(el, {
                zoom: 13,
                center:{
                    lat: vm.currentService.deployment_center_lat,
                    lng: vm.currentService.deployment_center_lon
                }
            });
            clearMarkers()
            var centerMarker = new google.maps.Marker({
                map: map,
                position: {
                    lat: vm.currentService.deployment_center_lat,
                    lng: vm.currentService.deployment_center_lon
                },
                icon: '/static/img/personalMarker.png'
            });

            markersArray.push({
                id : -1,
                marker: centerMarker
            });
            

            $q.all([djangoData.getServiceStreams(vm.currentService.id),djangoData.getTemplateById(vm.currentService.template_id)])
                .then(function(dataArray) {                    
                    vm.currentStreams = dataArray[0].data 
                    var expression = dataArray[1].data.expression
                    vm.expression = expression
                    var struct = {}

                    var infowindow =  new google.maps.InfoWindow({
                        content: ""
                    });

                    for(var i in vm.currentStreams){
                        var idStruct = idToClasses[vm.currentStreams[i]["data_class"]] 
                        struct[idStruct] = vm.currentStreams[i]["measurements"][0]["value"]

                        addMarker(vm.currentStreams,i,map,infowindow)
                    }

                    vm.value = math.eval(expression, struct)

                    
                },function (error) {
                    
                    
                });            
        })
        .error(function (e) {
            console.log(e);
        });
            
    }
})();
