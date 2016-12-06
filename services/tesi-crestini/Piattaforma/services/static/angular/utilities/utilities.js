var markersArray = []

var idToClasses = {
	"TEMP":"Temperature",
	"HUMY":"Humidity",
	"PRES":"Pressure",
	"VOLT":"Voltage",
	"WIDR":"Wind_Direction",
	"WISP":"Wind_Speed",
    "GASL":"Gas_Level",
    "BRTH":"Brightness",
    "POWR":"Power",
    "RAIN":"Rain_Index",
    "COPR": "COPR",
    "NO2A": "NO2A",
    "NOXO": "NOXO",
    "O3OZ": "O3OZ",
    "PM10": "PM10"
}

var classesToId = {
    'Temperature' : 'TEMP',
    'Gas_Level': 'GASL',
    'Brightness': 'BRTH',
    'Power':'POWR',
    'Pressure': 'PRES' ,
    'Voltage': 'VOLT',
    'Rain_Index': 'RAIN',
    'Humidity': 'HUMY',
    'Wind_Direction': 'WIDR',
    'Wind_Speed': 'WISP',
    "COPR": "COPR",
    "NO2A": "NO2A",
    "NOXO": "NOXO",
    "O3OZ": "O3OZ",
    "PM10": "PM10"	
}



function getClassesId(sensors){
    var serviceClassID = [] 

    for(var i in sensors){
        serviceClassID.push(classesToId[sensors[i]])
    }
    console.log(serviceClassID)
    return serviceClassID
}


function getClassesByExpression(expr,classes){
    var serviceClass = [] 

    for(classe in classes){
        if(expr.indexOf(classes[classe]) >= 0)
            serviceClass.push(classes[classe])
    }

    return serviceClass
}


/*Funzione che controlla che tutte le classi necessarie siano presenti*/
function checkClasses(selected,foundedStreams,neededSensors){
    if(selected.length < neededSensors.length)
        return null

    /*Struttura di controllo in cui tengo il conteggio di quanti sensori di una classe ho selezionato */
    var controlStruct = {}
    for(var sensor in neededSensors){
        controlStruct[neededSensors[sensor]]={
            streams: []
        }
    }

    /*Per ogni stream trovato se è tra quelli selezionato allora aumento di uno il conteggio relativo alla classe*/
    for(var stream in foundedStreams){
        if(selected.indexOf(foundedStreams[stream].id) >= 0){
            controlStruct[foundedStreams[stream].data_class]["streams"].push(foundedStreams[stream])
        }
    }


    return controlStruct

}

/*Funzione per aggiungere le infowindow ai vari marker*/
function bindInfoWindow(marker, map, infowindow, description) {
    marker.addListener('click', function() {
        infowindow.setContent(description);
        infowindow.open(map, this);
    });
}

function clearMarkers() {
    for (var i = 0; i < markersArray.length; i++) {
      markersArray[i].marker.setMap(null);
    }
    markersArray = []
}

function selectMarker(id){
    for (var i = 0; i < markersArray.length; i++) {
        if(markersArray[i].id == id){
            markersArray[i].marker.setIcon('/static/img/beachflag.png');
        }
    }
}

function deselectMarker(id){
    for (var i = 0; i < markersArray.length; i++) {
        if(markersArray[i].id == id){
            markersArray[i].marker.setIcon();
        }
    }
}

function checkMarker(lat,lng){
    var myLatLng = new google.maps.LatLng(lat, lng);

    /*Controllo che nonci siano marker nella stessa posizione
    Ripetuto cinque volte con valori diversi perchè potrebbe esistere già un marker doppione*/
    for(var i in markersArray){
        if(markersArray[i].marker.getPosition().equals( new google.maps.LatLng(lat,lng+0.001600) ) ){
            myLatLng = new google.maps.LatLng(lat,lng+0.002000);
        }
        else if(markersArray[i].marker.getPosition().equals( new google.maps.LatLng(lat,lng+0.001200) ) ){
            myLatLng = new google.maps.LatLng(lat,lng+0.001600);
        }
        else if(markersArray[i].marker.getPosition().equals( new google.maps.LatLng(lat,lng+0.000800) ) ){
            myLatLng = new google.maps.LatLng(lat,lng+0.001200);
        }
        else if(markersArray[i].marker.getPosition().equals( new google.maps.LatLng(lat,lng+0.000400) ) ){
            myLatLng = new google.maps.LatLng(lat,lng+0.000800);
        }
        else if(markersArray[i].marker.getPosition().equals(myLatLng)){
            myLatLng = new google.maps.LatLng(lat,lng+0.000400);
        }
    }

    return myLatLng
}

/*Funzione per aggiungere un marker alla mappa*/
function addMarker(foundedStreams,stream,map,infowindow,vm){
    var contentString = '<div>'+
        '<h1>' + foundedStreams[stream].name +'</h1> <div >'+
        '<p>'+ foundedStreams[stream].description + '</p>'+
        '<p><i><b>(Last update: ' + foundedStreams[stream].last_update_timestamp +')</b></i> </p>' +
        '<button class="fab" onclick="selectOnInfoWindow(' + foundedStreams[stream].id +')"><img class="imgInfo" src="/static/img/icons/ic_mode_edit_white_24dp.png" /></button>' +
        '</div>';                             
   
    var lat = foundedStreams[stream].measurements[0].gps_latitude
    var lng = foundedStreams[stream].measurements[0].gps_longitude
    //var position = checkMarker(lat,lng)
    
    var position = checkMarker(lat,lng)
    

    var marker = new google.maps.Marker({
        map: map,
        position: position,
        title: foundedStreams[stream].name
    });


    markersArray.push({
        id: foundedStreams[stream].id,
        marker: marker   
    });
    
    bindInfoWindow(marker, map, infowindow,contentString);
}

function addServiceMarker(foundedStreams,stream,map,infowindow){
    console.log("St")
    console.log(foundedStreams[stream])
    var contentString = '<div>'+
        '<div>'+
        '</div>'+
        '<h1 >' + foundedStreams[stream].name +'</h1> <div >'+
        '<p>'+ foundedStreams[stream].description + '</p>'+
        '<p><i><b>(Last update: ' + foundedStreams[stream].last_update_timestamp +')</b></i></p>' +
        '</div>'+
        '</div>';                             
   
    var lat = foundedStreams[stream].measurements[0].gps_latitude
    var lng = foundedStreams[stream].measurements[0].gps_longitude
    //var position = checkMarker(lat,lng)
    
    var position = checkMarker(lat,lng)
    

    var marker = new google.maps.Marker({
        map: map,
        position: position,
        title: foundedStreams[stream].name
    });


    markersArray.push({
        id: foundedStreams[stream].id,
        marker: marker   
    });
    
    bindInfoWindow(marker, map, infowindow,contentString);
}
