(function() {

  angular
    .module('crowdsense')
    .service('djangoData', djangoData);

  djangoData.$inject = ['$http', 'authentication'];
  function djangoData ($http, authentication) {

    /*Ritorna tutti i template creati dall'utente*/
    var getPersonalServiceTemplates = function () {
      return $http.get('/api/user/templates/', {
        headers: {
          Authorization: 'JWT '+ authentication.getToken()
        }
      });
    };

    /*Ritorna tutti i template disponibili*/
    var getServiceTemplates = function () {
      return $http.get('/api/templates/');
    };


    var getServices = function () {
      return $http.get('/api/services/', {
        headers: {
          Authorization: 'JWT '+ authentication.getToken()
        }
      });
    };

    var getServiceById = function (id) {
      var url = "/api/services/" + id + "/"
      return $http.get(url, {
        headers: {
          Authorization: 'JWT '+ authentication.getToken()
        }
      });
    };

    var getServiceStreams = function (id) {
      var url = '/api/service/streams/?service=' + id
      return $http.get(url);
    };

    /*Ritorna tutti i template disponibili*/
    var getTemplateById = function (id) {
      var url = "/api/templates/" + id + "/"
      return $http.get(url);
    };

    var createTemplate = function (template) {
      return $http.post('/api/user/templates/',template, {
        headers: {
          Authorization: 'JWT '+ authentication.getToken()
        }
      });
    };


    var getClasses = function(){
      return $http.get('/api/classes/');
    };

    var getStreams = function(lat,lng,classes){
        return $http({
            method: 'GET',
            url: '/api/streams/',
            params: {
                lat: lat,
                lng: lng,
                classes: classes
            }
        })
    }

    var instanceService = function(streams){

      return $http.post('/api/services/',streams, {
        headers: {
          Authorization: 'JWT '+ authentication.getToken()
        }
      });
    }

    var deleteService = function(id){

      return $http.delete('/api/services/'+id,streams, {
        headers: {
          Authorization: 'JWT '+ authentication.getToken()
        }
      });
    }

    var instanceMultisensors = function(data){
      return $http.post('/api/multisensors/',data, {
        headers: {
          Authorization: 'JWT '+ authentication.getToken()
        }
      });
    }

    return {
      getPersonalServiceTemplates: getPersonalServiceTemplates,
      getServiceTemplates: getServiceTemplates,
      getServiceById: getServiceById,
      getServices: getServices,
      getTemplateById: getTemplateById,
      createTemplate: createTemplate,
      getClasses: getClasses,
      getStreams: getStreams,
      getServiceStreams: getServiceStreams,
      instanceService: instanceService,
      instanceMultisensors: instanceMultisensors,
      deleteService: deleteService
    };
  }

})();