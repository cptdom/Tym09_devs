import React, { Component } from 'react';
import classes from './Layout.module.css';
import Navbar from './Navbar';

const layout = (props) => {
    return (
        <main className={classes.Content}>
            <Navbar/>
            {props.children}
        </main>
    )
}

export default layout;