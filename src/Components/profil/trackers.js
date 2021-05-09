import React, { useState, useEffect } from 'react';
import './trackers.css';
import SingleTracker from './singleTracker';
import axios from 'axios';
//import axios from '../../axios-firebase';


const Trackers = (props) => {

    const [state, changeState] = useState({
        data: [],
    })


    useEffect(() => {
        axios.get("/trackers")
        .then(res => 
            changeState((prevState) =>({
                ...prevState,
                data: res.data ? res.data : [],
            }))
        )
        .catch(error => {
            console.log(`An error occured with the following description: ${error}`)
        })
        .finally(console.log("Updating state"))
    },[])


    const listingHandler = () => {
        axios.get("/trackers")
        .then(res => 
            changeState((prevState) =>({
                ...prevState,
                data: res.data? res.data : [],
            }))
        )
        .catch(error => {
            console.log(`An error occured with the following description: ${error}`)
        })
        .finally(console.log("Updating state"))
    }



    return (
        <div className="Trackers" dataTransfer={state.trackerClicked}>
            <h3>Hlídače</h3>
            <p className="Refresh" onClick={listingHandler}>obnovit seznam</p>
            {Object.keys(state.data).length>0 ? null : <p className="RefreshAlert">Obnovte seznam nebo vytvořte hlídače</p>}
            {Object.keys(state.data).map(item => (
                <SingleTracker name={state.data[item].name} key={state.data[item].name}
                    clicked={() => props.passed(state.data[item], item)}/>
                ))}
        </div>
    )
}

export default Trackers;