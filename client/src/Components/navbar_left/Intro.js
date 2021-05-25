import React from 'react';
import './Intro.css';
import {NavLink} from 'react-router-dom';
//import Product from './Product';

const intro = (props) => {
    return (
        <div className="Intro">
            <h1>Kupte perspektivní nemovitosti. Výhodně.</h1>
            <p>Najdeme je za Vás.</p>
            <div className="More"><NavLink to='/product' style={{margin: 'auto'}} exact><h2>Chci zjistit více</h2></NavLink></div>
        </div>
    )
}

export default intro;