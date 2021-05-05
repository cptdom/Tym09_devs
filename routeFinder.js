const fs = require('fs');
const request = require('request');
let obj={ 
    locations:[]
}

let rawdatalokace = fs.readFileSync('locations.json');
let rawdatametro = fs.readFileSync('metrolokace.json');
let locations = JSON.parse(rawdatalokace).locations;
let metra = JSON.parse(rawdatametro).features;
console.log(metra[0].geometry.coordinates[0])

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
    request(`https://maps.googleapis.com/maps/api/distancematrix/json?origins=${propertyLat},${propertyLong}&destinations=${nejblizsiMetroLat},${nejblizsiMetroLong}&mode=transit&departure_time=1620111925&key=`, (err, res) => {
        if (err) { return console.log(err) }
        let response = (JSON.parse(res.body))
        console.log(response)
        console.log(response.rows)
        //obj.push(response)
        obj.locations.push(response)

    })
} 

setTimeout(function () {
    console.log("storing data") 
    let jsondata = JSON.stringify(obj);
    fs.writeFile("locationDistances.json", jsondata, "utf8", (err) => {
        if (err) throw err;
        console.log("The file has been saved!");
    });
}, 5000)