import React from 'react';
import './Navitem.css';
import {NavLink} from 'react-router-dom';

const navitem = (props) => {
    return (
        <li onClick={props.clicked}>{props.children}</li>
    )
}

export default navitem;