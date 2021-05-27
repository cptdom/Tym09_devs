import React, {useState} from 'react';
import Backdrop from '../../helpers/Backdrop/Backdrop';
import './modal.css'
import {useHistory} from 'react-router-dom';


const Modal = (props) => {

    const [state, changeState] = useState({
        password: "",
        correct: false,
    })

    const changeHandler = (event) => {
        changeState((prevState) => ({
            ...prevState,
            [event.target.id]: event.target.value,
        }));
    }
    const history = useHistory()

    const loginRedirectHandler = () => {
        props.login()
        history.push('/profile')
    }

    const password = "rootroot"


    return (
        <React.Fragment>
            <Backdrop show={props.show} clicked={props.clicked}/>
            <div className="Modal"
                style={{
                            transform: props.show ? 'translateY(0)' : 'translateY(-100vh)',
                            opacity: props.show ? '1' : '0'
                        }}>
                <div className="Closer" onClick={props.toggler}>Zavřít okno</div>
                <h2>RealQuik</h2>
                <h3>Přihlášení do aplikace</h3>
                <form action="" className="Form">
                    <label>E-mail: <input id="notok" type="text" value="testuser@test.com"></input></label>
                    <label>Heslo: <input id="password" className={state.password} type="password" value={state.password} onChange={changeHandler}/></label>
                </form>
                <p>Aplikace je v testovacím režimu. Momentálně nelze přidávat nové uživatele. Byl zřízen jeden uživatel pro účely testování.</p>
                <button className="Logger" onClick={state.password===password ? loginRedirectHandler : () => alert("Nesprávné heslo")}>Přihlásit</button>
            </div>
        </React.Fragment>
    )
}

export default Modal;