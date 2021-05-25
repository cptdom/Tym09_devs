import React from 'react';
import logo from '../../static/FIS.png'
import './Footer.css';

const footer = (props) => {

    const placeholder = <p>FIS LOGO</p>

    return (
        <div className="Footer">
            <img className="Fis"src={logo} alt={placeholder} />
            <div className="Ann">Tato aplikace byla vytvořena v rámci studentského projektu</div>
            <div className="TymTag">4IT500 Team 09</div>
        </div>
    )
}


export default footer