import React from 'react';
import { MapContainer, TileLayer, Polygon } from 'react-leaflet';
import "./map.css";


const mapElement = (props) => {

    const districtData = require('../../static/prague_districts_truncated.json')
    const fillBlueOptions = { fillColor: 'blue' }
    const center = [50.093245754000066, 14.427845018000048]

    return (
        <div className="MapContainer">
            <MapContainer center={center} zoom={11} scrollWheelZoom={false}>
                <TileLayer
                    attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>
                <Polygon pathOptions={fillBlueOptions} positions={districtData[props.district]}/>
            </MapContainer>
        </div>
    )
}


export default mapElement;

