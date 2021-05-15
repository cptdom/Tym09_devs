import React from 'react';
import Backdrop from '../../helpers/Backdrop/Backdrop';
import './modal.css'


const Modal = (props) => {
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
                    <label>E-mail: <input type="text" value="testuser@test.com"></input></label>
                    <label>Heslo: <input type="password" value="eskere123"></input></label>
                </form>
                <p>Aplikace je v testovacím režimu. Momentálně nelze přidávat nové uživatele. Byl zřízen jeden uživatel pro účely testování.</p>
                <button className="Logger" onClick={props.login}>Přihlásit</button>
            </div>
        </React.Fragment>
    )
}

export default Modal;