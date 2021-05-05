const fs = require('fs');

let rawdatalokace = fs.readFileSync('locationsTemp.json');
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
    console.log("Pro byt na " + locations[i].loc + " je nejblizsi metro " + nejblizsiMetroNazev + ' ' + nejblizsiMetroLat + ' ' + nejblizsiMetroLong  )
} 