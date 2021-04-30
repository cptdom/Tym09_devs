import React from 'react';
import { Route, Redirect } from 'react-router-dom';

//if needed later on, currently unused

const privateRoute = ({component: Component, authed, ...rest}) => {
    return (
        <Route 
        {...rest}
        render={(props) => authed === true
                ? <Component {...props} />
                : <Redirect to='/'  />} 
                />
    )
}

export default privateRoute