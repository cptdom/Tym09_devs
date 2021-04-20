import React from 'react';
import Navitem from './Navitem';
import './Navbar.css';
import {NavLink} from 'react-router-dom';


const navbar = (props) => {
    return (
        <div className="Navbar">
            <div className="LeftPanel">
                
            <div className="Logo"><NavLink to='/' style={{ textDecoration: 'none', color: 'snow' }} exact>RealQuik</NavLink></div>
                <Navitem>Produkt</Navitem>
                <Navitem>O nás</Navitem>
                <Navitem>Ceník</Navitem>
                <Navitem>Kontakt</Navitem>
            </div>
            
            <div className="RightPanel">
                <Navitem>Příhlášení</Navitem>
                <Navitem>Registrace</Navitem>
            </div>
            
        </div>
    )
}

export default navbar;