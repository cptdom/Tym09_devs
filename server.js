const express = require('express')
const app = express();

const cors = require('cors')
const mongoose = require('mongoose')


app.use('*', cors())
app.use(express.json())


mongoose.connect("mongodb+srv://admin_domik:tym09ftw@cluster0.mtfak.mongodb.net/user_requests?retryWrites=true&w=majority",
 {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})

app.use("/", require("./routes/trackerRoute"))


app.listen(3001, () => {
    console.log("The Express server is running on localhost:3001")
})