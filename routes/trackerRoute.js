const express = require("express")
const router = express.Router()
const Tracker = require("../models/requestModel")

router.route("/create").post((req, res) => {
    const name = req.body.name
    const email = req.body.email
    const city = req.body.city
    const district = req.body.district
    const propLow = req.body.propLow
    const propHigh = req.body.propHigh
    const schedule = req.body.schedule

    const newTracker = new Tracker({
        name,
        email,
        city,
        district,
        propLow,
        propHigh,
        schedule,
    })

    newTracker.save()
    .then(() => res.json({
        message: "Created tracker successfully"
    }))
    .catch(err => res.status(400).json({
        "error": err,
        "message": "Error creating tracker"
    }))
})


router.route("/trackers").get((req, res) => {
    Tracker.find()
    .then(response => {
        res.json(response)
        console.log("Data retrieved successfully")
    })
    .catch(error => {
        console.log(`An error occured during data retrieval: ${error}`)
    })
})

module.exports = router;