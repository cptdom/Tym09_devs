import React from 'react';
import './Navitem.css';
import {NavLink} from 'react-router-dom';

const navitem = (props) => {
    return (
        <li>{props.children}</li>
    )
}

export default navitem;