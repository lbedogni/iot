(function() {
  
  angular
    .module('crowdsense')
    .controller('profileCtrl', profileCtrl);


    profileCtrl.$inject = ['$location','authentication','djangoData','$mdDialog','$mdToast'];

    
    
    
    var COLORS = ['#FF2716','#464ABF','#FF7A09'];
     
    function randomColor() {
       return COLORS[Math.floor(Math.random() * COLORS.length)];
    }

    function randomSpan() {
		var r = Math.random();
		if (r < 0.8)
			return 1;
		else 
			return 2;

	}    

    function checkRules(rules,rulesNumber){
        var i = 1
        for(var rule in rules){
            if(i <= rulesNumber){
                if(rules[rule].firstclass == "" && rules[rule].secondclass == "")
                    return false
                else if(rules[rule].firstclass == "Constant" && !rules[rule].firstCostant)
                    return false
                else if(rules[rule].secondclass == "Constant" && !rules[rule].secondCostant)
                    return false                
                else if((rules[rule].firstclass != "" && rules[rule].secondclass != "") && rules[rule].operand == "")
                    return false
                else if(i != rulesNumber && rules[rule].connective == "")
                    return false
            }
            i++;
        }
        return true
    }

    function createExpression(rules,rulesNumber){
        var expr = ""
        var i = 1

        for(var rule in rules){
            if(i <= rulesNumber){
                var firstItem = ""
                var secondtItem = ""
                if(rules[rule].firstclass != "Constant")
                    firstItem = rules[rule].firstclass           
                else
                    firstItem = rules[rule].firstCostant

                if(rules[rule].secondclass != "Constant")
                    secondItem = rules[rule].secondclass           
                else
                    secondItem = rules[rule].secondCostant

                var currentRule = ""
                //Se in un espressione ho inserito entrambi gli operatori allora scrivo l'espressione componendola con i due operatpri e l'operando
                if(firstItem != "" && secondItem != "")
                    currentRule = "(" + firstItem + " " + rules[rule].operand + " " + secondItem + ")"
                else if(firstItem != "")
                    currentRule = "(" + firstItem + ")"
                else if(secondItem != "")
                    currentRule = "(" + secondItem + ")"
                

                expr = expr + currentRule
                
                if(i != rulesNumber)
                    expr = expr +  rules[rule].connective
            }
            i++;
        }
        console.log(expr)
        return expr
    }

    function profileCtrl ($location,authentication,djangoData,$mdDialog,$mdToast) {
		

        if(!authentication.isLoggedIn()){
            $location.path("/#");
            return;
        }

        var vm = this;
        vm.templates = []

        vm.currentUser = authentication.currentUser();
        
        djangoData.getServiceTemplates().success(function(data) {
            for(template in data){
                span = randomSpan()
            	tileTemplate = {
                    id: data[template].id,
            		title : data[template].title,
            		color: randomColor(),
            		rowspan: span,
            		colspan: span,
            	}
            	vm.templates.push(tileTemplate)
            }
            console.log(vm.templates)
        }).error(function (e) {
            console.log(e);
        });


        vm.showDetail = function(id){
            destination = "/templateDetail/"+id
            $location.path(destination);
        }


        vm.showCreateDialog = function(event) {
            var parentEl = angular.element(document.body);
                $mdDialog.show({
                parent: parentEl,
                targetEvent: event,
                templateUrl: '/static/angular/dialog/createTemplate.dialog.template.html',
                controller: CreateDialogController
            });
        }




        function CreateDialogController($scope, $mdDialog,$mdToast){

            $scope.classes = ['Constant']

            djangoData.getClasses()
                .success(function(data) {
                    console.log(data)
                    for(var classe in data)
                        $scope.classes.push(data[classe].data_type)
                })
                .error(function (e) {
                    $mdToast.show($mdToast.simple()
                        .textContent('Si è verificato un errore nella lettura delle calssi')                       
                        .hideDelay(3000)
                        .theme("error-toast")
                    );
                });

            $scope.operands = ['+','-','*','/']
            //$scope.connectives = ['and','or']
            $scope.types = ['Numeric']
            $scope.rulesNumber = 1;

            $scope.increaseRulesNumber = function(){
                if($scope.rulesNumber <=4)
                    $scope.rulesNumber++           
            }
            $scope.decreaseRulesNumber = function(){
                if($scope.rulesNumber >= 2)
                    $scope.rulesNumber--       
            }

            $scope.rules = {
                first:{
                    firstclass: '',
                    firstCostant: '',
                    operand: '',
                    secondclass: '',
                    secondCostant: '',
                    connective: ''
                },
                second:{
                    firstclass: '',
                    firstCostant: '',
                    operand: '',
                    secondclass: '',
                    secondCostant: '',
                    connective: ''
                },
                third:{
                    firstclass: '',
                    firstCostant: '',
                    operand: '',
                    secondclass: '',
                    secondCostant: '',
                    connective: ''
                },
                fourth:{
                    firstclass: '',
                    firstCostant: '',
                    operand: '',
                    secondclass: '',
                    secondCostant: '',
                    connective: ''
                },
                fifth:{
                    firstclass: '',
                    firstCostant: '',
                    operand: '',
                    secondclass: '',
                    secondCostant: ''
                },
                
            }
            
            $scope.template = {
                title: '',
                output_type: '',
                expression: ''
            }


            $scope.createTemplate = function() {
                if($scope.template.title == '' || $scope.template.output_type == '' || !checkRules($scope.rules,$scope.rulesNumber)){
                    $mdToast.show($mdToast.simple()
                        .textContent('E\' necessario inserire correttamente tutti i campi')                       
                        .hideDelay(3000)
                        .theme("error-toast")
                    );
                }
                else{
                    $scope.template.expression = createExpression($scope.rules,$scope.rulesNumber)
                    djangoData.createTemplate($scope.template).success(function(data) {
                        console.log(data)
                        $mdToast.show($mdToast.simple()
                            .textContent('Servizio creato con successo.')                       
                            .hideDelay(3000)
                            .theme("success-toast")
                        );
                        /*Aggiungo il nuovo servizio alla gridList*/
                
                        tileTemplate = {
                            id: data.id,
                            title : data.title,
                            color: randomColor(),
                            rowspan: randomSpan(),
                            colspan: randomSpan(),
                        }
                        vm.templates.push(tileTemplate)
                    }).error(function (e) {
                        $mdToast.show($mdToast.simple()
                            .textContent('Si è verificato un errore nell\'inserimento del servizio')                       
                            .hideDelay(3000)
                            .theme("error-toast")
                        );
                        console.log(e)
                    });

                    $mdDialog.hide();
                }
            }

            $scope.closeDialog = function() {
                $mdDialog.hide();
            }  
        }
		
		
		

    }

    

})();
