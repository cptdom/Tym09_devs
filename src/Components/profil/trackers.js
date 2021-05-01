import React, { useState, useEffect } from 'react';
import './trackers.css';
import SingleTracker from './singleTracker';
import axios from '../../axios-firebase';




const Trackers = (props) => {

    const [state, changeState] = useState([])


    useEffect(() => {
        axios.get('https://testwebapp-3ab8b-default-rtdb.europe-west1.firebasedatabase.app/realquik.json')
        .then((response) => {
            changeState(response.data);
        })
        .catch((error) => {
            console.log(`An error occured with the following description: ${error}`)
        })
    },[])


    return (
        <div className="Trackers">
            <h3>Trackery</h3>
            {Object.keys(state).map(item => (<SingleTracker name={state[item].name} key={state[item].name}/>))}
        </div>
    )
}

export default Trackers;