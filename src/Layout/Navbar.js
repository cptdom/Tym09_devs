import React from 'react';
import Navitem from './Navitem';
import './Navbar.css';
import {NavLink} from 'react-router-dom';
import {connect} from 'react-redux';
import {useState} from 'react';
import Modal from '../Components/modal/modal';


const Navbar = (props) => {

    const [state, toggleLoginDisplay] = useState({
        showLogin: false,
    })

    const showLoginHandler = () => {
        toggleLoginDisplay((prevState => ({
            ...prevState,
            showLogin: !state.showLogin,
        })))
    }

    const logAndHideHandler = () => {
        props.onLogin()
        toggleLoginDisplay((prevState => ({
            ...prevState,
            showLogin: !state.showLogin,
        })))
    }

    const loggedPanel  = 
        <div className="RightPanel">
            <Navitem pathTo='/profile' redirect='/'>Profil</Navitem>
            <Navitem clicked={props.onLogout} pathTo='/'>Odhlásit</Navitem>
        </div>;
   
    //props.onLogin
    const unloggedPanel  = 
        <div className="RightPanel">
            <Navitem clicked={showLoginHandler}>Přihlášení</Navitem>
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
            <Modal show={state.showLogin} toggler={showLoginHandler} login={logAndHideHandler}/>
            
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
        onLogin: () => dispatch({type: 'SWITCH_LOGIN_STATUS'}) && window.alert("Úspěšně jste se přihlásil/a"),
        onLogout: () => window.confirm("Opravdu se chcete odhlásit?") && dispatch({type: 'SWITCH_LOGIN_STATUS'}),
    }
}


export default connect(mapStateToProps, mapDispatchToProps)(Navbar);