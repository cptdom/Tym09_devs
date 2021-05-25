const express = require('express')
const app = express();
const port = process.env.PORT || 3001
const cors = require('cors')
const mongoose = require('mongoose')
const path = require("path")


app.use('*', cors())
app.use(express.json())


mongoose.connect("mongodb+srv://admin_domik:tym09ftw@cluster0.mtfak.mongodb.net/user_requests?retryWrites=true&w=majority",
 {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})

if (process.env.NODE_ENV === 'production') {
    app.use(express.static('build'), require("./routes/trackerRoute"))
    app.get("*", (req, res) => {
        res.sendFile(path.resolve(__dirname, "/client/build/index.html"))
    })
}
else {
    app.use("/", require("./routes/trackerRoute"))
}




app.listen(port, () => {
    console.log(`The Express server is running on localhost:${port}`)
})