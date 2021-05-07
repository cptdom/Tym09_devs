import React, { useState, useEffect } from 'react';
import axios from '../../axios-firebase';
import Map from './map';
import './setWindow.css';

const SetWindow = (props) => {

    const districtSelectionArray = ["Praha 1", "Praha 2", "Praha 3", "Praha 4", "Praha 5"]
    //TODO: pozor, data v JSON jsou momentalne jen po Prahu 5
    const proportionsArray = ["1+kk","1+1","2+kk","2+1","3+kk","3+1"]
    const scheduleOptionsArray = {1: "1x denně"}
    


    const [state, changeState] = useState({
        "name": "Můj tracker",
        "email": "dummy@dummy.com",
        "city": "Praha",
        "district": districtSelectionArray[0],
        "propLow": proportionsArray[0],
        "propHigh": proportionsArray[proportionsArray.length-1],
        "schedule": 1,
         
    })

    //TODO: remove when tested on Mongo
    useEffect(() => {
        console.log(state)
    })


    const changeHandler = (event) => {
        changeState((prevState) => ({
            ...prevState,
            [event.target.id]: event.target.value,
        }));
    }

    const buttonHandler = (event) => {
        event.preventDefault();
        const toPush = Object.assign(state);
        axios.post('/realquik.json', toPush)
        .then( response => {
            console.log(`Data sent successfully with the following message: ${response.data}`);
        })
        .catch(error => {
            console.log(`An error occured with the following description: ${error}`)
            window.alert(`Někde se stala chyba, tracker ${toPush.name} nebyl uložen.`)
        })
        window.confirm(`Opravdu chcete odeslat tracker ${toPush.name}?`) && props.closeClick()
        window.alert(`Tracker ${toPush.name} odeslán.`)

    }

    let proportionsConstrainedArray = proportionsArray.slice(
        0,
        proportionsArray.indexOf(state.propHigh)+1);



    return (
        <div className="SetWindow">
            <form action="">
                <h2>Nový hlídač</h2>
                <label>
                    Název: 
                    <input id="name" className={state.name} type="text" value={state.name} onChange={changeHandler}/>
                </label>
            </form>
            <form action="">
                <label>
                    Město:  
                    <input className="Immutable" type="text" value={state.city}/>
                </label>
            </form>
            <form action="">
                <label>
                    Část:  
                    <select id="district" value={state.district} onChange={changeHandler}>
                        {districtSelectionArray.map(districtKey => (
                            <option value={districtKey}>{districtKey}</option>
                        ))}
                    </select>
                </label>
                <label>
                    Minimální dispozice:  
                    <select id="propLow" value={state.propLow} onChange={changeHandler}>
                        {proportionsConstrainedArray.map(key => (
                            <option value={key} id={key}>{key}</option>
                        ))}
                    </select>
                </label>
                <label>
                    Maximální dispozice:  
                    <select id="propHigh" value={state.propHigh} onChange={changeHandler}>
                        {proportionsArray.map(key => (
                            <option value={key} id={key}>{key}</option>
                        ))}
                    </select>
                </label>
                <label>
                    Reportovat  
                    <select id="schedule" value={scheduleOptionsArray[state.schedule]} onChange={changeHandler}>
                        {Object.keys(scheduleOptionsArray).map(key => (
                            <option value={key}>{scheduleOptionsArray[key]}</option>
                        ))}
                    </select>
                </label>
            </form>
            <form action="">
                <label>
                    E-mail:  
                    <input className="Immutable" type="text" value={state.email}/>
                </label>
            </form>
            <button className="Launch" onClick={buttonHandler}>Odeslat</button>
            <button className="Close" onClick={props.closeClick}>Zavřít</button>
            <Map district={state.district}/>
        </div>
    )
}


export default SetWindow;