import Store from '../../store/store';
import React from 'react';
import { Redirect, NavLink } from 'react-router-dom';
import DashboardWidget from './dashboardWidget';
import './dashboard.css';



const Dashboard = (props) => {

    let loginState = Store.getState()

    const content = <div className="DashboardBackground">
                        <NavLink to='/profile'><div className="UserLog">{loginState.username}</div></NavLink>
                        <NavLink to='/profile/dashboard'><div className="ToDashboard">Přehled trhu</div></NavLink>
                        <DashboardWidget/>
                    </div>
    const gtfo = <Redirect to='/'/>


    return (
        <React.Fragment>
        {loginState.logged
        ? content
        : gtfo}
        </React.Fragment>
    )
}


export default Dashboard