import React from 'react';
import Navitem from './Navitem';
import './Navbar.css';
import {NavLink} from 'react-router-dom';
import {connect} from 'react-redux';


const navbar = (props) => {

    const loggedPanel  = 
        <div className="RightPanel">
            <Navitem pathTo='/profile' redirect='/'>Profil</Navitem>
            <Navitem clicked={props.onLogout} pathTo='/'>Odhlásit</Navitem>
        </div>;
   
    
    const unloggedPanel  = 
        <div className="RightPanel">
            <Navitem clicked={props.onLogin}>Přihlášení</Navitem>
            <Navitem>Registrace</Navitem>
        </div>;



    return (
        <div className="Navbar">
            <div className="LeftPanel">
                
            <div className="Logo"><NavLink to='/' style={{ textDecoration: 'none', color: 'snow' }} exact>RealQuik</NavLink></div>
                <Navitem pathTo='/product'>Produkt</Navitem>
                <Navitem pathTo='/about'>O nás</Navitem>
                {/* <Navitem pathTo='/pricing'>Ceník</Navitem> */}
                <Navitem pathTo='/contact'>Kontakt</Navitem>
            </div>
            
            {props.lgn
            ? loggedPanel
            : unloggedPanel}


            {/* <div className="RightPanel">
                <Navitem>Přihlášení</Navitem>
                <Navitem>Registrace</Navitem>
            </div> */}
            
        </div>
    )
}

//REDUX STATE FOR DUMMY LOGIN/LOGOUT

const mapStateToProps = state => {
    return {
        lgn: state.logged
    }
}

const mapDispatchToProps = dispatch => {
    return {
        onLogin: () => dispatch({type: 'SWITCH_LOGIN_STATUS'}),
        onLogout: () => window.confirm("Opravdu se chcete odhlásit?") && dispatch({type: 'SWITCH_LOGIN_STATUS'}),
    }
}


export default connect(mapStateToProps, mapDispatchToProps)(navbar);