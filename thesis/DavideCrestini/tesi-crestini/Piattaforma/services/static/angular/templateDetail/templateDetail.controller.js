(function() {
  
  angular
    .module('crowdsense')
    .controller('templateDetailCtrl', templateDetailCtrl);


    templateDetailCtrl.$inject = ['$location','$routeParams','authentication','djangoData','$mdToast','$q','$scope'];

    function templateDetailCtrl ($location,$routeParams,authentication,djangoData,$mdToast,$q,$scope) {

		var vm = this;

        if(!authentication.isLoggedIn()){
            $location.path("/#");
            return;
        }
        
        vm.keys = []
        vm.neededSensors = [];
        vm.selected = []
        vm.foundedStreams = []
        var dataClasses = []
        var currentId = $routeParams.id
        var currentLatLng = null
        var currentAddress = null
        var neededSensorsID
        /*Recupero le classi presenti nel database e dopodichè cerco quali di queste sono necessarie a risolvere l'espressione*/
        djangoData.getClasses()
            .success(function(data) {
                
                for(var classe in data){
                    dataClasses.push(data[classe].data_type)
                }

                djangoData.getTemplateById($routeParams.id).success(function(data) {
                    vm.currentTemplate = data;
                    vm.neededSensors = getClassesByExpression(data.expression,dataClasses)
                    neededSensorsID = getClassesId(vm.neededSensors)
                }).error(function (e) {
                    console.log(e);
                });
            })
            .error(function (e) {
                $mdToast.show($mdToast.simple()
                    .textContent('Si è verificato un errore nella lettura delle calssi')                       
                    .hideDelay(3000)
                    .theme("error-toast")
                );
            });

        /*Prendo i dati relativi al servizio*/


        var currentMarker = null
        var el = angular.element( document.querySelector('#map'))[0]
        var map = new google.maps.Map(el, {
          zoom: 13,
          center: {lat: 44.494887, lng: 11.342616}
        });
        
        var geocoder = new google.maps.Geocoder();
        
        google.maps.event.addListener(map, 'click', function(event) {
          geocoder.geocode({'latLng': event.latLng}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
              if (results[0]) {
                $scope.address = results[0].formatted_address
                $scope.$apply()
              }
            }
          });
        });


        
        vm.goBack = function(){
            $location.path("/profile");   
        }

        vm.onSubmit = function(){
            vm.selected = []
            currentAddress = $scope.address
            clearMarkers()
            currentLatLng = null
            geocoder.geocode({'address': $scope.address}, function(results, status) {
                if (status === 'OK') {
                    
                    currentLatLng = [results[0].geometry.location.lat(),results[0].geometry.location.lng()]

                    map.setCenter(results[0].geometry.location);
                    centerMarker = new google.maps.Marker({
                        map: map,
                        position: results[0].geometry.location,
                        icon: '/static/img/personalMarker.png'
                    });

                    markersArray.push({
                        id : -1,
                        marker: centerMarker
                    });
                    /*Quando cerco gli stream passo neededSsensorsID perch+ nella tabella DataStreams la calsse è presente tramite il proprio ID*/
                    djangoData.getStreams(results[0].geometry.location.lat(),results[0].geometry.location.lng(),neededSensorsID)
                        .success(function(data) {
                            console.log(data)
                            if(data.length == 0){
                                $mdToast.show($mdToast.simple()
                                    .textContent('Non è stato trovato nessuno stream')                       
                                    .hideDelay(3000)
                                    .theme("error-toast")
                                );
                                return;
                            }
                            vm.foundedStreams = data
                            
                            var infowindow =  new google.maps.InfoWindow({
                                content: ""
                            });

                            for(var stream in vm.foundedStreams){
                                addMarker(vm.foundedStreams,stream,map,infowindow,vm)
                            }
                        })
                        .error(function (e) {
                            $mdToast.show($mdToast.simple()
                                .textContent('Si è verificato un errore nella lettura delle classi')                       
                                .hideDelay(3000)
                                .theme("error-toast")
                            );
                        });

                } 
                else {
                    $mdToast.show($mdToast.simple()
                        .textContent('Si è verificato un\'errore nel rilevamento delle mappe. Riprovare.')                       
                        .hideDelay(3000)
                        .theme("error-toast")
                    );
                }
            });
        }   

        
        selectOnInfoWindow = function(id){
            var tr =  angular.element( document.querySelector('#tr'+id))
            var checkbox = tr[0].childNodes[0].childNodes[0]
            checkbox.click()
        }

        vm.selectStream = function(){
            selectMarker(this.model)
        }

        vm.deselectStream = function(){
            deselectMarker(this.model)
        }


        vm.instanceService = function(){
            
            var controlStruct = checkClasses(vm.selected,vm.foundedStreams,neededSensorsID)

            if(!controlStruct){
                $mdToast.show($mdToast.simple()
                        .textContent('Impossibile instanziare il servizio, è necessario selezionare tutti i sensori.')                       
                        .hideDelay(3000)
                        .theme("error-toast")
                    );
                return;
            }

            for(var item in controlStruct){
                if(controlStruct[item]["streams"].length == 0){
                    $mdToast.show($mdToast.simple()
                        .textContent('Impossibile instanziare il servizio, è necessario selezionare tutti i sensori.')                       
                        .hideDelay(3000)
                        .theme("error-toast")
                    );
                    return;
                }
                else if(controlStruct[item]["streams"].length > 1){
                     $mdToast.show($mdToast.simple()
                        .textContent('Impossibile instanziare il servizio, è necessario selezionare un solo sensore per ogni classe.')                       
                        .hideDelay(3000)
                        .theme("error-toast")
                    );
                    return;
                }
            }
            var service = {
                title: vm.currentTemplate.title + ' - ' + currentAddress ,
                deployment_center_lat:currentLatLng[0],
                deployment_center_lon:currentLatLng[1],
                deployment_radius: 500,
                template_id: currentId,
                sensors: vm.selected
            }
            
            djangoData.instanceService(service)
            .success(function(data) {

                /*Se l'instanziazione del servizio fa a buon fine allora instanzio pure gli stream selezionati*/
                var promiseArray = [];

                for (var i in vm.selected) {

                    var json = {
                        data_stream_id: vm.selected[i],
                        custom_service_id:data.id
                    }

                    promiseArray.push(djangoData.instanceMultisensors(json));
                }

                $q.all(promiseArray)
                    .then(function(dataArray) {
                        console.log("Fatto")
                        console.log(dataArray)
                        $mdToast.show($mdToast.simple()
                            .textContent('Servizio istanziato con sucesso.')
                            .hideDelay(3000)
                            .theme("success-toast")

                        );
                        $location.path('profile')
                    },function (error) {
                        $mdToast.show($mdToast.simple()
                            .textContent('Si è verificato un errore durante la creazione dei sensori.')                       
                            .hideDelay(3000)
                            .theme("error-toast")
                        );
                        /*Se l'istanziazione dei multisensors fallisce allora elimino il servizio appena creato*/
                        djangoData.deleteService(data.id)
                        .success(function(data){ console.log(data); console.log("Eliminato con successo")})
                        .error(function (e) {console.log(e) })
                        $mdToast.show($mdToast.simple()
                            .textContent('Si è verificato un errore durante la creazione dei sensori.')                       
                            .hideDelay(3000)
                            .theme("error-toast")
                        );
                    });
            })
            .error(function (e) {
                $mdToast.show($mdToast.simple()
                    .textContent('Si è verificato un errore durante l\'instanziazione del servizio.')                       
                    .hideDelay(3000)
                    .theme("error-toast")
                );
                console.log(e)
            });
        }
    }

    

})();
