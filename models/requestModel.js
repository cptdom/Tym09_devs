const mongoose = require('mongoose')

const trackerSchema = {
    name: String,
    email: String,
    city: String,
    district: String,
    propLow: String,
    propHigh: String,
    schedule: String,
}

const Tracker = mongoose.model("Tracker", trackerSchema)



module.exports = Tracker