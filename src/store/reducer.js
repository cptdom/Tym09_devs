const initialState = {
    logged: false,
}


const reducer = (state = initialState, action) => {

    switch(action.type) {
        case "SWITCH_LOGIN_STATUS":
            return {
                ...state,
                logged: !state.logged,
            }
    }

    return state;
}


export default reducer;
