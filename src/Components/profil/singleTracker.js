import React from 'react';
import './singleTracker.css';

const singleTracker = (props) => {
    return (
        <div className="singleTracker" onClick={props.clicked}>
            <p>{props.name}</p>
        </div>
    )
}


export default singleTracker;