import React from 'react';
import './trackerReview.css';

const TrackerReview = (props) => {

    const dummyHandler = () => {
        console.log("Hana von Schnabelhoff")
    }


    return (
        <div className="TrackerReview">
            <form action="">
                <h2>Přehled trackeru "{props.data.name}"</h2>
                <label>
                    Název: 
                    <input className="Immutable" type="text" value={props.data.name}/>
                </label>
            </form>
            <form action="">
                <label>
                    Město:  
                    <input className="Immutable" type="text" value={props.data.city}/>
                </label>
            </form>
            <form action="">
                <label>
                    Část:  
                    <input className="Immutable" type="text" value={props.data.district}>
                    </input>
                </label>
                <label>
                    Minimální dispozice:  
                    <input className="Immutable" type="text" value={props.data.propLow}>
                    </input>
                </label>
                <label>
                    Maximální dispozice:  
                    <input className="Immutable" type="text" value={props.data.propHigh}>
                    </input>
                </label>
                <label>
                    Reportovat  
                    <input className="Immutable" type="text" value={props.data.schedule}>
                    </input>
                </label>
            </form>
            <form action="">
                <label>
                    E-mail:  
                    <input className="Immutable" type="text" value={props.data.email}/>
                </label>
            </form>
            <button className="Delete" onClick={props.deleter}>Odstranit</button> 
            {/* props.deleter */}
            <button className="Close" onClick={props.closer}>Zavřít</button>
            </div>
    )
}


export default TrackerReview;