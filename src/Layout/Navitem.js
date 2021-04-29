import React from 'react';
import './Navitem.css';
import {NavLink} from 'react-router-dom';

const navitem = (props) => {

    const linkItem = <NavLink to={props.pathTo} exact style={{ textDecoration: 'none', color: 'snow' }}><li onClick={props.clicked}>{props.children}</li></NavLink>
    const unlinked = <li onClick={props.clicked}>{props.children}</li>
    
    
    return (
        <React.Fragment>
        {props.pathTo
        ? linkItem
        : unlinked}
        </React.Fragment>
        
    )
}

export default navitem;