import React, { useState, useEffect } from 'react';
import './trackers.css';
import SingleTracker from './singleTracker';
import axios from '../../axios-firebase';




const Trackers = (props) => {

    const [state, changeState] = useState({
        data: [],
        trackerClicked: null,
    })

    useEffect(() => {
        axios.get('https://testwebapp-3ab8b-default-rtdb.europe-west1.firebasedatabase.app/realquik.json')
        .then((response) => {
            changeState((prevState) => ({
                ...prevState,
                data: response.data,
            }));
        })
        .catch((error) => {
            console.log(`An error occured with the following description: ${error}`)
        })
    }, [state.data])


    //TODO: REMOVE AFTER USEEFFECT HAS BEEN TESTED
    const listingHandler = () => {
        axios.get('https://testwebapp-3ab8b-default-rtdb.europe-west1.firebasedatabase.app/realquik.json')
        .then((response) => {
            changeState((prevState) => ({
                ...prevState,
                data: response.data,
            }));
        })
        .catch((error) => {
            console.log(`An error occured with the following description: ${error}`)
        })
    }

    const chooseTrackerHandler = (item) => {
        changeState((prevState)=>({
            ...prevState,
            trackerClicked: item,
        }))
    }

    //TODO: REMOVE WHEN NOT NEEDED
    const checkHandler = () => {
        console.log(state)
        console.log(state.data[state.trackerClicked])
    }


    return (
        <div className="Trackers">
            <h3 onClick={checkHandler}>Trackery</h3>
            <p className="Refresh"onClick={listingHandler}>obnovit seznam</p>
            {Object.keys(state.data).length>0 ? null : <p className="RefreshAlert">Obnovte seznam</p>}
            {Object.keys(state.data).map(item => (
                <SingleTracker name={state.data[item].name} key={state.data[item].name}
                    clicked={() => chooseTrackerHandler(item)}/>
                ))}
        </div>
    )
}

export default Trackers;