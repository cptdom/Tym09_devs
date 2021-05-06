// 
const fs = require('fs'); 
const csv = require('csv-parser');
const request = require('request');



let addresses = []
let idcka = []
let obj={ 
    locations:[]
}
let souradnice
let i=0

fs.createReadStream('Jachym500.csv')
.pipe(csv())
.on('data', function(data){
    try {
        let adresa = data.street + ' ' + data.city_part + ' ' +data.city_part_number
        adresa = adresa.replace(/\s/g, "+")
        let idcko = data._id
        addresses.push(adresa)
        idcka.push(idcko)
        //perform the operation
    }
    catch(err) {
        //error handler
    }
    console.log(addresses)
})
.on('end',function(){
    let arrayLength = addresses.length
    for (let i = 0; i < arrayLength; i++) {  
        itemURI = encodeURI(addresses[i])
        request(`https://maps.googleapis.com/maps/api/geocode/json?address=${itemURI}&key=`, (err, res) => {
        if (err) { return console.log(err); }
        let location = (JSON.parse(res.body))
        try{
            souradnice= {
                id: idcka[i],
                loc: addresses[i],
                lat: location.results[0].geometry.location.lat,
                long: location.results[0].geometry.location.lng
            }
        }
        catch{
            souradnice= {
                id: idcka[i],
                loc: addresses[i],
                lat: 0,
                long: 0
            }
        }
        obj.locations.push(souradnice)
        }); 
    }
});

// json saving
setTimeout(function () {
    console.log("storing data") 
    let jsondata = JSON.stringify(obj);
    console.log(jsondata)
    fs.writeFile("Jachym500.json", jsondata, "utf8", (err) => {
        if (err) throw err;
        console.log("The file has been saved!");
    });
}, 60000)



