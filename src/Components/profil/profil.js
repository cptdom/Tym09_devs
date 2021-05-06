import React, { useState } from 'react';
import './profil.css';
import Store from '../../store/store';
import { Redirect } from 'react-router-dom';
import Trackers from './trackers';
import SetWindow from './setWindow';
import TrackerReview from './trackerReview';
import axios from '../../axios-firebase';

const Profil = (props) => {

    let loginState = Store.getState()

    const [state, changeState] = useState({
        displayNewTracker: false,
        dataFromChild: null,
        currentlyDisplayingId: null,
    })

    const newTrackerHandler = () => {
        changeState((prevState) => ({
            ...prevState,
            displayNewTracker: !state.displayNewTracker,
        }))
        resetShowTrackerToNull()
    }

    const showTrackerHandler = (data, name) => {
        changeState((prevState) => ({
            ...prevState,
            dataFromChild: data,
            currentlyDisplayingId: name,
        }))
    }

    const resetShowTrackerToNull = () => {
        changeState((prevState) => ({
            ...prevState,
            dataFromChild: null,
            currentlyDisplayingId: null,
        }))
    }

    const deleteSingleTrackerHandler = () => {
        let toBeDeleted = Object.assign(state.currentlyDisplayingId)
        let trackerName = Object.assign(state.dataFromChild.name)
        window.confirm(`Opravdu chcete smazat tracker ${trackerName}? Tato akce nejde zvrátit!`)
        && axios.delete(`https://testwebapp-3ab8b-default-rtdb.europe-west1.firebasedatabase.app/realquik/${toBeDeleted}.json`)
            .then((response) => {
                window.alert(`Tracker ${trackerName} byl úspěšně vymazán. Server response: ${response.status} ${response.statusText}`)
                console.log(response)
            })
            .catch((error) => {
                window.alert(`Někde se stala chyba. Server response: ${error}`)
            })
            .finally(resetShowTrackerToNull())
    }

    // const dummyHandler = () => {
    //     console.log(state)
    // }

    const trackerReview = state.dataFromChild ? <TrackerReview closer={resetShowTrackerToNull} deleter={deleteSingleTrackerHandler} data={state.dataFromChild}/>
    : <div className="Placeholder">Vyberte tracker nebo zvolte "Přidat nový"</div>


    const content = 
        <div className="Profil">
            <Trackers passed={showTrackerHandler}/>
            <button className="Addnew" onClick={newTrackerHandler}>Přidat nový</button>
            <div className="OutputFrame">
                {state.displayNewTracker ? <SetWindow closeClick={newTrackerHandler}/> : trackerReview}
            </div>
            
        </div>

    const gtfo = <Redirect to='/'/>
                

    return (
        <React.Fragment>
        {loginState.logged
        ? content
        : gtfo}
        </React.Fragment>
    )
}

export default Profil;