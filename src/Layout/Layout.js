import React from 'react';
import classes from './Layout.module.css';
import Navbar from './Navbar';

const layout = (props) => {
    return (
        <React.Fragment>
        <main className={classes.Content}>
            <Navbar/>
            {props.children}
        </main>
        </React.Fragment>
    )
}

export default layout;