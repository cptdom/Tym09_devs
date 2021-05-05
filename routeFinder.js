const fs = require('fs');

let rawdatalokace = fs.readFileSync('locations.json');
let rawdatametro = fs.readFileSync('metrolokace.json');

let locations = JSON.stringify(rawdatalokace);
let metra = JSON.stringify(rawdatametro);


for (let location of locations){
    console.log(location)
}