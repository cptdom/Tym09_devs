const fs = require('fs');
const request = require('request');
let obj={ 
    locations:[]
}

let rawdatalokace = fs.readFileSync('jachym500.json');
let rawdatametro = fs.readFileSync('metrolokace.json');
let locations = JSON.parse(rawdatalokace).locations;
let metra = JSON.parse(rawdatametro).features;

///
let propertyLat
let propertyLong
let defaultDistance = 99999999999999;
let nejblizsiMetroLat
let nejblizsiMetroLong
let nejblizsiMetroNazev
let currentMetroLat
let currentMetroLong
let distanceLat
let distanceLong
let distance 

///
for (let i = 0; i < locations.length; i++){
    propertyLat = locations[i].lat
    propertyLong = locations[i].long
    //console.log(locations[i].loc)
    defaultDistance = 99999999999999;
    for (let j = 0; j < metra.length; j++){
        currentMetroLat = metra[j].geometry.coordinates[1];
        currentMetroLong = metra[j].geometry.coordinates[0];
        distanceLat = Math.pow(propertyLat - currentMetroLat,2)
        distanceLong = Math.pow(propertyLong - currentMetroLong,2)
        distance = Math.sqrt(distanceLat + distanceLong)
        if (distance < defaultDistance){
            defaultDistance = distance
            nejblizsiMetroLat = currentMetroLat
            nejblizsiMetroLong = currentMetroLong
            nejblizsiMetroNazev = metra[j].properties.UZEL_NAZEV
        }
    }
    request(`https://maps.googleapis.com/maps/api/distancematrix/json?origins=${propertyLat},${propertyLong}&destinations=${nejblizsiMetroLat},${nejblizsiMetroLong}|50.082381,14.426107&mode=transit&departure_time=1620111925&key=`, (err, res) => {
        if (err) { return console.log(err) }
        let response = (JSON.parse(res.body))
        console.log(response)
        console.log(response.rows)
        let fittedResponse = {
            id: locations[i].id,
            response
        }
        //obj.push(response)
        obj.locations.push(fittedResponse)
    }) 
    console.log("Lat1: " + propertyLat)
    console.log("Lont1: "+ propertyLong)
} 

setTimeout(function () {
    console.log("storing data") 
    let jsondata = JSON.stringify(obj);
    fs.writeFile("JachymMetro.json", jsondata, "utf8", (err) => {
        if (err) throw err;
        console.log("The file has been saved!");
    });
}, 60000)