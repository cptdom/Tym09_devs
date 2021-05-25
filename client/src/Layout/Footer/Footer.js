import React from 'react';
import logo from '../../static/FIS.png'
import './Footer.css';

const footer = (props) => {

    const placeholder = <p>FIS LOGO</p>

    return (
        <div className="Footer">
            <img className="Fis"src={logo} alt={placeholder} />
            <p>Tato aplikace byla vytvořena v rámci studentského projektu</p>
            <h1>4IT500 Team 09</h1>
        </div>
    )
}


export default footer