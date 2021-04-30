import React from 'react';
import './profil.css';
import Store from '../../store/store';
import { Redirect } from 'react-router-dom';
import Trackers from './trackers';
import SetWindow from './setWindow';

const profil = (props) => {

    let state = Store.getState()
    const content = 
        <div className="Profil">
            <Trackers/>
            <SetWindow/>
        </div>

    const gtfo = <Redirect to='/'/>
                

    return (
        <React.Fragment>
        {state.logged
        ? content
        : gtfo}
        </React.Fragment>
    )
}

export default profil;