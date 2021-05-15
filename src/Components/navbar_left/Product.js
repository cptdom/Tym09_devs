import React from 'react';
import {connect} from 'react-redux';
import "./Product.css";

const Product = (props) => {
    return (
        <div className="Product">
            <div className="UpperSlider">
                <h3>Hledání dle požadavků</h3>
                <p>Naše hlídače budou hlídat dostupné nemovitosti podle <b>Vámi vybraných kritérií</b>.</p>
                <div className="Image0"/>
            </div>
            <div className="MiddleSlider">
                <div className="Image1"/>
                <div className="Card">
                <h3>Pravidelné hlášení do e-mailu</h3>
                <p>Veškeré výsledky Vám naservírujeme <b>přímo na Váš e-mail</b>. Tak často, jak budete chtít.</p>
                </div>
            </div>
            <div className="BottomSlider">
                <h3>Exkluzivní přehled o dění na trhu</h3>
                <p>Získáte přístup ke <b>sjednocenému přehledu</b> o dostupných nemovitostech na námi sledovaných trzích.</p>
                <div className="Image2"/>
            </div>
            <div className="More2" onClick={props.onInterested}><h2>Chci to zkusit</h2></div>
        </div>
    )
}

const mapStateToProps = state => {
    return {
        mdl: state.showModal,
    }
}

const mapDispatchToProps = dispatch => {
    return {
        onInterested: () => dispatch({type: 'SWITCH_LOGIN_MODAL'}),
    }
}


export default connect(mapStateToProps,mapDispatchToProps)(Product);