const express = require('express')
const app = express();
const port = process.env.PORT || 3001
const cors = require('cors')
const mongoose = require('mongoose')
const path = require("path")
const router = require("./routes/trackerRoute")


app.use('*', cors())
app.use(express.json())


mongoose.connect(process.env.MONGODB_URI || "mongodb+srv://admin_domik:tym09ftw@cluster0.mtfak.mongodb.net/user_requests?retryWrites=true&w=majority",
 {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})

mongoose.connection.on('connected', () => {
    console.log("mongoose connected successfully.")
})

if (process.env.NODE_ENV === 'production') {
    app.use(router)
    app.use(express.static('client/build'))
    app.get("*", (req, res) => {
        res.sendFile(path.resolve(__dirname, "client", "build", "index.html"))
    })
}
else {
    app.use("/", require("./routes/trackerRoute"))
}




app.listen(port, () => {
    console.log(`The Express server is running on localhost:${port}`)
})