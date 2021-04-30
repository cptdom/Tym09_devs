import React from 'react';
import './profil.css';
import Store from '../../store/store';
import { Redirect } from 'react-router-dom';

const profil = (props) => {

    let state = Store.getState()
    let content =  <div className="Profil"><p>profil</p></div>
    let gtfo = <Redirect to='/'/>
                

    return (
        <React.Fragment>
        {state.logged
        ? content
        : gtfo}
        </React.Fragment>
    )
}

export default profil;