// 
const fs = require('fs'); 
const csv = require('csv-parser');
const request = require('request');



let addresses = [];
let obj={ 
    locations:[]
}

fs.createReadStream('reality_df.csv')
.pipe(csv())
.on('data', function(data){
    try {
        let adresa = data.street + ' ' + data.city + ' ' +data.city_part
        adresa = adresa.replace(/\s/g, "+")
        addresses.push(adresa)
        //perform the operation
    }
    catch(err) {
        //error handler
    }
})
.on('end',function(){
    addresses.forEach(item => {  
        console.log(item)      
        itemURI = encodeURI(item)
        console.log(item)
        request(`https://maps.googleapis.com/maps/api/geocode/json?address=${itemURI}&key=`, (err, res) => {
        if (err) { return console.log(err); }
        let location = (JSON.parse(res.body))
        let souradnice= {
            loc: item,
            lat: location.results[0].geometry.location.lat,
            long: location.results[0].geometry.location.lng
        }
        console.log(souradnice)
        obj.locations.push(souradnice)
        }); 
    })
});

// json saving
setTimeout(function () {
    console.log("storing data") 
    let jsondata = JSON.stringify(obj);
    fs.writeFile("locations.json", jsondata, "utf8", (err) => {
        if (err) throw err;
        console.log("The file has been saved!");
    });
}, 60000)



