import React from 'react';
import './trackers.css';
import SingleTracker from './singleTracker';

const trackers = (props) => {
    return (
        <div className="Trackers">
            <p>Trackery</p>
            <SingleTracker/>
            <SingleTracker/>
            <SingleTracker/>
        </div>
    )
}

export default trackers;